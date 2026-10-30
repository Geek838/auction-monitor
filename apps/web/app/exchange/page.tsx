import type { Metadata } from 'next';
import ExchangeConverter from '../../components/exchange-converter';
import './exchange.css';

export const metadata: Metadata = {
  title: 'USD / GEL reference conversion — Auction Intelligence',
  description: 'Convert planning amounts using a dated official National Bank of Georgia reference rate.',
};

export default function ExchangePage() {
  return <div className="site-shell exchange-page">
    <header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><nav aria-label="Vehicle tools"><a href="/review">Evidence review</a><a href="/budget">Plan budget</a><a href="/local-inspection">Local photo analysis</a></nav></header>
    <main id="main-content"><div className="intro"><p className="eyebrow">TWO CURRENCIES. ONE DATED SOURCE.</p><h1>Translate the amount.<br /><em>Keep the rate visible.</em></h1><p className="intro-copy">Check a planning amount in US dollars or Georgian lari with the National Bank of Georgia’s official reference rate. Your budget stays as entered.</p></div><ExchangeConverter /></main>
    <footer><span>Auction Intelligence</span><span>Official reference data · No paid API</span></footer>
  </div>;
}
