# 001 — Fixture-first resolver boundaries

Status: accepted for Sprint 1; production integration is undecided.

The supplied handover and the user's Sprint 1 request govern this implementation. The handover is preserved in `docs/auction_intelligence_handover.md`; its appendix is reference text, not a separate instruction to expand scope.

## Decisions

- Use Next.js App Router with TypeScript for the browser and FastAPI/Pydantic for the API. A same-origin Next.js proxy avoids browser CORS configuration. The server API address is deployment configuration, never taken from a submitted URL.
- Use an in-memory fixture adapter behind `AuctionSource`. PostgreSQL, ORM migrations, queues, caching, accounts, and external API clients add no required capability to this milestone. Persistence and audit retention need a decision before production access.
- Parse URLs locally with a narrow exact hostname/path allowlist. Do not fetch input URLs, follow redirects, infer identity from vehicle titles, or convert identifiers to numbers.
- A Copart lot and an IAAI stock are canonical listing references. An IAAI internal page identifier is a different type of reference and needs an explicit provider mapping. VIN cross-checks may reject a candidate but do not replace auction identity.
- Keep separate auction records/events even when VINs repeat. Conflicting or competing candidates abstain with `AMBIGUOUS`; lack of an IAAI page mapping is `UNRESOLVED_ID`.
- Fixture values are synthetic, may resemble real URL shapes, and are never current auction inventory. Photos are omitted because there is no image license. Mock labels and historical status remain distinct.
- Use plain CSS and local/system fonts for a small inspection interface. No runtime font service, AI service, analytics, or image source is needed.

## Tradeoffs

The parser deliberately supports documented URL shapes rather than every historic/regional format. Unsupported URLs fail explicitly. Local in-memory data makes startup deterministic but does not validate provider coverage, licenses, or production freshness. The product cannot resolve arbitrary real links until an authorized integration supplies corroborated records.
