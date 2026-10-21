'use client';

import { useEffect, useRef, useState } from 'react';
import { guardedAssetUrl, readInspectionPreview, type InspectionFinding, type InspectionPreview as Preview } from './inspection-types';
import type { Resolution } from './resolution-types';

const groups = [
  { kind: 'OBSERVED', title: 'Observed in the illustration', note: 'Hand-authored visible features in the example image.' },
  { kind: 'SUSPECTED', title: 'Suspected — needs confirmation', note: 'Possible consequences, not confirmed damage or required repairs.' },
  { kind: 'UNKNOWN', title: 'Unknown — physical checks needed', note: 'An illustration cannot establish hidden condition or functionality.' },
] as const;

function displayTime(raw: string) {
  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? raw : date.toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC');
}

export default function InspectionPreview({ resolution }: { resolution: Resolution }) {
  const [report, setReport] = useState<Preview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusedFinding, setFocusedFinding] = useState<string | null>(null);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());
  const active = useRef(true);
  const sequence = useRef(0);
  const abort = useRef<AbortController | null>(null);
  const gallery = useRef<HTMLElement | null>(null);
  const fingerprint = resolution.snapshot_fingerprint;

  useEffect(() => {
    active.current = true;
    return () => { active.current = false; sequence.current += 1; abort.current?.abort(); };
  }, []);

  async function openPreview() {
    if (!fingerprint) return;
    const request = ++sequence.current;
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setLoading(true); setError(null); setReport(null); setSelectedId(null); setFocusedFinding(null); setFailedImages(new Set());
    try {
      const response = await fetch('/api/v1/inspections', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store', signal: controller.signal,
        body: JSON.stringify({ url: resolution.reference.url, expected_snapshot_fingerprint: fingerprint }),
      });
      if (!response.ok) throw new Error('The preview could not be prepared. No inspection findings have been supplied.');
      const body = readInspectionPreview(await response.json());
      if (!body) throw new Error('The preview response could not be verified. No inspection findings are shown.');
      if (!active.current || sequence.current !== request || controller.signal.aborted) return;
      if (body.outcome === 'COMPLETED' || body.outcome === 'PARTIAL') {
        const target = body.target;
        if (!target || target.snapshot_fingerprint !== fingerprint
          || target.provider_context.id !== resolution.provider_context.id
          || target.provider_context.mode !== resolution.provider_context.mode
          || target.identity.house !== resolution.identity?.house
          || target.identity.lot_or_stock_number !== resolution.identity?.lot_or_stock_number
          || target.record_id !== resolution.record_id || target.event_id !== resolution.event_id) {
          throw new Error('The listing snapshot changed. Resolve the listing again before opening a preview.');
        }
      }
      setReport(body);
      setSelectedId(body.assets[0]?.asset_id ?? null);
    } catch (cause) {
      if (!active.current || sequence.current !== request || controller.signal.aborted) return;
      setError(cause instanceof Error ? cause.message : 'The preview is unavailable. No inspection findings are shown.');
    } finally {
      if (active.current && sequence.current === request && !controller.signal.aborted) setLoading(false);
    }
  }

  const eligible = resolution.preview_eligibility?.available === true && Boolean(fingerprint);
  if (!eligible) return <section className="inspection-unavailable" aria-label="Inspection preview availability">
    <h3>Inspection preview</h3>
    <p>{resolution.preview_eligibility?.reason ?? 'No eligible authored preview images are available for this listing.'}</p>
    <p className="help">A matched listing does not establish photo rights or an inspected vehicle condition.</p>
  </section>;

  const targetChanged = report?.reason_code === 'TARGET_CHANGED';
  const successful = report?.outcome === 'COMPLETED' || report?.outcome === 'PARTIAL';
  const selected = report?.assets.find(asset => asset.asset_id === selectedId) ?? null;
  const selectedSrc = selected && fingerprint ? guardedAssetUrl(selected, fingerprint) : null;
  const selectedFailed = selected ? failedImages.has(selected.asset_id) : false;
  const allImagesFailed = Boolean(report?.assets.length) && report!.assets.every(asset => failedImages.has(asset.asset_id));

  function selectFinding(finding: InspectionFinding) {
    const id = finding.image_ids.find(imageId => !failedImages.has(imageId));
    if (id) {
      setSelectedId(id);
      setFocusedFinding(finding.finding_id);
      gallery.current?.focus({ preventScroll: true });
      gallery.current?.scrollIntoView({ behavior: 'instant', block: 'nearest' });
    }
  }

  return <section className="inspection-preview" aria-label="Mock inspection preview">
    <div className="inspection-heading"><div><p className="eyebrow">THE NEXT CHECK / DEMONSTRATION</p><h3>Mock inspection preview</h3></div><span className="tag">MOCK</span></div>
    <p className="inspection-mock-notice">MOCK INSPECTION PREVIEW — hand-authored example, no AI analysis</p>
    <p className="inspection-intro">Explore how image evidence, uncertainty and physical checks connect. These are project-authored illustrations, not auction photographs or an inspection of this vehicle.</p>
    {!targetChanged && <button type="button" className="inspection-button" onClick={openPreview} disabled={loading}>
      {loading ? 'Preparing MOCK preview…' : report || error ? 'Retry MOCK inspection preview' : 'Open MOCK inspection preview'}
    </button>}
    <div aria-live="polite" aria-atomic="false">
      {loading && <p className="processing" role="status">Checking the exact snapshot and authored image permissions…</p>}
      {error && <div className="inspection-message" role="alert"><h4>Preview could not be completed</h4><p>{error}</p></div>}
      {report && !successful && <div className="inspection-message" role="alert">
        <h4>{targetChanged ? 'Listing changed — resolve it again' : report.outcome === 'BLOCKED' ? 'Preview blocked' : 'Preview could not be completed'}</h4>
        <ul>{report.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>
        <p>No inspection findings have been supplied.</p>
      </div>}
      {successful && report && <div className="inspection-report">
        {report.outcome === 'PARTIAL' && <div className="inspection-message"><h4>Partial mock preview</h4><p>Some example evidence is unavailable or excluded. Missing evidence is not proof that damage is absent.</p></div>}
        {report.reasons.length > 0 && <ul className="inspection-notes">{report.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>}
        <section className="inspection-gallery" aria-label="Authored image gallery" tabIndex={-1} ref={gallery}>
          <div className="inspection-section-heading"><h4>Authored image gallery</h4><span>{report.assets.length} illustrative views</span></div>
          <div className="illustration-controls" role="group" aria-label="Select an authored illustration">
            {report.assets.map((asset, index) => <button key={asset.asset_id} type="button" aria-pressed={asset.asset_id === selectedId}
              aria-label={`Show ${asset.view_label} illustration`} onClick={() => { setSelectedId(asset.asset_id); setFocusedFinding(null); }}>
              <span className="mono">{String(index + 1).padStart(2, '0')}</span> {asset.view_label}{failedImages.has(asset.asset_id) && <span> · unavailable</span>}
            </button>)}
          </div>
          {selected && <figure className="inspection-figure">
            {selectedSrc && !selectedFailed ? <img key={`${selected.asset_id}-${selected.content_sha256}`} src={selectedSrc} width={selected.width} height={selected.height}
              alt={selected.alt_text} onError={() => setFailedImages(current => new Set(current).add(selected.asset_id))} />
              : <div className="illustration-unavailable" role="alert"><strong>Illustration unavailable</strong><p>Its evidence-linked observations are withheld. Retry the preview to recheck image access.</p></div>}
            <figcaption><strong>{selected.title}</strong><span>SELF-AUTHORED ILLUSTRATION · NOT AN AUCTION PHOTO</span><span>{selected.author} · Capture time: {selected.capture_time ? displayTime(selected.capture_time) : 'Not applicable to an illustration'}</span></figcaption>
          </figure>}
          {selected && !selectedFailed && <p className="help">Image references identify the illustration; no unverified damage-location overlays are drawn.</p>}
        </section>
        {allImagesFailed && <div className="inspection-message" role="alert"><h4>Illustrations unavailable</h4><p>Observed and suspected findings cannot be checked against their evidence and are withheld. Physical-inspection unknowns remain.</p></div>}
        <div className="inspection-findings" aria-label="Findings by evidence category">
          {groups.map(group => <section key={group.kind} className={`finding-group finding-group-${group.kind.toLowerCase()}`}>
            <div className="inspection-section-heading"><h4>{group.title}</h4><span className="tag archived">{group.kind}</span></div><p className="help">{group.note}</p>
            {report.findings.filter(finding => finding.classification === group.kind).length === 0 && <p className="finding-empty">No seeded finding in this category. This is not evidence of an undamaged vehicle.</p>}
            {report.findings.filter(finding => finding.classification === group.kind).map(finding => {
              const unavailable = finding.classification !== 'UNKNOWN' && finding.image_ids.some(id => failedImages.has(id));
              const related = selectedId !== null && finding.image_ids.includes(selectedId);
              return <article key={finding.finding_id} className={`finding-entry${related ? ' finding-related' : ''}${focusedFinding === finding.finding_id ? ' finding-focused' : ''}`}>
                {unavailable ? <p>Evidence image unavailable — this finding is withheld.</p> : <>
                  <p className="finding-component">{finding.component}<span>{finding.region}</span></p>
                  <p className="finding-description">{finding.description}</p>
                  <p className="finding-rationale">{finding.rationale}</p>
                  <p className="finding-confirmation"><strong>Recommended check:</strong> {finding.confirmation}</p>
                  <p className="help">Severity: {finding.severity} · Confidence: not scored. {finding.confidence_basis}</p>
                  {finding.image_ids.length > 0 && <button type="button" className="finding-image-link" onClick={() => selectFinding(finding)} disabled={finding.image_ids.every(id => failedImages.has(id))}>
                    View image for {finding.component}<svg className="external-arrow" aria-hidden="true" width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 12 12 4M4 4h8v8" stroke="currentColor" strokeWidth="1.5" /></svg>
                  </button>}
                  {related && <p className="finding-related-note">Related to the selected illustration</p>}
                </>}
              </article>;
            })}
          </section>)}
        </div>
        <section className="inspection-checks"><h4>Physical-inspection checklist</h4><ul>{report.checks.map((check, index) => <li key={index}>{check}</li>)}</ul><p className="help">These are suggested checks, not diagnoses, required repairs or a roadworthiness assessment.</p></section>
        <section className="inspection-limitations"><h4>Coverage and limitations</h4><ul>{report.limitations.map((limitation, index) => <li key={index}>{limitation}</li>)}</ul></section>
        {report.exclusions.length > 0 && <section className="inspection-exclusions"><h4>Excluded evidence</h4><ul>{report.exclusions.map((exclusion, index) => <li key={index}>{exclusion.asset_id ? `${exclusion.asset_id}: ` : ''}{exclusion.reason}</li>)}</ul></section>}
        {report.provenance && <details className="field-evidence inspection-provenance"><summary>Preview provenance</summary><dl>
          <div><dt>Engine</dt><dd>{report.provenance.engine_id} / {report.provenance.engine_version}</dd></div>
          <div><dt>Fixture / schema revision</dt><dd>{report.provenance.fixture_revision} / {report.provenance.schema_version}</dd></div>
          <div><dt>Preview generated at</dt><dd><time dateTime={report.provenance.generated_at}>{displayTime(report.provenance.generated_at)}</time></dd></div>
          <div><dt>Model and prompt</dt><dd>Not applicable — deterministic mock; no AI provider called.</dd></div>
          <div><dt>Bound snapshot</dt><dd className="mono">{report.target?.snapshot_fingerprint}</dd></div>
          <div><dt>Bound record / sale event</dt><dd>{report.target?.record_id} / {report.target?.event_id ?? 'Not supplied'}</dd></div>
        </dl></details>}
      </div>}
    </div>
  </section>;
}
