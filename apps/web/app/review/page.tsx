import { workflowReference, type WorkflowPageProps } from '../../components/workflow-reference';
import ManualReview from '../../components/manual-review';
import './review.css';

export default async function ReviewPage({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return <div className="site-shell manual-review-page">
    <header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><a className="manual-back-link" href="/">Back to listing resolver</a></header>
    <main id="main-content"><div className="review-intro"><p className="eyebrow">YOUR VEHICLE WORKSPACE</p><h1>Put the pieces together.</h1><p>Keep the listing, photos and questions in one place before you bid. Build a review you can take to an inspector.</p><div className="review-intro-steps"><span><b>1</b> Add the listing</span><span><b>2</b> Add photos &amp; notes</span><span><b>3</b> Build your review</span></div></div><ManualReview initialUrl={reference} /></main>
    <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
  </div>;
}
