'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';

type Currency = 'USD' | 'GEL';
type Input = { amount: string; from_currency: Currency; to_currency: Currency };
type Quote = { currency: 'USD'; quantity: number; rate_gel: string; gel_per_usd: string; effective_date: string; published_at: string; age_days: number; freshness: 'EFFECTIVE_TODAY' | 'PREVIOUS_EFFECTIVE_DATE' | 'STALE' | 'FUTURE_EFFECTIVE_DATE' };
type Report = { schema_version: 'exchange-v1'; source: 'NATIONAL_BANK_OF_GEORGIA'; source_url: string; source_request_date?: string | null; outcome: 'CONVERTED' | 'STALE' | 'UNAVAILABLE' | 'NOT_YET_EFFECTIVE'; request: Input; converted_amount: string | null; quote: Quote | null; retrieved_at: string; rounding: 'ROUND_HALF_UP_2_DECIMAL_PLACES'; max_age_days: 4; errors: { code: string; message: string }[]; warnings: string[] };
const sourceUrl = 'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json';
const decimal = /^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/;
const money = /^(?:0|[1-9][0-9]*)\.[0-9]{2}$/;
function record(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
function stamp(value: unknown): value is string { return typeof value === 'string' && Number.isFinite(Date.parse(value)); }
function readReport(value: unknown, expected: Input): Report | null {
  if (!record(value) || value.schema_version !== 'exchange-v1' || value.source !== 'NATIONAL_BANK_OF_GEORGIA' || value.source_url !== sourceUrl
    || !['CONVERTED', 'STALE', 'UNAVAILABLE', 'NOT_YET_EFFECTIVE'].includes(String(value.outcome))
    || !record(value.request) || value.request.amount !== expected.amount || value.request.from_currency !== expected.from_currency || value.request.to_currency !== expected.to_currency
    || !stamp(value.retrieved_at) || value.source_request_date != null && (typeof value.source_request_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value.source_request_date) || !stamp(value.source_request_date)) || value.rounding !== 'ROUND_HALF_UP_2_DECIMAL_PLACES' || value.max_age_days !== 4
    || !Array.isArray(value.errors) || !value.errors.every(item => record(item) && typeof item.code === 'string' && typeof item.message === 'string')
    || !Array.isArray(value.warnings) || !value.warnings.every(item => typeof item === 'string')) return null;
  if (value.quote !== null) {
    const q = value.quote;
    if (!record(q) || q.currency !== 'USD' || !Number.isInteger(q.quantity) || Number(q.quantity) < 1
      || typeof q.rate_gel !== 'string' || !decimal.test(q.rate_gel) || !/[1-9]/.test(q.rate_gel)
      || typeof q.gel_per_usd !== 'string' || !decimal.test(q.gel_per_usd) || !/[1-9]/.test(q.gel_per_usd)
      || typeof q.effective_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(q.effective_date) || !stamp(q.effective_date)
      || !stamp(q.published_at) || !Number.isInteger(q.age_days)
      || !['EFFECTIVE_TODAY', 'PREVIOUS_EFFECTIVE_DATE', 'STALE', 'FUTURE_EFFECTIVE_DATE'].includes(String(q.freshness))) return null;
  }
  if (value.outcome === 'CONVERTED') {
    if (!record(value.quote) || typeof value.converted_amount !== 'string' || !money.test(value.converted_amount)
      || !['EFFECTIVE_TODAY', 'PREVIOUS_EFFECTIVE_DATE'].includes(String(value.quote.freshness))
      || Number(value.quote.age_days) < 0 || Number(value.quote.age_days) > 4 || value.errors.length !== 0
      || value.quote.freshness === 'EFFECTIVE_TODAY' && value.quote.age_days !== 0
      || value.quote.freshness === 'PREVIOUS_EFFECTIVE_DATE' && Number(value.quote.age_days) < 1) return null;
  } else if (value.converted_amount !== null) return null;
  if (value.outcome === 'STALE' && (!record(value.quote) || value.quote.freshness !== 'STALE' || Number(value.quote.age_days) <= 4)) return null;
  if (value.outcome === 'NOT_YET_EFFECTIVE' && (!record(value.quote) || value.quote.freshness !== 'FUTURE_EFFECTIVE_DATE' || Number(value.quote.age_days) >= 0)) return null;
  return value as Report;
}
function normalizeAmount(value: string): string | null {
  if (!/^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?$/.test(value) || value.length > 13) return null;
  const [whole, fraction = ''] = value.split('.');
  if (whole.length > 10 || whole.length === 10 && whole > '1000000000' || whole === '1000000000' && /[1-9]/.test(fraction)) return null;
  return `${whole}.${fraction.padEnd(2, '0')}`;
}
function displayAmount(value: string): string { const [whole, cents] = value.split('.'); return `${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${cents}`; }

export default function ExchangeConverter() {
  const [amount, setAmount] = useState('');
  const [from, setFrom] = useState<Currency>('USD');
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const active = useRef(true); const sequence = useRef(0); const pending = useRef<AbortController | null>(null);
  useEffect(() => { active.current = true; return () => { active.current = false; sequence.current++; pending.current?.abort(); }; }, []);
  function invalidate() { sequence.current++; pending.current?.abort(); setReport(null); setError(null); setLoading(false); }
  async function convert(event: FormEvent) {
    event.preventDefault(); invalidate();
    const normalized = normalizeAmount(amount);
    if (normalized === null) { setError('Enter an amount from 0 to 1,000,000,000 with at most two decimal places. Use a decimal point without commas.'); return; }
    const request: Input = { amount: normalized, from_currency: from, to_currency: from === 'USD' ? 'GEL' : 'USD' };
    const id = ++sequence.current; const abort = new AbortController(); pending.current = abort; setLoading(true);
    try {
      const response = await fetch('/api/v1/exchange/convert', { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request), signal: abort.signal });
      if (!response.ok) throw new Error(response.status === 422 ? 'Check the amount and currencies before converting.' : 'The exchange-rate service is unavailable. No conversion was produced.');
      const result = readReport(await response.json(), request);
      if (!result) throw new Error('The exchange response could not be validated against your inputs. No conversion was displayed.');
      if (active.current && sequence.current === id && !abort.signal.aborted) setReport(result);
    } catch (cause) { if (active.current && sequence.current === id && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'The exchange rate is unavailable.'); }
    finally { if (active.current && sequence.current === id && !abort.signal.aborted) setLoading(false); }
  }
  return <section aria-label="Reference currency converter">
    <p className="exchange-notice">NBG’s official rate is indicative; its use is not obligatory except where legal requirements apply. Banks, cards and exchange desks may use different rates and fees. This is a planning aid, not a customs assessment.</p>
    <form className="exchange-form" onSubmit={convert} noValidate><div className="exchange-fields">
      <div><label htmlFor="exchange-amount">Amount to convert</label><input id="exchange-amount" inputMode="decimal" autoComplete="off" maxLength={13} value={amount} onChange={event => { invalidate(); setAmount(event.target.value); }} aria-describedby="exchange-help" /></div>
      <div><label htmlFor="exchange-direction">Conversion direction</label><select id="exchange-direction" value={from} onChange={event => { invalidate(); setFrom(event.target.value as Currency); }}><option value="USD">USD → GEL</option><option value="GEL">GEL → USD</option></select></div>
    </div><button type="submit" className="submit-button" disabled={loading}>{loading ? 'Retrieving official rate…' : 'Get rate and convert'}</button><p className="help" id="exchange-help">The rate is requested only when you select Convert. Only the currency selection goes to NBG; the amount is calculated by our backend. Budget totals are never changed automatically.</p></form>
    <div aria-live="polite">{error && <p role="alert" className="exchange-error">{error}</p>}
      {report && <section className="exchange-result" aria-label="Reference conversion result"><h2>{report.outcome === 'CONVERTED' ? 'Your reference conversion' : report.outcome === 'STALE' ? 'Rate is too old for this planner' : report.outcome === 'NOT_YET_EFFECTIVE' ? 'Rate is not effective yet' : 'Official rate unavailable'}</h2>
        {report.converted_amount !== null && <p className="exchange-amount">{displayAmount(report.converted_amount)} {report.request.to_currency}</p>}
        {report.converted_amount === null && <p>No conversion was produced. Your budget remains unchanged.</p>}
        {report.quote && <><dl className="exchange-facts"><div><dt>Official unit rate</dt><dd>1 USD = {report.quote.gel_per_usd} GEL</dd></div><div><dt>Effective date</dt><dd>{report.quote.effective_date}</dd></div><div><dt>Published by NBG (UTC)</dt><dd>{report.quote.published_at}</dd></div><div><dt>Source quote</dt><dd>{report.quote.quantity} USD = {report.quote.rate_gel} GEL</dd></div><div><dt>Age on retrieval (Georgia calendar)</dt><dd>{report.quote.age_days} calendar days</dd></div><div><dt>Retrieved (UTC)</dt><dd>{report.retrieved_at}</dd></div></dl>
          {report.quote.freshness === 'PREVIOUS_EFFECTIVE_DATE' && <p>The effective date precedes retrieval. This can be normal on weekends or holidays; check the displayed date before relying on the amount.</p>}</>}
        {report.errors.length > 0 && <ul className="exchange-warnings">{report.errors.map((item, index) => <li key={index}>{item.message}</li>)}</ul>}
        <p className="help">Converted amounts are rounded to two decimal places, with halves rounded up. This planner withholds rates older than four calendar days; this is our freshness policy, not a legal expiry rule.</p>
        <p className="help">Source: <a href="https://nbg.gov.ge/en/monetary-policy/currency" target="_blank" rel="noopener noreferrer">National Bank of Georgia official exchange rates</a>.{report.source_request_date && ` Rate requested for ${report.source_request_date} (Georgia calendar).`} Retrieved {report.retrieved_at}.</p>
        {report.warnings.length > 0 && <ul className="exchange-warnings">{report.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
      </section>}
    </div>
  </section>;
}
