# 003 — Guarded authored inspection preview

Status: implemented for the Sprint 3 offline slice. This is a deterministic preview of a report workflow, not image recognition or an inspection of a real vehicle.

## Contracts and API

Existing resolver fields and six outcomes remain. `POST /api/v1/auction/resolve` adds a server-derived `snapshot_fingerprint` and `preview_eligibility` (`available`, human-readable `reason`, optional `scenario_id`). Eligibility requires a corroborated registered snapshot, current local image/preview rights, and at least one intact eligible image. Failure of the image catalog cannot make metadata resolution fail.

`POST /api/v1/inspections` accepts only `{url, expected_snapshot_fingerprint}`. Both are bounded; the fingerprint is a 64-character lowercase SHA-256 digest. Extra client fields, image paths/URLs, provider/model overrides, status claims and findings are rejected. The server parses the allowlisted reference locally, resolves it through the existing guarded provider, independently computes the current fingerprint, and compares the precondition before selecting any image scenario.

Domain responses use HTTP 200 with `COMPLETED`, `PARTIAL`, `BLOCKED` or `FAILED`, distinct `reason_code`/reasons, and the actual original resolver outcome. Invalid inputs are HTTP 422. `COMPLETED` means the mock workflow completed, not that a vehicle passed an inspection. `TARGET_CHANGED` requires resolving again. Blocked/failed responses contain no images, findings or model provenance. Partial responses list the excluded assets and do not infer an all-clear result.

Reports have a target, permitted authored assets, typed findings/checks, coverage limitations, exclusions and explicit MOCK engine provenance. Model/provider/prompt identifiers are null because no model ran. The three finding classifications OBSERVED/SUSPECTED/UNKNOWN are separate from metadata-origin `FieldEvidence`. Observations describe deliberately drawn features; suspicions are inspection questions with rationale and confirmation steps. Six safety-critical systems remain unknown. Confidence is null, severity can be unknown, and no output claims calibrated accuracy or roadworthiness.

`GET /api/v1/inspection-assets/{asset_id}?url=...&expected_snapshot_fingerprint=...` serves only allowlisted raster IDs belonging to the currently resolved exact scenario. It rechecks snapshot and image rights, not an opaque caller's assertion that a previous report existed. Denied use is HTTP 403; changed target is 409; unknown/unpermitted/invalid asset is 404; unexpected validation failures are a sanitized 503. No raw file path is accepted or returned. Responses are PNG with `no-store`, `nosniff`, same-origin resource policy and a restrictive content policy. Preview JSON is also `no-store`.

## Stable identity and content boundaries

The full snapshot digest includes provider ID/mode/contract version, canonical house and exact string lot/stock, parsed IAAI page/country, record and sale-event IDs, event state/date, vehicle attributes, source provenance except request retrieval time, mapping/reference evidence and field evidence. Changing meaningful source observation/evidence/content changes the precondition. Tracking parameters, retrieval time and freshness-evaluation time do not identify a different snapshot. The digest is a comparison precondition, not a signature, license or authentication token.

The authored scenario binding is separate: it compares the record/event/vehicle/provider content projection with a pristine registered local fixture. This allows known fixture/simulation data to display an explicitly MOCK report without conflating source-age changes with who authored the illustration. The engine receives both the full snapshot digest and the narrower authored-content digest; the service still owns server-side full-snapshot validation. VIN similarity alone never selects a scenario.

After awaiting the engine, the service checks permissions again, re-resolves and compares the full snapshot again, then verifies current image rights and bytes before releasing a report. A changed record/event/evidence during generation is blocked. Clients must also discard late responses whose target or request no longer matches the displayed resolution; changing input or resolving another reference clears the report.

## Authored assets and rights

Three project-authored PNG illustrations are versioned under `app/inspections/assets`, with reproducible generation instructions and an explicit authored-asset review manifest. No auction photographs or other third-party image bytes are included. Their authorship/review record is not represented as a qualified mechanical review or a commercial-provider license.

The manifest records meaningful author, rights reference, fixture reviewer, view/alt text, decoded dimensions/MIME, digest and independent display/mock-preview permissions. Revoked/expired/unknown use denies that asset. Local provider policy now explicitly grants image retrieval/display and the narrow `mock_inspection_preview` capability in fixture/simulation modes; inference, training, image storage and external data access remain denied. Metadata permission alone does not grant image use.

Manifest content is re-read and compared by digest on each use, including reused catalog instances. Missing, invalid or changed manifest data cannot fall back to a cached approval. PNG bytes are bounded and hashed on every delivery/generation check. Pillow verifies the actual PNG format and dimensions and fully decodes the single-frame raster. Symlinks and files outside the configured catalog root are rejected.

Seeded observations additionally pin the exact reviewed image digests in a versioned code allowlist independently of the manifest. Replacing a PNG and updating its manifest digest does not authorize old canned findings for the replacement bytes. Changed artwork requires a deliberate fixture revision and copy review. Unknown user/customer assets are not accepted; there is no upload endpoint or remote fetch.

## Scenarios and failure examples

| Reference | Preview |
| --- | --- |
| Copart `51374586` | Two authored views, observed/suspected examples and safety unknowns |
| IAAI page `41000001~US` (stock `45371195`) | Same permitted illustrations explicitly bound to this separate authored listing/event |
| Copart `70000002` | Historical PARTIAL example; the side view is deliberately excluded for this scenario |
| Copart `00012345` | Matched metadata with no registered preview images |
| Copart `70000007` | Explicit mock-engine failure, no findings released |
| Copart `70000008` | Rear illustration without highlighted cosmetic marks; UNKNOWN findings and physical checks remain |

Fixture and simulation modes are explicitly registered independently; an external licensed record can never inherit a mock scenario. Original ambiguous/unresolved/denied/unavailable cases remain resolver outcomes and block preview.

## Resource, lifecycle and trust limits

Engineering limits for this fixed local demo: at most six manifest assets, 64 KiB manifest bytes, 1 MiB per PNG, 2048×2048 decoded pixels per image, six images and thirty findings per response, bounded finding text and list lengths. Resolver/preview POST JSON is limited to 16 KiB before full JSON parsing; URL fields remain 2048 characters. These limits comfortably contain the three 960×600 authored illustrations and small URL/fingerprint documents. They are implementation choices, not provider limits or an upload service.

No report database, upload store, cache, shared history, job queue or polling API is added. Reports are computed synchronously and held in the current browser view. Images/manifests are immutable project source artifacts; deleting a private upload or retracting a downloaded client copy is not a capability this system claims. Per-request permission guards stop later delivery when rights change.

The mock adapter outputs only a known authored scenario. Image captions, metadata and future output fixtures are data, never executable instructions. Pydantic validators reject broken references/geometry, mismatched digests, invalid provenance and a narrow set of explicitly prohibited safety assertions. These validators and reviewed fixed seed wording are not a general automotive safety classifier or proof of vision-model accuracy. Future real AI needs separate source/inference/processor rights, selected documented model, operating bounds and blinded domain-reviewed evaluation. Paid APIs, arbitrary uploads, real images, financial estimates and production deployment remain outside this slice.
