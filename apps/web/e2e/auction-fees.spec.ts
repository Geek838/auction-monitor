import { expect, test, type Page } from '@playwright/test';

const endpoint = '**/api/v1/auction-fees/estimate';
async function selections(page: Page) {
  await page.getByLabel('Your bid (USD)', { exact: true }).fill('5000');
  await page.getByLabel('Auction', { exact: true }).selectOption('copart');
  await page.getByLabel('How will you bid?', { exact: true }).selectOption('online');
  await page.getByLabel('Payment or buyer fee category', { exact: true }).selectOption('secured');
  await page.getByLabel('Vehicle / buyer category', { exact: true }).selectOption('standard');
  await page.getByLabel('Copart buyer volume', { exact: true }).selectOption('low');
}
function result(body: Record<string, unknown>) { return { schema_version: 'auction-fee-estimate-v1', source_kind: 'INDICATIVE_EXTERNAL_UNVERIFIED', source_url: 'https://api.auctionfeescalculator.com', outcome: 'ESTIMATED', request: body, currency: 'USD', bid_amount: '5000.00', auction_fee: '1030.00', total_amount: '6030.00', schedule_as_of: null, retrieved_at: '2026-10-31T12:00:00Z', errors: [], warnings: ['Controlled test data; not an official auction quote.'] }; }
if ((process.env.E2E_PROVIDER_MODE ?? 'fixture') === 'fixture') {
  test.beforeEach(async ({ page }) => { await page.goto('/auction-fees'); });
  test('requires consent and shows an attributed undated estimate without changing budget', async ({ page }) => {
    const calls: unknown[] = [];
    await page.route(endpoint, async route => { const body = route.request().postDataJSON(); calls.push(body); await route.fulfill({ json: result(body) }); });
    await selections(page); await page.getByRole('button', { name: 'Request fee estimate' }).click();
    await expect(page.getByRole('region', { name: 'Auction fee estimate', exact: true }).getByRole('alert')).toContainText('confirm permission'); expect(calls).toHaveLength(0);
    await page.getByRole('checkbox', { name: /I agree to send/ }).check();
    await page.getByRole('button', { name: 'Request fee estimate' }).click();
    await expect(page.getByRole('heading', { name: 'Indicative auction fee' })).toBeVisible();
    await expect(page.getByText('$1,030.00', { exact: true })).toBeVisible();
    await expect(page.getByText('Not supplied by provider', { exact: true })).toBeVisible();
    expect(calls).toEqual([{ bid_amount: '5000.00', auction: 'copart', bid_type: 'online', bid_pay: 'secured', bid_vehicle: 'standard', volume: 'low', consent_to_send: true }]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
  test('unavailable and mismatched responses do not show fees', async ({ page }) => {
    let count = 0;
    await page.route(endpoint, async route => { const body = route.request().postDataJSON(); const good = result(body); count++; await route.fulfill({ json: count === 1 ? { ...good, outcome: 'UNAVAILABLE', auction_fee: null, total_amount: null, errors: [{ code: 'SOURCE_UNAVAILABLE', message: 'Unavailable' }] } : { ...good, request: { ...body, bid_amount: '9999.00' } } }); });
    await selections(page); await page.getByRole('checkbox', { name: /I agree to send/ }).check();
    await page.getByRole('button', { name: 'Request fee estimate' }).click();
    await expect(page.getByRole('heading', { name: 'Fee estimate unavailable' })).toBeVisible();
    await page.getByRole('button', { name: 'Request fee estimate' }).click();
    await expect(page.getByRole('region', { name: 'Auction fee estimate', exact: true }).getByRole('alert')).toContainText('could not be matched');
    await expect(page.getByText('$1,030.00', { exact: true })).toHaveCount(0);
  });
  test('editing inputs aborts an in-flight estimate', async ({ page }) => {
    let release!: () => void; let seen!: () => void;
    const hold = new Promise<void>(resolve => { release = resolve; }); const ready = new Promise<void>(resolve => { seen = resolve; });
    await page.route(endpoint, async route => { const body = route.request().postDataJSON(); seen(); await hold; try { await route.fulfill({ json: result(body) }); } catch { /* Aborted by edit. */ } });
    await selections(page); await page.getByRole('checkbox', { name: /I agree to send/ }).check();
    await page.getByRole('button', { name: 'Request fee estimate' }).click(); await ready;
    await page.getByLabel('Your bid (USD)', { exact: true }).fill('7000'); release();
    await expect(page.getByRole('region', { name: 'Your fee estimate' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Request fee estimate' })).toBeEnabled();
  });
}
