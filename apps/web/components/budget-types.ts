export const costCategories = [
  { id: 'auction_broker', name: 'Auction and broker charges', help: 'Non-percentage broker or transaction charges. Put bid-dependent auction fees in the fee schedule below.' },
  { id: 'us_transport', name: 'US inland transport', help: 'Transport from the auction location to the departure port.' },
  { id: 'ocean_port', name: 'Ocean freight and port charges', help: 'Shipping, handling and port charges for this route.' },
  { id: 'georgia_clearance', name: 'Georgia clearance', help: 'Use a dated vehicle-specific quote or your explicit assumption. No tax formula is supplied.' },
  { id: 'registration', name: 'Registration', help: 'Registration and related charges for the intended destination/use.' },
  { id: 'parts', name: 'Parts', help: 'Dated compatible-part quotes or a declared allowance. No part compatibility is inferred.' },
  { id: 'labor', name: 'Labor and materials', help: 'Bodywork, paint, materials and other labor in your repair scope.' },
  { id: 'diagnostics', name: 'Diagnostics and calibration', help: 'Inspections, scans and specialist calibration where needed.' },
  { id: 'contingency', name: 'Repair contingency', help: 'An explicit allowance for uncertain repair scope; it is not a diagnosis.' },
  { id: 'other', name: 'Other costs', help: 'Insurance, storage or other applicable costs. Mark not applicable only with a reason.' },
] as const;
export type CostCategory = typeof costCategories[number]['id'];
export type EvidenceKind = 'QUOTE' | 'ASSUMPTION';
export type BudgetCost = { category: CostCategory; label: string; low: string; base: string; high: string; kind: EvidenceKind; source: string | null; as_of: string | null; expires_on: string | null };
export type FeeTier = { from_bid: string; to_bid: string | null; flat: string; percent: string };
export type FeeSchedule = { tiers: FeeTier[]; kind: EvidenceKind; source: string | null; as_of: string | null; expires_on: string | null };
export type BudgetRequest = { currency: 'USD'; hammer_bid: string; costs: BudgetCost[]; not_applicable: { category: CostCategory; reason: string }[]; auction_fees: FeeSchedule | null; market_value: string | null; required_savings: string | null; risk_reserve: string | null };
export type MoneyRange = { low: string; base: string; high: string };
export type BudgetReport = {
  schema_version: 'budget-v1'; currency: 'USD'; source_kind: 'USER_SUPPLIED_UNVERIFIED'; status: 'COMPLETE' | 'INCOMPLETE';
  request: BudgetRequest; hammer_bid: string; costs: BudgetCost[]; not_applicable: BudgetRequest['not_applicable']; missing_categories: CostCategory[];
  issues: { code: string; category: string | null; message: string }[]; known_non_bid_totals: MoneyRange; auction_fee_at_bid: string | null;
  known_total_at_bid: MoneyRange; total_at_bid: MoneyRange | null;
  max_bid: { status: 'INDICATIVE' | 'WITHHELD' | 'NO_FEASIBLE_BID'; amount: string | null; reason: string; high_non_bid_total: string; auction_fee_at_max: string | null };
  warnings: string[]; generated_at: string;
};
const money = (value: unknown): value is string => typeof value === 'string' && /^\d+\.\d{2}$/.test(value);
function record(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }
function range(value: unknown): value is MoneyRange { return record(value) && money(value.low) && money(value.base) && money(value.high); }
function normalizedNumber(value: string) { const [whole, fraction = ''] = value.split('.'); return `${whole.replace(/^0+(?=\d)/, '')}.${fraction.replace(/0+$/, '')}`; }
function normalize(value: unknown, key = ''): unknown {
  if (Array.isArray(value)) return value.map(item => normalize(item));
  if (record(value)) return Object.fromEntries(Object.keys(value).sort().map(name => [name, normalize(value[name], name)]));
  if (typeof value === 'string' && ['hammer_bid', 'low', 'base', 'high', 'from_bid', 'to_bid', 'flat', 'percent', 'market_value', 'required_savings', 'risk_reserve'].includes(key)) return normalizedNumber(value);
  return value;
}
export function readBudgetReport(value: unknown, request: BudgetRequest): BudgetReport | null {
  if (!record(value) || value.schema_version !== 'budget-v1' || value.currency !== 'USD' || value.source_kind !== 'USER_SUPPLIED_UNVERIFIED'
    || !['COMPLETE', 'INCOMPLETE'].includes(String(value.status)) || !record(value.request)
    || JSON.stringify(normalize(value.request)) !== JSON.stringify(normalize(request))
    || !money(value.hammer_bid) || !Array.isArray(value.costs) || !Array.isArray(value.not_applicable) || !Array.isArray(value.missing_categories)
    || !Array.isArray(value.issues) || !value.issues.every(item => record(item) && typeof item.message === 'string' && typeof item.code === 'string')
    || !range(value.known_non_bid_totals) || !range(value.known_total_at_bid) || value.total_at_bid !== null && !range(value.total_at_bid)
    || value.auction_fee_at_bid !== null && !money(value.auction_fee_at_bid)
    || !record(value.max_bid) || !['INDICATIVE', 'WITHHELD', 'NO_FEASIBLE_BID'].includes(String(value.max_bid.status))
    || value.max_bid.amount !== null && !money(value.max_bid.amount) || typeof value.max_bid.reason !== 'string'
    || !Array.isArray(value.warnings) || !value.warnings.every(item => typeof item === 'string')
    || typeof value.generated_at !== 'string' || !Number.isFinite(Date.parse(value.generated_at))) return null;
  if (JSON.stringify(normalize(value.costs)) !== JSON.stringify(normalize(value.request.costs))
    || JSON.stringify(normalize(value.not_applicable)) !== JSON.stringify(normalize(value.request.not_applicable))
    || normalizedNumber(value.hammer_bid) !== normalizedNumber(request.hammer_bid)) return null;
  if (value.status === 'COMPLETE' && value.total_at_bid === null) return null;
  if (value.max_bid.status === 'INDICATIVE' && (value.max_bid.amount === null || request.market_value === null || request.required_savings === null || request.risk_reserve === null)) return null;
  if (value.status === 'INCOMPLETE' && (value.total_at_bid !== null || value.max_bid.status === 'INDICATIVE' || value.max_bid.amount !== null)) return null;
  if (value.max_bid.status !== 'INDICATIVE' && value.max_bid.amount !== null) return null;
  return value as BudgetReport;
}
