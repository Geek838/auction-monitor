import Resolver from '../components/resolver';

export default function Home() {
  return (
    <div className="site-shell">
      <header className="masthead">
        <a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a>
        <nav aria-label="Vehicle tools"><a href="/review">Review evidence</a><a href="/budget">Plan budget</a><a href="/local-inspection">Local photo analysis</a></nav>
        <span className="edition">GEORGIA / RESEARCH EDITION</span>
      </header>
      <main id="main-content">
        <div className="intro">
          <p className="eyebrow">VEHICLE IDENTITY, FIRST</p>
          <h1>Start with the<br /><em>exact vehicle.</em></h1>
          <p className="intro-copy">Before the bid, check the identity. Paste a Copart or IAAI link to match the exact auction listing and see the evidence behind it.</p>
        </div>
        <Resolver />
        <section className="manual-home-link"><p className="eyebrow">HAVE YOUR OWN DETAILS AND PHOTOS?</p><a href="/review">Review your own evidence</a><p>Compile a manual review with your photos and notes. No paid API is needed; your entries remain unverified.</p></section>
      </main>
      <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
    </div>
  );
}
