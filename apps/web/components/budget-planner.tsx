'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import { costCategories, readBudgetReport, type BudgetCost, type BudgetReport, type BudgetRequest, type CostCategory, type EvidenceKind, type FeeTier, type MoneyRange } from './budget-types';

type CostDraft = Omit<BudgetCost, 'category' | 'source' | 'as_of' | 'expires_on'> & { source: string; as_of: string; expires_on: string };
type CategoryDraft = { mode: 'UNKNOWN' | 'COSTS' | 'NOT_APPLICABLE'; reason: string; rows: CostDraft[] };
const emptyCost = (): CostDraft => ({ label: '', low: '', base: '', high: '', kind: 'QUOTE', source: '', as_of: '', expires_on: '' });
const emptyCategories = () => Object.fromEntries(costCategories.map(category => [category.id, { mode: 'UNKNOWN', reason: '', rows: [emptyCost()] }])) as Record<CostCategory, CategoryDraft>;
const emptyTier = (from = '0'): FeeTier => ({ from_bid: from, to_bid: null, flat: '', percent: '' });
const amount = (value: string) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value));
function Range({ values, label }: { values: MoneyRange; label: string }) {
  return <div className="budget-range" aria-label={label}>{(['low', 'base', 'high'] as const).map(key => <div key={key}><dt>{key === 'base' ? 'Base' : key === 'low' ? 'Low' : 'High'}</dt><dd>{amount(values[key])}</dd></div>)}</div>;
}

export default function BudgetPlanner() {
  const [hammer, setHammer] = useState('');
  const [categories, setCategories] = useState(emptyCategories);
  const [hasFees, setHasFees] = useState(false);
  const [tiers, setTiers] = useState<FeeTier[]>([emptyTier()]);
  const [feeKind, setFeeKind] = useState<EvidenceKind>('QUOTE');
  const [feeSource, setFeeSource] = useState('');
  const [feeDate, setFeeDate] = useState('');
  const [feeExpiry, setFeeExpiry] = useState('');
  const [wantCeiling, setWantCeiling] = useState(false);
  const [market, setMarket] = useState('');
  const [savings, setSavings] = useState('');
  const [reserve, setReserve] = useState('');
  const [report, setReport] = useState<BudgetReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const sequence = useRef(0);
  const active = useRef(true);
  const controller = useRef<AbortController | null>(null);
  const reportHeading = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => { active.current = true; return () => { active.current = false; sequence.current++; controller.current?.abort(); }; }, []);
  function invalidate() { sequence.current++; controller.current?.abort(); setLoading(false); setReport(null); setError(null); }
  function change(setter: (value: string) => void, value: string) { invalidate(); setter(value); }
  function categoryChange(category: CostCategory, patch: Partial<CategoryDraft>) { invalidate(); setCategories(current => ({ ...current, [category]: { ...current[category], ...patch } })); }
  function rowChange(category: CostCategory, index: number, patch: Partial<CostDraft>) {
    invalidate(); setCategories(current => ({ ...current, [category]: { ...current[category], rows: current[category].rows.map((row, position) => position === index ? { ...row, ...patch } : row) } }));
  }
  function tierChange(index: number, patch: Partial<FeeTier>) {
    invalidate(); setTiers(current => current.map((tier, position) => position === index ? { ...tier, ...patch } : position === index + 1 && patch.to_bid !== undefined ? { ...tier, from_bid: patch.to_bid ?? '' } : tier));
  }
  function reset() {
    invalidate(); setHammer(''); setCategories(emptyCategories()); setHasFees(false); setTiers([emptyTier()]);
    setFeeKind('QUOTE'); setFeeSource(''); setFeeDate(''); setFeeExpiry(''); setWantCeiling(false); setMarket(''); setSavings(''); setReserve('');
  }
  function moneyInput(id: string, label: string, value: string, onChange: (value: string) => void, required = true) {
    return <div><label htmlFor={id}>{label}</label><input id={id} inputMode="decimal" pattern="[0-9]+([.][0-9]{1,2})?" value={value} onChange={event => onChange(event.target.value)} maxLength={13} required={required} /></div>;
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); invalidate();
    const body: BudgetRequest = {
      currency: 'USD', hammer_bid: hammer.trim(),
      costs: costCategories.flatMap(category => categories[category.id].mode === 'COSTS' ? categories[category.id].rows.map(row => ({ ...row, category: category.id, label: row.label.trim() || category.name, low: row.low.trim(), base: row.base.trim(), high: row.high.trim(), source: row.source.trim() || null, as_of: row.as_of || null, expires_on: row.expires_on || null })) : []),
      not_applicable: costCategories.flatMap(category => categories[category.id].mode === 'NOT_APPLICABLE' ? [{ category: category.id, reason: categories[category.id].reason.trim() }] : []),
      auction_fees: hasFees ? { tiers: tiers.map(tier => ({ ...tier, from_bid: tier.from_bid.trim(), to_bid: tier.to_bid?.trim() || null, flat: tier.flat.trim(), percent: tier.percent.trim() })), kind: feeKind, source: feeSource.trim() || null, as_of: feeDate || null, expires_on: feeExpiry || null } : null,
      market_value: wantCeiling && market.trim() ? market.trim() : null,
      required_savings: wantCeiling && savings.trim() ? savings.trim() : null,
      risk_reserve: wantCeiling && reserve.trim() ? reserve.trim() : null,
    };
    const request = ++sequence.current; const abort = new AbortController(); controller.current = abort; setLoading(true);
    try {
      const response = await fetch('/api/v1/budgets/evaluate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store', body: JSON.stringify(body), signal: abort.signal });
      if (!response.ok) {
        let message = 'Check the amounts, ordered low/base/high ranges and contiguous fee bands. No calculation has been attached.';
        try { const errorBody = await response.json(); if (typeof errorBody.detail === 'string') message = errorBody.detail; else if (Array.isArray(errorBody.detail)) { const first = errorBody.detail[0]; if (typeof first?.msg === 'string') message = first.msg.replace(/^Value error, /, ''); } } catch { /* Preserve bounded fallback for non-JSON errors. */ }
        throw new Error(message);
      }
      const result = readBudgetReport(await response.json(), body);
      if (!result) throw new Error('The budget response did not match your inputs. No result has been attached.');
      if (active.current && sequence.current === request && !abort.signal.aborted) {
        setReport(result); requestAnimationFrame(() => { if (active.current && sequence.current === request) reportHeading.current?.focus(); });
      }
    } catch (cause) { if (active.current && sequence.current === request && !abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'The budget could not be calculated.'); }
    finally { if (active.current && sequence.current === request && !abort.signal.aborted) setLoading(false); }
  }
  function download() {
    if (!report) return;
    const objectUrl = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a'); anchor.href = objectUrl; anchor.download = 'auction-intelligence-budget.json'; anchor.click(); setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  }
  const covered = costCategories.filter(category => categories[category.id].mode !== 'UNKNOWN').length;

  return <div className="budget-workspace">
    <aside className="budget-notice"><strong>User-supplied planning scenario</strong><p>Enter your own dated quotes or explicit assumptions in USD. Nothing is fetched or priced automatically. A complete calculation still depends on your evidence and is not a market-validated purchase recommendation.</p></aside>
    <form className="budget-form" onSubmit={submit} aria-busy={loading}>
      <section className="budget-section"><div className="budget-section-title"><span className="mono">01</span><h2>Your bid assumption</h2></div>{moneyInput('budget-hammer', 'Hammer bid (USD)', hammer, value => change(setHammer, value))}<p className="help">The assumed winning bid, before fees and other costs. Enter zero explicitly where appropriate; blank does not mean zero.</p></section>
      <section className="budget-section"><div className="budget-section-title"><span className="mono">02</span><h2>Account for every cost</h2><span className="budget-coverage">{covered} / {costCategories.length} categories addressed</span></div><p className="budget-section-copy">Leave an unknown category visible, enter one or more cost lines, or give a reason it does not apply. Missing evidence will keep the scenario incomplete.</p>
        {costCategories.map(category => {
          const draft = categories[category.id];
          return <section className="budget-category" key={category.id} id={`cost-category-${category.id}`} aria-label={`${category.name} costs`}>
            <div className="budget-category-heading"><div><h3>{category.name}</h3><p className="help">{category.help}</p></div><div><label htmlFor={`coverage-${category.id}`}>{category.name} coverage</label><select id={`coverage-${category.id}`} value={draft.mode} onChange={event => categoryChange(category.id, { mode: event.target.value as CategoryDraft['mode'] })}><option value="UNKNOWN">Unknown / missing</option><option value="COSTS">Enter costs</option><option value="NOT_APPLICABLE">Not applicable</option></select></div></div>
            {draft.mode === 'NOT_APPLICABLE' && <div className="budget-na"><label htmlFor={`reason-${category.id}`}>Why {category.name.toLowerCase()} does not apply</label><input id={`reason-${category.id}`} value={draft.reason} required maxLength={200} onChange={event => categoryChange(category.id, { reason: event.target.value })} /></div>}
            {draft.mode === 'COSTS' && <div className="budget-cost-lines">{draft.rows.map((row, index) => {
              const prefix = `${category.id}-${index}`; const title = `${category.name} line ${index + 1}`;
              return <fieldset key={index} className="budget-cost-line"><legend>{title}</legend><label htmlFor={`label-${prefix}`}>{title} label (optional)</label><input id={`label-${prefix}`} value={row.label} maxLength={120} onChange={event => rowChange(category.id, index, { label: event.target.value })} placeholder={category.name} />
                <div className="budget-three-fields">{moneyInput(`low-${prefix}`, `${title} low (USD)`, row.low, value => rowChange(category.id, index, { low: value }))}{moneyInput(`base-${prefix}`, `${title} base (USD)`, row.base, value => rowChange(category.id, index, { base: value }))}{moneyInput(`high-${prefix}`, `${title} high (USD)`, row.high, value => rowChange(category.id, index, { high: value }))}</div>
                <details className="budget-evidence"><summary>Source and date for {title.toLowerCase()}</summary><div className="budget-two-fields"><div><label htmlFor={`kind-${prefix}`}>{title} evidence type</label><select id={`kind-${prefix}`} value={row.kind} onChange={event => rowChange(category.id, index, { kind: event.target.value as EvidenceKind })}><option value="QUOTE">Quote supplied by you</option><option value="ASSUMPTION">Your planning assumption</option></select></div><div><label htmlFor={`source-${prefix}`}>{title} source or basis</label><input id={`source-${prefix}`} value={row.source} maxLength={200} onChange={event => rowChange(category.id, index, { source: event.target.value })} /></div><div><label htmlFor={`date-${prefix}`}>{title} as-of date</label><input id={`date-${prefix}`} type="date" value={row.as_of} onChange={event => rowChange(category.id, index, { as_of: event.target.value })} /></div><div><label htmlFor={`expiry-${prefix}`}>{title} expires on</label><input id={`expiry-${prefix}`} type="date" value={row.expires_on} onChange={event => rowChange(category.id, index, { expires_on: event.target.value })} /></div></div><p className="help">A source/basis and as-of date are needed for a complete scenario. Quotes also need a current expiry date. They remain user-supplied and are not checked with the supplier.</p></details>
                {draft.rows.length > 1 && <button className="budget-text-button" type="button" onClick={() => categoryChange(category.id, { rows: draft.rows.filter((_, position) => position !== index) })}>Remove {title.toLowerCase()}</button>}
              </fieldset>;
            })}<button type="button" className="inspection-button" disabled={draft.rows.length >= 5} onClick={() => categoryChange(category.id, { rows: [...draft.rows, emptyCost()] })}>Add {category.name.toLowerCase()} cost line</button></div>}
          </section>;
        })}
      </section>
      <section className="budget-section"><div className="budget-section-title"><span className="mono">03</span><h2>Bid-dependent auction fees</h2></div><label className="budget-checkbox"><input type="checkbox" checked={hasFees} onChange={event => { invalidate(); setHasFees(event.target.checked); }} />I have a fee schedule to enter</label><p className="help">No default fee schedule is assumed; a quoted schedule needs a source, as-of date and current expiry. This amount is added to any separate auction/broker charges above; avoid double counting. An unknown schedule prevents an all-in total and bid ceiling.</p>
        {hasFees && <div className="budget-fee-editor"><div className="budget-two-fields"><div><label htmlFor="fee-kind">Fee schedule evidence type</label><select id="fee-kind" value={feeKind} onChange={event => { invalidate(); setFeeKind(event.target.value as EvidenceKind); }}><option value="QUOTE">Quote supplied by you</option><option value="ASSUMPTION">Your planning assumption</option></select></div><div><label htmlFor="fee-source">Fee schedule source or basis</label><input id="fee-source" value={feeSource} maxLength={200} onChange={event => change(setFeeSource, event.target.value)} /></div><div><label htmlFor="fee-date">Fee schedule as-of date</label><input id="fee-date" type="date" value={feeDate} onChange={event => change(setFeeDate, event.target.value)} /></div><div><label htmlFor="fee-expiry">Fee schedule expires on</label><input id="fee-expiry" type="date" value={feeExpiry} onChange={event => change(setFeeExpiry, event.target.value)} /></div></div>
          <p className="help">Each band includes its starting bid and excludes its upper bound. The final band has no upper bound. Fee = flat amount + percentage of the full bid; bands are not marginal tax brackets.</p>
          {tiers.map((tier, index) => <fieldset key={index} className="budget-fee-tier"><legend>Fee band {index + 1}</legend><div className="budget-two-fields"><div><label htmlFor={`fee-from-${index}`}>Fee band {index + 1} from bid (USD)</label><input id={`fee-from-${index}`} value={tier.from_bid} readOnly /><p className="help">Starts at zero or the preceding upper bound.</p></div>{moneyInput(`fee-to-${index}`, `Fee band ${index + 1} up to bid (USD, optional)`, tier.to_bid ?? '', value => tierChange(index, { to_bid: value || null }), index < tiers.length - 1)}{moneyInput(`fee-flat-${index}`, `Fee band ${index + 1} flat amount (USD)`, tier.flat, value => tierChange(index, { flat: value }))}<div><label htmlFor={`fee-percent-${index}`}>Fee band {index + 1} percentage</label><input id={`fee-percent-${index}`} inputMode="decimal" pattern="[0-9]+([.][0-9]{1,4})?" value={tier.percent} required maxLength={10} onChange={event => tierChange(index, { percent: event.target.value })} /></div></div></fieldset>)}
          <div className="budget-inline-actions"><button type="button" className="inspection-button" disabled={tiers.length >= 10 || !tiers[tiers.length - 1].to_bid} onClick={() => { invalidate(); setTiers(current => [...current, emptyTier(current[current.length - 1].to_bid!)]); }}>Add fee band</button>{tiers.length > 1 && <button type="button" className="budget-text-button" onClick={() => { invalidate(); setTiers(current => current.slice(0, -1).map((tier, index) => index === current.length - 2 ? { ...tier, to_bid: null } : tier)); }}>Remove final fee band</button>}</div><p className="help">To add a band, first enter the current band's upper bound. Leave the final upper bound blank when finished.</p>
        </div>}
      </section>
      <section className="budget-section"><div className="budget-section-title"><span className="mono">04</span><h2>An optional planning bid ceiling</h2></div><label className="budget-checkbox"><input type="checkbox" checked={wantCeiling} onChange={event => { invalidate(); setWantCeiling(event.target.checked); }} />Calculate a planning bid ceiling</label><p className="help">Uses your conservative value, high cost scenario and fee schedule. No market value is fetched. The risk reserve below is additional to the contingency cost above; avoid counting the same allowance twice.</p>{wantCeiling && <div className="budget-three-fields">{moneyInput('budget-market', 'Conservative vehicle value (USD)', market, value => change(setMarket, value), false)}{moneyInput('budget-savings', 'Required savings or margin (USD)', savings, value => change(setSavings, value), false)}{moneyInput('budget-reserve', 'Additional risk reserve (USD)', reserve, value => change(setReserve, value), false)}</div>}</section>
      <div className="budget-submit"><button type="submit" className="submit-button" disabled={loading}>{loading ? 'Calculating…' : 'Calculate budget'}</button><button type="button" className="budget-text-button" onClick={reset}>Clear budget</button><p className="help">This page does not save your scenario. Editing clears the old result; download a report if you want to keep it.</p></div>
    </form>
    {error && <div className="budget-error" role="alert"><h2>Budget needs attention</h2><p>{error}</p></div>}
    {report && <section className="budget-report" aria-label="Your budget scenario"><div className="budget-report-heading"><div><p className="eyebrow">USER-SUPPLIED PLANNING SCENARIO</p><h2 tabIndex={-1} ref={reportHeading}>Your budget scenario</h2></div><span className="tag">{report.status === 'COMPLETE' ? 'INPUTS COMPLETE' : 'INCOMPLETE'}</span></div><p className="budget-result-notice">Calculated from your entries. Prices, scope, vehicle condition and market value have not been independently verified.</p>
      <section className="budget-result-section"><h3>{report.total_at_bid ? 'All-in scenario at your bid' : 'Known subtotal at your bid'}</h3><Range label="Budget scenario totals" values={report.total_at_bid ?? report.known_total_at_bid} />{!report.total_at_bid && <p className="help">This is a partial subtotal, not a complete landed-and-repaired cost. Missing costs have not been treated as zero.</p>}<dl className="budget-result-facts"><div><dt>Hammer bid</dt><dd>{amount(report.hammer_bid)}</dd></div><div><dt>Bid-dependent auction fee</dt><dd>{report.auction_fee_at_bid === null ? 'Unknown / missing' : amount(report.auction_fee_at_bid)}</dd></div></dl></section>
      <section className="budget-result-section budget-ceiling"><h3>Planning bid ceiling</h3>{report.max_bid.status === 'INDICATIVE' && report.max_bid.amount !== null ? <><p className="budget-ceiling-number">{amount(report.max_bid.amount)}</p><span className="tag">INDICATIVE · USER INPUTS</span></> : <p className="budget-ceiling-withheld">{report.max_bid.status === 'NO_FEASIBLE_BID' ? 'No feasible bid in this scenario' : 'Withheld — inputs are incomplete'}</p>}<p>{report.max_bid.reason}</p><p className="help">This is a scenario limit, not a verified recommendation to buy or bid.</p></section>
      {report.issues.length > 0 && <section className="budget-result-section"><h3>Resolve these gaps</h3><ul>{report.issues.map((issue, index) => <li key={index}>{issue.message}</li>)}</ul></section>}
      {report.costs.length > 0 && <section className="budget-result-section"><h3>Cost evidence used</h3><div className="budget-report-lines">{report.costs.map((cost, index) => <article key={index}><div className="budget-line-heading"><h4>{cost.label}</h4><span className="tag archived">{cost.kind}</span></div><p>{costCategories.find(category => category.id === cost.category)?.name}</p><Range label={`${cost.label} range`} values={cost} /><p className="help">{cost.source ?? 'Source/basis missing'} · As of {cost.as_of ?? 'not supplied'}{cost.expires_on ? ` · Expires ${cost.expires_on}` : ''}</p></article>)}</div></section>}
      {report.not_applicable.length > 0 && <section className="budget-result-section"><h3>Categories you excluded</h3><ul>{report.not_applicable.map(item => <li key={item.category}><strong>{costCategories.find(category => category.id === item.category)?.name}:</strong> {item.reason}</li>)}</ul></section>}
      <aside className="warnings" aria-label="Budget limitations"><h3>Before you rely on these figures</h3><ul>{report.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></aside>
      <div className="budget-report-actions"><button type="button" className="inspection-button" onClick={download}>Download budget JSON</button><button type="button" className="inspection-button" onClick={() => window.print()}>Print budget</button><p className="help">Export contains your inputs, sources and computed scenario. Treat supplier details and vehicle budgets as private.</p></div>
    </section>}
  </div>;
}
