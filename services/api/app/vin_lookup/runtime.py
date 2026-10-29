"""One fixed official HTTPS destination, normal proxy/TLS policy and bounded reads."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

SOURCE_ROOT = "https://vpic.nhtsa.dot.gov"
MAX_RESPONSE_BYTES = 1024 * 1024


class VinSourceFailure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def source_url(vin: str) -> str:
    # Validate again at the transport boundary, including direct/internal callers.
    if len(vin) != 17 or any(char not in "0123456789ABCDEFGHJKLMNPRSTUVWXYZ" for char in vin):
        raise VinSourceFailure("INVALID_REQUEST", "A complete syntactically valid VIN is required.")
    return f"{SOURCE_ROOT}/api/vehicles/DecodeVinValues/{vin}?format=json"


class VpicClient:
    def request_json(self, vin: str) -> dict:
        request = Request(source_url(vin), headers={
            "Accept": "application/json", "User-Agent": "AuctionIntelligence-VIN-Enrichment/0.5",
        })
        try:
            # Default HTTPS verification and configured network proxies remain active.
            with build_opener(NoRedirect()).open(request, timeout=10) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise VinSourceFailure("RESPONSE_TOO_LARGE", "Manufacturer metadata exceeded its response limit.")
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata could not be validated.")
                return value
        except VinSourceFailure:
            raise
        except HTTPError as exc:
            raise VinSourceFailure("SOURCE_UNAVAILABLE", "The manufacturer metadata service could not complete this request.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise VinSourceFailure("SOURCE_UNAVAILABLE", "The manufacturer metadata service is unavailable or timed out.") from exc
        except (ValueError, UnicodeError) as exc:
            raise VinSourceFailure("INVALID_RESPONSE", "Manufacturer metadata could not be validated.") from exc
