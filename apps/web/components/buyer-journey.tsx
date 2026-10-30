import { workflowHref, workflowReference } from './workflow-reference';

const steps = [
  { path: '/', label: 'Listing identity', detail: 'Demo lookup until authorized live data is available.' },
  { path: '/review', label: 'Your evidence', detail: 'Record your details, photos and inspection questions.' },
  { path: '/local-inspection', label: 'Local photo analysis', detail: 'Optional experimental model; local setup required.' },
  { path: '/budget', label: 'Budget & bid planning', detail: 'Calculate from your dated quotes and assumptions.' },
];

export default function BuyerJourney({ current, reference = '' }: { current: string; reference?: string }) {
  const safe = workflowReference(reference);
  return <section className="buyer-journey" aria-label="Buyer workflow">
    <div className="journey-heading"><p className="eyebrow">YOUR NEXT CHECK</p><p>Each step keeps its own evidence and limitations. <a href="/exchange">Exchange rates</a> · <a href="/georgia-excise">Georgia excise</a></p></div>
    <nav aria-label="Buyer workflow steps"><ol>{steps.map((step, index) => <li key={step.path}>
      <span className="mono" aria-hidden="true">0{index + 1}</span><div><a href={workflowHref(step.path, safe)} aria-current={current === step.path ? 'step' : undefined}>{step.label}</a><p>{step.detail}</p></div>
    </li>)}</ol></nav>
    <p className="journey-privacy">{safe ? 'Only the listing URL follows these links. It is a reference, not a verified auction match. ' : 'Enter a supported listing URL to carry that reference between steps. '}Photos, notes and costs do not transfer; download your report before leaving. The reference appears in browser history.</p>
  </section>;
}
