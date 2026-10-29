import LocalInspection from './workspace';
import './vision.css';

export default function LocalInspectionPage() {
  return <div className="site-shell local-vision-page">
    <header className="masthead"><a className="wordmark" href="/">Auction Intelligence<span className="wordmark-dot">.</span></a><nav aria-label="Workspace"><a href="/review">Review evidence</a><a href="/budget">Plan budget</a><a href="/">Listing resolver</a></nav></header>
    <main id="main-content"><div className="intro"><p className="eyebrow">LOCAL PHOTO ANALYSIS / EXPERIMENTAL</p><h1>Look closer.<br /><em>Keep the unknowns.</em></h1><p className="intro-copy">Use a locally installed vision model to review permitted photos. Model findings need human checking; the vehicle and auction identity remain unverified.</p></div><LocalInspection /></main>
    <footer><span>Auction Intelligence</span><span>No paid AI API. Local hardware and model setup required.</span></footer>
  </div>;
}
