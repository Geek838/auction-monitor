'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';

type Input = {
  production_year_confirmed: boolean | null; planned_declaration_date: string | null; declaration_year: number | null; production_year: number | null; engine_cc: number | null;
  commodity_code: string; vehicle_category: string; powertrain: string; steering: string; procedure: string;
  exemption_claimed: boolean | null; special_status: boolean | null;
};
type Report = {
  schema_version: 'georgia-excise-v1'; source_kind: 'STATUTORY_COMPONENT_USER_DECLARED_FACTS'; outcome: 'CALCULATED_COMPONENT' | 'WITHHELD'; currency: 'GEL';
  excise_amount: string | null; age_years: number | null; rate_gel_per_cc: string | null; request: Input;
  rule: { id: string; source_url: string; source_publication: string; source_clauses: string[]; reviewed_on: string; supported_declaration_year: 2026; application_review_expires_on: string };
  issues: { code: string; message: string }[]; other_clearance_components: 'NOT_CALCULATED'; generated_at: string; warnings: string[];
};
const selectFields = [
  { key: 'commodity_code', label: 'Commodity classification', options: [['8703', '8703 — confirmed'], ['OTHER', 'Another classification']] },
  { key: 'vehicle_category', label: 'Vehicle category', options: [['ORDINARY_PASSENGER', 'Ordinary passenger car'], ['SPORT', 'Sport'], ['CLASSIC', 'Classic'], ['OTHER', 'Other']] },
  { key: 'powertrain', label: 'Powertrain', options: [['PETROL', 'Conventional petrol (not hybrid)'], ['DIESEL', 'Conventional diesel (not hybrid)'], ['HYBRID', 'Hybrid'], ['ELECTRIC', 'Electric'], ['OTHER', 'Other']] },
  { key: 'steering', label: 'Steering configuration', options: [['ORIGINAL_LEFT', 'Original left-hand drive, never converted'], ['RIGHT', 'Right-hand drive'], ['CONVERTED', 'Converted steering']] },
  { key: 'procedure', label: 'Import procedure', options: [['GEORGIA_FREE_CIRCULATION', 'Free circulation for registration in Georgia'], ['RE_EXPORT', 'Re-export'], ['OTHER', 'Other']] },
] as const;
function record(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
function strings(value: unknown): value is string[] { return Array.isArray(value) && value.every(item => typeof item === 'string'); }
function readReport(value: unknown, request: Input): Report | null {
  if (!record(value) || value.schema_version !== 'georgia-excise-v1' || !['CALCULATED_COMPONENT', 'WITHHELD'].includes(String(value.outcome))
    || value.source_kind !== 'STATUTORY_COMPONENT_USER_DECLARED_FACTS' || value.currency !== 'GEL' || value.other_clearance_components !== 'NOT_CALCULATED' || !record(value.request)
    || Object.entries(request).some(([key, item]) => (value.request as Record<string, unknown>)[key] !== item)
    || !record(value.rule) || typeof value.rule.id !== 'string' || typeof value.rule.source_url !== 'string'
    || !/^https:\/\/matsne\.gov\.ge\//.test(value.rule.source_url) || typeof value.rule.source_publication !== 'string' || !strings(value.rule.source_clauses)
    || typeof value.rule.reviewed_on !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value.rule.reviewed_on)
    || value.rule.supported_declaration_year !== 2026 || typeof value.rule.application_review_expires_on !== 'string'
    || !Array.isArray(value.issues) || !value.issues.every(item => record(item) && typeof item.code === 'string' && typeof item.message === 'string')
    || !strings(value.warnings) || typeof value.generated_at !== 'string' || !Number.isFinite(Date.parse(value.generated_at))) return null;
  if (value.outcome === 'CALCULATED_COMPONENT') {
    if (typeof value.excise_amount !== 'string' || !/^(?:0|[1-9][0-9]*)\.[0-9]{2}$/.test(value.excise_amount)
      || typeof value.rate_gel_per_cc !== 'string' || !/^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/.test(value.rate_gel_per_cc)
      || !Number.isInteger(value.age_years) || Number(value.age_years) < 0 || value.issues.length !== 0) return null;
  } else if (value.excise_amount !== null || value.rate_gel_per_cc !== null) return null;
  return value as Report;
}
const initial: Input = { production_year_confirmed: false, planned_declaration_date: null, declaration_year: null, production_year: null, engine_cc: null, commodity_code: 'UNKNOWN', vehicle_category: 'UNKNOWN', powertrain: 'UNKNOWN', steering: 'UNKNOWN', procedure: 'UNKNOWN', exemption_claimed: null, special_status: null };
function display(value: string) { const [whole, cents] = value.split('.'); return `${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${cents}`; }

export default function GeorgiaExcise() {
  const [input, setInput] = useState<Input>(initial);
  const [productionYear, setProductionYear] = useState('');
  const [engineCc, setEngineCc] = useState('');
  const [report, setReport] = useState<Report | null>(null); const [error, setError] = useState<string | null>(null); const [loading, setLoading] = useState(false);
  const active = useRef(true); const sequence = useRef(0); const pending = useRef<AbortController | null>(null);
  useEffect(() => { active.current = true; return () => { active.current = false; sequence.current++; pending.current?.abort(); }; }, []);
  function invalidate() { sequence.current++; pending.current?.abort(); setReport(null); setError(null); setLoading(false); }
  function update(key: keyof Input, value: Input[keyof Input]) { invalidate(); setInput(previous => ({ ...previous, [key]: value })); }
  async function calculate(event: FormEvent) {
    event.preventDefault(); invalidate();
    if (productionYear && !/^[0-9]{4}$/.test(productionYear) || engineCc && !/^[1-9][0-9]{0,4}$/.test(engineCc)) {
      setError('Use a four-digit production year and a whole engine displacement in cm³, such as 2000. Do not enter litres such as 2.0.'); return;
    }
    const request = { ...input, production_year: productionYear ? Number(productionYear) : null, engine_cc: engineCc ? Number(engineCc) : null };
    const id = ++sequence.current; const abort = new AbortController(); pending.current = abort; setLoading(true);
    try {
      const response = await fetch('/api/v1/georgia/excise', { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request), signal: abort.signal });
      if (!response.ok) throw new Error(response.status === 422 ? 'Check the production year and engine displacement. This tool accepts years from 1886 to 2100 and displacement from 1 to 20,000 cm³.' : 'The excise component could not be calculated. No amount was produced.');
      const result = readReport(await response.json(), request);
      if (!result) throw new Error('The excise response could not be validated against your inputs. No amount was displayed.');
      if (active.current && sequence.current === id && !abort.signal.aborted) setReport(result);
    } catch (cause) { if (active.current && sequence.current === id && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'The excise component is unavailable.'); }
    finally { if (active.current && sequence.current === id && !abort.signal.aborted) setLoading(false); }
  }
  return <section aria-label="Georgia excise component calculator">
    <p className="excise-notice">This limited tool supports ordinary 8703 passenger cars with conventional petrol or diesel engines, original unconverted left-hand steering, and free circulation for registration in Georgia. It excludes exemptions and special status. The supported subset covers ages 0–30 years and engine displacement from 100 to 7000 cm³. Unknown or unsupported inputs withhold the amount. It does not verify your vehicle declarations.</p>
    <form className="excise-form" onSubmit={calculate} noValidate><div className="excise-inputs">
      <div><label htmlFor="excise-declaration">Declaration registration year</label><select id="excise-declaration" value={input.declaration_year ?? ''} onChange={event => update('declaration_year', event.target.value ? Number(event.target.value) : null)}><option value="">Unknown / not confirmed</option><option value="2026">2026</option><option value="2027">2027 — outside supported period</option></select></div>
      <div><label htmlFor="excise-planned-date">Planned declaration registration date</label><input id="excise-planned-date" type="date" value={input.planned_declaration_date ?? ''} onChange={event => update('planned_declaration_date', event.target.value || null)} aria-describedby="excise-date-help" /><p className="help" id="excise-date-help">Current or future planning only, through 31 December 2026. Historical dates are unsupported; rules changed during 2026.</p></div>
      <div><label htmlFor="excise-production">Production year</label><input id="excise-production" inputMode="numeric" maxLength={4} value={productionYear} onChange={event => { invalidate(); setProductionYear(event.target.value); setInput(previous => ({ ...previous, production_year_confirmed: false })); }} aria-describedby="excise-production-help" /><p className="help" id="excise-production-help">Use the actual production year from vehicle evidence. A VIN decoder’s model year is not automatically the production year.</p></div>
      <div><label htmlFor="excise-engine">Engine displacement (cm³)</label><input id="excise-engine" inputMode="numeric" maxLength={5} value={engineCc} onChange={event => { invalidate(); setEngineCc(event.target.value); }} aria-describedby="excise-engine-help" /><p className="help" id="excise-engine-help">Whole cubic centimetres, for example 2000 cm³. Do not enter 2.0 litres. Supported subset: 100–7000 cm³.</p></div>
      {selectFields.map(field => <div key={field.key}><label htmlFor={`excise-${field.key}`}>{field.label}</label><select id={`excise-${field.key}`} value={String(input[field.key])} onChange={event => update(field.key, event.target.value)}><option value="UNKNOWN">Unknown / not confirmed</option>{field.options.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>)}
      <div><label htmlFor="excise-exemption">Any exemption claimed?</label><select id="excise-exemption" value={input.exemption_claimed === null ? '' : String(input.exemption_claimed)} onChange={event => update('exemption_claimed', event.target.value === '' ? null : event.target.value === 'true')}><option value="">Unknown / not confirmed</option><option value="false">No exemption claimed</option><option value="true">Yes — exemption claimed</option></select></div>
      <div><label htmlFor="excise-special">Any special vehicle or taxpayer status?</label><select id="excise-special" value={input.special_status === null ? '' : String(input.special_status)} onChange={event => update('special_status', event.target.value === '' ? null : event.target.value === 'true')}><option value="">Unknown / not confirmed</option><option value="false">No special status</option><option value="true">Yes — special status</option></select></div>
    </div><fieldset className="excise-scope"><legend>Production-year evidence</legend><label><input type="checkbox" checked={input.production_year_confirmed === true} onChange={event => update('production_year_confirmed', event.target.checked)} />I have checked the actual production year against vehicle evidence, separately from a VIN decoder’s model year.</label><p className="help">This is your evidence declaration; the application does not independently verify it. Leave unchecked if you only know model year.</p></fieldset><p className="help">Re-export and conditional refunds require separate treatment. Choosing re-export does not produce a zero-tax result.</p><button type="submit" className="submit-button" disabled={loading}>{loading ? 'Checking supported excise rule…' : 'Calculate excise component'}</button></form>
    <div aria-live="polite">{error && <p className="excise-errors" role="alert">{error}</p>}
      {report && <section className="excise-result" aria-label="Your excise component"><h2>{report.outcome === 'CALCULATED_COMPONENT' ? 'Excise component estimate' : 'Excise amount withheld'}</h2>
        {report.excise_amount !== null && <p className="excise-amount">{display(report.excise_amount)} GEL</p>}
        {report.outcome === 'CALCULATED_COMPONENT' && <dl className="excise-facts"><div><dt>Production-year-based age</dt><dd>{report.age_years} years</dd></div><div><dt>Applicable component rate</dt><dd>{report.rate_gel_per_cc} GEL / cm³</dd></div><div><dt>Engine displacement declared</dt><dd>{report.request.engine_cc} cm³</dd></div><div><dt>Declaration year</dt><dd>{report.request.declaration_year}</dd></div></dl>}
        {report.issues.length > 0 && <ul className="excise-errors">{report.issues.map((issue, index) => <li key={index}>{issue.message}</li>)}</ul>}
        <div className="excise-unknowns"><h3>Full clearance total remains unknown</h3><p>Import duty, VAT treatment where applicable, registration, declaration and other service fees are not calculated here. This amount is one excise component, not your total tax or landed cost. It does not fill any budget category automatically.</p></div>
        <p className="help">Rule: {report.rule.id}. <a href={report.rule.source_url} target="_blank" rel="noopener noreferrer">Official Tax Code — {report.rule.source_publication}</a>. Clauses: {report.rule.source_clauses.join(', ')}. Rule and selected official Revenue Service calculator cases checked {report.rule.reviewed_on}. Supported declaration year: {report.rule.supported_declaration_year}. Application review deadline: {report.rule.application_review_expires_on}.</p>
        <p className="help">Future law changes may affect the actual declaration. The review deadline is an application limit, not statutory expiry. Generated {report.generated_at}. Calculated from your declarations; not a customs assessment.</p>
        {report.warnings.length > 0 && <ul className="excise-errors">{report.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
      </section>}
    </div>
  </section>;
}
