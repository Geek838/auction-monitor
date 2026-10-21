import { expect, test, type Page } from '@playwright/test';

test.skip((process.env.E2E_PROVIDER_MODE ?? 'fixture') !== 'fixture', 'Sprint 1 fixture regression runs only against the fixture provider.');

async function resolve(page: Page, url: string) {
  await page.getByLabel('Copart or IAAI listing URL').fill(url);
  await page.getByRole('button', { name: 'Resolve listing', exact: true }).click();
}

function fact(page: Page, label: string) {
  return page.getByRole('term').filter({ hasText: new RegExp(`^${label}$`) }).locator('..').getByRole('definition');
}

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test('health and rendered mode identify the actual fixture provider', async ({ page, request }) => {
  const response = await request.get('/api/v1/health');
  expect(response.ok()).toBe(true);
  const health = await response.json();
  expect(health.provider_context.mode).toBe('FIXTURE');
  expect(health.provider_context.available).toBe(true);
  await expect(page.getByText('MOCK DATA', { exact: true })).toBeVisible();
  await expect(page.getByText('SIMULATED DATA', { exact: true })).toHaveCount(0);
});

test('failed health lookup stays unknown until an actual resolution supplies context', async ({ page }) => {
  await page.route('**/api/v1/health', route => route.abort());
  await page.reload();
  await expect(page.getByText('SOURCE UNKNOWN', { exact: true })).toBeVisible();
  await expect(page.getByText('MOCK DATA', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Try a matched Copart fixture', exact: true })).toHaveCount(0);
  await resolve(page, 'https://copart.com/lot/51374586');
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
  await expect(page.getByText('MOCK DATA', { exact: true })).toBeVisible();
});

test('keyboard submission resolves the exact fixture with visible mock provenance', async ({ page }) => {
  const input = page.getByLabel('Copart or IAAI listing URL');
  await input.fill('https://www.copart.com/lot/51374586/?tracking=test');
  await input.press('Enter');
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
  await expect(fact(page, 'Canonical lot number')).toHaveText('51374586');
  await expect(page.getByText('MOCK', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Record provenance' })).toBeVisible();
  await expect(page.getByText('Freshness unknown', { exact: true })).toBeVisible();
  await expect(fact(page, 'Retrieved at')).toContainText('UTC');
  await expect(fact(page, 'Data type')).toContainText('Not a real-time feed');
  await expect(page.getByText('No licensed photos supplied', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: /no selection made/i })).toHaveCount(0);
});

test('IAAI page ID and canonical stock remain distinct', async ({ page }) => {
  await resolve(page, 'https://www.iaai.com/VehicleDetail/41000001~US');
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
  await expect(fact(page, 'IAAI page ID')).toHaveText('41000001');
  await expect(fact(page, 'Canonical stock number')).toHaveText('45371195');
});

test('leading zeros and missing VIN render without fabricated metadata', async ({ page }) => {
  await resolve(page, 'https://copart.com/lot/00012345');
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
  await expect(fact(page, 'Canonical lot number')).toHaveText('00012345');
  await expect(fact(page, 'VIN')).toHaveText('Not supplied');
  await expect(page.getByText(/VIN is unavailable/)).toBeVisible();
});

for (const scenario of [
  { url: 'https://copart.com/lot/70000001', heading: 'We could not confirm one exact match' },
  { url: 'https://copart.com/lot/99999999', heading: 'No fixture record found' },
  { url: 'https://iaai.com/VehicleDetail/45371195~US', heading: 'The IAAI stock number is not confirmed' },
  { url: 'https://copart.com/lot/70000003', heading: 'The data provider is unavailable' },
  { url: 'https://copart.com/lot/70000004', heading: 'Authorized data access is not available' },
]) {
  test(`provider state: ${scenario.heading}`, async ({ page }) => {
    await resolve(page, scenario.url);
    await expect(page.getByRole('heading', { name: scenario.heading, exact: true })).toBeVisible();
    await expect(page.getByText('MOCK', { exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toHaveCount(0);
  });
}

test('invalid hostname has actionable validation and preserves input', async ({ page }) => {
  const malicious = 'https://copart.com.evil.example/lot/51374586';
  await resolve(page, malicious);
  await expect(page.getByRole('alert').filter({ has: page.getByRole('heading', { name: 'This link cannot be resolved' }) })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'This link cannot be resolved' })).toBeVisible();
  await expect(page.getByLabel('Copart or IAAI listing URL')).toHaveValue(malicious);
  await expect(page.getByLabel('Copart or IAAI listing URL')).toHaveAttribute('aria-invalid', 'true');
});

test('archive is historical and mobile content stays within viewport', async ({ page }, testInfo) => {
  if (testInfo.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
  await resolve(page, 'https://copart.com/lot/70000002');
  await expect(page.getByText('ARCHIVED', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Historical auction record. This does not show a current listing or current bid.', { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('a later failed lookup clears the previous vehicle', async ({ page }) => {
  await resolve(page, 'https://copart.com/lot/51374586');
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
  await resolve(page, 'https://copart.com/lot/99999999');
  await expect(page.getByRole('heading', { name: 'No fixture record found' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '2021 Toyota Camry SE', exact: true })).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Record provenance' })).toHaveCount(0);
});
