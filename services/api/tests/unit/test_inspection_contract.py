"""Inspection output is untrusted until evidence links and bounded fields validate."""
from copy import deepcopy
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.inspections.models import InspectionFinding, InspectionPreview, Localization, PreviewRequest

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc).isoformat()
DIGEST = "a" * 64
OTHER_DIGEST = "b" * 64


def finding(**updates):
    data = dict(finding_id="authored-mark", classification="OBSERVED", region="Front",
                component="Illustrated bumper", description="A rust-colored split is drawn in the front illustration.",
                rationale="Hand-authored fixture observation, not analysis of a vehicle.", severity="MINOR",
                image_ids=["front-illustration-v1"], confirmation="Inspect the actual vehicle to establish its condition.")
    data.update(updates)
    return data


def report_data():
    return dict(request_id="test-request", outcome="COMPLETED", reason_code="MOCK_PREVIEW",
        resolver_status="MATCHED", target=dict(
            reference=dict(house="COPART", url="https://copart.com/lot/51374586", lot_number="51374586"),
            provider_context=dict(id="fixture", name="Synthetic test", mode="FIXTURE",
                authorization="NOT_REQUIRED", enabled=True, available=True, reasons=[]),
            identity=dict(house="COPART", lot_or_stock_number="51374586"), record_id="fixture-record",
            event_id="fixture-event", snapshot_fingerprint=DIGEST, content_fingerprint=DIGEST, retrieved_at=NOW),
        assets=[dict(asset_id="front-illustration-v1", title="Authored front illustration",
            alt_text="Synthetic front vehicle diagram with an authored rust-colored mark", view_label="FRONT",
            content_sha256=OTHER_DIGEST, width=960, height=600, author="Project-authored synthetic test",
            rights_reference="fixture://authored-demo-rights", asset_url="/api/v1/inspection-assets/front-illustration-v1")],
        findings=[finding()], checks=["Obtain a qualified physical inspection."],
        limitations=["Synthetic fixture, not a vehicle inspection."],
        provenance=dict(scenario_id="synthetic-case", generated_at=NOW, target_digest=DIGEST,
                        image_digests={"front-illustration-v1": OTHER_DIGEST}))


@pytest.mark.parametrize("body", [
    {"url": "https://copart.com/lot/51374586"},
    {"url": "https://copart.com/lot/51374586", "expected_snapshot_fingerprint": "not-a-digest"},
    {"url": "https://copart.com/lot/51374586", "expected_snapshot_fingerprint": DIGEST, "status": "MATCHED"},
    {"url": "https://copart.com/lot/51374586", "expected_snapshot_fingerprint": DIGEST, "provider": "licensed"},
    {"url": "https://copart.com/lot/51374586", "expected_snapshot_fingerprint": DIGEST, "image_url": "http://127.0.0.1/private"},
    {"url": "https://copart.com/lot/51374586", "expected_snapshot_fingerprint": DIGEST, "findings": []},
])
def test_preview_request_cannot_omit_precondition_or_supply_authority_and_evidence(body):
    with pytest.raises(ValidationError):
        PreviewRequest.model_validate(body)


@pytest.mark.parametrize("classification", ["OBSERVED", "SUSPECTED"])
def test_non_unknown_findings_require_image_evidence(classification):
    with pytest.raises(ValidationError):
        InspectionFinding.model_validate(finding(classification=classification, image_ids=[]))


def test_unknown_is_explicit_and_does_not_invent_a_model_confidence():
    item = InspectionFinding.model_validate(finding(classification="UNKNOWN", image_ids=[], severity="UNKNOWN",
        description="Airbag function cannot be established from an illustration.",
        rationale="No diagnostic evidence is supplied.", confirmation="Ask a qualified specialist to inspect SRS."))
    assert item.confidence is None
    assert item.localization is None


@pytest.mark.parametrize("updates", [
    {"confidence": 0.99}, {"price": 500}, {"oem_part_number": "invented-part"},
    {"classification": "SAFE"}, {"severity": "CERTAIN"},
    {"description": "This vehicle is safe to drive."},
    {"rationale": "There is no hidden damage."},
    {"confirmation": "The structure is sound."},
])
def test_unsupported_confidence_financial_fields_and_safety_assertions_are_rejected(updates):
    with pytest.raises(ValidationError):
        InspectionFinding.model_validate(finding(**updates))


@pytest.mark.parametrize("updates", [
    {"x": -0.01}, {"x": float("nan")}, {"width": float("inf")}, {"width": 0},
    {"x": 0.9, "width": 0.2}, {"y": 0.9, "height": 0.2},
    {"verified_by": " "}, {"review_basis": ""},
])
def test_localization_needs_bounded_geometry_and_an_actual_review_reference(updates):
    data = dict(asset_id="front-illustration-v1", content_sha256=OTHER_DIGEST,
        x=0.1, y=0.2, width=0.3, height=0.4,
        verified_by="Synthetic fixture author", review_basis="Authored fixture dimensions and shape review")
    data.update(updates)
    with pytest.raises(ValidationError):
        Localization.model_validate(data)


@pytest.mark.parametrize("change", ["dangling-image", "target-digest", "asset-digest", "duplicate-image", "wrong-localization"])
def test_report_cannot_attach_findings_or_provenance_to_different_evidence(change):
    data = report_data()
    InspectionPreview.model_validate(data)  # Negative mutations start from a valid contract.
    if change == "dangling-image":
        data["findings"][0]["image_ids"] = ["another-vehicle-image"]
    elif change == "target-digest":
        data["provenance"]["target_digest"] = OTHER_DIGEST
    elif change == "asset-digest":
        data["provenance"]["image_digests"]["front-illustration-v1"] = DIGEST
    elif change == "duplicate-image":
        data["assets"].append(deepcopy(data["assets"][0]))
    else:
        data["findings"][0]["localization"] = dict(asset_id="front-illustration-v1", content_sha256=DIGEST,
            x=0.1, y=0.1, width=0.2, height=0.2, verified_by="Fixture author", review_basis="Synthetic review")
    expected = {
        "dangling-image": "outside this report", "target-digest": "target digest",
        "asset-digest": "image digests", "duplicate-image": "Duplicate image IDs",
        "wrong-localization": "Localization must match",
    }[change]
    with pytest.raises(ValidationError, match=expected):
        InspectionPreview.model_validate(data)


@pytest.mark.parametrize("outcome", ["BLOCKED", "FAILED"])
def test_failure_outcomes_cannot_smuggle_a_successful_report(outcome):
    data = report_data()
    data["outcome"] = outcome
    with pytest.raises(ValidationError):
        InspectionPreview.model_validate(data)


def test_mock_preview_keeps_real_model_and_prompt_identifiers_absent():
    preview = InspectionPreview.model_validate(report_data())
    assert preview.provenance.mode == "MOCK"
    assert preview.provenance.model_provider is None
    assert preview.provenance.model_id is None
    assert preview.provenance.prompt_version is None
    assert preview.findings[0].confidence is None
    assert preview.findings[0].localization is None
