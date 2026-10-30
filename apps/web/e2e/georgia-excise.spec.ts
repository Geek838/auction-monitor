import { expect, test, type Page } from '@playwright/test';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const endpoint = '/api/v1/georgia/excise';
async function fillSupported(page: Page, production = '2021') {
  await page.getByLabel('Declaration registration year', { exact: true }).selectOption('2026');
  await page.getByLabel('Planned declaration registration date', { exact: true }).fill('2026-12-31');
  await page.getByLabel('Production year', { exact: true }).fill(production);
  await page.getByRole('checkbox', { name: 'I have checked the actual production year against vehicle evidence, separately from a VIN decoder’s model year.', exact: true }).check();
  await page.getByLabel('Engine displacement (cm³)', { exact: true }).fill('2000');
  await page.getByLabel('Commodity classification', { exact: true }).selectOption('8703');
  await page.getByLabel('Vehicle category', { exact: true }).selectOption('ORDINARY_PASSENGER');
  await page.getByLabel('Powertrain', { exact: true }).selectOption('PETROL');
  await page.getByLabel('Steering configuration', { exact: true }).selectOption('ORIGINAL_LEFT');
  await page.getByLabel('Import procedure', { exact: true }).selectOption('GEORGIA_FREE_CIRCULATION');
  await page.getByLabel('Any exemption claimed?', { exact: true }).selectOption('false');
  await page.getByLabel('Any special vehicle or taxpayer status?', { exact: true }).selectOption('false');
}
async function calculate(page: Page) {
  const received = page.waitForResponse(response => response.url().endsWith(endpoint) && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Calculate excise component', exact: true }).click();
  return (await received).json();
}
if (mode === 'fixture') {
  test.beforeEach(async ({ page }) => { await page.goto('/georgia-excise'); });

  test('eligible declarations calculate only excise and preserve unknown clearance remainder', async ({ page }) => {
    await fillSupported(page);
    const result = await calculate(page);
    expect(result.outcome).toBe('CALCULATED_COMPONENT');
    expect(result.source_kind).toBe('STATUTORY_COMPONENT_USER_DECLARED_FACTS');
    expect(result.excise_amount).toBe('3000.00');
    expect(result.other_clearance_components).toBe('NOT_CALCULATED');
    expect(result.request.planned_declaration_date).toBe('2026-12-31');
    expect(result.request.production_year_confirmed).toBe(true);
    const region = page.getByRole('region', { name: 'Your excise component', exact: true });
    await expect(region.getByRole('heading', { name: 'Excise component estimate', exact: true })).toBeVisible();
    await expect(region.getByText('3,000.00 GEL', { exact: true })).toBeVisible();
    await expect(region.getByRole('heading', { name: 'Full clearance total remains unknown', exact: true })).toBeVisible();
    await expect(region.getByRole('link', { name: /Official Tax Code/ })).toHaveAttribute('href', /https:\/\/matsne\.gov\.ge\//);
    await expect(page.getByText('A VIN decoder’s model year is not automatically the production year.', { exact: false })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.getByLabel('Production year', { exact: true }).fill('2019');
    await expect(region).toHaveCount(0);
    await expect(page.getByRole('checkbox', { name: /I have checked the actual production year/ })).not.toBeChecked();
    const unconfirmedEdit = await calculate(page);
    expect(unconfirmedEdit.outcome).toBe('WITHHELD');
    expect(unconfirmedEdit.issues.some((issue: { code: string }) => issue.code === 'PRODUCTION_YEAR_NOT_CONFIRMED')).toBe(true);
    await page.getByRole('checkbox', { name: /I have checked the actual production year/ }).check();
    const older = await calculate(page);
    expect(older.excise_amount).toBe('9000.00');
    await expect(region.getByText('9,000.00 GEL', { exact: true })).toBeVisible();
  });

  test('eligible hybrid calculates while unknown, unsupported hybrid and re-export withhold', async ({ page }) => {
    const unknown = await calculate(page);
    expect(unknown.outcome).toBe('WITHHELD'); expect(unknown.excise_amount).toBeNull();
    await expect(page.getByRole('heading', { name: 'Excise amount withheld', exact: true })).toBeVisible();
    await fillSupported(page);
    await page.getByLabel('Powertrain', { exact: true }).selectOption('HYBRID');
    const hybrid = await calculate(page);
    expect(hybrid.outcome).toBe('CALCULATED_COMPONENT'); expect(hybrid.excise_amount).toBe('1200.00');
    await page.getByLabel('Steering configuration', { exact: true }).selectOption('RIGHT');
    const unsupportedHybrid = await calculate(page);
    expect(unsupportedHybrid.outcome).toBe('WITHHELD'); expect(unsupportedHybrid.excise_amount).toBeNull();
    await page.getByLabel('Steering configuration', { exact: true }).selectOption('ORIGINAL_LEFT');
    await page.getByLabel('Powertrain', { exact: true }).selectOption('DIESEL');
    await page.getByLabel('Import procedure', { exact: true }).selectOption('RE_EXPORT');
    const reExport = await calculate(page);
    expect(reExport.outcome).toBe('WITHHELD'); expect(reExport.excise_amount).toBeNull();
    await expect(page.getByText('0.00 GEL', { exact: true })).toHaveCount(0);
  });

  test('historical dates are withheld and litres are rejected before calculation', async ({ page }) => {
    await fillSupported(page);
    await page.getByLabel('Planned declaration registration date', { exact: true }).fill('2026-03-01');
    const result = await calculate(page);
    expect(result.outcome).toBe('WITHHELD'); expect(result.excise_amount).toBeNull();
    await page.getByLabel('Engine displacement (cm³)', { exact: true }).fill('2.0');
    await page.getByRole('button', { name: 'Calculate excise component', exact: true }).click();
    await expect(page.getByRole('region', { name: 'Georgia excise component calculator', exact: true }).getByRole('alert')).toContainText('Do not enter litres such as 2.0');
    await expect(page.getByRole('region', { name: 'Your excise component', exact: true })).toHaveCount(0);
  });

  test('edited inputs discard a late response and mismatched responses are rejected', async ({ page }) => {
    await fillSupported(page);
    let release!: () => void; let intercepted!: () => void;
    const held = new Promise<void>(done => { release = done; }); const ready = new Promise<void>(done => { intercepted = done; });
    await page.route(`**${endpoint}`, async route => {
      const response = await route.fetch(); intercepted(); await held;
      try { await route.fulfill({ response }); } catch { /* Edit aborts prior request. */ }
    });
    await page.getByRole('button', { name: 'Calculate excise component', exact: true }).click(); await ready;
    await page.getByLabel('Production year', { exact: true }).fill('2019'); release();
    await expect(page.getByRole('region', { name: 'Your excise component', exact: true })).toHaveCount(0);
    await page.unroute(`**${endpoint}`);
    await page.route(`**${endpoint}`, async route => {
      const response = await route.fetch(); const report = await response.json(); report.request.engine_cc = 1500;
      await route.fulfill({ response, json: report });
    });
    await page.getByRole('button', { name: 'Calculate excise component', exact: true }).click();
    await expect(page.getByRole('region', { name: 'Georgia excise component calculator', exact: true }).getByRole('alert')).toContainText('could not be validated against your inputs');
    await expect(page.getByRole('region', { name: 'Your excise component', exact: true })).toHaveCount(0);
  });

  test('a typed production year without separate evidence confirmation stays withheld', async ({ page }) => {
    await expect(page.getByRole('checkbox', { name: /I have checked the actual production year/ })).not.toBeChecked();
    await fillSupported(page);
    await page.getByRole('checkbox', { name: /I have checked the actual production year/ }).uncheck();
    const report = await calculate(page);
    expect(report.outcome).toBe('WITHHELD'); expect(report.excise_amount).toBeNull();
    expect(report.issues.some((issue: { code: string }) => issue.code === 'PRODUCTION_YEAR_NOT_CONFIRMED')).toBe(true);
    await expect(page.getByRole('heading', { name: 'Excise amount withheld', exact: true })).toBeVisible();
  });

}
