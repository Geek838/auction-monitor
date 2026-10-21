import type { ProviderContext } from './resolution-types';

export default function ProviderNotice({ context, loading }: { context: ProviderContext | null; loading: boolean }) {
  let label = loading ? 'CHECKING SOURCE' : 'SOURCE UNKNOWN';
  let explanation = loading
    ? 'Checking the configured data source before describing this environment.'
    : 'The configured source could not be verified. No fixture mode or live access is assumed.';
  if (context?.mode === 'FIXTURE') {
    label = 'MOCK DATA';
    explanation = 'Mock data environment. Results use test fixtures. No live auction data or inspection advice is provided.';
  } else if (context?.mode === 'SIMULATED') {
    label = 'SIMULATED DATA';
    explanation = 'Offline provider simulation. Every record is synthetic; no commercial license or live auction access is implied.';
  } else if (context?.mode === 'EXTERNAL') {
    if (context.authorization === 'DENIED' || !context.enabled) {
      label = 'ACCESS UNAVAILABLE';
      explanation = 'The selected external source is disabled or lacks authorized access. A failed lookup will not be replaced with mock data.';
    } else {
      label = context.available ? 'EXTERNAL SOURCE' : 'SOURCE UNAVAILABLE';
      explanation = 'An external provider is selected. Check each result’s provenance and source date; permitted access does not imply live auction data.';
    }
  }
  return <div className="provider-notice" aria-label="Configured data source" aria-live="polite">
    <div className="mode-notice"><span className="tag">{label}</span><p>{explanation}</p></div>
    {context && <div className="provider-context">
      <p><span>Selected provider</span><strong>{context.name}</strong></p>
      <p><span>Access status</span>{context.authorization === 'DENIED' ? 'Not authorized' : context.mode === 'FIXTURE' ? 'Local fixture access' : context.mode === 'SIMULATED' ? 'Synthetic offline access' : 'Permission reviewed; record availability varies'}</p>
      {context.reasons.length > 0 && <ul>{context.reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>}
    </div>}
  </div>;
}
