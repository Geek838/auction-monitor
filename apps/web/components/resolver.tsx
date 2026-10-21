'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import ProviderNotice from './provider-notice';
import InspectionPreview from './inspection-preview';
import { readProviderContext, type EvidenceOrigin, type ProviderContext, type Resolution, type ResolutionStatus, type Vehicle } from './resolution-types';

const statusCopy: Record<ResolutionStatus, { title: string; description: string }> = {
  MATCHED: { title: 'Exact auction identity matched', description: 'The provider record corroborates the auction house and exact listing identifier.' },
  AMBIGUOUS: { title: 'We could not confirm one exact match', description: 'The available evidence conflicts or identifies more than one listing. We have not selected a vehicle.' },
  NOT_FOUND: { title: 'No provider record found', description: 'The selected provider has no exact record for this reference. This does not establish whether the auction listing exists.' },
  UNRESOLVED_ID: { title: 'The IAAI stock number is not confirmed', description: 'The IAAI page ID is known, but its stock number has not been corroborated. These identifiers are not interchangeable.' },
  SOURCE_UNAVAILABLE: { title: 'The data provider is unavailable', description: 'The provider could not complete this lookup. Try again later; no match has been assumed.' },
  NOT_AUTHORIZED: { title: 'Authorized data access is not available', description: 'This operation is not authorized for the selected source. No replacement fixture result has been supplied.' },
};
const examples = [
  { url: 'https://www.copart.com/lot/51374586', fixture: 'Try a matched Copart fixture', simulation: 'Try a Copart simulation' },
  { url: 'https://www.iaai.com/VehicleDetail/41000001~US', fixture: 'Try an IAAI page reference', simulation: 'Try an IAAI simulation' },
];
const freshnessLabels = { FRESH: 'Fresh snapshot', STALE: 'Stale snapshot', UNKNOWN: 'Freshness unknown', HISTORICAL: 'Historical record' };

function ExternalArrow() {
  return <svg className="external-arrow" aria-hidden="true" width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 12 12 4M4 4h8v8" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
function value(text: string | number | null | undefined) {
  return text === null || text === undefined || text === '' ? 'Not supplied' : text;
}
function vehicleTitle(vehicle: Vehicle | null | undefined) {
  return vehicle ? [vehicle.year, vehicle.make, vehicle.model, vehicle.trim].filter(Boolean).join(' ') || 'Vehicle details not supplied' : 'Vehicle details not supplied';
}
function timestamp(raw: string) {
  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? raw : date.toISOString().replace('T', ' ').replace('.000Z', ' UTC');
}
function Time({ raw }: { raw: string | null | undefined }) {
  return raw ? <time dateTime={raw}>{timestamp(raw)}</time> : <>Not supplied</>;
}
function safeSourceUrl(raw: string | null): string | undefined {
  if (!raw) return undefined;
  try {
    const url = new URL(raw);
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : undefined;
  } catch { return undefined; }
}
function OriginDetails({ origin }: { origin: EvidenceOrigin }) {
  return <dl className="origin-facts">
    <div><dt>Evidence source</dt><dd>{origin.source}</dd></div>
    <div><dt>Evidence channel</dt><dd>{origin.channel}</dd></div>
    <div><dt>Evidence reference</dt><dd className="mono">{origin.reference}</dd></div>
    <div><dt>Evidence observed at</dt><dd><Time raw={origin.observed_at} /></dd></div>
    <div><dt>Evidence classification</dt><dd>{origin.kind}</dd></div>
  </dl>;
}
function resultCopy(result: Resolution) {
  if (result.status === 'NOT_FOUND' && result.provider_context.mode === 'FIXTURE') {
    return { title: 'No fixture record found', description: 'This link was parsed, but our test dataset has no matching record. It does not tell us whether the auction listing exists.' };
  }
  if (result.status === 'NOT_FOUND' && result.provider_context.mode === 'SIMULATED') {
    return { title: 'No simulation record found', description: 'The offline simulation has no matching synthetic record. No live auction lookup was made.' };
  }
  return statusCopy[result.status];
}
function resultBadge(result: Resolution) {
  if (result.provenance?.data_type === 'MOCK' || result.provider_context.mode === 'FIXTURE') return 'MOCK';
  if (result.provenance?.data_type === 'SIMULATED' || result.provider_context.mode === 'SIMULATED') return 'SIMULATED';
  if (result.provider_context.authorization === 'DENIED') return 'ACCESS DENIED';
  if (result.provenance?.data_type === 'LICENSED') return 'LICENSED DATA';
  return 'EXTERNAL SOURCE';
}

export default function Resolver() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Resolution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<ProviderContext | null>(null);
  const [checkingProvider, setCheckingProvider] = useState(true);
  const input = useRef<HTMLInputElement>(null);
  const resolveSequence = useRef(0);
  const resolveAbort = useRef<AbortController | null>(null);

  useEffect(() => () => { resolveSequence.current += 1; resolveAbort.current?.abort(); }, []);

  function updateUrl(next: string) {
    resolveSequence.current += 1;
    resolveAbort.current?.abort();
    setUrl(next); setResult(null); setError(null); setLoading(false);
  }

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    async function loadProvider() {
      try {
        const response = await fetch('/api/v1/health', { signal: controller.signal, cache: 'no-store' });
        if (!response.ok) throw new Error('Provider context unavailable');
        const health: { provider_context?: unknown } = await response.json();
        if (active && !controller.signal.aborted) setProvider(readProviderContext(health.provider_context));
      } catch {
        if (active) setProvider(null);
      } finally {
        clearTimeout(timer);
        if (active) setCheckingProvider(false);
      }
    }
    void loadProvider();
    return () => { active = false; clearTimeout(timer); controller.abort(); };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const request = ++resolveSequence.current;
    resolveAbort.current?.abort();
    const controller = new AbortController();
    resolveAbort.current = controller;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/api/v1/auction/resolve', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: url.trim() }), signal: controller.signal,
      });
      if (!response.ok) {
        let message = response.status === 422
          ? 'Enter a supported Copart or IAAI listing URL. Check the hostname and listing identifier.'
          : 'The resolver is unavailable. No replacement data has been supplied; please try again later.';
        try {
          const body = await response.json();
          if (response.status === 422 && typeof body.detail === 'string') message = body.detail;
        } catch { /* Preserve a useful fallback if a proxy returns HTML. */ }
        throw new Error(message);
      }
      const body = await response.json() as Resolution;
      if (!Object.hasOwn(statusCopy, body.status) || !readProviderContext(body.provider_context)
        || !body.reference || !Array.isArray(body.reasons) || !Array.isArray(body.evidence)
        || !Array.isArray(body.warnings) || !Array.isArray(body.candidates)) {
        throw new Error('The resolver returned an unexpected response. No match is assumed; please try again later.');
      }
      if (body.status === 'MATCHED' && (body.provider_context.authorization === 'DENIED'
        || !body.provider_context.enabled || !body.provider_context.available)) {
        throw new Error('The source did not confirm available, authorized access. No match is assumed.');
      }
      if (controller.signal.aborted || resolveSequence.current !== request) return;
      setResult(body);
      setProvider(body.provider_context);
    } catch (cause) {
      if (!controller.signal.aborted && resolveSequence.current === request) {
        setError(cause instanceof Error ? cause.message : 'The resolver could not be reached. Please try again later.');
      }
    } finally {
      if (!controller.signal.aborted && resolveSequence.current === request) setLoading(false);
    }
  }

  const context = result?.provider_context ?? provider;
  const eventStatus = result?.event_status;
  const archived = eventStatus === 'ARCHIVED';
  const historical = archived || eventStatus === 'SOLD' || result?.freshness?.status === 'HISTORICAL';
  const provenance = result?.provenance;
  const sourceUrl = provenance ? safeSourceUrl(provenance.source_url) : undefined;
  const offline = context?.mode === 'FIXTURE' || context?.mode === 'SIMULATED';
  const copy = result ? resultCopy(result) : null;

  return <>
    <section className="lookup-section" aria-label="Resolve an auction listing">
      <ProviderNotice context={context} loading={checkingProvider && !context} />
      <form onSubmit={submit} aria-busy={loading}>
        <label htmlFor="auction-url">Copart or IAAI listing URL</label>
        <div className="input-row">
          <input ref={input} id="auction-url" name="url" type="url" autoComplete="off" required maxLength={2048}
            placeholder="https://www.copart.com/lot/51374586" value={url}
            onChange={event => updateUrl(event.target.value)}
            aria-describedby={`url-help${error ? ' lookup-error' : ''}`} aria-invalid={Boolean(error)} />
          <button className="submit-button" disabled={loading} type="submit">{loading ? 'Resolving…' : 'Resolve listing'}<ExternalArrow /></button>
        </div>
        <p id="url-help" className="help">Links are parsed without opening the auction page. IAAI page IDs stay distinct from stock numbers.</p>
      </form>
      {offline && <div className="examples"><span>{context.mode === 'FIXTURE' ? 'Try a fixture:' : 'Try a simulation:'}</span>
        {examples.map(example => <button key={example.url} type="button" disabled={loading}
          onClick={() => { updateUrl(example.url); input.current?.focus(); }}>
          {context.mode === 'FIXTURE' ? example.fixture : example.simulation}<ExternalArrow />
        </button>)}
      </div>}
    </section>

    <div className="result-region" aria-live="polite" aria-atomic="true">
      {loading && <div className="processing" role="status"><span className="loading-dot" aria-hidden="true" />Checking the listing identity…</div>}
      {error && <section className="error-panel" id="lookup-error" role="alert">
        <p className="eyebrow">URL COULD NOT BE RESOLVED</p><h2>This link cannot be resolved</h2><p>{error}</p>
      </section>}
      {!result && !error && !loading && <div className="empty-state"><span className="sheet-number">01</span><div>
        <h2>Identity first. Evidence always.</h2><p>Your result will show what matched, where the record came from, and what remains unknown.</p>
      </div></div>}
      {result && copy && <section className={`result-sheet ${result.status === 'MATCHED' ? 'is-matched' : 'needs-review'}`} aria-label="Listing resolution result">
        <div className="result-heading"><div><p className="eyebrow">RESOLUTION / {result.status.replaceAll('_', ' ')}</p><h2>{copy.title}</h2></div>
          <div className="badges"><span className="tag">{resultBadge(result)}</span>{result.provider_context.mode !== 'EXTERNAL' && result.provider_context.authorization === 'DENIED' && <span className="tag">ACCESS DENIED</span>}{historical && <span className="tag archived">{archived ? 'ARCHIVED' : 'HISTORICAL'}</span>}</div>
        </div>
        <p className="status-description">{copy.description}</p>
        {historical && <p className="historical-note">Historical auction record. This does not show a current listing or current bid.</p>}
        <dl className="identity-line">
          <div><dt>Auction house</dt><dd>{result.reference.house}</dd></div>
          {result.reference.page_id && <div><dt>IAAI page ID</dt><dd className="mono">{result.reference.page_id}</dd></div>}
          {result.reference.house === 'IAAI' && <div><dt>IAAI market</dt><dd>{value(result.reference.country)}</dd></div>}
          <div><dt>{result.reference.house === 'IAAI' ? 'Canonical stock number' : 'Canonical lot number'}</dt><dd className="mono">{result.identity?.lot_or_stock_number ?? 'Unresolved'}</dd></div>
        </dl>
        {result.vehicle && <div className="vehicle-block">
          <h3>{vehicleTitle(result.vehicle)}</h3><dl className="vehicle-facts">
            <div><dt>VIN</dt><dd className="mono">{value(result.vehicle.vin)}</dd></div>
            <div><dt>Reported primary damage</dt><dd>{value(result.vehicle.primary_damage)}</dd></div>
            <div><dt>Auction event status</dt><dd>{value(eventStatus)}</dd></div>
            <div><dt>Event date</dt><dd>{value(result.event_date)}</dd></div>
            <div><dt>Provider record ID</dt><dd className="mono">{value(result.record_id)}</dd></div>
            <div><dt>Sale event ID</dt><dd className="mono">{value(result.event_id)}</dd></div>
          </dl>
          <p className="help">{offline ? 'Synthetic metadata only. ' : ''}Vehicle condition has not been inspected.</p>
          <p className="help">No licensed photos supplied</p>
        </div>}
        {result.reasons.length > 0 && <div className="evidence-section"><h3>Resolution notes</h3><ul>{result.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul></div>}
        {result.evidence.length > 0 && <div className="evidence-section"><h3>Match evidence</h3><ul>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></div>}
        {result.status === 'AMBIGUOUS' && result.candidates.length > 0 && <div className="evidence-section">
          <h3>Candidate records — no selection made</h3><ol className="candidates">{result.candidates.map((candidate, index) => <li key={`${candidate.record_id}-${index}`}>
            <strong>{vehicleTitle(candidate.vehicle)}</strong>
            <span>{candidate.identity.house} / <span className="mono">{candidate.identity.lot_or_stock_number}</span></span>
            <span>VIN: <span className="mono">{value(candidate.vehicle.vin)}</span></span>
            <span>Record: <span className="mono">{candidate.record_id}</span> · Event: <span className="mono">{value(candidate.event_id)}</span></span>
            <span>{value(candidate.event_date)} / {value(candidate.event_status)}</span>
          </li>)}</ol>
        </div>}
        {provenance && <div className="provenance"><h3>Record provenance</h3><dl>
          <div><dt>Provider</dt><dd>{provenance.provider} / {provenance.source_name}</dd></div>
          <div><dt>Retrieved at</dt><dd><Time raw={provenance.retrieved_at} /></dd></div>
          <div><dt>Data type</dt><dd>{provenance.data_type} · {provenance.realtime ? 'Provider claims real-time; check source age' : 'Not a real-time feed'}</dd></div>
          <div><dt>Usage scope</dt><dd>{provenance.license_scope}</dd></div>
          <div><dt>Record reference</dt><dd className="mono">{provenance.source_url ?? 'Not supplied'}</dd></div>
        </dl>
          {sourceUrl && <a href={sourceUrl} target="_blank" rel="noopener noreferrer">Source reference <ExternalArrow /></a>}
          {safeSourceUrl(result.reference.url) && <p className="help"><a href={safeSourceUrl(result.reference.url)} target="_blank" rel="noopener noreferrer">Submitted auction link <ExternalArrow /></a> · Parsed only; page not fetched.</p>}
        </div>}
        {result.freshness && <section className={`freshness-section freshness-${result.freshness.status.toLowerCase()}`} aria-label="Source freshness">
          <div className="freshness-heading"><h3>Source freshness</h3><span className="tag archived">{freshnessLabels[result.freshness.status]}</span></div>
          <p>{result.freshness.basis}</p><dl className="freshness-facts">
            <div><dt>Source observed at</dt><dd><Time raw={result.freshness.source_observed_at} /></dd></div>
            <div><dt>Freshness assessment</dt><dd><Time raw={result.freshness.evaluated_at} /></dd></div>
          </dl>
          <p className="help">A recent retrieval does not make an old record current. Licensed access does not imply live auction data.</p>
        </section>}
        {(result.mapping_evidence || result.reference_evidence) && <details className="field-evidence identity-evidence">
          <summary>Identity verification details</summary>
          {result.mapping_evidence && <section><h3>{result.status === 'MATCHED' ? 'Page-to-stock mapping' : 'Page-to-stock mapping supplied for review'}</h3>
            {result.status !== 'MATCHED' && <p className="help">This mapping has not established a match. Review the resolution notes for missing or conflicting evidence.</p>}
            <p className="mapping-summary">IAAI market <span className="mono">{value(result.mapping_evidence.country)}</span> · Page <span className="mono">{result.mapping_evidence.page_id}</span> → {result.mapping_evidence.identity.house} stock <span className="mono">{result.mapping_evidence.identity.lot_or_stock_number}</span></p>
            <OriginDetails origin={result.mapping_evidence.origin} />
          </section>}
          {result.reference_evidence && <section><h3>Provider reference metadata</h3>{result.status !== 'MATCHED' && <p className="help">Supplied for review; its presence alone does not prove independent corroboration.</p>}<OriginDetails origin={result.reference_evidence.origin} /></section>}
        </details>}
        {result.field_evidence && Object.keys(result.field_evidence).length > 0 && <details className="field-evidence">
          <summary>Field-level evidence</summary><dl>{Object.entries(result.field_evidence).map(([field, evidence]) => <div key={field}>
            <dt>{field.replaceAll('_', ' ')}</dt><dd>{evidence.kind} · {evidence.source}<br />{evidence.note}</dd>
          </div>)}</dl>
        </details>}
        {result.status === 'MATCHED' && <InspectionPreview key={`${result.reference.url}-${result.snapshot_fingerprint ?? 'unbound'}`} resolution={result} />}
        {result.warnings.length > 0 && <aside className="warnings" aria-label="Data limitations"><h3>Read before using this result</h3><ul>{result.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></aside>}
      </section>}
    </div>
    <section className="scope-note"><p className="eyebrow">THE FIRST CHECK</p><p>This prototype checks listing identity and demonstrates an authored mock inspection workflow. It does not analyze actual vehicle photos, estimate repairs, or recommend a bid.</p></section>
  </>;
}
