"""Stable content preconditions, not permission tokens or client identity assertions."""
import hashlib
import json

from app.domain.models import ResolutionResult


def content_projection(result: ResolutionResult) -> dict:
    return {
        "binding_version": "inspection-target-v1",
        "provider_id": result.provider_context.id,
        "provider_mode": result.provider_context.mode,
        "identity": result.identity.model_dump(mode="json") if result.identity else None,
        "record_id": result.record_id,
        "event_id": result.event_id,
        "event_status": result.event_status,
        "event_date": result.event_date,
        "vehicle": result.vehicle.model_dump(mode="json") if result.vehicle else None,
        "source_reference": result.provenance.source_url if result.provenance else None,
        "data_type": result.provenance.data_type if result.provenance else None,
    }


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def stable_snapshot_fingerprint(result: ResolutionResult) -> str | None:
    if result.status != "MATCHED" or not result.identity or not result.vehicle or not result.provenance or not result.record_id:
        return None
    projection = content_projection(result)
    projection["reference"] = {
        "house": result.reference.house,
        "page_id": result.reference.page_id,
        "country": result.reference.country,
        "lot_number": result.reference.lot_number,
        "stock_number": result.reference.stock_number,
    }
    projection["source_provenance"] = result.provenance.model_dump(mode="json", exclude={"retrieved_at"})
    projection["provider_contract_version"] = result.provider_context.contract_version
    projection["mapping_evidence"] = result.mapping_evidence.model_dump(mode="json") if result.mapping_evidence else None
    projection["reference_evidence"] = result.reference_evidence.model_dump(mode="json") if result.reference_evidence else None
    projection["field_evidence"] = {key: value.model_dump(mode="json") for key, value in sorted(result.field_evidence.items())}
    return digest(projection)
