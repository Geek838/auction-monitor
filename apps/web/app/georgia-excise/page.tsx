import type { Metadata } from 'next';
import GeorgiaExcise from '../../components/georgia-excise';
import './excise.css';

export const metadata: Metadata = {
  title: 'Georgia vehicle excise component — Auction Intelligence',
  description: 'A limited 2026 statutory excise estimate for explicitly eligible vehicles, with unsupported cases withheld.',
};

export default function GeorgiaExcisePage() {
  return <div className="site-shell excise-page">
    <header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><nav aria-label="Vehicle tools"><a href="/budget">Plan budget</a><a href="/exchange">Exchange rates</a><a href="/review">Evidence review</a></nav></header>
    <main id="main-content"><div className="intro"><p className="eyebrow">ONE TAX COMPONENT. A DEFINED SCOPE.</p><h1>Check the excise.<br /><em>Keep the rest open.</em></h1><p className="intro-copy">Estimate the statutory excise component for a supported vehicle declared in Georgia in 2026. Other duties, taxes and service charges remain separate and unknown.</p></div><GeorgiaExcise /></main>
    <footer><span>Auction Intelligence</span><span>Limited statutory component · Not an official assessment</span></footer>
  </div>;
}
