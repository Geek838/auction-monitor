import { workflowReference, type WorkflowPageProps } from '../../components/workflow-reference';
import BudgetPlanner from '../../components/budget-planner';

export default async function BudgetPage({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return <div className="site-shell budget-page">
    <header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><nav aria-label="Vehicle tools"><a href="/review">Evidence review</a><a href="/local-inspection">Local photo analysis</a><a href="/">Listing resolver</a></nav></header>
    <main id="main-content"><div className="intro"><p className="eyebrow">THE NUMBERS, WITH THEIR SOURCES</p><h1>Set a budget.<br /><em>Keep the unknowns.</em></h1><p className="intro-copy">Build a purchase and repair scenario from your quotes and assumptions. Missing costs stay visible, and a bid ceiling appears only when the required inputs are complete.</p></div><BudgetPlanner reference={reference} /></main>
    <footer><span>Auction Intelligence</span><span>User-supplied planning scenarios · No paid API</span></footer>
  </div>;
}
