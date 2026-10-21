# 002 — Provider contract v1 and offline feasibility boundaries

Status: implemented for the Sprint 2 offline development slice. This is an internal contract, not a vendor API or an executed commercial agreement.

## Selection and compatibility

`AUCTION_PROVIDER` selects one closed registry entry at API process startup:

| Value | Runtime | Data and permissions |
| --- | --- | --- |
| `fixture` (default) | Local hand-authored records | `MOCK`, metadata-only demonstration |
| `simulation` | Local authored provider simulation | `SIMULATED`, explicitly synthetic; exercises provider-aware failures and freshness |
| `bidcars` | Disabled placeholder | `EXTERNAL` and `NOT_AUTHORIZED`; no API/client or rights are presumed |

An unknown selection fails startup. Changing a setting requires restarting the API. No HTTP request can select or enable a provider, and none of these entries makes outbound calls. Returned snapshot data type must agree with configured mode; an external result cannot silently substitute MOCK/SIMULATED data. A future actual adapter needs separately documented implementation and permissions; selecting a name or setting a credential is insufficient.

`provider_context` is additive on every domain resolution outcome and on health. Existing health `provider`, `data_type`, and service `status` fields remain. A healthy API process is distinct from its selected source being permitted/available. Context availability means configuration permits the operation, not that a remote network health check has occurred. Resolution denial/failure marks the request's context unavailable; no synthetic record is substituted.

Existing result fields and the six status values remain. Additions include mapping/reference evidence, selected record/event IDs, source observation time and an assessed freshness object. Actual provider state vocabularies must be normalized from documented semantics before future integration; the current `ACTIVE`, `SOLD`, `ARCHIVED`, `UNKNOWN`, and synthetic `FIXTURE` values are internal, not alleged vendor payloads.

## Static authorization and capabilities

`ProviderPolicy` is validated static configuration; no database, legal workflow service or permission-administration UI is introduced. Permissions are independent for metadata lookup/display/cache, image retrieval/display/storage, AI inference, model training and redistribution. An absent permission denies that use. Metadata-only development does not depend on image rights.

`GuardedProvider` checks enabled state and lookup/display purposes before **both** `resolve` and `get_vehicle`. It checks canonical/page/vehicle lookup capabilities and supported houses. For an external policy, the requested purposes must also be present in reviewed authorization evidence, currently effective, unexpired and unrevoked. Credentials are checked by name/presence only if documented as required. Values never enter API results or logs. Permission is checked again after awaited work so expiry/revocation cannot release an in-flight result.

Authorization evidence includes a private evidence reference, reviewer and review/effective/expiry dates. These fields record a trusted operator's reviewed decision; software cannot determine that an uploaded contract is genuine or that a label proves legal rights. Real configurations need human rights review. The only registered external entry remains unconditionally disabled.

Use permissions are separate from data freshness. A narrative `license_scope` or a `LICENSED` result label never enables a provider. No runtime component currently performs image, AI, training, export or persistent caching operations, even if an isolated test config permits such a purpose.

## Exact identity and evidence

IAAI URLs retain `page_id` and optional uppercase country suffix separately from canonical stock. Fixture mappings explicitly support the US examples and unsuffixed examples only; another suffix cannot resolve through the US mapping. The matcher requires exact page, country, house and stock agreement in `MappingEvidence` and a usable origin (source, reference, evidence channel, observation time and supplied/observed classification). Missing, inferred, future-dated or candidate-derived mapping cannot yield `MATCHED`.

Independent reference metadata uses a separate `ReferenceEvidence` origin. Origins that point to a candidate record/URI, use a candidate channel, lack meaningful identifying text, have inferred/missing classification, or are future-dated do not prove corroboration. The adapter still owns the actual independence/accuracy of its documented source channel; strings alone cannot prove truth. Tests enforce the local gates and separate fixtures, not external source accuracy.

The legacy `expected_vehicle` field is retained only for conservative conflict rejection. It never produces an independent VIN/model corroboration claim. Missing independent metadata is explicitly warned. Any conflicting available VIN/year/make/model, wrong exact auction identity, or competing sale events produces ambiguity. VIN never substitutes for listing identity and never merges events.

Fixture record fields now identify their evidence for vehicle values, canonical identity and event metadata. A candidate's separate `record_id` and `event_id` survive matching. No event is silently chosen when records compete.

## Freshness

Freshness is computed with an injectable clock from `source_observed_at`, **never** `retrieved_at`. Missing/future observation time or missing supported threshold means `UNKNOWN`; archived/sold events remain `HISTORICAL` even with recent retrieval. When an explicit positive threshold and documented basis exist, source age is `FRESH` or `STALE` against that threshold. Neither is a live-feed guarantee.

The fixture policy has no real freshness promise and normally reports unknown. The simulation has a documented synthetic 24-hour threshold and seven-day-old observations with recent retrieval, intentionally illustrating stale data. Its partial record has unknown observation time. These are UI/contract test cases, not promises about a commercial source.

## Lifecycle and outbound policy

No provider-response cache or persistent data store is implemented. Unknown cache rights default to disabled, so no fabricated retention value is needed. A proposed cache TTL must have explicit cache permission and a retention ceiling at least as long as the TTL. Those configuration checks do not activate storage.

A future permitted cache key must include provider, canonical auction identity, and event/reference context; VIN alone is inadequate. Before enabling storage, implement and test source-age versus cache-age semantics, expiry, revocation invalidation, retention limits and verified deletion of originals/derived records/backups to the agreement's scope. Restrict access before serving any old cached value; cached possession is not permission. This future lifecycle test plan does not claim deletion infrastructure already exists.

Before adding any network adapter, establish official API documentation and use-specific rights, static destination allowlists, TLS verification, bounded connection/read timeouts, response/schema size limits, a documented finite retry/rate-limit policy, DNS/IP checks and redirect restrictions. Do not fetch submitted auction URLs or forward credentials across redirect hosts. Provider schema/connection/timeout/rate-limit failures become `SOURCE_UNAVAILABLE`; only a successful negative lookup is `NOT_FOUND`. Safe logs include outcome/house and exclude raw provider errors, bodies, URLs, VINs and credentials.

No third-party photographs, licensed datasets, credentials, personal interview records or invoices are included in the repository. Actual provider rights, live coverage and business feasibility remain pending external evidence; the offline slice does not complete those Sprint 2 targets.
