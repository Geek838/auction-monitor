'use client';
import { FormEvent, useEffect, useRef, useState } from 'react';

type RequestBody = { bid_amount: string; auction: 'copart' | 'iaai'; bid_type: string; bid_pay: string; bid_vehicle: string; volume: string | null; consent_to_send: true };
type Report = { outcome: 'ESTIMATED' | 'UNAVAILABLE'; source_kind: 'INDICATIVE_EXTERNAL_UNVERIFIED'; request: RequestBody; bid_amount: string | null; auction_fee: string | null; total_amount: string | null; schedule_as_of: null; retrieved_at: string; source_url: string; warnings: string[]; errors: unknown[] };
const source = 'https://api.auctionfeescalculator.com';
const moneyPattern = /^(?:0|[1-9][0-9]*)\.[0-9]{2}$/;
function obj(value: unknown): value is Record<string, unknown> { return value !== null && typeof value === 'object' && !Array.isArray(value); }
function parseReport(value: unknown, body: RequestBody): Report | null {
  if (!obj(value) || value.schema_version !== 'auction-fee-estimate-v1' || value.currency !== 'USD' || !['ESTIMATED','UNAVAILABLE'].includes(String(value.outcome)) || value.source_kind !== 'INDICATIVE_EXTERNAL_UNVERIFIED' || value.source_url !== source || value.schedule_as_of !== null || !obj(value.request) || Object.entries(body).some(([k,v]) => (value.request as Record<string,unknown>)[k] !== v) || typeof value.retrieved_at !== 'string' || !Number.isFinite(Date.parse(value.retrieved_at)) || !Array.isArray(value.warnings) || !value.warnings.every(v => typeof v === 'string') || !Array.isArray(value.errors)) return null;
  if (value.outcome === 'ESTIMATED') {
    if (![value.bid_amount, value.auction_fee, value.total_amount].every(v => typeof v === 'string' && moneyPattern.test(v))) return null;
    if (value.bid_amount !== body.bid_amount) return null;
  } else if (value.auction_fee !== null || value.total_amount !== null) return null;
  return value as Report;
}
function normalize(raw: string): string | null {
  if (!/^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?$/.test(raw) || raw.length > 13) return null;
  const [whole, fraction = ''] = raw.split('.');
  if (whole.length > 10 || whole.length === 10 && whole > '1000000000' || whole === '1000000000' && /[1-9]/.test(fraction)) return null;
  const result = `${whole}.${fraction.padEnd(2, '0')}`;
  return result === '0.00' ? null : result;
}
function display(amount: string) { const [whole, cents] = amount.split('.'); return `${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${cents}`; }

export default function AuctionFeeEstimate() {
  const [amount, setAmount] = useState(''); const [auction, setAuction] = useState(''); const [bidType, setBidType] = useState('');
  const [payment, setPayment] = useState(''); const [vehicle, setVehicle] = useState(''); const [volume, setVolume] = useState(''); const [consent, setConsent] = useState(false);
  const [report, setReport] = useState<Report | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  const seq = useRef(0); const active = useRef(true); const pending = useRef<AbortController | null>(null);
  useEffect(() => { active.current = true; return () => { active.current = false; seq.current++; pending.current?.abort(); }; }, []);
  function invalidate() { seq.current++; pending.current?.abort(); setReport(null); setError(''); setLoading(false); }
  function change(set: (value: string) => void, value: string) { invalidate(); set(value); }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); invalidate(); const normalized = normalize(amount);
    if (!normalized) { setError('Enter a bid above zero, up to 1,000,000,000 USD, using a decimal point and at most two decimal places.'); return; }
    if (!auction || !bidType || !payment || !vehicle || auction === 'copart' && !volume || !consent) { setError('Select each relevant option and confirm permission to send this bid to the fee provider.'); return; }
    const body: RequestBody = { bid_amount: normalized, auction: auction as 'copart'|'iaai', bid_type: bidType, bid_pay: payment, bid_vehicle: vehicle, volume: auction === 'copart' ? volume : null, consent_to_send: true };
    const id = ++seq.current; const abort = new AbortController(); pending.current = abort; setLoading(true);
    try {
      const response = await fetch('/api/v1/auction-fees/estimate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), cache: 'no-store', signal: abort.signal });
      if (!response.ok) throw new Error('The fee estimate could not be requested. Check your selections and try again.');
      const result = parseReport(await response.json(), body);
      if (!result) throw new Error('The returned estimate could not be matched to your request. No amount was shown.');
      if (active.current && seq.current === id && !abort.signal.aborted) setReport(result);
    } catch (cause) { if (active.current && seq.current === id && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'The fee estimate is unavailable.'); }
    finally { if (active.current && seq.current === id && !abort.signal.aborted) setLoading(false); }
  }
  return <section aria-label="Auction fee estimate">
    <p className="fees-notice">This optional estimate comes from <a href="https://www.auctionfeescalculator.com/" target="_blank" rel="noopener noreferrer">Auction Fees Calculator</a>, an independent third party. It is not an official auction or broker quote. Its response does not provide a fee schedule date or expiry. Taxes, broker charges and other costs may be missing.</p>
    <form className="fees-form" onSubmit={submit} noValidate><div className="fees-fields">
      <div><label htmlFor="fee-bid">Your bid (USD)</label><input id="fee-bid" inputMode="decimal" autoComplete="off" maxLength={13} value={amount} onChange={e => change(setAmount,e.target.value)} /></div>
      <div><label htmlFor="fee-auction">Auction</label><select id="fee-auction" value={auction} onChange={e => { invalidate(); setAuction(e.target.value); setPayment(''); setVehicle(''); setVolume(''); }}><option value="">Choose an auction</option><option value="copart">Copart</option><option value="iaai">IAAI</option></select></div>
      <div><label htmlFor="fee-bid-type">How will you bid?</label><select id="fee-bid-type" value={bidType} onChange={e => change(setBidType,e.target.value)}><option value="">Choose bid type</option><option value="online">Online</option><option value="kiosk">Kiosk</option><option value="non-kiosk">Non-kiosk</option></select></div>
      <div><label htmlFor="fee-payment">Payment or buyer fee category</label><select id="fee-payment" value={payment} onChange={e => change(setPayment,e.target.value)}><option value="">Choose a category</option>{auction === 'copart' ? <><option value="secured">Secured payment</option><option value="unsecured">Unsecured payment</option></> : auction === 'iaai' ? <><option value="high">High</option><option value="standard">Standard</option></> : null}</select></div>
      <div><label htmlFor="fee-vehicle">Vehicle / buyer category</label><select id="fee-vehicle" value={vehicle} onChange={e => change(setVehicle,e.target.value)}><option value="">Choose a category</option>{auction === 'copart' ? <><option value="standard">Standard vehicle</option><option value="heavy">Heavy vehicle</option><option value="crashedToys">Crashed toys</option></> : auction === 'iaai' ? <><option value="licensed">Licensed buyer</option><option value="non-licensed">Non-licensed buyer</option><option value="recRides">Recreational rides</option><option value="heavy">Heavy vehicle</option></> : null}</select></div>
      {auction === 'copart' && <div><label htmlFor="fee-volume">Copart buyer volume</label><select id="fee-volume" value={volume} onChange={e => change(setVolume,e.target.value)}><option value="">Choose volume</option><option value="low">Low volume</option><option value="high">High volume</option></select></div>}
    </div><p className="help">The categories come from the provider. If you are unsure which applies, check with your auction or broker; the estimate may change.</p><label className="fees-consent"><input type="checkbox" checked={consent} onChange={e => { invalidate(); setConsent(e.target.checked); }} />I agree to send this bid amount and selected auction, bidding, payment and vehicle categories to Auction Fees Calculator. No VIN, listing URL, photos or towing location are sent.</label><button className="submit-button" type="submit" disabled={loading}>{loading ? 'Requesting estimate…' : 'Request fee estimate'}</button></form>
    <div aria-live="polite">{error && <p className="fees-error" role="alert">{error}</p>}{report && <section className="fees-result" aria-label="Your fee estimate"><h2>{report.outcome === 'ESTIMATED' ? 'Indicative auction fee' : 'Fee estimate unavailable'}</h2>{report.outcome === 'ESTIMATED' && report.auction_fee !== null && report.total_amount !== null ? <><p className="fees-result-value">${display(report.auction_fee)}</p><p>Estimated fee for your ${display(report.bid_amount!)} bid.</p><dl className="fees-facts"><div><dt>Bid plus this estimated fee</dt><dd>${display(report.total_amount)}</dd></div><div><dt>Schedule date</dt><dd>Not supplied by provider</dd></div><div><dt>Retrieved</dt><dd>{report.retrieved_at}</dd></div></dl></> : <p>No estimate was produced. No fee has been added to your budget.</p>}<p className="help">The provider’s estimate is undated and unverified. It may omit taxes, broker charges or other fees. It does not change your budget, provide a fee schedule, or establish a bid ceiling.</p>{report.warnings.length > 0 && <ul>{report.warnings.map((warning,i)=><li key={i}>{warning}</li>)}</ul>}</section>}</div>
  </section>;
}
