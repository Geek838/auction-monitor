# Authored inspection-preview illustrations

These three PNGs are procedural test illustrations authored for Auction Intelligence Sprint 3. They are not photographs, auction records, images of a Toyota or other identified vehicle, or evidence of any vehicle's actual condition. They do not depict hidden structure, functioning safety systems, mechanical condition or roadworthiness.

## Origin and permitted use

The source is [`generate_fixtures.py`](../services/api/app/inspections/assets/generate_fixtures.py): project-authored drawing primitives, colors, geometry and captions rendered locally with Pillow and its bundled default font. No third-party car photograph, logo, auction-site data or downloaded image was used, and no image-generation or image-analysis service was called. No system font or remote resource is loaded.

The project authors record these assets as permitted for this repository's local synthetic display and deterministic mock-preview demonstration. That is the scope of the manifest's `image_display` and `mock_preview` permissions. AI inference and model-training permissions remain false; image display does not grant either. This record does not establish rights to unrelated external images, real-provider records, customer uploads, or unrestricted commercial image redistribution.

`reviewed_by` means procedural illustration/source review by the project fixture author. It does **not** claim an external legal review, a commercial data agreement, or a qualified mechanical inspection. A future real-user pilot still needs the rights/domain reviews in the Sprint 3 requirements.

Each illustration visibly says **SYNTHETIC ILLUSTRATION** and **NOT AUCTION PHOTO**; the rear plate additionally says MOCK ONLY. The footer identifies its hand-authored nature and explicitly says hidden components and vehicle safety are not shown. Rust-colored marks are authored illustration pixels, not image-model localization or automatic damage highlights. No localization coordinates are supplied by these assets.

## Asset catalog

All assets are RGB PNG, 960 × 600 pixels. Their immutable IDs, hashes, dimensions, MIME type, meaningful alt text, source, permissions and current-use fields are in [manifest.json](../services/api/app/inspections/assets/manifest.json).

| Asset ID | Visible authored content | Seeded finding boundary |
| --- | --- | --- |
| `front-illustration-v1` | Generic front-quarter silhouette with a rust-colored bumper mark | A mock observation can describe the **drawn** mark only. It cannot establish real bumper damage, hidden reinforcement damage or repair needs. |
| `side-illustration-v1` | Generic side silhouette with rust-colored panel scuff strokes | A mock observation can describe the **drawn** strokes only. Door function, paint depth, structure and mechanical effects remain unknown. |
| `rear-illustration-v1` | Generic rear silhouette without a highlighted cosmetic feature | Absence of a highlighted feature is not evidence of no damage. Underbody, electronics, safety systems and structure remain unknown. |

The backend owns scenario-to-provider/listing/record/event binding. These generic illustrations have no independent VIN, lot or stock identity, and cannot establish a vehicle match. A preview may use them only through its explicit authored scenario and current-use checks; a shared VIN or similar-looking model is insufficient. Unknown or altered bytes must not receive their seeded mock findings.

## Regeneration and integrity

From the repository root, after installing dependencies:

```sh
.venv/bin/python services/api/app/inspections/assets/generate_fixtures.py
```

PowerShell equivalent:

```powershell
.\.venv\Scripts\python.exe services/api/app/inspections/assets/generate_fixtures.py
```

Generation was verified with the project's pinned Pillow 13.0.0: the decoded files are RGB PNG at the manifest dimensions, and rerunning the generator repeats their byte hashes. PNGs carry no EXIF, GPS, source capture timestamp or remote metadata. Generation time is not an image capture time. The generator is a development tool, not a request-time path or a runtime mechanism to approve arbitrary bytes.

The manifest freezes exact SHA-256 digests. The backend separately pins reviewed bytes in `APPROVED_CONTENT` in `app/inspections/catalog.py`; changing only a manifest hash cannot authorize replacement artwork for seeded findings. Pillow/renderer changes can alter bytes; regenerated images, their manifest, independent pins and affected seeded findings require explicit source/visual review together before accepting new hashes. Do not auto-rewrite expected hashes to make a failed runtime integrity check pass. Keep IDs/revisions explicit when the fixture meaning changes.

`revoked=false` and `expires_at=null` record the present authored-demo permission; they are not substitutes for current server checks. The API must validate the requested asset, binding, permission, bytes and decoded type/dimensions before delivery. Static files in Git and client-downloaded copies cannot be recalled as a private upload store; no such store is implemented here.
