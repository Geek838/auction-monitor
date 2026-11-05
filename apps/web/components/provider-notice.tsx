import type { ProviderContext } from './resolution-types';

export default function ProviderNotice({ context, loading }: { context: ProviderContext | null; loading: boolean }) {
  let label = loading ? 'CHECKING SOURCE' : 'SOURCE UNKNOWN';
  let explanation = loading
    ? 'Checking the configured source.'
    : 'The configured source could not be verified.';
  if (context?.mode === 'FIXTURE') {
    label = 'MOCK DATA';
    explanation = 'Sample listings only. No live auction data.';
  } else if (context?.mode === 'SIMULATED') {
    label = 'SIMULATED DATA';
    explanation = 'Offline sample listings. No live auction data.';
  } else if (context?.mode === 'EXTERNAL') {
    if (context.authorization === 'DENIED' || !context.enabled) {
      label = 'ACCESS UNAVAILABLE';
      explanation = 'Check the provider configuration. No sample data will be substituted.';
    } else if (context.authorization === 'UNVERIFIED') {
      label = context.available ? 'EXTERNAL SOURCE' : 'SOURCE UNAVAILABLE';
      explanation = 'Provider data and freshness are not independently verified.';
    } else {
      label = context.available ? 'EXTERNAL SOURCE' : 'SOURCE UNAVAILABLE';
      explanation = 'Check the source and date for each result.';
    }
  }
  return <div className="provider-notice" aria-label="Configured data source" aria-live="polite">
    <div className="mode-notice"><span className="tag">{label}</span><p>{explanation}</p></div>
    {context && <details className="provider-context"><summary>Source details</summary>
      <p><span>Selected provider</span><strong>{context.name}</strong></p>
      <p><span>Access status</span>{context.authorization === 'DENIED' ? 'Not authorized' : context.mode === 'FIXTURE' ? 'Local fixture access' : context.mode === 'SIMULATED' ? 'Synthetic offline access' : context.authorization === 'UNVERIFIED' ? 'User-declared access; not independently verified' : 'Permission reviewed; record availability varies'}</p>
      {context.reasons.length > 0 && <ul>{context.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>}
    </details>}
  </div>;
}
