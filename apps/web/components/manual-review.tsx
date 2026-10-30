'use client';

import BuyerJourney from './buyer-journey';

import { ChangeEvent, FormEvent, useEffect, useRef, useState } from 'react';
import { FILE_LIMIT, PHOTO_LIMIT, TOTAL_LIMIT, preparePhoto, type LocalPhoto } from './manual-review-photos';
import VinLookup from './vin-lookup';
import { readManualReview, type ManualReviewReport, type ManualReviewRequest, type ReviewClassification, type ReviewFinding } from './manual-review-types';

const emptyFinding = (): ReviewFinding => ({ classification: 'UNKNOWN', photo_id: null, component: '', description: '' });
const classificationCopy = { OBSERVED: 'Observed by you', SUSPECTED: 'Suspected by you', UNKNOWN: 'Unknown / needs checking' };

export default function ManualReview({ initialUrl = '' }: { initialUrl?: string }) {
  const [url, setUrl] = useState(initialUrl);
  const [vin, setVin] = useState('');
  const [year, setYear] = useState('');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [stock, setStock] = useState('');
  const [notes, setNotes] = useState('');
  const [photos, setPhotos] = useState<LocalPhoto[]>([]);
  const [findings, setFindings] = useState<ReviewFinding[]>([]);
  const [permission, setPermission] = useState(false);
  const [preparing, setPreparing] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ManualReviewReport | null>(null);
  const photoState = useRef<LocalPhoto[]>([]);
  const active = useRef(true);
  const generation = useRef(0);
  const preparation = useRef(0);
  const photoLabels = useRef(0);
  const pending = useRef<AbortController | null>(null);
  const reportHeading = useRef<HTMLHeadingElement | null>(null);
  const iaai = /^https:\/\/(?:www\.|m\.)?iaai\.com(?::443)?(?:\/|$)/i.test(url.trim());

  useEffect(() => {
    active.current = true; setHydrated(true);
    return () => {
      active.current = false; generation.current++; preparation.current++; pending.current?.abort();
      photoState.current.forEach(photo => URL.revokeObjectURL(photo.preview_url));
    };
  }, []);

  function invalidate() {
    generation.current++; pending.current?.abort(); setLoading(false); setReport(null); setError(null);
  }
  function change(setter: (value: string) => void, value: string) { invalidate(); setter(value); }
  function assignPhotos(next: LocalPhoto[]) { photoState.current = next; setPhotos(next); }
  function updateFinding(index: number, patch: Partial<ReviewFinding>) {
    invalidate(); setFindings(current => current.map((finding, currentIndex) => currentIndex === index ? { ...finding, ...patch } : finding));
  }
  function removePhoto(id: string) {
    invalidate(); preparation.current++; setPreparing(false);
    const photo = photoState.current.find(item => item.photo_id === id);
    if (photo) URL.revokeObjectURL(photo.preview_url);
    assignPhotos(photoState.current.filter(item => item.photo_id !== id));
    setFindings(current => current.map(finding => finding.photo_id === id ? { ...finding, photo_id: null } : finding));
  }

  function clearReview() {
    invalidate(); preparation.current++; setPreparing(false);
    photoState.current.forEach(photo => URL.revokeObjectURL(photo.preview_url));
    assignPhotos([]); photoLabels.current = 0;
    setUrl(''); setVin(''); setYear(''); setMake(''); setModel(''); setStock(''); setNotes('');
    setFindings([]); setPermission(false);
  }

  async function choosePhotos(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = '';
    if (!files.length) return;
    invalidate();
    const batch = ++preparation.current;
    const current = photoState.current;
    if (current.length + files.length > PHOTO_LIMIT) { setError('Choose no more than six photos in total.'); return; }
    if (files.some(file => file.size > FILE_LIMIT || file.size === 0)) { setError('Each photo must be between 1 byte and 8 MiB.'); return; }
    if (current.reduce((total, photo) => total + photo.original_size, 0) + files.reduce((total, file) => total + file.size, 0) > TOTAL_LIMIT) {
      setError('Choose no more than 24 MiB of original photos in total.'); return;
    }
    setPreparing(true); setPermission(false);
    const prepared: LocalPhoto[] = [];
    try {
      for (const file of files) {
        prepared.push(await preparePhoto(file, `Photo ${++photoLabels.current}`));
        if (!active.current || preparation.current !== batch) { prepared.forEach(photo => URL.revokeObjectURL(photo.preview_url)); return; }
      }
      assignPhotos([...current, ...prepared]);
    } catch (cause) {
      prepared.forEach(photo => URL.revokeObjectURL(photo.preview_url));
      if (active.current && preparation.current === batch) setError(cause instanceof Error ? cause.message : 'The photos could not be prepared.');
    } finally {
      if (active.current && preparation.current === batch) setPreparing(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    invalidate();
    if (photos.length && !permission) { setError('Confirm permission to use the selected photos before building a review.'); return; }
    const body: ManualReviewRequest = {
      url: url.trim(), stock_number: iaai && stock.trim() ? stock.trim() : null,
      vehicle: { vin: vin.trim() || null, year: year ? Number(year) : null, make: make.trim() || null, model: model.trim() || null },
      photos: photos.map(({ photo_id, sha256, width, height, label }) => ({ photo_id, sha256, width, height, label })),
      findings: findings.map(finding => ({ ...finding, component: finding.component.trim(), description: finding.description.trim() })), notes,
    };
    if (body.findings.some(finding => finding.classification !== 'UNKNOWN' && !finding.photo_id)) { setError('Link every observed or suspected finding to one of your photos.'); return; }
    const request = ++generation.current;
    const controller = new AbortController(); pending.current = controller; setLoading(true);
    try {
      const response = await fetch('/api/v1/manual-reviews', { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });
      if (!response.ok) {
        let message = response.status === 422 ? 'Check the listing URL, VIN and finding details. Safety verdicts are not accepted in a manual review.' : 'The review could not be prepared. Your photos remain in this browser.';
        try { const errorBody = await response.json(); if (typeof errorBody.detail === 'string') message = errorBody.detail; } catch { /* Preserve the useful fallback. */ }
        throw new Error(message);
      }
      const result = readManualReview(await response.json(), body);
      if (!result) throw new Error('The review response could not be verified. No report has been attached.');
      if (active.current && generation.current === request && !controller.signal.aborted) {
        setReport(result);
        requestAnimationFrame(() => { if (active.current && generation.current === request) reportHeading.current?.focus(); });
      }
    } catch (cause) {
      if (active.current && generation.current === request && !controller.signal.aborted) setError(cause instanceof Error ? cause.message : 'The review is unavailable.');
    } finally {
      if (active.current && generation.current === request && !controller.signal.aborted) setLoading(false);
    }
  }

  function download() {
    if (!report) return;
    const objectUrl = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a'); anchor.href = objectUrl; anchor.download = 'auction-intelligence-manual-review.json'; anchor.click();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  }

  return <div className="manual-review-workspace">
    <BuyerJourney current="/review" reference={url} />
    <aside className="manual-intro-note"><strong>Your evidence. Clearly attributed.</strong><p>Record your own details and findings, keep photo references together, and take a checklist to an independent inspector. No paid API or AI service is used.</p></aside>
    <form className="manual-review-form" onSubmit={submit} aria-busy={loading || preparing}>
      <section className="manual-section"><div className="manual-section-title"><span className="mono">01</span><h2>Identify your reference</h2></div>
        <label htmlFor="review-url">Copart or IAAI listing URL</label><input id="review-url" type="url" required maxLength={2048} value={url} onChange={event => change(setUrl, event.target.value)} placeholder="https://www.copart.com/lot/51374586" />
        <p className="help">The URL is parsed, never fetched. Details you enter remain unverified.</p>
        <div className="manual-fields">
          <div><label htmlFor="review-vin">VIN (optional)</label><input id="review-vin" value={vin} maxLength={17} minLength={17} autoCapitalize="characters" onChange={event => change(setVin, event.target.value)} /></div>
          <div><label htmlFor="review-year">Year (optional)</label><input id="review-year" type="number" min={1900} max={new Date().getUTCFullYear() + 2} step={1} value={year} onChange={event => change(setYear, event.target.value)} /></div>
          <div><label htmlFor="review-make">Make (optional)</label><input id="review-make" value={make} maxLength={80} onChange={event => change(setMake, event.target.value)} /></div>
          <div><label htmlFor="review-model">Model (optional)</label><input id="review-model" value={model} maxLength={80} onChange={event => change(setModel, event.target.value)} /></div>
          {iaai && <div><label htmlFor="review-stock">IAAI stock number (optional)</label><input id="review-stock" value={stock} maxLength={32} inputMode="numeric" pattern="[0-9]+" onChange={event => change(setStock, event.target.value)} /><p className="help">Your reported stock number. It does not verify a page-to-stock match.</p></div>}
        </div>
        <VinLookup vin={vin} onApply={details => { invalidate(); setVin(details.vin); if (details.year !== null) setYear(String(details.year)); if (details.make !== null) setMake(details.make); if (details.model !== null) setModel(details.model); }} />
      </section>
      <section className="manual-section"><div className="manual-section-title"><span className="mono">02</span><h2>Keep photos beside your notes</h2></div>
        <label htmlFor="review-photos">Choose vehicle photos</label><input id="review-photos" type="file" accept="image/png,image/jpeg,.png,.jpg,.jpeg" multiple disabled={!hydrated || preparing} onChange={choosePhotos} />
        <p className="help">Optional: up to six PNG/JPEG photos, 8 MiB each and 24 MiB total. Photos stay in this browser. Prepared copies are resized to 2048 pixels and original metadata is removed.</p>
        {preparing && <p role="status" className="help">Preparing local photo copies…</p>}
        {photos.length > 0 && <><div className="manual-photo-grid" aria-label="Selected local photos">{photos.map(photo => <figure key={photo.photo_id}>
          <img src={photo.preview_url} width={photo.width} height={photo.height} alt={`${photo.label} — local review evidence`} />
          <figcaption><strong>{photo.label}</strong><span>{photo.width} × {photo.height} · browser-local</span><button type="button" className="manual-text-button" onClick={() => removePhoto(photo.photo_id)} aria-label={`Remove ${photo.label}`}>Remove</button></figcaption>
        </figure>)}</div><label className="manual-checkbox"><input type="checkbox" checked={permission} onChange={event => { invalidate(); setPermission(event.target.checked); }} />I have permission to use these photos for this local review.</label></>}
      </section>
      <section className="manual-section"><div className="manual-section-title"><span className="mono">03</span><h2>Write what you know</h2></div>
        <p className="manual-section-copy">These are your reported observations and questions. The application does not inspect the images or confirm damage.</p>
        {findings.map((finding, index) => <fieldset className="manual-finding-editor" key={index}><legend>Finding {index + 1}</legend>
          <div className="manual-fields"><div><label htmlFor={`finding-category-${index}`}>Finding {index + 1} category</label><select id={`finding-category-${index}`} value={finding.classification} onChange={event => updateFinding(index, { classification: event.target.value as ReviewClassification })}>{Object.entries(classificationCopy).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></div>
          <div><label htmlFor={`finding-photo-${index}`}>Finding {index + 1} photo</label><select id={`finding-photo-${index}`} required={finding.classification !== 'UNKNOWN'} value={finding.photo_id ?? ''} onChange={event => updateFinding(index, { photo_id: event.target.value || null })}><option value="">No photo reference</option>{photos.map(photo => <option key={photo.photo_id} value={photo.photo_id}>{photo.label}</option>)}</select></div></div>
          <label htmlFor={`finding-component-${index}`}>Finding {index + 1} component</label><input id={`finding-component-${index}`} value={finding.component} maxLength={100} required onChange={event => updateFinding(index, { component: event.target.value })} />
          <label htmlFor={`finding-description-${index}`}>Finding {index + 1} description</label><textarea id={`finding-description-${index}`} value={finding.description} maxLength={1200} required rows={3} onChange={event => updateFinding(index, { description: event.target.value })} />
          <button type="button" className="manual-text-button" onClick={() => { invalidate(); setFindings(current => current.filter((_, currentIndex) => currentIndex !== index)); }}>Remove finding {index + 1}</button>
        </fieldset>)}
        <button type="button" className="inspection-button" disabled={findings.length >= 30} onClick={() => { invalidate(); setFindings(current => [...current, emptyFinding()]); }}>Add a finding</button>
        <label htmlFor="review-notes" className="manual-notes-label">Review notes (optional)</label><textarea id="review-notes" value={notes} maxLength={2000} rows={4} onChange={event => change(setNotes, event.target.value)} />
      </section>
      <div className="manual-submit"><p className="help">Vehicle details, notes and photo descriptions/hashes go to the local backend. Photo files are never uploaded. This session clears on reload.</p><div className="manual-submit-actions"><button className="submit-button" type="submit" disabled={loading || preparing}>{loading ? 'Building your review…' : 'Build my review'}</button><button type="button" className="manual-text-button" onClick={clearReview}>Clear review</button></div></div>
    </form>
    {error && <div className="manual-error" role="alert"><strong>Review needs attention</strong><p>{error}</p></div>}
    {report && <section className="manual-review-report" aria-label="Your evidence review">
      <div className="manual-report-heading"><div><p className="eyebrow">YOUR REVIEW / {new Date(report.generated_at).toISOString().slice(0, 10)}</p><h2 ref={reportHeading} tabIndex={-1}>Your evidence review</h2></div><span className="tag">USER-SUPPLIED · UNVERIFIED</span></div>
      <p className="manual-report-notice">Compiled from your entries. No provider match, image analysis or vehicle-condition assessment was performed.</p>
      <dl className="manual-report-facts"><div><dt>Auction house</dt><dd>{report.reference.house}</dd></div><div><dt>{report.reference.house === 'IAAI' ? 'User-reported stock number' : 'Lot number parsed from URL'}</dt><dd>{report.canonical_claim.lot_or_stock_number ?? 'Not supplied'}</dd></div>
        {report.reference.page_id && <div><dt>IAAI page ID</dt><dd>{report.reference.page_id}</dd></div>}{report.reference.country && <div><dt>IAAI market</dt><dd>{report.reference.country}</dd></div>}
        <div><dt>Vehicle details supplied by you</dt><dd>{[report.vehicle.year, report.vehicle.make, report.vehicle.model].filter(Boolean).join(' ') || 'Not supplied'}</dd></div><div><dt>User-reported VIN</dt><dd className="mono">{report.vehicle.vin ?? 'Not supplied'}</dd></div><div className="manual-wide"><dt>Parsed source reference</dt><dd>{report.reference.url}</dd></div></dl>
      {report.notes && <section className="manual-report-section"><h3>Your notes</h3><p className="manual-preserve-text">{report.notes}</p></section>}
      {report.photos.length > 0 && <section className="manual-report-section"><h3>Your local evidence</h3><p className="help">Hashes describe prepared browser copies and are client-declared. The server has not received or verified their pixels or listing linkage.</p><div className="manual-photo-grid">{report.photos.map(photo => {
        const local = photos.find(item => item.photo_id === photo.photo_id);
        return local && <figure key={photo.photo_id} id={`evidence-${photo.photo_id}`}><img src={local.preview_url} width={photo.width} height={photo.height} alt={`${photo.label} — local review evidence`} /><figcaption><strong>{photo.label}</strong><span className="mono manual-hash">SHA-256 {photo.sha256}</span></figcaption></figure>;
      })}</div></section>}
      <section className="manual-report-section"><h3>Your reported findings</h3>{report.findings.length === 0 ? <p>No findings entered. This does not establish that damage is absent.</p> : report.findings.map((finding, index) => <article key={index} className="manual-reported-finding"><span className="tag archived">{finding.classification} · USER REPORTED</span><h4>{finding.component}</h4><p className="manual-preserve-text">{finding.description}</p>{finding.photo_id && <a href={`#evidence-${finding.photo_id}`}>View {report.photos.find(photo => photo.photo_id === finding.photo_id)?.label ?? 'referenced photo'}</a>}</article>)}</section>
      <section className="manual-report-section"><h3>Take these questions to an inspector</h3><p>These six systems remain unknown. This checklist is guidance for qualified physical inspection.</p><div className="manual-checklist">{report.checks.map(check => <article key={check.system}><div><h4>{check.system}</h4><span className="tag archived">UNKNOWN</span></div><p>{check.recommendation}</p></article>)}</div></section>
      <aside className="warnings" aria-label="Manual review limitations"><h3>Review limitations</h3><ul>{report.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></aside>
      <div className="manual-report-actions"><button type="button" className="inspection-button" onClick={download}>Download review JSON</button><button type="button" className="inspection-button" onClick={() => window.print()}>Print review</button><p className="help">JSON contains the report and photo metadata; image files are not included. Printing can include the browser-local photos.</p></div>
    </section>}
  </div>;
}
