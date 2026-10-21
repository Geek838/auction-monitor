import { expect, test, type Page } from '@playwright/test';
import path from 'node:path';
import { mkdir } from 'node:fs/promises';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';

async function resolve(page: Page, url: string) {
  await page.getByLabel('Copart or IAAI listing URL').fill(url);
  await page.getByRole('button', { name: 'Resolve listing', exact: true }).click();
}

test.beforeEach(async ({ page, request }) => {
  // Check the real backend, so a reused/wrong-mode server cannot give false confidence.
  const response = await request.get('/api/v1/health');
  expect(response.ok()).toBe(true);
  const health = await response.json();
  expect(health.provider_context.mode).toBe(mode === 'simulation' ? 'SIMULATED' : 'EXTERNAL');
  expect(health.provider_context.available).toBe(mode === 'simulation');
  await page.goto('/');
});

if (mode === 'simulation') {
  test('offline simulation is visibly synthetic and never presented as a licensed result', async ({ page }, testInfo) => {
    if (testInfo.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
    await expect(page.getByText('SIMULATED DATA', { exact: true })).toBeVisible();
    await expect(page.getByText('MOCK DATA', { exact: true })).toHaveCount(0);
    await resolve(page, 'https://copart.com/lot/51374586');
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
    await expect(page.getByText('SIMULATED', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('LICENSED', { exact: true })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Source freshness' })).toBeVisible();
    await expect(page.getByText('Stale snapshot', { exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    const directory = path.resolve(__dirname, '../../../.cache/qa/sprint2');
    await mkdir(directory, { recursive: true });
    await page.screenshot({ path: path.join(directory, `simulation-${testInfo.project.name}.png`), fullPage: true });
  });

  test('missing source observation stays unknown rather than using recent retrieval', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/00012345');
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
    await expect(page.getByText('Freshness unknown', { exact: true })).toBeVisible();
    await expect(page.getByRole('term').filter({ hasText: /^Source observed at$/ }).locator('..').getByRole('definition')).toHaveText('Not supplied');
    await expect(page.getByText('Fresh snapshot', { exact: true })).toHaveCount(0);
  });

  for (const scenario of [
    { url: 'https://copart.com/lot/70000001', heading: 'We could not confirm one exact match' },
    { url: 'https://copart.com/lot/99999999', heading: 'No simulation record found' },
    { url: 'https://iaai.com/VehicleDetail/45371195~US', heading: 'The IAAI stock number is not confirmed' },
    { url: 'https://copart.com/lot/70000003', heading: 'The data provider is unavailable' },
    { url: 'https://copart.com/lot/70000004', heading: 'Authorized data access is not available' },
  ]) {
    test(`simulation outcome: ${scenario.heading}`, async ({ page }) => {
      await resolve(page, scenario.url);
      await expect(page.getByRole('heading', { name: scenario.heading, exact: true })).toBeVisible();
      await expect(page.getByText('SIMULATED', { exact: true }).first()).toBeVisible();
      await expect(page.getByText('MOCK', { exact: true })).toHaveCount(0);
      await expect(page.getByText('LICENSED', { exact: true })).toHaveCount(0);
      await expect(page.getByRole('heading', { name: 'Record provenance' })).toHaveCount(0);
    });
  }

  test('an archived simulation remains historical despite provider availability', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/70000002');
    await expect(page.getByText('ARCHIVED', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Historical auction record. This does not show a current listing or current bid.', { exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Source freshness' })).toBeVisible();
  });

  test('a failed simulated lookup does not silently replace it with a matched fixture', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/51374586');
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
    await resolve(page, 'https://copart.com/lot/70000003');
    await expect(page.getByRole('heading', { name: 'The data provider is unavailable' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '2021 Toyota Camry SE', exact: true })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Record provenance' })).toHaveCount(0);
    await expect(page.getByText('MOCK', { exact: true })).toHaveCount(0);
  });
} else if (mode === 'bidcars') {
  test('disabled external provider is unavailable from initial health through resolution', async ({ page }, testInfo) => {
    if (testInfo.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
    await expect(page.getByText('ACCESS UNAVAILABLE', { exact: true })).toBeVisible();
    await expect(page.getByText('MOCK DATA', { exact: true })).toHaveCount(0);
    await expect(page.getByText('SIMULATED DATA', { exact: true })).toHaveCount(0);
    await resolve(page, 'https://copart.com/lot/51374586');
    await expect(page.getByRole('heading', { name: 'Authorized data access is not available' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toHaveCount(0);
    await expect(page.getByText('LICENSED', { exact: true })).toHaveCount(0);
    await expect(page.getByText('MOCK', { exact: true })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Record provenance' })).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    const directory = path.resolve(__dirname, '../../../.cache/qa/sprint2');
    await mkdir(directory, { recursive: true });
    await page.screenshot({ path: path.join(directory, `denied-${testInfo.project.name}.png`), fullPage: true });
  });

  test('disabled provider cannot bypass URL validation or convert denial to an empty lookup', async ({ page }) => {
    await resolve(page, 'https://copart.com.evil.example/lot/51374586');
    await expect(page.getByRole('heading', { name: 'This link cannot be resolved' })).toBeVisible();
    await resolve(page, 'https://iaai.com/VehicleDetail/41000001~US');
    await expect(page.getByRole('heading', { name: 'Authorized data access is not available' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'No provider record found' })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toHaveCount(0);
  });
}
