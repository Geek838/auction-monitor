import { workflowReference, type WorkflowPageProps } from '../components/workflow-reference';
import Resolver from '../components/resolver';
import './home.css';

export default async function Home({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return <div className="site-shell home-page">
    <header className="masthead">
      <a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a>
      <nav aria-label="Vehicle tools">
        <a href="/review">Review</a><a href="/budget">Budget</a><a href="/auction-fees">Auction fees</a><a href="/georgia-excise">Georgia excise</a>
      </nav>
    </header>
    <main id="main-content">
      <div className="home-heading"><h1>Check a vehicle</h1></div>
      <Resolver initialUrl={reference} />
      <section className="home-tools" aria-labelledby="tools-title">
        <h2 id="tools-title">Tools</h2>
        <div className="home-tool-grid">
          <a href="/review" className="home-tool"><span>Review your own evidence</span><span aria-hidden="true">→</span></a>
          <a href="/budget" className="home-tool"><span>Plan a budget</span><span aria-hidden="true">→</span></a>
          <a href="/auction-fees" className="home-tool"><span>Estimate auction fees</span><span aria-hidden="true">→</span></a>
          <a href="/georgia-excise" className="home-tool"><span>Calculate Georgia excise</span><span aria-hidden="true">→</span></a>
          <a href="/exchange" className="home-tool"><span>Convert USD / GEL</span><span aria-hidden="true">→</span></a>
        </div>
      </section>
    </main>
    <footer><span>Auction Intelligence</span></footer>
  </div>;
}
