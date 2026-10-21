export type ReviewClassification = 'OBSERVED' | 'SUSPECTED' | 'UNKNOWN';
export type ReviewPhoto = { photo_id: string; sha256: string; width: number; height: number; label: string };
export type ReviewFinding = { photo_id: string | null; classification: ReviewClassification; component: string; description: string };
export type ManualReviewRequest = {
  url: string;
  stock_number: string | null;
  vehicle: { vin: string | null; year: number | null; make: string | null; model: string | null };
  photos: ReviewPhoto[];
  findings: ReviewFinding[];
  notes: string;
};
export type ManualReviewReport = {
  schema_version: 'manual-review-v1';
  source_kind: 'USER_SUPPLIED_UNVERIFIED';
  verification_status: 'UNVERIFIED';
  reference: { url: string; house: 'COPART' | 'IAAI'; lot_number: string | null; page_id: string | null; country: string | null; stock_number: string | null };
  canonical_claim: { house: 'COPART' | 'IAAI'; lot_or_stock_number: string | null; verification_status: 'UNVERIFIED' };
  vehicle: ManualReviewRequest['vehicle'];
  photos: (ReviewPhoto & { verification_status: 'CLIENT_DECLARED_NOT_SERVER_VERIFIED' })[];
  findings: (ReviewFinding & { source_kind: 'USER_REPORTED' })[];
  notes: string;
  checks: { system: string; status: 'UNKNOWN'; recommendation: string }[];
  warnings: string[];
  generated_at: string;
};

function record(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

export function readManualReview(value: unknown, input: ManualReviewRequest): ManualReviewReport | null {
  if (!record(value) || value.schema_version !== 'manual-review-v1' || value.source_kind !== 'USER_SUPPLIED_UNVERIFIED'
    || value.verification_status !== 'UNVERIFIED' || !record(value.reference) || !record(value.canonical_claim)
    || !['COPART', 'IAAI'].includes(String(value.reference.house))
    || value.canonical_claim.house !== value.reference.house || value.canonical_claim.verification_status !== 'UNVERIFIED'
    || !record(value.vehicle) || typeof value.notes !== 'string' || typeof value.generated_at !== 'string'
    || !Array.isArray(value.photos) || !Array.isArray(value.findings) || !Array.isArray(value.checks)
    || !Array.isArray(value.warnings) || !value.warnings.every(item => typeof item === 'string')
    || value.photos.length !== input.photos.length || value.findings.length !== input.findings.length
    || value.notes !== input.notes || !Number.isFinite(Date.parse(value.generated_at))) return null;
  let expectedUrl: URL;
  try { expectedUrl = new URL(input.url); } catch { return null; }
  expectedUrl.search = ''; expectedUrl.hash = '';
  expectedUrl.pathname = expectedUrl.pathname.replace(/\/$/, '');
  const expectedHouse = /(?:^|\.)iaai\.com$/i.test(expectedUrl.hostname) ? 'IAAI' : 'COPART';
  const path = expectedUrl.pathname;
  const copart = /\/(?:[a-z]{2}\/)?lot\/([0-9]+)(?:\/[A-Za-z0-9_-]+)?$/i.exec(path);
  const iaai = /\/(?:[a-z]{2}(?:-[a-z]{2})?\/)?VehicleDetail\/([A-Za-z0-9-]+)(?:~([A-Za-z]{2}))?$/i.exec(path);
  if (expectedHouse === 'COPART' && !copart || expectedHouse === 'IAAI' && !iaai) return null;
  const lot = expectedHouse === 'COPART' ? copart![1] : null;
  const page = expectedHouse === 'IAAI' ? iaai![1] : null;
  const country = expectedHouse === 'IAAI' ? iaai![2]?.toUpperCase() ?? null : null;
  const expectedVin = input.vehicle.vin?.trim().toUpperCase() ?? null;
  if (value.reference.url !== expectedUrl.href || value.reference.house !== expectedHouse
    || value.reference.lot_number !== lot || value.reference.page_id !== page || value.reference.country !== country
    || value.reference.stock_number !== null
    || value.vehicle.vin !== expectedVin || value.vehicle.year !== input.vehicle.year
    || value.vehicle.make !== input.vehicle.make || value.vehicle.model !== input.vehicle.model
    || value.canonical_claim.lot_or_stock_number !== (expectedHouse === 'IAAI' ? input.stock_number : lot)) return null;
  for (const photo of value.photos) {
    if (!record(photo) || photo.verification_status !== 'CLIENT_DECLARED_NOT_SERVER_VERIFIED') return null;
    const sent = input.photos.find(item => item.photo_id === photo.photo_id);
    if (!sent || sent.sha256 !== photo.sha256 || sent.width !== photo.width || sent.height !== photo.height || sent.label !== photo.label) return null;
  }
  if (new Set(value.photos.map(photo => (photo as Record<string, unknown>).photo_id)).size !== input.photos.length) return null;
  for (let index = 0; index < value.findings.length; index++) {
    const finding = value.findings[index];
    const sent = input.findings[index];
    if (!record(finding) || finding.source_kind !== 'USER_REPORTED' || finding.classification !== sent.classification
      || finding.photo_id !== sent.photo_id || finding.component !== sent.component || finding.description !== sent.description) return null;
  }
  const systems = ['Structural integrity', 'SRS and airbags', 'ADAS', 'Cooling', 'Suspension', 'Mechanical condition'];
  if (value.checks.length !== systems.length || !value.checks.every(item => record(item) && systems.includes(String(item.system)) && item.status === 'UNKNOWN' && typeof item.recommendation === 'string')
    || new Set(value.checks.map(item => (item as Record<string, unknown>).system)).size !== systems.length) return null;
  return value as ManualReviewReport;
}
