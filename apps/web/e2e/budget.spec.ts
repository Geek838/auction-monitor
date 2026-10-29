import { expect, test, type Page } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const categories = ['Auction and broker charges', 'US inland transport', 'Ocean freight and port charges', 'Georgia clearance', 'Registration', 'Parts', 'Labor and materials', 'Diagnostics and calibration', 'Repair contingency', 'Other costs'];
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Asia/Tbilisi' }).format(new Date());
const expires = new Date(new Date(`${today}T12:00:00Z`).getTime() + 2 * 86400000).toISOString().slice(0, 10);

async function calculate(page: Page) {
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/v1/budgets/evaluate') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Calculate budget', exact: true }).click();
  const response = await responsePromise;
  expect(response.ok()).toBe(true);
  const report = await response.json();
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toBeVisible();
  return { report, request: response.request().postDataJSON() };
}

async function fillComplete(page: Page) {
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('5000');
  for (const category of categories) {
    await page.getByLabel(`${category} coverage`, { exact: true }).selectOption(category === 'Parts' ? 'COSTS' : 'NOT_APPLICABLE');
    if (category !== 'Parts') await page.getByLabel(`Why ${category.toLowerCase()} does not apply`, { exact: true }).fill('Excluded only for this engineering arithmetic case.');
  }
  await page.getByLabel('Parts line 1 low (USD)', { exact: true }).fill('100');
  await page.getByLabel('Parts line 1 base (USD)', { exact: true }).fill('200');
  await page.getByLabel('Parts line 1 high (USD)', { exact: true }).fill('300');
  await page.getByText('Source and date for parts line 1', { exact: true }).click();
  await page.getByLabel('Parts line 1 source or basis', { exact: true }).fill('Engineering quote, not a supplier price');
  await page.getByLabel('Parts line 1 as-of date', { exact: true }).fill(today);
  await page.getByLabel('Parts line 1 expires on', { exact: true }).fill(expires);
  await page.getByLabel('I have a fee schedule to enter', { exact: true }).check();
  await page.getByLabel('Fee schedule source or basis', { exact: true }).fill('Engineering fee schedule only');
  await page.getByLabel('Fee schedule as-of date', { exact: true }).fill(today);
  await page.getByLabel('Fee schedule expires on', { exact: true }).fill(expires);
  await page.getByLabel('Fee band 1 flat amount (USD)', { exact: true }).fill('50');
  await page.getByLabel('Fee band 1 percentage', { exact: true }).fill('10');
  await page.getByLabel('Calculate a planning bid ceiling', { exact: true }).check();
  await page.getByLabel('Conservative vehicle value (USD)', { exact: true }).fill('10000');
  await page.getByLabel('Required savings or margin (USD)', { exact: true }).fill('1000');
  await page.getByLabel('Additional risk reserve (USD)', { exact: true }).fill('500');
}

test.beforeEach(async ({ page, request }) => {
  expect((await (await request.get('/api/v1/health')).json()).provider_context.id).toBe(mode);
  await page.goto('/budget');
});

test('sourced manual cost scenario computes ranges and a fee-aware indicative ceiling', async ({ page }, info) => {
  if (info.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
  const external: string[] = [];
  page.on('request', request => { if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(page.url()).origin) external.push(request.url()); });
  await fillComplete(page);
  const { report, request } = await calculate(page);
  expect(report.status).toBe('COMPLETE');
  expect(report.source_kind).toBe('USER_SUPPLIED_UNVERIFIED');
  expect(report.total_at_bid).toEqual({ low: '5650.00', base: '5750.00', high: '5850.00' });
  expect(report.max_bid.status).toBe('INDICATIVE');
  expect(report.max_bid.amount).toBe('7409.09');
  expect(typeof request.hammer_bid).toBe('string');
  expect(request.costs[0].kind).toBe('QUOTE');
  const reportRegion = page.getByRole('region', { name: 'Your budget scenario', exact: true });
  await expect(reportRegion.getByRole('heading', { name: 'All-in scenario at your bid', exact: true })).toBeVisible();
  await expect(reportRegion.getByText('$7,409.09', { exact: true })).toBeVisible();
  await expect(reportRegion.getByText('INDICATIVE · USER INPUTS', { exact: true })).toBeVisible();
  expect(external).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: path.resolve(__dirname, `../../../.cache/qa/v1/budget-${mode}-${info.project.name}.png`), fullPage: true });
  if (info.project.name === 'mobile-chromium' && mode === 'fixture') {
    await reportRegion.getByRole('heading', { name: 'Planning bid ceiling', exact: true }).scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.resolve(__dirname, '../../../.cache/qa/v1/budget-mobile.png') });
  }
});

test('missing categories and fees remain visible and withhold the all-in cost and ceiling', async ({ page }) => {
  await expect(page.getByLabel('Hammer bid (USD)', { exact: true })).toHaveValue('');
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('5000');
  const { report } = await calculate(page);
  expect(report.status).toBe('INCOMPLETE');
  expect(report.missing_categories).toHaveLength(10);
  expect(report.auction_fee_at_bid).toBeNull();
  expect(report.total_at_bid).toBeNull();
  expect(report.max_bid.status).toBe('WITHHELD');
  await expect(page.getByRole('heading', { name: 'Known subtotal at your bid', exact: true })).toBeVisible();
  await expect(page.getByText('Withheld — inputs are incomplete', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Resolve these gaps', exact: true })).toBeVisible();
});

test('budget JSON export matches the actual calculation and print retains unverified labels', async ({ page }) => {
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('123.45');
  const { report } = await calculate(page);
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download budget JSON', exact: true }).click();
  const download = await downloadPromise;
  const file = await download.path();
  expect(file).not.toBeNull();
  expect(JSON.parse(await readFile(file!, 'utf8'))).toEqual(report);
  await page.evaluate(() => { window.print = () => { (window as unknown as Record<string, unknown>).__budgetPrinted = true; }; });
  const print = page.getByRole('button', { name: 'Print budget', exact: true });
  await print.focus(); await print.press('Enter');
  expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__budgetPrinted)).toBe(true);
  await page.emulateMedia({ media: 'print' });
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toBeVisible();
  await expect(page.getByText('USER-SUPPLIED PLANNING SCENARIO', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Calculate budget', exact: true })).toBeHidden();
  await page.emulateMedia({ media: 'screen' });
  await page.getByRole('button', { name: 'Clear budget', exact: true }).click();
  await expect(page.getByLabel('Hammer bid (USD)', { exact: true })).toHaveValue('');
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toHaveCount(0);
});

test('editing invalidates the calculated scenario and rejects a late response', async ({ page }) => {
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('500');
  await calculate(page);
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('600');
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toHaveCount(0);
  let release!: () => void;
  let intercepted!: () => void;
  const held = new Promise<void>(done => { release = done; });
  const ready = new Promise<void>(done => { intercepted = done; });
  await page.route('**/api/v1/budgets/evaluate', async route => {
    const response = await route.fetch(); intercepted(); await held;
    try { await route.fulfill({ response }); } catch { /* Old request is aborted on edit. */ }
  });
  await page.getByRole('button', { name: 'Calculate budget', exact: true }).click();
  await ready;
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('700');
  release();
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toHaveCount(0);
});

test('a returned calculation for different inputs is rejected', async ({ page }) => {
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('500');
  await page.route('**/api/v1/budgets/evaluate', async route => {
    const response = await route.fetch(); const report = await response.json();
    report.request.hammer_bid = '999.00';
    await route.fulfill({ response, json: report });
  });
  const response = page.waitForResponse(response => response.url().endsWith('/api/v1/budgets/evaluate'));
  await page.getByRole('button', { name: 'Calculate budget', exact: true }).click();
  await response;
  await expect(page.getByRole('main').getByRole('alert')).toContainText('The budget response did not match your inputs.');
  await expect(page.getByRole('heading', { name: 'Your budget scenario', exact: true })).toHaveCount(0);
});

test('supplier text remains literal data in the report', async ({ page }) => {
  const hostile = '<img src=x onerror="window.__budgetInjected=true">';
  await page.getByLabel('Hammer bid (USD)', { exact: true }).fill('500');
  await page.getByLabel('Parts coverage', { exact: true }).selectOption('COSTS');
  await page.getByLabel('Parts line 1 label (optional)', { exact: true }).fill(hostile);
  for (const field of ['low', 'base', 'high']) await page.getByLabel(`Parts line 1 ${field} (USD)`, { exact: true }).fill('100');
  await calculate(page);
  await expect(page.getByRole('heading', { name: hostile, exact: true })).toBeVisible();
  await expect(page.locator('img[src="x"]')).toHaveCount(0);
  expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__budgetInjected)).toBeUndefined();
});
