'use client';

import { useEffect, useRef, useState } from 'react';

export type ManufacturerDetails = { vin: string; year: number | null; make: string | null; model: string | null };
type Decode = {
  schema_version: 'vin-decode-v1'; vin: string; outcome: 'DECODED' | 'PARTIAL' | 'UNAVAILABLE' | 'INVALID_VIN';
  source: 'NHTSA_VPIC'; source_url: string; retrieved_at: string; identity_status: 'NOT_AUCTION_VERIFIED';
  vehicle: Omit<ManufacturerDetails, 'vin'> & { body_class?: string | null; drive_type?: string | null; fuel_type?: string | null; engine_displacement_cc?: string | null }; errors: { code: string; description: string }[]; warnings: string[];
};
function record(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
function readDecode(value: unknown, vin: string): Decode | null {
  if (!record(value) || value.schema_version !== 'vin-decode-v1' || value.vin !== vin
    || !['DECODED', 'PARTIAL', 'UNAVAILABLE', 'INVALID_VIN'].includes(String(value.outcome))
    || value.source !== 'NHTSA_VPIC' || value.identity_status !== 'NOT_AUCTION_VERIFIED'
    || typeof value.source_url !== 'string' || typeof value.retrieved_at !== 'string' || !Number.isFinite(Date.parse(value.retrieved_at))
    || !record(value.vehicle) || !Array.isArray(value.errors) || !value.errors.every(item => record(item) && typeof item.code === 'string' && typeof item.description === 'string')
    || !Array.isArray(value.warnings) || !value.warnings.every(item => typeof item === 'string')) return null;
  const vehicle = value.vehicle;
  if (vehicle.year !== null && (typeof vehicle.year !== 'number' || !Number.isInteger(vehicle.year) || vehicle.year < 1886 || vehicle.year > 2100)
    || vehicle.make !== null && typeof vehicle.make !== 'string' || vehicle.model !== null && typeof vehicle.model !== 'string') return null;
  for (const key of ['body_class', 'drive_type', 'fuel_type', 'engine_displacement_cc']) {
    const field = vehicle[key];
    if (field !== undefined && field !== null && (typeof field !== 'string' || field.length > 200)) return null;
  }
  if (['UNAVAILABLE', 'INVALID_VIN'].includes(String(value.outcome)) && Object.values(vehicle).some(item => item !== null)) return null;
  return value as Decode;
}

export default function VinLookup({ vin, onApply }: { vin: string; onApply: (details: ManufacturerDetails) => void }) {
  const normalizedVin = vin.trim().toUpperCase();
  const valid = /^[A-HJ-NPR-Z0-9]{17}$/.test(normalizedVin);
  const [result, setResult] = useState<Decode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [applied, setApplied] = useState(false);
  const active = useRef(true);
  const sequence = useRef(0);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => {
    sequence.current++; pending.current?.abort(); setResult(null); setError(null); setLoading(false); setApplied(false);
  }, [vin]);
  useEffect(() => { active.current = true; return () => { active.current = false; sequence.current++; pending.current?.abort(); }; }, []);
  async function lookup() {
    if (!valid) { setError('Enter a 17-character VIN using letters and digits, excluding I, O and Q.'); return; }
    const request = ++sequence.current; pending.current?.abort();
    const abort = new AbortController(); pending.current = abort; setLoading(true); setResult(null); setError(null); setApplied(false);
    try {
      const response = await fetch('/api/v1/vehicles/decode-vin', { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ vin: normalizedVin }), signal: abort.signal });
      if (!response.ok) throw new Error(response.status === 422 ? 'Check the VIN format before looking up manufacturer details.' : 'Manufacturer details could not be retrieved. You can still enter your own details.');
      const decoded = readDecode(await response.json(), normalizedVin);
      if (!decoded) throw new Error('The manufacturer response did not match this VIN. No details have been applied.');
      if (active.current && sequence.current === request && !abort.signal.aborted) setResult(decoded);
    } catch (cause) { if (active.current && sequence.current === request && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'Manufacturer details are unavailable.'); }
    finally { if (active.current && sequence.current === request && !abort.signal.aborted) setLoading(false); }
  }
  const current = result?.vin === normalizedVin ? result : null;
  const usable = current ? { year: current.vehicle.year !== null && current.vehicle.year >= 1900 && current.vehicle.year <= new Date().getUTCFullYear() + 2 ? current.vehicle.year : null, make: current.vehicle.make && current.vehicle.make.length <= 80 ? current.vehicle.make : null, model: current.vehicle.model && current.vehicle.model.length <= 80 ? current.vehicle.model : null } : null;
  const canApply = current && usable && ['DECODED', 'PARTIAL'].includes(current.outcome) && Object.values(usable).some(value => value !== null);
  const outsideFormBounds = current && usable && Object.keys(usable).some(key => usable[key as keyof typeof usable] !== current.vehicle[key as keyof typeof usable]);
  return <section className="vin-lookup" aria-label="Manufacturer VIN lookup">
    <div className="vin-lookup-heading"><h3>Check manufacturer details</h3><span className="tag archived">FREE · NHTSA vPIC</span></div>
    <p className="help">Optional: sends this VIN to NHTSA’s free US government service. No photos are sent. This decodes manufacturing details; it does not check auction identity, vehicle history or condition.</p>
    <button type="button" className="inspection-button" disabled={loading || !valid} onClick={lookup}>{loading ? 'Looking up manufacturer details…' : 'Look up manufacturer details'}</button>
    <div aria-live="polite">
      {error && <p role="alert" className="vin-lookup-error">{error}</p>}
      {current && <div className="vin-lookup-result">
        <h4>{current.outcome === 'DECODED' ? 'Manufacturer details returned' : current.outcome === 'PARTIAL' ? 'Partial manufacturer details' : current.outcome === 'INVALID_VIN' ? 'VIN could not be decoded' : 'Manufacturer service unavailable'}</h4>
        {canApply && <><dl><div><dt>Make</dt><dd>{current.vehicle.make ?? 'Not returned'}</dd></div><div><dt>Model</dt><dd>{current.vehicle.model ?? 'Not returned'}</dd></div><div><dt>Model year</dt><dd>{current.vehicle.year ?? 'Not returned'}</dd></div></dl><button type="button" className="inspection-button" disabled={applied} onClick={() => {
          if (current.vin !== vin.trim().toUpperCase()) return;
          if (!usable) return;
          onApply({ vin: current.vin, ...usable }); setApplied(true);
        }}>{applied ? 'Manufacturer details applied' : 'Use manufacturer details'}</button></>}
        {['DECODED', 'PARTIAL'].includes(current.outcome) && [current.vehicle.body_class, current.vehicle.drive_type, current.vehicle.fuel_type, current.vehicle.engine_displacement_cc].some(Boolean) && <><h4>More manufacturer-reported details</h4><dl>{([['Body', current.vehicle.body_class], ['Drivetrain', current.vehicle.drive_type], ['Fuel', current.vehicle.fuel_type], ['Engine displacement (cm³)', current.vehicle.engine_displacement_cc]] as const).map(([label, detail]) => detail && <div key={label}><dt>{label}</dt><dd>{detail}</dd></div>)}</dl><p className="help">Manufacturer-reported specifications are unverified for this physical vehicle and are not applied to your review or tax calculation.</p></>}
        {outsideFormBounds && <p className="help">Some returned values exceed this review form’s supported bounds and will not be copied. Missing values leave your existing entries unchanged.</p>}
        {current.errors.length > 0 && <ul>{current.errors.map((item, index) => <li key={index}>{item.description}</li>)}</ul>}
        {current.warnings.length > 0 && <ul>{current.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
        <p className="help">Source: <a href="https://vpic.nhtsa.dot.gov/api/" target="_blank" rel="noopener noreferrer">NHTSA vPIC</a>. Auction identity remains unverified. Details are copied only when you select Use manufacturer details.</p>
      </div>}
    </div>
  </section>;
}
