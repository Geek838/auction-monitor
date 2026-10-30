import type { Metadata } from 'next';
import AuctionFeeEstimate from '../../components/auction-fee-estimate';
import './fees.css';

export const metadata: Metadata = { title: 'Auction fee estimate — Auction Intelligence', description: 'Request an indicative third-party auction fee estimate.' };
export default function AuctionFeesPage() {
  return <div className="site-shell fees-page"><header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><nav aria-label="Vehicle tools"><a href="/review">Vehicle review</a><a href="/budget">Budget planner</a></nav></header><main id="main-content"><div className="intro"><p className="eyebrow">ONE BID. ONE ESTIMATE.</p><h1>Plan for the<br /><em>auction fees.</em></h1><p className="intro-copy">Request an indicative third-party estimate for your bid. Check the amount against the auction or your broker before relying on it.</p></div><AuctionFeeEstimate /></main><footer><span>Auction Intelligence</span><span>Third-party estimate · no account required</span></footer></div>;
}
