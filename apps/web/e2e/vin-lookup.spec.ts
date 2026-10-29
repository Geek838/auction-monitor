import { expect, test } from '@playwright/test';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const vin = '1HGCM82633A004352';
const anotherVin = '5YJ3E1EA7JF000001';

function decoded(requestedVin = vin) {
  return { schema_version: 'vin-decode-v1', vin: requestedVin, outcome: 'DECODED', source: 'NHTSA_VPIC', source_url: `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/${requestedVin}?format=json`, retrieved_at: new Date().toISOString(), identity_status: 'NOT_AUCTION_VERIFIED', vehicle: { year: 2003, make: 'HONDA', model: 'Accord' }, errors: [], warnings: ['Controlled manufacturer response fixture. This is not an auction match.'] };
}

if (mode === 'fixture') {
  test('manufacturer lookup is explicit and returned details apply only on a second action', async ({ page }) => {
    const requests: unknown[] = [];
    // Consumer-boundary fixture: routine browser checks never depend on a live
    // government service. Backend transport tests cover the actual route/client.
    await page.route('**/api/v1/vehicles/decode-vin', async route => {
      const input = route.request().postDataJSON(); requests.push(input);
      await route.fulfill({ json: decoded(input.vin) });
    });
    await page.goto('/review');
    await page.getByLabel('Make (optional)', { exact: true }).fill('Existing user entry');
    await page.getByLabel('VIN (optional)', { exact: true }).fill(vin.toLowerCase());
    expect(requests).toEqual([]);
    await page.getByRole('button', { name: 'Look up manufacturer details', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Manufacturer details returned', exact: true })).toBeVisible();
    expect(requests).toEqual([{ vin }]);
    await expect(page.getByLabel('Make (optional)', { exact: true })).toHaveValue('Existing user entry');
    await page.getByRole('button', { name: 'Use manufacturer details', exact: true }).click();
    await expect(page.getByLabel('Make (optional)', { exact: true })).toHaveValue('HONDA');
    await expect(page.getByLabel('Model (optional)', { exact: true })).toHaveValue('Accord');
    await expect(page.getByLabel('Year (optional)', { exact: true })).toHaveValue('2003');
    await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill('https://copart.com/lot/00012345');
    const reviewResponse = page.waitForResponse(response => response.url().endsWith('/api/v1/manual-reviews') && response.request().method() === 'POST');
    await page.getByRole('button', { name: 'Build my review', exact: true }).click();
    const report = await (await reviewResponse).json();
    expect(report.verification_status).toBe('UNVERIFIED');
    expect(report.source_kind).toBe('USER_SUPPLIED_UNVERIFIED');
    expect(report.vehicle).toEqual({ vin, year: 2003, make: 'HONDA', model: 'Accord' });
    await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toBeVisible();
  });

  test('manufacturer results for an edited VIN are discarded before they can overwrite the current facts', async ({ page }) => {
    let release!: () => void; let intercepted!: () => void;
    const held = new Promise<void>(done => { release = done; });
    const ready = new Promise<void>(done => { intercepted = done; });
    await page.route('**/api/v1/vehicles/decode-vin', async route => {
      const input = route.request().postDataJSON(); intercepted(); await held;
      try { await route.fulfill({ json: decoded(input.vin) }); } catch { /* Old lookup was aborted when VIN changed. */ }
    });
    await page.goto('/review');
    await page.getByLabel('VIN (optional)', { exact: true }).fill(vin);
    await page.getByRole('button', { name: 'Look up manufacturer details', exact: true }).click();
    await ready;
    await page.getByLabel('VIN (optional)', { exact: true }).fill(anotherVin);
    release();
    await expect(page.getByRole('heading', { name: 'Manufacturer details returned', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Use manufacturer details', exact: true })).toHaveCount(0);
    await expect(page.getByLabel('Make (optional)', { exact: true })).toHaveValue('');
    await expect(page.getByLabel('VIN (optional)', { exact: true })).toHaveValue(anotherVin);
  });
}
