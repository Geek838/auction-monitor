import { expect, test } from '@playwright/test';

// Consumer-boundary doubles: these browser checks prove UI behavior, not NBG
// availability. Official transport/schema and live evidence are tested separately.
const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const sourceUrl = 'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json';
type Input = { amount: string; from_currency: string; to_currency: string };
function converted(request: Input) {
  return { schema_version: 'exchange-v1', source: 'NATIONAL_BANK_OF_GEORGIA', source_url: sourceUrl, outcome: 'CONVERTED', request,
    converted_amount: request.from_currency === 'USD' ? '259.59' : '38.52',
    quote: { currency: 'USD', quantity: 1, rate_gel: '2.5959', gel_per_usd: '2.5959', effective_date: '2026-10-30', published_at: '2026-10-29T17:01:14.556Z', age_days: 0, freshness: 'EFFECTIVE_TODAY' },
    retrieved_at: '2026-10-30T10:00:00Z', rounding: 'ROUND_HALF_UP_2_DECIMAL_PLACES', max_age_days: 4, errors: [], warnings: ['Controlled browser response fixture; no live NBG request.'] };
}

if (mode === 'fixture') {
  test.beforeEach(async ({ page }) => { await page.goto('/exchange'); });

  test('conversion is explicit and displays dated source and rounding without changing a budget', async ({ page }) => {
    const requests: Input[] = [];
    await page.route('**/api/v1/exchange/convert', async route => {
      const request = route.request().postDataJSON(); requests.push(request); await route.fulfill({ json: converted(request) });
    });
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    expect(requests).toEqual([]);
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Your reference conversion', exact: true })).toBeVisible();
    expect(requests).toEqual([{ amount: '100.00', from_currency: 'USD', to_currency: 'GEL' }]);
    await expect(page.getByText('259.59 GEL', { exact: true })).toBeVisible();
    await expect(page.getByText('2026-10-30', { exact: true })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Reference conversion result', exact: true }).locator('dl > div').filter({ has: page.locator('dt').filter({ hasText: /^Official unit rate$/ }) }).locator('dd')).toHaveText('1 USD = 2.5959 GEL');
    await expect(page.getByText('Budget totals are never changed automatically.', { exact: false })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.getByLabel('Conversion direction', { exact: true }).selectOption('GEL');
    await expect(page.getByRole('region', { name: 'Reference conversion result', exact: true })).toHaveCount(0);
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByText('38.52 USD', { exact: true })).toBeVisible();
    expect(requests[1]).toEqual({ amount: '100.00', from_currency: 'GEL', to_currency: 'USD' });
  });

  test('stale or unavailable official quotes withhold amounts', async ({ page }) => {
    let requestCount = 0;
    await page.route('**/api/v1/exchange/convert', async route => {
      const result = converted(route.request().postDataJSON()); requestCount++;
      if (requestCount === 1) {
        await route.fulfill({ json: { ...result, outcome: 'STALE', converted_amount: null,
          quote: { ...result.quote, effective_date: '2026-10-23', age_days: 7, freshness: 'STALE' },
          errors: [{ code: 'STALE_RATE', message: 'The quote exceeds the application freshness limit.' }] } });
      } else await route.fulfill({ json: { ...result, outcome: 'UNAVAILABLE', converted_amount: null, quote: null, errors: [{ code: 'SOURCE_UNAVAILABLE', message: 'Official exchange-rate service unavailable.' }] } });
    });
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Rate is too old for this planner', exact: true })).toBeVisible();
    await expect(page.getByText('No conversion was produced. Your budget remains unchanged.', { exact: true })).toBeVisible();
    await expect(page.getByText('259.59 GEL', { exact: true })).toHaveCount(0);
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Official rate unavailable', exact: true })).toBeVisible();
    await expect(page.getByText('259.59 GEL', { exact: true })).toHaveCount(0);
  });

  test('editing invalidates the result and discards an in-flight conversion', async ({ page }) => {
    let release!: () => void; let intercepted!: () => void;
    const held = new Promise<void>(done => { release = done; });
    const ready = new Promise<void>(done => { intercepted = done; });
    await page.route('**/api/v1/exchange/convert', async route => {
      const result = converted(route.request().postDataJSON()); intercepted(); await held;
      try { await route.fulfill({ json: result }); } catch { /* edit aborts prior request */ }
    });
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await ready;
    await page.getByLabel('Amount to convert', { exact: true }).fill('200'); release();
    await expect(page.getByRole('region', { name: 'Reference conversion result', exact: true })).toHaveCount(0);
    await expect(page.getByLabel('Amount to convert', { exact: true })).toHaveValue('200');
    await expect(page.getByRole('button', { name: 'Get rate and convert', exact: true })).toBeEnabled();
  });

  test('mismatched response and non-decimal amount are rejected', async ({ page }) => {
    let requests = 0;
    await page.route('**/api/v1/exchange/convert', async route => {
      requests++;
      const result = converted(route.request().postDataJSON());
      await route.fulfill({ json: { ...result, request: { ...result.request, amount: '999.00' } } });
    });
    await page.getByLabel('Amount to convert', { exact: true }).fill('1,000');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('region', { name: 'Reference currency converter', exact: true }).getByRole('alert')).toContainText('Use a decimal point without commas'); expect(requests).toBe(0);
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('region', { name: 'Reference currency converter', exact: true }).getByRole('alert')).toContainText('could not be validated against your inputs');
    await expect(page.getByRole('region', { name: 'Reference conversion result', exact: true })).toHaveCount(0);
  });

  test('a previous effective date is disclosed and a future effective quote is withheld', async ({ page }) => {
    let requests = 0;
    await page.route('**/api/v1/exchange/convert', async route => {
      const result = converted(route.request().postDataJSON()); requests++;
      await route.fulfill({ json: requests === 1 ? { ...result, quote: { ...result.quote, effective_date: '2026-10-29', age_days: 1, freshness: 'PREVIOUS_EFFECTIVE_DATE' } } : {
        ...result, outcome: 'NOT_YET_EFFECTIVE', converted_amount: null,
        quote: { ...result.quote, effective_date: '2026-10-31', age_days: -1, freshness: 'FUTURE_EFFECTIVE_DATE' },
        errors: [{ code: 'FUTURE_EFFECTIVE_DATE', message: 'The official rate is not effective yet.' }],
      } });
    });
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByText('259.59 GEL', { exact: true })).toBeVisible();
    await expect(page.getByText('The effective date precedes retrieval.', { exact: false })).toBeVisible();
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Rate is not effective yet', exact: true })).toBeVisible();
    await expect(page.getByText('259.59 GEL', { exact: true })).toHaveCount(0);
  });

  test('transport failure does not invent a fallback rate', async ({ page }) => {
    await page.route('**/api/v1/exchange/convert', route => route.fulfill({ status: 503, json: { detail: 'Controlled transport failure' } }));
    await page.getByLabel('Amount to convert', { exact: true }).fill('100');
    await page.getByRole('button', { name: 'Get rate and convert', exact: true }).click();
    await expect(page.getByRole('region', { name: 'Reference currency converter', exact: true }).getByRole('alert')).toContainText('No conversion was produced');
    await expect(page.getByRole('region', { name: 'Reference conversion result', exact: true })).toHaveCount(0);
  });

}
