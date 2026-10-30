"""Authored synthetic accounting checks; no vehicle-model quality evidence."""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig

import pytest
from PIL import Image

from tools.evaluate_vision import evaluate as evaluate_impl, finding_digest, prepare, ratio, write_json

_pixels = BytesIO()
Image.new("RGB", (32, 32), "red").save(_pixels, format="JPEG")
IMAGE_BYTES = _pixels.getvalue()
IMAGE_DIGEST = sha256(IMAGE_BYTES).hexdigest()


def evaluate(report_paths, review_paths):
    return evaluate_impl(report_paths, review_paths, list({p.parent / "image.jpg" for p in report_paths}))


def finding(classification="OBSERVED"):
    return {"classification": classification, "component": "Synthetic square", "region": "Top left",
            "description": "Authored engineering fixture only.", "rationale": "Accounting self-test.",
            "confirmation": "No vehicle was evaluated.", "image_ids": ["front"], "confidence": None}


def report(findings=None):
    return {"schema_version": "local-inspection-v1", "outcome": "COMPLETED", "reason_code": "TEST",
            "reasons": [], "reference": {"house": "COPART", "url": "https://copart.com/lot/12345678", "lot_number": "12345678"},
            "images": [{"image_id": "front", "label": "Synthetic", "source_sha256": "b" * 64,
                        "inference_sha256": IMAGE_DIGEST, "width": 32, "height": 32}],
            "findings": [finding()] if findings is None else findings,
            "provenance": {"model": "synthetic:latest", "model_digest": "c" * 64,
                           "image_digests": {"front": IMAGE_DIGEST}, "generated_at": "2026-10-30T00:00:00Z", "elapsed_ms": 1}}


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    (path.parent / "image.jpg").write_bytes(IMAGE_BYTES)
    return path


def completed_review(path):
    review = prepare(path)
    review.update(dataset_id="authored-self-test", dataset_kind="ENGINEERING", reviewer_id="test-author",
                  reviewer_background="Synthetic test author; no automotive qualification asserted.",
                  independent_review_declared=True, permitted_evidence_declared=True,
                  reviewed_at="2026-10-30T00:01:00Z", visible_targets_complete=True)
    review["visible_targets"] = [{"target_id": "square", "component_code": "TEST_SQUARE",
                                  "description": "Synthetic square.", "image_ids": ["front"], "critical": True}]
    for item in review["adjudications"]:
        item.update(support="SUPPORTED", component_correct=True, evidence_correct=True,
                    target_ids=["square"], rationale="Synthetic accounting expectation.")
    return review


@pytest.fixture
def pair(tmp_path):
    rp = write(tmp_path / "report.json", report())
    review = completed_review(rp)
    return rp, write(tmp_path / "review.json", review), review


def test_complete_engineering_accounting_never_establishes_release_quality(pair):
    rp, ap, _ = pair
    result = evaluate([rp], [ap])
    assert result["evidence_state"] == "ENGINEERING_ONLY"
    assert result["release_quality_established"] is False
    assert result["metrics"]["visible_target_recall"] == "1.0000"
    assert result["metrics"]["observed_supported_fraction"] == "1.0000"
    assert result["metrics"]["critical_visible_targets_missed"] == 0


def test_vehicle_declaration_does_not_certify_qualification_or_release(pair):
    rp, ap, review = pair
    review["dataset_kind"] = "VEHICLE"
    write(ap, review)
    result = evaluate([rp], [ap])
    assert result["evidence_state"] == "REVIEW_ACCOUNTED"
    assert result["release_quality_established"] is False


@pytest.mark.parametrize("mutation", ["missing_review", "missing_claim", "truth_incomplete", "independence_missing", "permission_missing"])
def test_missing_evidence_never_yields_numeric_aggregate(pair, mutation):
    rp, ap, review = pair
    if mutation == "missing_claim": review["adjudications"] = []
    if mutation == "truth_incomplete": review["visible_targets_complete"] = False
    if mutation == "independence_missing": review["independent_review_declared"] = False
    if mutation == "permission_missing": review["permitted_evidence_declared"] = False
    write(ap, review)
    result = evaluate([rp], [] if mutation == "missing_review" else [ap])
    assert result["evidence_state"] == "INCOMPLETE"
    assert result["metrics"] is None


@pytest.mark.parametrize("field,value", [("model_digest", "d" * 64), ("prompt_version", "changed"),
                                         ("inference_image_digests", {"front": "e" * 64})])
def test_changed_model_prompt_or_image_refused(pair, field, value):
    rp, ap, review = pair
    review[field] = value
    write(ap, review)
    with pytest.raises(ValueError, match="exact model"):
        evaluate([rp], [ap])


def test_report_whitespace_change_breaks_raw_byte_binding(pair):
    rp, ap, _ = pair
    rp.write_bytes(rp.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="absent"):
        evaluate([rp], [ap])


@pytest.mark.parametrize("mutation", ["hash", "index", "duplicate_index", "target", "duplicate_target", "wrong_evidence", "unsupported_match"])
def test_invalid_adjudication_binding_refused(pair, mutation):
    rp, ap, review = pair
    claim = review["adjudications"][0]
    if mutation == "hash": claim["finding_sha256"] = "f" * 64
    if mutation == "index": claim["finding_index"] = 10
    if mutation == "duplicate_index": review["adjudications"].append(deepcopy(claim))
    if mutation == "target": claim["target_ids"] = ["not-a-target"]
    if mutation == "duplicate_target": review["visible_targets"].append(deepcopy(review["visible_targets"][0]))
    if mutation == "wrong_evidence": review["visible_targets"][0]["image_ids"] = ["not-an-image"]
    if mutation == "unsupported_match": claim["support"] = "UNSUPPORTED"
    write(ap, review)
    with pytest.raises(ValueError): evaluate([rp], [ap])


def test_unknown_cannot_hide_critical_visible_miss(tmp_path):
    rp = write(tmp_path / "r.json", report([finding("UNKNOWN")]))
    review = completed_review(rp)
    review["adjudications"][0].update(support="ABSTENTION", target_ids=[])
    ap = write(tmp_path / "a.json", review)
    metrics = evaluate([rp], [ap])["metrics"]
    assert metrics["unknown_abstentions"] == 1
    assert metrics["observed_supported_fraction"] is None
    assert metrics["visible_target_recall"] == "0.0000"
    assert metrics["critical_visible_targets_missed"] == 1


def test_suspected_does_not_count_as_observed_detection(tmp_path):
    rp = write(tmp_path / "r.json", report([finding("SUSPECTED")]))
    ap = write(tmp_path / "a.json", completed_review(rp))
    metrics = evaluate([rp], [ap])["metrics"]
    assert metrics["suspected_claims_not_counted_as_detections"] == 1
    assert metrics["visible_target_recall"] == "0.0000"
    assert metrics["critical_visible_targets_missed"] == 1


def test_empty_truth_and_findings_yield_no_fake_perfect_precision_or_recall(tmp_path):
    rp = write(tmp_path / "r.json", report([]))
    review = completed_review(rp)
    review["visible_targets"] = []
    ap = write(tmp_path / "a.json", review)
    metrics = evaluate([rp], [ap])["metrics"]
    assert metrics["observed_supported_fraction"] is None
    assert metrics["visible_target_recall"] is None
    assert metrics["reports_without_observed_or_suspected_claims"] == 1


@pytest.mark.parametrize("support,component,evidence", [("UNSUPPORTED", False, False), ("INDETERMINATE", False, False),
                                                       ("SUPPORTED", False, True), ("SUPPORTED", True, False)])
def test_incorrect_or_indeterminate_claim_reduces_supported_fraction(pair, support, component, evidence):
    rp, ap, review = pair
    review["adjudications"][0].update(support=support, component_correct=component, evidence_correct=evidence, target_ids=[])
    write(ap, review)
    metrics = evaluate([rp], [ap])["metrics"]
    assert metrics["observed_supported_fraction"] == "0.0000"
    assert metrics["critical_visible_targets_missed"] == 1


def test_duplicates_and_orphan_reviews_refused(pair, tmp_path):
    rp, ap, _ = pair
    with pytest.raises(ValueError, match="Duplicate report"): evaluate([rp, rp], [ap])
    with pytest.raises(ValueError, match="Exactly one"): evaluate([rp], [ap, ap])
    extra = write(tmp_path / "extra.json", report([]))
    with pytest.raises(ValueError, match="absent"): evaluate([extra], [ap])


def test_different_model_cohorts_refused(pair, tmp_path):
    rp, ap, _ = pair
    other = report([])
    other["provenance"]["model_digest"] = "f" * 64
    other_path = write(tmp_path / "other.json", other)
    with pytest.raises(ValueError, match="Separate model"): evaluate([rp, other_path], [ap])


def test_repeated_image_cohort_cannot_be_inflated_by_changed_report_timestamp(pair, tmp_path):
    rp, ap, _ = pair
    repeated = report()
    repeated["provenance"]["generated_at"] = "2026-10-30T00:05:00Z"
    other_path = write(tmp_path / "repeat.json", repeated)
    with pytest.raises(ValueError, match="Repeated inference image sets"):
        evaluate([rp, other_path], [ap])


def test_reordered_images_and_changed_ids_cannot_inflate_cohort(tmp_path):
    original = report([])
    second_image = deepcopy(original["images"][0])
    second_image.update(image_id="side", inference_sha256="d" * 64)
    original["images"].append(second_image)
    original["provenance"]["image_digests"]["side"] = "d" * 64
    first_path = write(tmp_path / "first.json", original)
    repeated = deepcopy(original)
    repeated["images"].reverse()
    repeated["images"][0]["image_id"] = "renamed"
    repeated["provenance"]["image_digests"] = {"renamed": "d" * 64, "front": IMAGE_DIGEST}
    repeated_path = write(tmp_path / "repeat.json", repeated)
    with pytest.raises(ValueError, match="Repeated inference image sets"):
        evaluate([first_path, repeated_path], [])


def test_failed_reports_are_counted_not_turned_into_success(tmp_path):
    value = report()
    value.update(outcome="FAILED", findings=[], images=[], provenance=None)
    rp = write(tmp_path / "failure.json", value)
    result = evaluate([rp], [])
    assert result["evidence_state"] == "INCOMPLETE"
    assert result["failed_or_blocked_report_count"] == 1
    assert result["metrics"] is None
    with pytest.raises(ValueError, match="completed"): prepare(rp)


def test_finding_hash_is_key_order_independent():
    assert finding_digest({"b": 1, "a": 2}) == finding_digest({"a": 2, "b": 1})


def test_outputs_never_overwrite_existing_evidence(tmp_path):
    path = tmp_path / "result.json"
    write_json(path, {"x": 1})
    with pytest.raises(FileExistsError): write_json(path, {"x": 2})
    assert json.loads(path.read_text())["x"] == 1


def test_incomplete_cli_exits_two_and_preparation_is_intentionally_invalid(pair, tmp_path):
    rp, _, _ = pair
    script = Path(__file__).parents[1] / "evaluate_vision.py"
    result = subprocess.run([sys.executable, str(script), "evaluate", "--reports", str(rp)], capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["metrics"] is None
    draft = tmp_path / "draft.json"
    result = subprocess.run([sys.executable, str(script), "prepare", str(rp), "--output", str(draft)], capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(draft.read_text())["visible_targets_complete"] is False


def test_checkout_cli_does_not_require_editable_install_or_pth_activation(pair, tmp_path):
    rp, _, _ = pair
    script = Path(__file__).parents[1] / "evaluate_vision.py"
    # -S skips site initialization, including editable-install .pth activation.
    # Expose pinned dependencies only, with no inherited repository PYTHONPATH.
    env = {**os.environ, "PYTHONPATH": sysconfig.get_paths()["purelib"]}
    probe = subprocess.run([sys.executable, "-S", "-c", "import app"],
                           cwd=tmp_path, env=env, capture_output=True, text=True)
    assert probe.returncode != 0
    assert "No module named 'app'" in probe.stderr
    help_result = subprocess.run([sys.executable, "-S", str(script), "--help"],
                                 cwd=tmp_path, env=env, capture_output=True, text=True)
    assert help_result.returncode == 0, help_result.stderr
    result = subprocess.run([sys.executable, "-S", str(script), "evaluate", "--reports", str(rp)],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout)["evidence_state"] == "INCOMPLETE"


def test_decimal_ratios_are_explicit_and_no_zero_division():
    assert ratio(2, 3) == "0.6667"
    assert ratio(0, 0) is None


def test_missing_exact_inference_pixels_withholds_metrics(pair):
    rp, ap, _ = pair
    result = evaluate_impl([rp], [ap], [])
    assert result["evidence_state"] == "INCOMPLETE"
    assert result["metrics"] is None
    assert result["incomplete"][0]["reason"] == "MISSING_EXACT_INFERENCE_IMAGE_BYTES"


def test_different_image_bytes_do_not_satisfy_evidence_gate(pair, tmp_path):
    rp, ap, _ = pair
    pixels = BytesIO()
    Image.new("RGB", (32, 32), "blue").save(pixels, format="JPEG")
    wrong = tmp_path / "wrong.jpg"
    wrong.write_bytes(pixels.getvalue())
    result = evaluate_impl([rp], [ap], [wrong])
    assert result["metrics"] is None
    assert result["unmatched_image_artifact_count"] == 1


def test_non_raster_artifact_refused(pair, tmp_path):
    rp, ap, _ = pair
    invalid = tmp_path / "not-image.jpg"
    invalid.write_bytes(b"synthetic invalid bytes")
    with pytest.raises(OSError): evaluate_impl([rp], [ap], [invalid])
