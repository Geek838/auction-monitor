'use client';

import { FormEvent, useRef, useState } from 'react';

type ResolutionStatus = 'MATCHED' | 'AMBIGUOUS' | 'NOT_FOUND' | 'UNRESOLVED_ID' | 'SOURCE_UNAVAILABLE' | 'NOT_AUTHORIZED';
type House = 'COPART' | 'IAAI';
type Vehicle = { vin: string | null; year: number | null; make: string | null; model: string | null; trim: string | null; primary_damage: string | null };
type Identity = { house: House; lot_or_stock_number: string };
type Provenance = { provider: string; source_name: string; source_url: string | null; retrieved_at: string; license_scope: string; data_type: string; realtime: boolean };
type Candidate = { identity?: Identity | null; vehicle?: Vehicle | null; event_status?: string | null; event_date?: string | null; [key: string]: unknown };
type Resolution = {
  status: ResolutionStatus;
  reference: { house: House; url: string; lot_number: string | null; stock_number: string | null; page_id: string | null };
  identity: Identity | null; vehicle: Vehicle | null; candidates: Candidate[];
  provenance: Provenance | null; evidence: string[]; warnings: string[]; reasons: string[];
  field_evidence?: Record<string, { kind: string; source: string; note: string }>;
  event_status?: string | null; event_date?: string | null;
  listing?: { event_status?: string | null; event_date?: string | null } | null;
};

const statusCopy: Record<ResolutionStatus, { title: string; description: string }> = {
  MATCHED: { title: 'Exact auction identity matched', description: 'The provider record corroborates the auction house and exact listing identifier.' },
  AMBIGUOUS: { title: 'We could not confirm one exact match', description: 'The available evidence conflicts or identifies more than one listing. We have not selected a vehicle.' },
  NOT_FOUND: { title: 'No fixture record found', description: 'This link was parsed, but our test dataset has no matching record. It does not tell us whether the auction listing exists.' },
  UNRESOLVED_ID: { title: 'The IAAI stock number is not confirmed', description: 'The IAAI page ID is known, but its stock number has not been corroborated. These identifiers are not interchangeable.' },
  SOURCE_UNAVAILABLE: { title: 'The data provider is unavailable', description: 'The provider could not complete this lookup. Try again later; no match has been assumed.' },
  NOT_AUTHORIZED: { title: 'Authorized data access is not available', description: 'This lookup requires authorized provider access. No live commercial integration is enabled.' },
};
const examples = [
  { label: 'Try a matched Copart fixture', url: 'https://www.copart.com/lot/51374586' },
  { label: 'Try an IAAI page reference', url: 'https://www.iaai.com/VehicleDetail/41000001~US' },
];
function ExternalArrow() {
  return <svg className="external-arrow" aria-hidden="true" width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 12 12 4M4 4h8v8" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
function value(text: string | number | null | undefined) { return text === null || text === undefined || text === '' ? 'Not supplied' : text; }
function vehicleTitle(vehicle: Vehicle | null | undefined) {
  return vehicle ? [vehicle.year, vehicle.make, vehicle.model, vehicle.trim].filter(Boolean).join(' ') || 'Vehicle details not supplied' : 'Vehicle details not supplied';
}
function timestamp(raw: string) {
  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? raw : date.toISOString().replace('T', ' ').replace('.000Z', ' UTC');
}
function safeSourceUrl(raw: string | null): string | undefined {
  if (!raw) return undefined;
  try { const url = new URL(raw); return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : undefined; } catch { return undefined; }
}
export default function Resolver() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Resolution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await fetch('/api/v1/auction/resolve', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: url.trim() }),
      });
      if (!response.ok) {
        let message = response.status === 422 ? 'Enter a supported Copart or IAAI listing URL. Check the hostname and listing identifier.' : 'The resolver is unavailable. Please try again later.';
        try {
          const body = await response.json();
          if (response.status === 422 && typeof body.detail === 'string') message = body.detail;
        } catch { /* Keep the helpful fallback when a proxy returns HTML. */ }
        throw new Error(message);
      }
      const body = await response.json() as Resolution;
      if (!Object.hasOwn(statusCopy, body.status)) throw new Error('The resolver returned an unexpected response. Please try again later.');
      setResult(body);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'The resolver could not be reached. Please try again later.');
    } finally { setLoading(false); }
  }
  const eventStatus = result?.listing?.event_status ?? result?.event_status;
  const eventDate = result?.listing?.event_date ?? result?.event_date;
  const archived = eventStatus?.toUpperCase() === 'ARCHIVED';
  const provenance = result?.provenance;
  const sourceUrl = provenance ? safeSourceUrl(provenance.source_url) : undefined;
  return <>
    <section className="lookup-section" aria-label="Resolve an auction listing">
      <div className="mode-notice"><span className="tag">MOCK DATA</span><p><strong>Mock data environment.</strong> Results use test fixtures. No live auction data or inspection advice is provided.</p></div>
      <form onSubmit={submit} aria-busy={loading}>
        <label htmlFor="auction-url">Copart or IAAI listing URL</label>
        <div className="input-row">
          <input ref={input} id="auction-url" name="url" type="url" autoComplete="off" required maxLength={2048} placeholder="https://www.copart.com/lot/51374586" value={url} onChange={event => setUrl(event.target.value)} aria-describedby={`url-help${error ? ' lookup-error' : ''}`} aria-invalid={Boolean(error)} disabled={loading} />
          <button className="submit-button" disabled={loading} type="submit">{loading ? 'Resolving…' : 'Resolve listing'}<ExternalArrow /></button>
        </div>
        <p id="url-help" className="help">Links are parsed without opening the auction page. IAAI page IDs stay distinct from stock numbers.</p>
      </form>
      <div className="examples"><span>Try a fixture:</span>{examples.map(example => <button key={example.label} type="button" disabled={loading} onClick={() => { setUrl(example.url); input.current?.focus(); }}>{example.label}<ExternalArrow /></button>)}</div>
    </section>
    <div className="result-region" aria-live="polite" aria-atomic="true">
      {loading && <div className="processing" role="status"><span className="loading-dot" aria-hidden="true" />Checking the listing identity…</div>}
      {error && <section className="error-panel" id="lookup-error" role="alert"><p className="eyebrow">URL COULD NOT BE RESOLVED</p><h2>This link cannot be resolved</h2><p>{error}</p></section>}
      {!result && !error && !loading && <div className="empty-state"><span className="sheet-number">01</span><div><h2>Identity first. Evidence always.</h2><p>Your result will show what matched, where the record came from, and what remains unknown.</p></div></div>}
      {result && <section className={`result-sheet ${result.status === 'MATCHED' ? 'is-matched' : 'needs-review'}`} aria-label="Listing resolution result">
        <div className="result-heading"><div><p className="eyebrow">RESOLUTION / {result.status.replaceAll('_', ' ')}</p><h2>{statusCopy[result.status].title}</h2></div><div className="badges"><span className="tag">MOCK</span>{archived && <span className="tag archived">ARCHIVED</span>}</div></div>
        <p className="status-description">{statusCopy[result.status].description}</p>{archived && <p className="historical-note">Historical auction record. This does not show a current listing or current bid.</p>}
        <dl className="identity-line"><div><dt>Auction house</dt><dd>{result.reference.house}</dd></div>{result.reference.page_id && <div><dt>IAAI page ID</dt><dd className="mono">{result.reference.page_id}</dd></div>}<div><dt>{result.reference.house === 'IAAI' ? 'Canonical stock number' : 'Canonical lot number'}</dt><dd className="mono">{result.identity?.lot_or_stock_number ?? 'Unresolved'}</dd></div></dl>
        {result.vehicle && <div className="vehicle-block"><h3>{vehicleTitle(result.vehicle)}</h3><dl className="vehicle-facts"><div><dt>VIN</dt><dd className="mono">{value(result.vehicle.vin)}</dd></div><div><dt>Reported primary damage</dt><dd>{value(result.vehicle.primary_damage)}</dd></div><div><dt>Auction event status</dt><dd>{value(eventStatus)}</dd></div><div><dt>Event date</dt><dd>{value(eventDate)}</dd></div></dl><p className="help">Fixture metadata only. Vehicle condition has not been inspected.</p><p className="help">No licensed photos supplied</p></div>}
        {result.reasons.length > 0 && <div className="evidence-section"><h3>Resolution notes</h3><ul>{result.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul></div>}
        {result.evidence.length > 0 && <div className="evidence-section"><h3>Match evidence</h3><ul>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></div>}
        {result.status === 'AMBIGUOUS' && result.candidates.length > 0 && <div className="evidence-section"><h3>Candidate records — no selection made</h3><ol className="candidates">{result.candidates.map((candidate, index) => <li key={index}><strong>{vehicleTitle(candidate.vehicle)}</strong><span>{candidate.identity?.house ?? 'Auction not supplied'} / <span className="mono">{candidate.identity?.lot_or_stock_number ?? 'Identifier not supplied'}</span></span><span>VIN: <span className="mono">{value(candidate.vehicle?.vin)}</span></span><span>Record: <span className="mono">{String(candidate.record_id ?? 'Not supplied')}</span> · Event: {value(candidate.event_date)} / {value(candidate.event_status)}</span></li>)}</ol></div>}
        {provenance && <div className="provenance"><h3>Record provenance</h3><dl><div><dt>Provider</dt><dd>{provenance.provider} / {provenance.source_name}</dd></div><div><dt>Retrieved at</dt><dd><time dateTime={provenance.retrieved_at}>{timestamp(provenance.retrieved_at)}</time></dd></div><div><dt>Data type</dt><dd>{provenance.data_type} · {provenance.realtime ? 'Provider reports real-time' : 'Not a real-time feed'}</dd></div><div><dt>Usage scope</dt><dd>{provenance.license_scope}</dd></div><div><dt>Record reference</dt><dd className="mono">{provenance.source_url ?? 'Not supplied'}</dd></div></dl>{sourceUrl && <a href={sourceUrl} target="_blank" rel="noopener noreferrer">Source reference <ExternalArrow /></a>}{safeSourceUrl(result.reference.url) && <p className="help"><a href={safeSourceUrl(result.reference.url)} target="_blank" rel="noopener noreferrer">Submitted auction link <ExternalArrow /></a> · Parsed only; page not fetched.</p>}</div>}
        {result.field_evidence && Object.keys(result.field_evidence).length > 0 && <details className="field-evidence"><summary>Field-level evidence</summary><dl>{Object.entries(result.field_evidence).map(([field, evidence]) => <div key={field}><dt>{field.replaceAll('_', ' ')}</dt><dd>{evidence.kind} · {evidence.source}<br />{evidence.note}</dd></div>)}</dl></details>}
        {result.warnings.length > 0 && <aside className="warnings" aria-label="Data limitations"><h3>Read before using this result</h3><ul>{result.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></aside>}
      </section>}
    </div>
    <section className="scope-note"><p className="eyebrow">THE FIRST CHECK</p><p>This prototype verifies listing identity using fixtures. It does not assess damage, estimate repairs, or recommend a bid.</p></section>
  </>;
}
