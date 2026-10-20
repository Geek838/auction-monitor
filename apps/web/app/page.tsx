import Resolver from '../components/resolver';

export default function Home() {
  return (
    <div className="site-shell">
      <header className="masthead">
        <a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a>
        <span className="edition">GEORGIA / RESEARCH EDITION</span>
      </header>
      <main id="main-content">
        <div className="intro">
          <p className="eyebrow">VEHICLE IDENTITY, FIRST</p>
          <h1>Start with the<br /><em>exact vehicle.</em></h1>
          <p className="intro-copy">Before the bid, check the identity. Paste a Copart or IAAI link to match the exact auction listing and see the evidence behind it.</p>
        </div>
        <Resolver />
      </main>
      <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
    </div>
  );
}
