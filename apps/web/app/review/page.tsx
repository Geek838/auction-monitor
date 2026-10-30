import { workflowReference, type WorkflowPageProps } from '../../components/workflow-reference';
import ManualReview from '../../components/manual-review';

export default async function ReviewPage({ searchParams }: WorkflowPageProps) {
  const reference = workflowReference((await searchParams).reference);
  return <div className="site-shell manual-review-page">
    <header className="masthead"><a className="wordmark" href="/" aria-label="Auction Intelligence home">Auction Intelligence<span className="wordmark-dot">.</span></a><a className="manual-back-link" href="/">Back to listing resolver</a></header>
    <main id="main-content"><div className="intro"><p className="eyebrow">A WORKING FILE, BEFORE THE BID</p><h1>Review your<br /><em>own evidence.</em></h1><p className="intro-copy">Turn your vehicle details, photos and inspection questions into one review you can print or keep. Your entries remain clearly identified as user-supplied.</p></div><ManualReview initialUrl={reference} /></main>
    <footer><span>Auction Intelligence</span><span>Built for buyers importing into Georgia.</span></footer>
  </div>;
}
