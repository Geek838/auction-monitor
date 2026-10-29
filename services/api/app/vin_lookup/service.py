"""Decode user-supplied VIN manufacturing facts without inventing auction identity."""
import asyncio
from datetime import datetime, timezone
import re
from threading import BoundedSemaphore

from app.vin_lookup.models import DecodeError, DecodedVehicle, VinDecodeReport, VinDecodeRequest
from app.vin_lookup.runtime import VpicClient, VinSourceFailure, source_url

REQUEST_SLOTS = BoundedSemaphore(2)
WARNINGS = [
    "NHTSA vPIC reports manufacturer-submitted specifications, not auction records, ownership, accident history or vehicle condition.",
    "Decoding a user-entered VIN does not verify the VIN on a physical vehicle or match a Copart/IAAI lot, page, stock or sale event.",
    "Missing decoded values mean the source lacks that information; they do not establish that a feature is absent.",
    "This lookup uses the entered VIN with the official NHTSA service; no photos or review notes are included.",
]


def _text(value) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str) or len(value) > 200:
        raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata could not be validated.")
    return value.strip() or None


def _decode(request: VinDecodeRequest) -> VinDecodeReport:
    report = VinDecodeReport(vin=request.vin, outcome="UNAVAILABLE", source_url=source_url(request.vin),
                             retrieved_at=datetime.now(timezone.utc), warnings=list(WARNINGS))
    if not REQUEST_SLOTS.acquire(blocking=False):
        report.errors = [DecodeError(code="BUSY", description="Two manufacturer metadata requests are already in progress; retry shortly.")]
        return report
    try:
        body = VpicClient().request_json(request.vin)
        results = body.get("Results")
        if type(body.get("Count")) is not int or body["Count"] != 1 or not isinstance(results, list) or len(results) != 1 or not isinstance(results[0], dict):
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata did not identify a single requested VIN response.")
        row = results[0]
        if row.get("VIN") != request.vin:
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata did not match the requested VIN.")
        raw_codes = row.get("ErrorCode")
        if not isinstance(raw_codes, str) or not re.fullmatch(r"\s*\d+(?:\s*,\s*\d+)*\s*", raw_codes) or len(raw_codes) > 200:
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata omitted a usable decode outcome.")
        codes = list(dict.fromkeys(code.strip() for code in raw_codes.split(",")))
        make, model = _text(row.get("Make")), _text(row.get("Model"))
        year_text = _text(row.get("ModelYear"))
        if year_text is not None and (not re.fullmatch(r"[0-9]{4}", year_text) or not 1886 <= int(year_text) <= datetime.now(timezone.utc).year + 2):
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata returned an unsupported model year.")
        report.vehicle = DecodedVehicle(year=int(year_text) if year_text else None, make=make, model=model)
        error_text = row.get("ErrorText")
        if not isinstance(error_text, str) or len(error_text) > 3000:
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata returned an invalid error description.")
        report.errors = [DecodeError(code=code, description=error_text[:1200]) for code in codes if code != "0"]
        complete = make is not None and model is not None and report.vehicle.year is not None
        report.outcome = "DECODED" if complete and codes == ["0"] else ("PARTIAL" if any((make, model, year_text)) or codes == ["0"] else "INVALID_VIN")
        if report.outcome == "PARTIAL":
            report.warnings.append("The source returned incomplete facts or decode errors. Review its errors before applying any details.")
        return report
    except VinSourceFailure as exc:
        report.vehicle = DecodedVehicle()
        report.outcome = "UNAVAILABLE"
        report.errors = [DecodeError(code=exc.code, description=exc.message)]
        return report
    except (TypeError, ValueError, KeyError, AttributeError):
        report.vehicle = DecodedVehicle()
        report.outcome = "UNAVAILABLE"
        report.errors = [DecodeError(code="INVALID_RESPONSE", description="Manufacturer metadata could not be validated.")]
        return report
    finally:
        report.retrieved_at = datetime.now(timezone.utc)
        REQUEST_SLOTS.release()


async def decode_vin(request: VinDecodeRequest) -> VinDecodeReport:
    return await asyncio.to_thread(_decode, request)
