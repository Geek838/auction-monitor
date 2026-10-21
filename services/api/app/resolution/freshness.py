"""Age assessment uses source observation, never retrieval as a freshness proxy."""
from datetime import datetime

from app.domain.models import Freshness, VehicleSnapshot


def assess_freshness(snapshot: VehicleSnapshot, *, now: datetime,
                     threshold_seconds: int | None = None, basis: str | None = None) -> Freshness:
    source = snapshot.provenance.source_observed_at
    common = dict(source_observed_at=source, evaluated_at=now, threshold_seconds=threshold_seconds)
    if snapshot.event_status in {"ARCHIVED", "SOLD"}:
        return Freshness(status="HISTORICAL", basis="Historical sold/archived auction event; recent retrieval cannot make it current.", **common)
    if source is None or source > now:
        return Freshness(status="UNKNOWN", basis="Source observation time is absent or invalid; retrieval time is not source freshness.", **common)
    if threshold_seconds is None or not basis:
        return Freshness(status="UNKNOWN", basis="No reviewed source-age threshold is configured.", **common)
    age = (now - source).total_seconds()
    return Freshness(status="STALE" if age > threshold_seconds else "FRESH", basis=basis, **common)
