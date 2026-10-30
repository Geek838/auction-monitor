"""Offline human-adjudication accounting; never an automatic vehicle-quality certification."""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationError
from PIL import Image

# The documented setup installs pinned dependencies, not this repository as an
# editable package. Resolve its API contracts from this checkout, regardless of
# the caller's working directory or unrelated installed versions of ``app``.
API_SOURCE_ROOT = Path(__file__).resolve().parents[1] / "services" / "api"
sys.path.insert(0, str(API_SOURCE_ROOT))
from app.local_vision.models import LocalInspectionReport

MAX_FILE_BYTES = 4 * 1024 * 1024


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VisibleTarget(StrictModel):
    target_id: str = Field(min_length=1, max_length=80)
    component_code: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1200)
    image_ids: list[str] = Field(min_length=1, max_length=3)
    critical: bool = Field(strict=True)


class Adjudication(StrictModel):
    finding_index: int = Field(strict=True, ge=0, le=19)
    finding_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    support: Literal["SUPPORTED", "UNSUPPORTED", "INDETERMINATE", "ABSTENTION"]
    component_correct: bool = Field(strict=True)
    evidence_correct: bool = Field(strict=True)
    target_ids: list[str] = Field(max_length=20)
    rationale: str = Field(min_length=1, max_length=1200)


class Review(StrictModel):
    schema_version: Literal["vision-adjudication-v1"]
    report_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    dataset_id: str = Field(min_length=1, max_length=100)
    dataset_kind: Literal["ENGINEERING", "VEHICLE"]
    reviewer_id: str = Field(min_length=1, max_length=100)
    reviewer_background: str = Field(min_length=1, max_length=1200)
    independent_review_declared: bool = Field(strict=True)
    permitted_evidence_declared: bool = Field(strict=True)
    reviewed_at: AwareDatetime
    model_digest: str
    prompt_version: str
    inference_image_digests: dict[str, str]
    visible_targets_complete: bool = Field(strict=True)
    visible_targets: list[VisibleTarget] = Field(max_length=100)
    adjudications: list[Adjudication] = Field(max_length=20)


def finding_digest(finding: dict) -> str:
    """Stable content binding, independent of JSON whitespace and key ordering."""
    return sha256(json.dumps(finding, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError(f"{path}: file exceeds 4 MiB")
    return raw


def read_report(path: Path) -> tuple[str, LocalInspectionReport]:
    raw = read_bytes(path)
    return sha256(raw).hexdigest(), LocalInspectionReport.model_validate_json(raw)


def prepare(path: Path) -> dict:
    digest, report = read_report(path)
    if report.outcome != "COMPLETED":
        raise ValueError("Only a completed local report can be prepared for visual adjudication.")
    provenance = report.provenance
    assert provenance is not None
    return {
        "schema_version": "vision-adjudication-v1", "report_sha256": digest,
        "dataset_id": None, "dataset_kind": None, "reviewer_id": None,
        "reviewer_background": None, "independent_review_declared": False,
        "permitted_evidence_declared": False, "reviewed_at": None,
        "model_digest": provenance.model_digest, "prompt_version": provenance.prompt_version,
        "inference_image_digests": provenance.image_digests,
        "visible_targets_complete": False, "visible_targets": [],
        "adjudications": [{"finding_index": i, "finding_sha256": finding_digest(f.model_dump(mode="json")),
                           "support": None, "component_correct": False, "evidence_correct": False,
                           "target_ids": [], "rationale": None}
                          for i, f in enumerate(report.findings)],
    }


def validate_binding(report: LocalInspectionReport, review: Review) -> None:
    provenance = report.provenance
    assert provenance is not None
    if (review.model_digest != provenance.model_digest or review.prompt_version != provenance.prompt_version
            or review.inference_image_digests != provenance.image_digests):
        raise ValueError("Review does not bind to the exact model, prompt and inference image hashes.")
    targets = {t.target_id: t for t in review.visible_targets}
    if len(targets) != len(review.visible_targets):
        raise ValueError("Visible target IDs must be unique.")
    for target in targets.values():
        if len(set(target.image_ids)) != len(target.image_ids) or not set(target.image_ids) <= set(provenance.image_digests):
            raise ValueError("A visible target must reference distinct images from this exact report.")
    indices = [a.finding_index for a in review.adjudications]
    if len(indices) != len(set(indices)) or any(i >= len(report.findings) for i in indices):
        raise ValueError("Finding adjudication indices are duplicate or outside this report.")
    for judgment in review.adjudications:
        finding = report.findings[judgment.finding_index]
        if judgment.finding_sha256 != finding_digest(finding.model_dump(mode="json")):
            raise ValueError("Adjudication does not bind to the exact finding content.")
        if len(set(judgment.target_ids)) != len(judgment.target_ids) or not set(judgment.target_ids) <= targets.keys():
            raise ValueError("Adjudicated target IDs must be distinct and present in the reviewed truth set.")
        if finding.classification == "UNKNOWN":
            if judgment.support != "ABSTENTION" or judgment.target_ids:
                raise ValueError("UNKNOWN findings are abstentions, never matched visible detections.")
        elif judgment.support == "ABSTENTION":
            raise ValueError("Only UNKNOWN findings may use ABSTENTION.")
        if judgment.target_ids and not (judgment.support == "SUPPORTED" and judgment.component_correct and judgment.evidence_correct):
            raise ValueError("Only fully supported component/evidence-correct claims may match targets.")
        if judgment.support == "SUPPORTED" and judgment.component_correct and judgment.evidence_correct and finding.classification != "UNKNOWN" and not judgment.target_ids:
            raise ValueError("A correct visible claim must identify its explicitly reviewed target(s).")
        for target_id in judgment.target_ids:
            if not set(targets[target_id].image_ids).intersection(finding.image_ids):
                raise ValueError("A matched target and finding need shared exact image evidence.")


def ratio(numerator: int, denominator: int) -> str | None:
    if denominator == 0:
        return None
    return str((Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def evaluate(report_paths: list[Path], review_paths: list[Path], image_paths: list[Path] | None = None) -> dict:
    if not report_paths or len(report_paths) > 1000 or len(review_paths) > 1000:
        raise ValueError("Supply between 1 and 1000 reports and at most 1000 reviews.")
    if len(image_paths or []) > 3000:
        raise ValueError("Supply at most 3000 inference artifacts.")
    reports = [read_report(p) for p in report_paths]
    if len({digest for digest, _ in reports}) != len(reports):
        raise ValueError("Duplicate report bytes cannot inflate the evaluation cohort.")
    reviews = [Review.model_validate_json(read_bytes(p)) for p in review_paths]
    reviews_by_hash = {r.report_sha256: r for r in reviews}
    if len(reviews_by_hash) != len(reviews):
        raise ValueError("Exactly one adjudication file per report is supported; reconcile reviewers explicitly.")
    completed = [(digest, r) for digest, r in reports if r.outcome == "COMPLETED"]
    if set(reviews_by_hash) - {digest for digest, _ in completed}:
        raise ValueError("An adjudication references absent or non-completed report bytes.")
    cohorts = {(r.provenance.model, r.provenance.model_digest, r.provenance.adapter_version,
                r.provenance.prompt_version, r.provenance.schema_version) for _, r in completed}
    if len(cohorts) > 1:
        raise ValueError("Separate model/prompt/adapter versions into distinct evaluation runs.")
    image_sets = [tuple(sorted(set(r.provenance.image_digests.values()))) for _, r in completed]
    if len(set(image_sets)) != len(image_sets):
        raise ValueError("Repeated inference image sets cannot inflate a single-run evidence cohort.")
    datasets = {(r.dataset_id, r.dataset_kind) for r in reviews}
    if len(datasets) > 1:
        raise ValueError("Do not combine different datasets or engineering and vehicle reviews.")
    artifact_digests = set()
    for image_path in image_paths or []:
        raw = read_bytes(image_path)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("An inference artifact exceeds the local-analysis 2 MiB image limit.")
        with Image.open(BytesIO(raw)) as image:
            if image.format not in {"PNG", "JPEG"} or getattr(image, "n_frames", 1) != 1 or max(image.size) > 2048 or image.width * image.height > 4_000_000:
                raise ValueError("Evaluation artifacts must be bounded single-frame PNG/JPEG inference images.")
            image.verify()
        artifact_digests.add(sha256(raw).hexdigest())
    expected_image_digests = {digest for _, r in completed for digest in r.provenance.image_digests.values()}
    incomplete = []
    if expected_image_digests - artifact_digests:
        incomplete.append({"reason": "MISSING_EXACT_INFERENCE_IMAGE_BYTES",
                           "sha256": sorted(expected_image_digests - artifact_digests)})
    observed = suspected = unknown = correct_observed = unsupported_observed = indeterminate_observed = 0
    truth_count = matched_count = critical_count = critical_missed = no_claim_reports = 0
    for digest, report in completed:
        review = reviews_by_hash.get(digest)
        if review is None:
            incomplete.append({"report_sha256": digest, "reason": "MISSING_REVIEW"})
            continue
        validate_binding(report, review)
        if not (review.independent_review_declared and review.permitted_evidence_declared and review.visible_targets_complete):
            incomplete.append({"report_sha256": digest, "reason": "INCOMPLETE_REVIEW_DECLARATIONS_OR_TRUTH"})
        if len(review.adjudications) != len(report.findings):
            incomplete.append({"report_sha256": digest, "reason": "MISSING_FINDING_ADJUDICATIONS"})
        matched = set()
        no_claim_reports += not any(f.classification != "UNKNOWN" for f in report.findings)
        for judgment in review.adjudications:
            finding = report.findings[judgment.finding_index]
            if finding.classification == "UNKNOWN":
                unknown += 1
            elif finding.classification == "SUSPECTED":
                suspected += 1
            else:
                observed += 1
                correct = judgment.support == "SUPPORTED" and judgment.component_correct and judgment.evidence_correct
                correct_observed += correct
                unsupported_observed += judgment.support == "UNSUPPORTED" or (judgment.support == "SUPPORTED" and not correct)
                indeterminate_observed += judgment.support == "INDETERMINATE"
                if correct:
                    matched.update(judgment.target_ids)
        truth_count += len(review.visible_targets)
        matched_count += len(matched)
        critical_count += sum(t.critical for t in review.visible_targets)
        critical_missed += sum(t.critical and t.target_id not in matched for t in review.visible_targets)
    if not completed:
        incomplete.append({"reason": "NO_COMPLETED_REPORTS"})
    dataset_kind = next(iter(datasets))[1] if datasets else None
    state = "INCOMPLETE" if incomplete else ("ENGINEERING_ONLY" if dataset_kind == "ENGINEERING" else "REVIEW_ACCOUNTED")
    return {
        "schema_version": "vision-evaluation-v1", "evidence_state": state,
        "release_quality_established": False,
        "warning": "Human declarations and adjudications are inputs, not verified qualifications, source rights or a release certification. No hidden-damage, cost or safety accuracy is measured.",
        "report_count": len(reports), "completed_report_count": len(completed),
        "failed_or_blocked_report_count": len(reports) - len(completed),
        "unique_inference_image_sets": len(set(image_sets)),
        "verified_inference_artifact_count": len(expected_image_digests & artifact_digests),
        "unmatched_image_artifact_count": len(artifact_digests - expected_image_digests),
        "dataset": {"id": next(iter(datasets))[0], "kind": dataset_kind} if datasets else None,
        "cohort": list(next(iter(cohorts))) if cohorts else None,
        "incomplete": incomplete,
        "metrics": None if incomplete else {
            "observed_claims": observed, "fully_supported_observed_claims": correct_observed,
            "unsupported_or_component_evidence_incorrect_observed_claims": unsupported_observed,
            "indeterminate_observed_claims": indeterminate_observed,
            "observed_supported_fraction": ratio(correct_observed, observed),
            "suspected_claims_not_counted_as_detections": suspected,
            "unknown_abstentions": unknown, "reports_without_observed_or_suspected_claims": no_claim_reports,
            "visible_targets": truth_count, "visible_targets_detected_as_observed": matched_count,
            "visible_target_recall": ratio(matched_count, truth_count),
            "critical_visible_targets": critical_count, "critical_visible_targets_missed": critical_missed,
        },
    }


def write_json(path: Path | None, result: dict) -> None:
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        print(payload, end="")
    else:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    draft = commands.add_parser("prepare", help="Create an intentionally incomplete human review template.")
    draft.add_argument("report", type=Path)
    draft.add_argument("--output", type=Path, required=True)
    assessment = commands.add_parser("evaluate", help="Account exact report/review pairs; never certify a release.")
    assessment.add_argument("--reports", type=Path, nargs="+", required=True)
    assessment.add_argument("--reviews", type=Path, nargs="*", default=[])
    assessment.add_argument("--images", type=Path, nargs="*", default=[], help="Exact normalized inference PNG/JPEG files; hashes must match reports.")
    assessment.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            write_json(args.output, prepare(args.report))
            return 0
        result = evaluate(args.reports, args.reviews, args.images)
        write_json(args.output, result)
        return 2 if result["evidence_state"] == "INCOMPLETE" else 0
    except (OSError, ValueError, ValidationError, Image.DecompressionBombError) as exc:
        print(f"Evaluation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
