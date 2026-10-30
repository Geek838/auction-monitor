import { expect, test } from '@playwright/test';

// Consumer-boundary double only; this does not exercise an external provider.
const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
if (mode === 'fixture') {
  test('an unverified external source is described honestly throughout resolution', async ({ page }) => {
    const context = { id: 'apibara', name: 'Apibara', mode: 'EXTERNAL', authorization: 'UNVERIFIED', enabled: true, available: true, contract_version: '1', reasons: [] };
    await page.route('**/api/v1/health', route => route.fulfill({ json: { status: 'ok', provider: 'APIBARA', data_type: 'UNAVAILABLE', provider_context: context } }));
    await page.route('**/api/v1/auction/resolve', async route => {
      const response = await route.fetch();
      const result = await response.json();
      result.provider_context = context;
      result.provenance = { ...result.provenance, provider: 'apibara', source_name: 'Apibara', data_type: 'EXTERNAL_UNVERIFIED', realtime: false };
      result.preview_eligibility = { available: false, reason: 'No source photos supplied.' };
      await route.fulfill({ response, json: result });
    });
    await page.goto('/');
    const notice = page.getByLabel('Configured data source');
    await expect(notice).toContainText('User-declared access; not independently verified');
    await expect(notice).toContainText('EXTERNAL SOURCE');
    await expect(page.getByRole('button', { name: 'Try a matched Copart fixture' })).toHaveCount(0);
    await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill('https://www.copart.com/lot/51374586');
    await page.getByRole('button', { name: /Resolve listing/ }).click();
    const result = page.getByLabel('Listing resolution result');
    await expect(result.getByRole('heading', { name: 'Provider record matches the submitted lot' })).toBeVisible();
    await expect(result).toContainText('VIN and listing details have not been independently verified');
    await expect(result).toContainText('UNVERIFIED DATA');
    await expect(result).not.toContainText('LICENSED DATA');
    await expect(result).not.toContainText('MOCK DATA');
  });
}
