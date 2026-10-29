'use client';

import { ChangeEvent, FormEvent, useEffect, useRef, useState } from 'react';
import { preparePhoto, type LocalPhoto } from '../../components/manual-review-photos';

type RuntimeStatus = { enabled: boolean; available: boolean; reason_code: string; message: string; model: string | null };
type Finding = { classification: 'OBSERVED' | 'SUSPECTED' | 'UNKNOWN'; component: string; region: string; description: string; rationale: string; confirmation: string; image_ids: string[]; confidence: null };
type Report = {
  schema_version: 'local-inspection-v1'; outcome: 'COMPLETED' | 'BLOCKED' | 'FAILED'; reason_code: string; reasons: string[];
  verification_status: 'UNVERIFIED'; review_status: 'EXPERIMENTAL_UNREVIEWED'; reference: { url: string; house: string; lot_number: string | null; page_id: string | null; country: string | null; stock_number: null };
  images: { image_id: string; label: string; source_sha256: string; inference_sha256: string; width: number; height: number }[];
  findings: Finding[]; checks: { system: string; status: 'UNKNOWN'; recommendation: string }[]; limitations: string[];
  provenance: { model: string; model_digest: string; mode: 'LOCAL_MODEL'; prompt_version: string; generated_at: string; image_digests: Record<string, string>; elapsed_ms: number } | null;
};
const classes = ['OBSERVED', 'SUSPECTED', 'UNKNOWN'] as const;
const classNames = { OBSERVED: 'Model observations — check against the photo', SUSPECTED: 'Model questions — confirmation needed', UNKNOWN: 'Unknown from these photos' };
const systems = ['Structural integrity', 'SRS and airbags', 'ADAS', 'Cooling', 'Suspension', 'Mechanical condition'];
const digestPattern = /^[a-f0-9]{64}$/;
function record(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
function strings(value: unknown): value is string[] { return Array.isArray(value) && value.every(item => typeof item === 'string'); }

function readReport(value: unknown, url: string, photos: LocalPhoto[], model: string | null): Report | null {
  if (!record(value) || value.schema_version !== 'local-inspection-v1' || !['COMPLETED', 'BLOCKED', 'FAILED'].includes(String(value.outcome))
    || value.verification_status !== 'UNVERIFIED' || value.review_status !== 'EXPERIMENTAL_UNREVIEWED' || !strings(value.reasons)
    || !strings(value.limitations) || !record(value.reference) || !Array.isArray(value.images) || !Array.isArray(value.findings) || !Array.isArray(value.checks)) return null;
  let parsed: URL;
  try { parsed = new URL(url); } catch { return null; }
  parsed.search = ''; parsed.hash = ''; parsed.pathname = parsed.pathname.replace(/\/$/, '');
  const copart = /^\/(?:[a-z]{2}\/)?lot\/([0-9]+)(?:\/[A-Za-z0-9_-]+)?$/i.exec(parsed.pathname);
  const iaai = /^\/(?:[a-z]{2}(?:-[a-z]{2})?\/)?VehicleDetail\/([A-Za-z0-9-]+)(?:~([A-Za-z]{2}))?$/i.exec(parsed.pathname);
  if (value.reference.url !== parsed.href || value.reference.stock_number !== null
    || value.reference.house !== (copart ? 'COPART' : 'IAAI') || value.reference.lot_number !== (copart?.[1] ?? null)
    || value.reference.page_id !== (iaai?.[1] ?? null) || value.reference.country !== (iaai?.[2]?.toUpperCase() ?? null)) return null;
  if (value.outcome !== 'COMPLETED') return value.images.length || value.findings.length || value.provenance ? null : value as Report;
  if (!record(value.provenance) || value.provenance.mode !== 'LOCAL_MODEL' || value.provenance.model !== model
    || !record(value.provenance.image_digests) || value.images.length !== photos.length || value.findings.length > 20
    || new Set(value.images.map(image => record(image) ? image.image_id : null)).size !== photos.length) return null;
  for (const image of value.images) {
    if (!record(image)) return null;
    const sent = photos.find(photo => photo.photo_id === image.image_id);
    if (!sent || image.source_sha256 !== sent.sha256 || typeof image.inference_sha256 !== 'string' || !digestPattern.test(image.inference_sha256)
      || value.provenance.image_digests[sent.photo_id] !== image.inference_sha256 || image.label !== sent.label) return null;
  }
  for (const finding of value.findings) {
    if (!record(finding) || !classes.includes(finding.classification as Finding['classification']) || finding.confidence !== null
      || !strings(finding.image_ids) || !finding.image_ids.every(id => photos.some(photo => photo.photo_id === id))
      || !['component', 'region', 'description', 'rationale', 'confirmation'].every(key => typeof finding[key] === 'string')
      || finding.classification !== 'UNKNOWN' && !finding.image_ids.length) return null;
  }
  if (value.checks.length !== 6 || !value.checks.every(check => record(check) && systems.includes(String(check.system)) && check.status === 'UNKNOWN' && typeof check.recommendation === 'string')
    || new Set(value.checks.map(check => (check as Record<string, unknown>).system)).size !== 6) return null;
  return value as Report;
}

async function prepareLocalPhoto(file: File, label: string): Promise<LocalPhoto> {
  const safe = await preparePhoto(file, label);
  const image = new Image();
  try {
    image.src = safe.preview_url; await image.decode();
    const ratio = Math.min(1, 1600 / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(1, Math.round(image.naturalWidth * ratio));
    const height = Math.max(1, Math.round(image.naturalHeight * ratio));
    const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
    const context = canvas.getContext('2d'); if (!context) throw new Error('This browser cannot prepare photos.');
    context.fillStyle = '#fff'; context.fillRect(0, 0, width, height); context.drawImage(image, 0, 0, width, height);
    const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob(value => value ? resolve(value) : reject(new Error('Photo preparation failed.')), 'image/jpeg', 0.85));
    if (blob.size > 2 * 1024 * 1024) throw new Error('The prepared image exceeds 2 MiB. Select a smaller photo.');
    const hash = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
    return { ...safe, width, height, sha256: Array.from(new Uint8Array(hash), value => value.toString(16).padStart(2, '0')).join(''), preview_url: URL.createObjectURL(blob) };
  } finally { image.src = ''; URL.revokeObjectURL(safe.preview_url); }
}
async function pixels(photo: LocalPhoto) {
  const blob = await (await fetch(photo.preview_url)).blob();
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader(); reader.onload = () => resolve(String(reader.result).split(',')[1]); reader.onerror = () => reject(new Error('The local photo is unavailable.'));
    reader.readAsDataURL(blob);
  });
}

export default function LocalInspection() {
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [checking, setChecking] = useState(true);
  const [url, setUrl] = useState(''); const [permission, setPermission] = useState(false);
  const [photos, setPhotos] = useState<LocalPhoto[]>([]); const [preparing, setPreparing] = useState(false);
  const [loading, setLoading] = useState(false); const [error, setError] = useState<string | null>(null); const [report, setReport] = useState<Report | null>(null);
  const local = useRef<LocalPhoto[]>([]); const alive = useRef(true); const sequence = useRef(0); const preparation = useRef(0);
  const controller = useRef<AbortController | null>(null); const heading = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => { alive.current = true; return () => { alive.current = false; sequence.current++; preparation.current++; controller.current?.abort(); local.current.forEach(photo => URL.revokeObjectURL(photo.preview_url)); }; }, []);
  async function refreshStatus(signal?: AbortSignal) {
    setChecking(true);
    try {
      const response = await fetch('/api/v1/local-vision/status', { cache: 'no-store', signal }); const data: unknown = await response.json();
      if (!response.ok || !record(data) || typeof data.enabled !== 'boolean' || typeof data.available !== 'boolean' || typeof data.message !== 'string') throw new Error();
      if (alive.current && !signal?.aborted) setRuntime(data as RuntimeStatus);
    } catch { if (alive.current && !signal?.aborted) { setRuntime(null); setError('Local model status could not be checked. No analysis has run.'); } }
    finally { if (alive.current && !signal?.aborted) setChecking(false); }
  }
  useEffect(() => { const abort = new AbortController(); void refreshStatus(abort.signal); return () => abort.abort(); }, []);
  function invalidate() { sequence.current++; controller.current?.abort(); setReport(null); setLoading(false); setError(null); }
  function clear() { invalidate(); preparation.current++; local.current.forEach(photo => URL.revokeObjectURL(photo.preview_url)); local.current = []; setPhotos([]); setUrl(''); setPermission(false); setPreparing(false); }
  async function select(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []); event.target.value = ''; if (!files.length) return;
    invalidate(); const batch = ++preparation.current; setPermission(false);
    if (files.length > 3 || files.reduce((total, file) => total + file.size, 0) > 24 * 1024 * 1024) { setError('Select up to three photos, no more than 24 MiB total.'); return; }
    setPreparing(true); const prepared: LocalPhoto[] = [];
    try {
      for (const [index, file] of files.entries()) {
        prepared.push(await prepareLocalPhoto(file, `Image ${index + 1}`));
        if (!alive.current || preparation.current !== batch) { prepared.forEach(photo => URL.revokeObjectURL(photo.preview_url)); return; }
      }
      local.current.forEach(photo => URL.revokeObjectURL(photo.preview_url)); local.current = prepared; setPhotos(prepared);
    } catch (cause) { prepared.forEach(photo => URL.revokeObjectURL(photo.preview_url)); if (alive.current && preparation.current === batch) setError(cause instanceof Error ? cause.message : 'Photo preparation failed.'); }
    finally { if (alive.current && preparation.current === batch) setPreparing(false); }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); invalidate();
    if (!permission || !photos.length || !runtime?.available) { setError('An available local model, photos and processing permission are required.'); return; }
    const request = ++sequence.current; const abort = new AbortController(); controller.current = abort; setLoading(true);
    const originalUrl = url.trim(); const selected = [...photos];
    try {
      const images = await Promise.all(selected.map(async photo => ({ image_id: photo.photo_id, label: photo.label, sha256: photo.sha256, content_base64: await pixels(photo) })));
      if (!alive.current || sequence.current !== request || abort.signal.aborted) return;
      const response = await fetch('/api/v1/local-inspections', { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, signal: abort.signal, body: JSON.stringify({ url: originalUrl, local_processing_permission: true, images }) });
      if (!response.ok) throw new Error('The local analysis request was rejected. Check the URL, image limits and processing permission.');
      const result = readReport(await response.json(), originalUrl, selected, runtime.model);
      if (!result) throw new Error('The response could not be bound to your selected photos. No model findings are shown.');
      if (alive.current && sequence.current === request && !abort.signal.aborted) { setReport(result); requestAnimationFrame(() => heading.current?.focus()); }
    } catch (cause) { if (alive.current && sequence.current === request && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'Local analysis failed.'); }
    finally { if (alive.current && sequence.current === request && !abort.signal.aborted) setLoading(false); }
  }
  function download() { if (!report) return; const object = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })); const a = document.createElement('a'); a.href = object; a.download = 'auction-intelligence-local-analysis.json'; a.click(); setTimeout(() => URL.revokeObjectURL(object), 1000); }
  return <div className="lv-workspace">
    <section className="lv-status" aria-label="Local model availability"><div><strong>{checking ? 'Checking local model…' : runtime?.available ? 'Local vision model ready' : 'Local vision is not ready'}</strong><p>{runtime?.message ?? 'An installed local Ollama vision model is required.'}</p>{runtime?.model && <p className="mono">{runtime.model}</p>}</div><button type="button" className="inspection-button" disabled={checking} onClick={() => void refreshStatus()}>Check local model</button></section>
    <form className="lv-form" onSubmit={submit} aria-busy={loading || preparing}>
      <label htmlFor="local-url">Copart or IAAI listing URL</label><input id="local-url" type="url" required maxLength={2048} value={url} onChange={event => { invalidate(); setUrl(event.target.value); }} /><p className="help">The reference is parsed only. No provider match or auction-page fetch takes place.</p>
      <label htmlFor="local-photos">Photos for local analysis</label><input id="local-photos" type="file" accept="image/png,image/jpeg,.png,.jpg,.jpeg" multiple disabled={preparing || loading} onChange={select} /><p className="help">Up to three PNG/JPEG originals, 8 MiB each. Prepared copies are resized and stripped of metadata. Selecting again replaces the photos.</p>
      {preparing && <p role="status">Preparing photos in this browser…</p>}
      <div className="lv-photos">{photos.map(photo => <figure key={photo.photo_id} id={`local-${photo.photo_id}`}><img src={photo.preview_url} width={photo.width} height={photo.height} alt={`${photo.label} — selected local evidence`} /><figcaption>{photo.label}</figcaption></figure>)}</div>
      <label className="lv-permission"><input type="checkbox" checked={permission} onChange={event => { invalidate(); setPermission(event.target.checked); }} />I have permission to process these photos with the local model.</label>
      <p className="lv-privacy">On Analyze, prepared photo bytes go to your application backend and its local Ollama service. Unlike the manual-review page, this action transmits photos to that backend. Use a trusted local installation; no hosted AI API is configured.</p>
      <div className="lv-actions"><button className="submit-button" disabled={!runtime?.available || loading || preparing || !photos.length || !permission}>{loading ? 'Local model is reviewing photos…' : 'Analyze with local model'}</button><button type="button" className="manual-text-button" onClick={clear}>Clear local analysis</button></div>
      {loading && <p role="status">CPU inference can take up to three minutes. Leaving this view does not guarantee the local model stops immediately.</p>}
    </form>
    {error && <div className="lv-error" role="alert">{error}</div>}
    {report && <section className="lv-report" aria-label="Local photo analysis result"><p className="eyebrow">EXPERIMENTAL / UNREVIEWED · IDENTITY UNVERIFIED</p><h2 tabIndex={-1} ref={heading}>{report.outcome === 'COMPLETED' ? 'Local model review' : 'Local analysis could not complete'}</h2><ul>{report.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>
      {report.outcome === 'COMPLETED' && <><p className="lv-privacy">Model-generated findings are unverified. Check each against the supplied photo and arrange qualified physical inspection.</p>{classes.map(kind => <section className="lv-findings" key={kind}><h3>{classNames[kind]}</h3>{report.findings.filter(finding => finding.classification === kind).length === 0 && <p>No model finding in this category. This does not establish absence of damage.</p>}{report.findings.filter(finding => finding.classification === kind).map((finding, index) => <article key={index}><h4>{finding.component} · {finding.region}</h4><p>{finding.description}</p><p>{finding.rationale}</p><p><strong>Physical confirmation:</strong> {finding.confirmation}</p>{finding.image_ids.map(id => <a key={id} href={`#local-${id}`}>View {photos.find(photo => photo.photo_id === id)?.label ?? 'evidence'} </a>)}</article>)}</section>)}
      <section><h3>Physical checks still needed</h3>{report.checks.map(check => <p key={check.system}><strong>{check.system} — UNKNOWN:</strong> {check.recommendation}</p>)}</section><section><h3>Coverage and limitations</h3><ul>{report.limitations.map((text, index) => <li key={index}>{text}</li>)}</ul></section><details><summary>Model and evidence provenance</summary><pre>{JSON.stringify(report.provenance, null, 2)}</pre></details><button type="button" className="inspection-button" onClick={download}>Download local analysis JSON</button></>}
    </section>}
  </div>;
}
