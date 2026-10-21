# Sprint 4 — zero-paid-API delivery

Delivery date: 22 October 2026 (Asia/Tbilisi). The latest client budget is zero spending on APIs. The [zero-API scope](sprint-4-zero-api-scope.md) governs this implementation; the [provider research](research/provider-selection-2026-10-22.md) remains evidence for future integration.

## Delivered behavior

- A separate `/review` page, linked from the home page, compiles actual user-entered vehicle facts, local photos and user-reported findings into an unverified review.
- Original Copart/IAAI URLs are parsed without fetching. Copart lots stay strings; IAAI page/country and a manually claimed stock remain distinct. VIN syntax checking does not verify vehicle identity.
- Browser-local PNG/JPEG selection is bounded to six files, 8 MiB each, 24 MiB total and 20 million original pixels. The browser decodes, normalizes to a longest side of at most 2048 pixels, strips original metadata and hashes prepared PNG bytes. No image bytes, original filenames or embedded source metadata are sent to the API.
- `POST /api/v1/manual-reviews` validates bounded text and client-declared photo metadata. It emits USER_SUPPLIED_UNVERIFIED, USER_REPORTED findings and CLIENT_DECLARED_NOT_SERVER_VERIFIED hashes. It does not return MATCHED, use a provider, store a report or run a model. Its pre-parse JSON cap is 32 KiB; inherited resolver/preview caps remain 16 KiB.
- Six safety-critical systems remain UNKNOWN with physical-inspection questions. No automatic observations, repair amounts, safety verdict or maximum bid is generated. Known safety-verdict phrases are narrowly rejected; that validation is not a general safety classifier.
- The report supports metadata/text JSON download and browser printing with the local evidence images. Clear/reset releases application-owned image URLs and cancels pending work. Editing clears the report, and late or mismatched responses cannot attach to changed inputs.

## Architecture and limits

Keeping pixels in the browser avoids server photo storage and external inference transmission. It also means the server cannot verify image pixels, their hashes or their relationship to a vehicle. All user facts and findings are explicitly unverified. Permission confirmation is the user's statement, not a copyright license or independent auction match.

Reports are temporary page state. Reloading or clearing removes them from the application view; downloaded JSON contains no photo bytes. Printing can retain images, but saved copies, browser caches and print destinations are controlled by the user. This is not a server retention/deletion service or persistent report history. No new dependency or API key is required.

Existing fixture resolution, simulation, disabled Bid.Cars behavior and authored MOCK inspection previews remain separate. Real user images cannot receive the fixture engine's seeded observations. No production source, external AI service, local model or inference weights were activated. Zero paid API usage does not promise zero hosting or device compute costs.

## Verification

**371 backend tests and 142 distinct browser checks passed**, plus final TypeScript and production build checks. See the [executed test report](sprint-4-test-report.md) for coverage and platform limits. Native Windows and hosted CI were not observed. Backend unit/API checks cover the new metadata boundary and inherited regressions; frontend checks exercise real endpoints and browser-local photo preparation, export/print, clearing, escaping and stale-response rejection. Test images are generated engineering fixtures, not vehicle evidence or a measured damage benchmark.

## Remaining product work

This delivers a usable user-supplied review fallback, not the complete automatic URL-to-AI product. No reviewed source establishes a free authorized production auction resolver. Supplier inquiries are drafted but unsent; paid plans are excluded by the client's budget. Any later free source still needs exact identity and supported access. A local vision option would require an actual model/license, installed weights, hardware/resource limits and quality evaluation before use.

The team continues to own research and implementation. No client research, supplier account purchase or new cloud-network configuration was required for this delivery.
