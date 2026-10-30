export type ResolutionStatus = 'MATCHED' | 'AMBIGUOUS' | 'NOT_FOUND' | 'UNRESOLVED_ID' | 'SOURCE_UNAVAILABLE' | 'NOT_AUTHORIZED';
export type House = 'COPART' | 'IAAI';
export type Vehicle = { vin: string | null; year: number | null; make: string | null; model: string | null; trim: string | null; primary_damage: string | null };
export type Identity = { house: House; lot_or_stock_number: string };
export type ProviderContext = {
  id: string;
  name: string;
  mode: 'FIXTURE' | 'SIMULATED' | 'EXTERNAL';
  authorization: 'NOT_REQUIRED' | 'APPROVED' | 'UNVERIFIED' | 'DENIED';
  enabled: boolean;
  available: boolean;
  contract_version: string;
  reasons: string[];
};
export type Provenance = {
  provider: string; source_name: string; source_url: string | null;
  retrieved_at: string; source_observed_at?: string | null;
  license_scope: string; data_type: 'MOCK' | 'SIMULATED' | 'LICENSED' | 'EXTERNAL_UNVERIFIED'; realtime: boolean;
};
export type EvidenceOrigin = { source: string; reference: string; channel: string; observed_at: string; kind: 'SUPPLIED' | 'OBSERVED' | 'INFERRED' | 'MISSING' };
export type Freshness = {
  status: 'FRESH' | 'STALE' | 'UNKNOWN' | 'HISTORICAL';
  source_observed_at: string | null; evaluated_at: string;
  threshold_seconds: number | null; basis: string;
};
export type Candidate = {
  record_id: string; event_id?: string | null; identity: Identity; vehicle: Vehicle;
  provenance: Provenance; event_status: string; event_date: string | null;
};
export type Resolution = {
  status: ResolutionStatus;
  provider_context: ProviderContext;
  reference: { house: House; url: string; lot_number: string | null; stock_number: string | null; page_id: string | null; country?: string | null };
  identity: Identity | null; vehicle: Vehicle | null; candidates: Candidate[];
  provenance: Provenance | null; evidence: string[]; warnings: string[]; reasons: string[];
  field_evidence?: Record<string, { kind: string; source: string; note: string }>;
  mapping_evidence?: { page_id: string; country?: string | null; identity: Identity; origin: EvidenceOrigin } | null;
  reference_evidence?: { vehicle: Vehicle; origin: EvidenceOrigin } | null;
  record_id?: string | null; event_id?: string | null;
  event_status?: string | null; event_date?: string | null;
  freshness?: Freshness | null;
  snapshot_fingerprint?: string | null;
  preview_eligibility?: { available: boolean; reason: string; scenario_id?: string | null };
};

export function readProviderContext(value: unknown): ProviderContext | null {
  if (!value || typeof value !== 'object') return null;
  const context = value as Partial<ProviderContext>;
  if (typeof context.id !== 'string' || typeof context.name !== 'string'
    || !['FIXTURE', 'SIMULATED', 'EXTERNAL'].includes(context.mode ?? '')
    || !['NOT_REQUIRED', 'APPROVED', 'UNVERIFIED', 'DENIED'].includes(context.authorization ?? '')
    || typeof context.enabled !== 'boolean' || typeof context.available !== 'boolean'
    || typeof context.contract_version !== 'string' || !Array.isArray(context.reasons)
    || !context.reasons.every(reason => typeof reason === 'string')) return null;
  return context as ProviderContext;
}
