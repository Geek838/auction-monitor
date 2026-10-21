import { expect, test, type Page } from '@playwright/test';
import path from 'node:path';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const copart = 'https://copart.com/lot/51374586';
const iaai = 'https://iaai.com/VehicleDetail/41000001~US';
const previewLabel = 'MOCK INSPECTION PREVIEW — hand-authored example, no AI analysis';

async function resolve(page: Page, url = copart) {
  await page.getByLabel('Copart or IAAI listing URL').fill(url);
  await page.getByRole('button', { name: 'Resolve listing', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
}

async function openPreview(page: Page) {
  const response = page.waitForResponse(response => response.url().endsWith('/api/v1/inspections') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Open MOCK inspection preview', exact: true }).click();
  const report = await (await response).json();
  await expect(page.getByRole('region', { name: 'Mock inspection preview', exact: true }).getByText(previewLabel, { exact: true })).toBeVisible();
  return report;
}

test.beforeEach(async ({ page, request }) => {
  const response = await request.get('/api/v1/health');
  expect(response.ok()).toBe(true);
  expect((await response.json()).provider_context.id).toBe(mode);
  await page.goto('/');
});

if (mode === 'fixture' || mode === 'simulation') {
  test('Copart preview links real raster evidence to observed, suspected and unknown groups', async ({ page }, testInfo) => {
    if (testInfo.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
    await resolve(page);
    const report = await openPreview(page);
    expect(report.outcome).toBe('COMPLETED');
    const region = page.getByRole('region', { name: 'Mock inspection preview', exact: true });
    await expect(region.getByRole('heading', { name: 'Authored image gallery', exact: true })).toBeVisible();
    for (const heading of ['Observed in the illustration', 'Suspected — needs confirmation', 'Unknown — physical checks needed', 'Physical-inspection checklist', 'Coverage and limitations']) {
      await expect(region.getByRole('heading', { name: heading, exact: true })).toBeVisible();
    }
    const first = report.assets[0];
    const image = region.getByRole('img', { name: first.alt_text, exact: true });
    await expect(image).toBeVisible();
    await expect.poll(() => image.evaluate(node => (node as HTMLImageElement).naturalWidth)).toBe(first.width);
    const second = report.assets[1];
    const selectSecond = region.getByRole('button', { name: `Show ${second.view_label} illustration`, exact: true });
    await selectSecond.focus();
    await selectSecond.press('Enter');
    await expect(selectSecond).toHaveAttribute('aria-pressed', 'true');
    await expect(region.getByRole('img', { name: second.alt_text, exact: true })).toBeVisible();
    const observed = report.findings.find((item: { classification: string; image_ids: string[] }) => item.classification === 'OBSERVED' && item.image_ids.includes(first.asset_id));
    const article = region.getByText(observed.description, { exact: true }).locator('..');
    await article.getByRole('button', { name: `View image for ${observed.component}`, exact: true }).click();
    await expect(region.getByRole('button', { name: `Show ${first.view_label} illustration`, exact: true })).toHaveAttribute('aria-pressed', 'true');
    await expect(article.getByText('Related to the selected illustration', { exact: true })).toBeVisible();
    await region.getByText('Preview provenance', { exact: true }).click();
    await expect(region.getByText('Not applicable — deterministic mock; no AI provider called.', { exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: path.resolve(__dirname, `../../../.cache/qa/sprint3/${mode}-${testInfo.project.name}.png`), fullPage: true });
    if (testInfo.project.name === 'mobile-chromium' && mode === 'fixture') {
      await region.getByRole('heading', { name: 'Authored image gallery', exact: true }).scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.resolve(__dirname, '../../../.cache/qa/sprint3/gallery-mobile.png') });
    }
  });

  test('IAAI preview stays bound to its page, stock and sale event', async ({ page }) => {
    await resolve(page, iaai);
    const report = await openPreview(page);
    expect(report.outcome).toBe('COMPLETED');
    expect(report.target.reference.page_id).toBe('41000001');
    expect(report.target.reference.country).toBe('US');
    expect(report.target.identity.lot_or_stock_number).toBe('45371195');
    expect(report.target.record_id).not.toBe(report.target.event_id);
    await expect(page.getByRole('region', { name: 'Mock inspection preview', exact: true }).getByRole('img').first()).toBeVisible();
  });

  test('partial archived preview retains historical context and explains excluded evidence', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/70000002');
    const report = await openPreview(page);
    expect(report.outcome).toBe('PARTIAL');
    await expect(page.getByText('ARCHIVED', { exact: true }).first()).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Partial mock preview', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Excluded evidence', exact: true })).toBeVisible();
    const availableIds = report.assets.map((asset: { asset_id: string }) => asset.asset_id);
    expect(report.exclusions.every((item: { asset_id: string }) => !availableIds.includes(item.asset_id))).toBe(true);
  });

  test('a matched record without authored images has no usable preview action', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/00012345');
    const availability = page.getByRole('region', { name: 'Inspection preview availability', exact: true });
    await expect(availability).toBeVisible();
    await expect(availability.getByText('A matched listing does not establish photo rights or an inspected vehicle condition.', { exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Open MOCK inspection preview', exact: true })).toHaveCount(0);
  });

  test('engine failure yields no gallery or invented findings', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/70000007');
    const report = await openPreview(page);
    expect(report.outcome).toBe('FAILED');
    await expect(page.getByRole('heading', { name: 'Preview could not be completed', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Authored image gallery', exact: true })).toHaveCount(0);
    await expect(page.getByText('No inspection findings have been supplied.', { exact: true })).toBeVisible();
  });

  test('an illustration without a visible mark still reports physical-inspection unknowns', async ({ page }) => {
    await resolve(page, 'https://copart.com/lot/70000008');
    const report = await openPreview(page);
    expect(report.outcome).toBe('COMPLETED');
    expect(report.findings.length).toBeGreaterThan(0);
    expect(report.findings.every((item: { classification: string }) => item.classification === 'UNKNOWN')).toBe(true);
    await expect(page.getByRole('heading', { name: 'Unknown — physical checks needed', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Physical-inspection checklist', exact: true })).toBeVisible();
    await expect(page.getByText('No seeded finding in this category. This is not evidence of an undamaged vehicle.', { exact: true }).first()).toBeVisible();
  });

  test('editing the URL removes the previous preview before another lookup', async ({ page }) => {
    await resolve(page);
    await openPreview(page);
    await expect(page.getByRole('heading', { name: 'Authored image gallery', exact: true })).toBeVisible();
    await page.getByLabel('Copart or IAAI listing URL').fill(iaai);
    await expect(page.getByRole('region', { name: 'Mock inspection preview', exact: true })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toHaveCount(0);
  });
}

if (mode === 'fixture') {
  test('untrusted caption and finding text render as text without executing markup', async ({ page }) => {
    await resolve(page);
    const caption = '<img src=x onerror="window.__inspectionInjected=true">';
    await page.route('**/api/v1/inspections', async route => {
      const response = await route.fetch();
      const report = await response.json();
      // Controlled consumer-boundary fixture; the real backend still creates the report.
      report.assets[0].title = caption;
      report.findings[0].description = caption;
      await route.fulfill({ response, json: report });
    });
    await openPreview(page);
    const region = page.getByRole('region', { name: 'Mock inspection preview', exact: true });
    await expect(region.getByText(caption, { exact: true }).first()).toBeVisible();
    await expect(page.locator('img[src="x"]')).toHaveCount(0);
    expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__inspectionInjected)).toBeUndefined();
  });

  test('an actual target-precondition rejection asks for fresh resolution', async ({ page }) => {
    await resolve(page);
    await page.route('**/api/v1/inspections', route => {
      const input = route.request().postDataJSON();
      return route.continue({ postData: JSON.stringify({ ...input, expected_snapshot_fingerprint: 'f'.repeat(64) }) });
    });
    const report = await openPreview(page);
    expect(report.outcome).toBe('BLOCKED');
    expect(report.reason_code).toBe('TARGET_CHANGED');
    await expect(page.getByRole('heading', { name: 'Listing changed — resolve it again', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Authored image gallery', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Retry MOCK inspection preview', exact: true })).toHaveCount(0);
  });

  test('failed image delivery withholds its observed and suspected finding text', async ({ page }) => {
    await resolve(page);
    await page.route('**/api/v1/inspection-assets/front-illustration-v1?**', route => route.abort());
    const report = await openPreview(page);
    await expect(page.getByText('Illustration unavailable', { exact: true })).toBeVisible();
    const affected = report.findings.filter((item: { classification: string; image_ids: string[] }) => item.classification !== 'UNKNOWN' && item.image_ids.includes('front-illustration-v1'));
    expect(affected.length).toBeGreaterThan(0);
    for (const item of affected) await expect(page.getByText(item.description, { exact: true })).toHaveCount(0);
    await expect(page.getByText('Evidence image unavailable — this finding is withheld.', { exact: true }).first()).toBeVisible();
  });

  test('a delayed response for the previous listing never appears under a new listing', async ({ page }) => {
    await resolve(page);
    let release!: () => void;
    let intercepted!: () => void;
    const held = new Promise<void>(done => { release = done; });
    const ready = new Promise<void>(done => { intercepted = done; });
    await page.route('**/api/v1/inspections', async route => {
      const actual = await route.fetch();
      intercepted();
      await held;
      try { await route.fulfill({ response: actual }); } catch { /* Abort on old component unmount is expected. */ }
    });
    await page.getByRole('button', { name: 'Open MOCK inspection preview', exact: true }).click();
    await ready;
    await page.getByLabel('Copart or IAAI listing URL').fill(iaai);
    release();
    await page.unroute('**/api/v1/inspections');
    await page.getByRole('button', { name: 'Resolve listing', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Exact auction identity matched' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Authored image gallery', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Open MOCK inspection preview', exact: true })).toBeVisible();
  });
}

if (mode === 'bidcars') {
  test('disabled external access cannot obtain an inspection through UI or direct API', async ({ page, request }) => {
    await page.getByLabel('Copart or IAAI listing URL').fill(copart);
    await page.getByRole('button', { name: 'Resolve listing', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Authorized data access is not available', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Open MOCK inspection preview', exact: true })).toHaveCount(0);
    const response = await request.post('/api/v1/inspections', { data: { url: copart, expected_snapshot_fingerprint: 'a'.repeat(64) } });
    expect(response.ok()).toBe(true);
    const report = await response.json();
    expect(report.outcome).toBe('BLOCKED');
    expect(report.resolver_status).toBe('NOT_AUTHORIZED');
    expect(report.assets).toEqual([]);
    expect(report.findings).toEqual([]);
  });
}
