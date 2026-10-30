import { workflowReference, type WorkflowPageProps } from '../components/workflow-reference';
import Resolver from '../components/resolver';

export default async function Home({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return (
    <div className="site-shell">
      <header className="masthead">
        <a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a>
        <nav aria-label="Vehicle tools"><a href="/review">Review evidence</a><a href="/budget">Plan budget</a><a href="/local-inspection">Local photo analysis</a><a href="/georgia-excise">Georgia excise</a></nav>
        <span className="edition">GEORGIA / RESEARCH EDITION</span>
      </header>
      <main id="main-content">
        <div className="intro">
          <p className="eyebrow">VEHICLE IDENTITY, FIRST</p>
          <h1>Start with the<br /><em>exact vehicle.</em></h1>
          <p className="intro-copy">Before the bid, check the identity, evidence and costs. Explore the demonstration resolver, or start a working review with your own vehicle details and photos.</p>
        </div>
        <Resolver initialUrl={reference} />
        <section className="manual-home-link"><p className="eyebrow">HAVE YOUR OWN DETAILS AND PHOTOS?</p><a href="/review">Review your own evidence</a><p>Compile a manual review with your photos and notes. No paid API is needed; your entries remain unverified.</p></section>
      </main>
      <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
    </div>
  );
}
