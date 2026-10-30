import { workflowReference, type WorkflowPageProps } from '../components/workflow-reference';
import Resolver from '../components/resolver';
import './home.css';

export default async function Home({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return (
    <div className="site-shell home-page">
      <header className="masthead">
        <a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a>
        <nav aria-label="Vehicle tools"><a href="/review">Vehicle review</a><a href="/budget">Budget planner</a><a href="/auction-fees">Auction fees</a><a href="/georgia-excise">Georgia excise</a></nav>
        <a className="home-header-action" href="/review">Start a review <span aria-hidden="true">→</span></a>
      </header>
      <main id="main-content">
        <section className="home-hero" aria-labelledby="home-title">
          <div className="home-hero-copy">
            <p className="home-kicker"><span /> BUILT FOR BUYERS IN GEORGIA</p>
            <h1 id="home-title">A clearer view<br />before you <em>bid.</em></h1>
            <p>Bring the listing details, photos and costs together. Take a little more certainty into your next vehicle purchase.</p>
            <div className="home-actions"><a className="home-primary" href="/review">Start a vehicle review <span aria-hidden="true">→</span></a><a className="home-secondary" href="/budget">Plan your budget <span aria-hidden="true">→</span></a></div>
            <p className="home-hero-note">Free to use locally · No account required</p>
          </div>
          <aside className="home-brief" aria-label="What you can do today">
            <div className="home-brief-top"><span>YOUR BUYER WORKSPACE</span><span>01 / 03</span></div>
            <h2>Make the details<br />work for you.</h2>
            <div className="home-brief-row"><span>01</span><div><strong>Review the evidence</strong><p>Keep photos and notes in one place.</p></div><span aria-hidden="true">→</span></div>
            <div className="home-brief-row"><span>02</span><div><strong>Understand your costs</strong><p>Build a budget from your own quotes.</p></div><span aria-hidden="true">→</span></div>
            <div className="home-brief-row"><span>03</span><div><strong>Check Georgian excise</strong><p>Estimate the supported tax component.</p></div><span aria-hidden="true">→</span></div>
          </aside>
        </section>
        <section className="home-tools" aria-label="Available tools"><div className="home-section-heading"><div><p className="home-kicker">YOUR NEXT MOVE</p><h2>Start where you are.</h2></div><p>Use one tool or work through the full checklist at your own pace.</p></div>
          <div className="home-tool-grid">
            <a href="/review" className="home-tool"><span className="home-tool-icon" aria-hidden="true">01</span><h3>Vehicle review</h3><p>Organize your details, photos and questions before you buy.</p><span className="home-tool-link">Start a review →</span></a>
            <a href="/budget" className="home-tool"><span className="home-tool-icon" aria-hidden="true">02</span><h3>Budget planner</h3><p>Bring bids, transport and repair quotes into one picture.</p><span className="home-tool-link">Plan your budget →</span></a>
            <a href="/auction-fees" className="home-tool"><span className="home-tool-icon" aria-hidden="true">03</span><h3>Auction fees</h3><p>Request an indicative fee estimate for your bid.</p><span className="home-tool-link">Estimate fees →</span></a>
            <a href="/georgia-excise" className="home-tool"><span className="home-tool-icon" aria-hidden="true">04</span><h3>Georgia excise</h3><p>Calculate the supported excise component for your vehicle.</p><span className="home-tool-link">Check excise →</span></a>
          </div>
        </section>
        <section className="home-demo-heading"><p className="home-kicker">LISTING LOOKUP · DEMONSTRATION</p><h2>See how matching works.</h2><p>Live auction lookup is not available yet. Try a sample listing below to explore the identity checks.</p></section>
        <Resolver initialUrl={reference} />
        <section className="manual-home-link"><p className="eyebrow">HAVE YOUR OWN DETAILS AND PHOTOS?</p><a href="/review">Review your own evidence</a><p>Compile a manual review with your photos and notes. No paid API is needed; your entries remain unverified.</p></section>
      </main>
      <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
    </div>
  );
}
