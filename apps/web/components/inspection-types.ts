import { readProviderContext, type Freshness, type Identity, type ProviderContext } from './resolution-types';

export type PhotoAsset = {
  asset_id: string; title: string; alt_text: string; view_label: string;
  content_sha256: string; width: number; height: number; mime_type: 'image/png';
  source_kind: 'SELF_AUTHORED_FIXTURE'; author: string; rights_reference: string;
  capture_time: string | null; asset_url: string;
};
export type InspectionFinding = {
  finding_id: string; classification: 'OBSERVED' | 'SUSPECTED' | 'UNKNOWN';
  region: string; component: string; description: string; rationale: string;
  severity: 'MINOR' | 'MODERATE' | 'SEVERE' | 'UNKNOWN'; confidence: null;
  confidence_basis: string; image_ids: string[]; confirmation: string;
};
export type InspectionTarget = {
  reference: { house: string; url: string; page_id?: string | null; country?: string | null };
  provider_context: ProviderContext; identity: Identity; record_id: string; event_id: string | null;
  event_status: string | null; event_date: string | null; snapshot_fingerprint: string;
  vin: string | null; source_observed_at: string | null; retrieved_at: string; freshness: Freshness | null;
};
export type InspectionPreview = {
  request_id: string; outcome: 'COMPLETED' | 'PARTIAL' | 'BLOCKED' | 'FAILED';
  reason_code: string; resolver_status: string; reasons: string[];
  target: InspectionTarget | null; assets: PhotoAsset[]; findings: InspectionFinding[];
  checks: string[]; limitations: string[]; exclusions: { asset_id: string | null; reason: string }[];
  provenance: {
    mode: 'MOCK'; engine_id: string; engine_version: string; scenario_id: string;
    fixture_revision: string; schema_version: string; generated_at: string;
    target_digest: string; image_digests: Record<string, string>;
    model_provider: null; model_id: null; prompt_version: null;
  } | null;
};

const digest = /^[a-f0-9]{64}$/;
function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
}

// Never route an illustration through a remote URL or Next's image optimizer.
export function guardedAssetUrl(asset: PhotoAsset, fingerprint: string): string | null {
  try {
    const url = new URL(asset.asset_url, 'http://local.invalid');
    if (url.origin !== 'http://local.invalid'
      || url.pathname !== `/api/v1/inspection-assets/${encodeURIComponent(asset.asset_id)}`
      || url.searchParams.get('expected_snapshot_fingerprint') !== fingerprint
      || !url.searchParams.has('url') || url.hash) return null;
    return `${url.pathname}${url.search}`;
  } catch { return null; }
}

export function readInspectionPreview(raw: unknown): InspectionPreview | null {
  if (!raw || typeof raw !== 'object') return null;
  const report = raw as InspectionPreview;
  if (!['COMPLETED', 'PARTIAL', 'BLOCKED', 'FAILED'].includes(report.outcome)
    || typeof report.request_id !== 'string' || typeof report.reason_code !== 'string'
    || typeof report.resolver_status !== 'string' || !strings(report.reasons)
    || !strings(report.checks) || !strings(report.limitations)
    || !Array.isArray(report.exclusions) || report.exclusions.some(item => !item || typeof item.reason !== 'string')
    || !Array.isArray(report.assets) || report.assets.length > 6
    || !Array.isArray(report.findings) || report.findings.length > 30) return null;
  if (report.outcome === 'BLOCKED' || report.outcome === 'FAILED') {
    return report.assets.length === 0 && report.findings.length === 0 && report.provenance === null ? report : null;
  }
  const { target, provenance } = report;
  if (!target || !readProviderContext(target.provider_context) || !target.identity
    || typeof target.identity.house !== 'string' || typeof target.identity.lot_or_stock_number !== 'string'
    || typeof target.record_id !== 'string' || !digest.test(target.snapshot_fingerprint)
    || !provenance || provenance.mode !== 'MOCK' || provenance.target_digest !== target.snapshot_fingerprint
    || !provenance.image_digests || typeof provenance.generated_at !== 'string'
    || provenance.model_provider !== null || provenance.model_id !== null || provenance.prompt_version !== null
    || report.assets.length === 0) return null;
  const ids = new Set<string>();
  for (const asset of report.assets) {
    if (!asset || typeof asset.asset_id !== 'string' || ids.has(asset.asset_id)
      || ![asset.title, asset.alt_text, asset.view_label, asset.author, asset.rights_reference].every(item => typeof item === 'string')
      || asset.source_kind !== 'SELF_AUTHORED_FIXTURE' || asset.mime_type !== 'image/png'
      || !digest.test(asset.content_sha256) || provenance.image_digests[asset.asset_id] !== asset.content_sha256
      || !Number.isInteger(asset.width) || !Number.isInteger(asset.height)
      || asset.width <= 0 || asset.width > 2048 || asset.height <= 0 || asset.height > 2048
      || !guardedAssetUrl(asset, target.snapshot_fingerprint)) return null;
    ids.add(asset.asset_id);
  }
  for (const finding of report.findings) {
    if (!finding || !['OBSERVED', 'SUSPECTED', 'UNKNOWN'].includes(finding.classification)
      || !['MINOR', 'MODERATE', 'SEVERE', 'UNKNOWN'].includes(finding.severity)
      || ![finding.finding_id, finding.region, finding.component, finding.description, finding.rationale, finding.confirmation, finding.confidence_basis].every(item => typeof item === 'string')
      || finding.confidence !== null || !strings(finding.image_ids)
      || finding.image_ids.some(id => !ids.has(id))
      || (finding.classification !== 'UNKNOWN' && finding.image_ids.length === 0)) return null;
  }
  return report;
}
