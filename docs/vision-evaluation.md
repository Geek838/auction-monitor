# Offline visual-evidence evaluation

Implemented **30 October 2026 (Asia/Tbilisi)**. This is an evaluation-accounting tool, not a vehicle benchmark result. No qualified automotive review, measured vehicle accuracy or launch approval was produced by adding it.

`tools/evaluate_vision.py` compares actual exported `local-inspection-v1` reports with explicit human adjudications and the exact inference image bytes. It imports API contracts directly from this checkout's `services/api` directory and uses the existing pinned Python dependencies. It does not require an editable package installation or a caller-provided `PYTHONPATH`. It performs no network calls, model inference, heuristic text matching or automatic judging.

## Dataset and review method

The team must collect a permitted, representative vehicle cohort and preserve each complete report and exact normalized inference JPEG. A source photograph, browser-selected original and metadata-stripped inference copy can have different SHA-256 hashes. The tool requires **the bytes whose hash equals `provenance.image_digests`**, not a visually similar replacement. The current browser JSON export contains hashes, not image bytes. A benchmark collector must retain those exact inference artifacts locally during dataset preparation or deterministically reconstruct them and verify the hashes. Missing artifacts withhold all aggregate metrics.

Before inspecting model findings, a reviewer should enumerate visible targets from the evidence, using a fixed component vocabulary and predeclared criticality rules. Hidden damage is not a visible detection target. Record critical visible misses separately from conditions which could never be inferred from the photographs. Freeze the target set before adjudicating model output. This tool cannot enforce blinding or verify that a reviewer followed it; the release evidence must document that procedure and reviewer competence separately.

For each actual finding, the reviewer explicitly adjudicates evidence support, component correctness and evidence-reference correctness. Free-text component names are **never** automatically matched. `target_ids` identify the independently enumerated visible targets which the claim supports. The per-finding hash binds this judgment to exact content and classification. Qualification and permission fields are declarations, not proof of either. Do not use an AI-generated target set as independent truth.

One reconciled review is supported per report. Where two reviewers disagree, reconcile and retain their independent originals outside the aggregate cohort; do not count repeated reviews as extra vehicles. Component vocabularies, supported vehicle categories, reviewer procedures, acceptable critical-miss thresholds and a qualified approval process remain release work. No arbitrary numeric launch threshold has been invented here.

## Commands

Install the pinned API dependencies in the project virtual environment first, using the documented setup. Create an intentionally incomplete review template:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_vision.py prepare .cache/evaluation/report.json --output .cache/evaluation/review.json
```

Fill the review fields from actual independent review. `dataset_kind` must be `ENGINEERING` for authored shapes, simulated claims or other non-vehicle self-tests. `VEHICLE` is a dataset declaration, not a certification. The draft starts with null reviewer fields, false declarations and no truth targets so it cannot accidentally count as completed evidence.

Evaluate exact files:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_vision.py evaluate --reports .cache/evaluation/report.json --reviews .cache/evaluation/review.json --images .cache/evaluation/front-inference.jpg --output .cache/evaluation/results.json
```

On Linux/macOS replace the executable with `.venv/bin/python`. Options accept multiple explicit file paths. Keep these artifacts under an ignored private directory with a permitted retention policy; the application does not upload them. Output creation is exclusive and refuses to overwrite existing evidence.

Exit codes are `0` for completed accounting, `2` for incomplete evidence and `1` for invalid inputs/contract bindings or file errors. **Exit zero never means release approval.** JSON always contains `release_quality_established: false`.

## Review fields

| Field | Meaning |
| --- | --- |
| `report_sha256` | SHA-256 of the exact exported report file bytes; even whitespace edits invalidate the binding |
| `model_digest`, `prompt_version`, `inference_image_digests` | Must exactly equal the report's model/prompt/image provenance |
| `dataset_id`, `dataset_kind` | One cohort per run; engineering and vehicle reviews cannot be combined |
| `reviewer_id`, `reviewer_background`, `reviewed_at` | Actual review provenance, not a verified qualification claim |
| `independent_review_declared`, `permitted_evidence_declared` | Must be true for complete accounting; declarations alone do not establish independence or rights |
| `visible_targets_complete` | Reviewer explicitly states the visible target set is complete for this image evidence |
| `visible_targets` | Unique target IDs, a component code, description, exact report image IDs and explicit criticality |
| `adjudications` | Exactly one judgment for each finding index, bound to its canonical content hash |
| `support` | `SUPPORTED`, `UNSUPPORTED`, `INDETERMINATE`, or `ABSTENTION` for `UNKNOWN` findings only |
| `component_correct`, `evidence_correct`, `target_ids` | Explicit correctness judgments and exact targets; incorrect/indeterminate claims cannot match a target |
| `rationale` | Human reason for the judgment; no auto-grading of prose |

Every target must refer to an image in the exact report. Matched targets and findings need a shared image ID. This is evidence-reference consistency; it does not prove that a visual claim is true. Exact inference artifacts are read, raster-validated and SHA-256 checked. Reports are unsigned: a content hash binds bytes, not an authenticated origin. Model versions, prompt/adapter/schema versions and datasets must be evaluated in separate runs. Duplicate report bytes, duplicate adjudications and repeated identical inference-image sets are rejected, even if report timestamps or image IDs differ. A reordered copy of the same image set cannot inflate the cohort. Partially overlapping evidence sets or different photographs of the same vehicle still need dataset-level deduplication outside this tool; image hashes cannot establish independent vehicles.

## Metrics and evidence states

With full annotations and exact image artifacts, the tool reports:

- **Observed supported fraction:** fully supported, component-correct and evidence-correct `OBSERVED` claims divided by all `OBSERVED` claims. Unsupported and indeterminate claims cannot increase this fraction.
- **Visible-target recall:** unique explicit visible targets matched by correct `OBSERVED` claims divided by all reviewed visible targets. Repeated claims do not multiply detections.
- Counts of unsupported/component/evidence-incorrect observed claims, indeterminate observed claims, suspected claims, unknown abstentions, no-claim reports and critical visible targets missed.
- Completed versus failed/blocked report counts and unique inference-image-set count. Visual metrics are conditional on completed reports; failed/blocked runs are not converted into empty successful inspections.

`SUSPECTED` questions are counted separately and cannot count as observed detections. `UNKNOWN` is an abstention and cannot satisfy a visible target. An empty visible target set has undefined recall (`null`), not perfect recall; no observed claims means undefined supported fraction (`null`). A complete critical miss remains a miss when the model abstains.

Missing reviews, declarations, finding judgments or exact inference artifacts return `INCOMPLETE` with **all aggregate metrics withheld**. Invalid hashes or reference bindings are rejected. A fully annotated engineering cohort returns `ENGINEERING_ONLY`. A declared vehicle cohort returns `REVIEW_ACCOUNTED`, which means only that accounting is complete. The tool never upgrades either state into measured commercial readiness, source authorization, physical safety, hidden-damage accuracy, financial accuracy or reviewer qualification.

## Executed engineering checks

```powershell
.\.venv\Scripts\python.exe -m pytest tools/tests -q
```

The final executed Linux run passed **38 authored accounting checks**. Cases include supported/unsupported/indeterminate claims, component/evidence errors, suspected/unknown non-detections, critical misses, empty denominators, missing annotations and artifacts, exact byte hash changes, repeated evidence despite changed report timestamps/image IDs/ordering, mixed model cohorts, invalid rasters, safe output creation and CLI exit codes. A subprocess test disables Python site initialization (`-S`) and exposes only the installed dependency directory, proves `import app` fails without the tool's bootstrap, then executes the CLI help and evaluation from a separate working directory. All inputs are synthetic self-tests; no automotive accuracy score follows from their passing.
