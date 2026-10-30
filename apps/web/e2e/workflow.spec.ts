import { expect, test } from '@playwright/test';

const source = 'https://www.iaai.com:443/VehicleDetail/00041000001~US/?utm_source=private#fragment';
const canonical = 'https://www.iaai.com/VehicleDetail/00041000001~US';
const steps = (page: import('@playwright/test').Page) => page.getByRole('navigation', { name: 'Buyer workflow steps', exact: true });

test('the buyer follows one unverified reference without transferring private work or starting analysis', async ({ page }) => {
  const sensitiveRequests: string[] = [];
  page.on('request', request => { if (request.method() === 'POST' || request.url().includes('decode-vin')) sensitiveRequests.push(request.url()); });
  await page.goto('/');
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill(source);
  await steps(page).getByRole('link', { name: 'Your evidence', exact: true }).click();
  expect(new URL(page.url()).searchParams.get('reference')).toBe(canonical);
  await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue(canonical);
  await page.getByLabel('Review notes (optional)', { exact: true }).fill('PRIVATE NOTES NEVER TRANSFER');
  await steps(page).getByRole('link', { name: 'Local photo analysis', exact: true }).click();
  await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue(canonical);
  await expect(steps(page).getByRole('link', { name: 'Local photo analysis', exact: true })).toHaveAttribute('aria-current', 'step');
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill('https://m.copart.com/lot/00000123?tracking=discard');
  await steps(page).getByRole('link', { name: 'Budget & bid planning', exact: true }).click();
  await expect(page.locator('.journey-reference')).toContainText('https://m.copart.com/lot/00000123');
  await expect(page.locator('.journey-reference')).toContainText('unverified');
  expect(await page.locator('body').textContent()).not.toContain('PRIVATE NOTES NEVER TRANSFER');
  expect(new URL(page.url()).searchParams.size).toBe(1);
  await expect(page.getByLabel('Hammer bid (USD)', { exact: true })).toHaveValue('');
  expect(sensitiveRequests).toEqual([]);
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
});

test('unsafe, duplicate and malformed reference queries cannot prefill a tool or become navigation targets', async ({ page }) => {
  for (const reference of ['javascript:alert(1)', 'https://copart.com.evil.test/lot/123', 'https://name:secret@copart.com/lot/123', 'https://@copart.com/lot/123', 'https://copart.com/lot/%31', 'https://copart.com/path/../lot/123', 'https://127.0.0.1/lot/123', 'https://copart.com:8443/lot/123']) {
    await page.goto(`/review?${new URLSearchParams({ reference })}`);
    await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue('');
    await expect(steps(page).getByRole('link', { name: 'Budget & bid planning', exact: true })).toHaveAttribute('href', '/budget');
  }
  await page.goto('/review?reference=https%3A%2F%2Fcopart.com%2Flot%2F123&reference=https%3A%2F%2Fiaai.com%2FVehicleDetail%2F456');
  await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue('');
});

test('editing or clearing a reference immediately changes the next-step link', async ({ page }) => {
  await page.goto(`/review?${new URLSearchParams({ reference: canonical })}`);
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill('https://copart.com/lot/00999');
  await expect(steps(page).getByRole('link', { name: 'Budget & bid planning', exact: true })).toHaveAttribute('href', `/budget?${new URLSearchParams({ reference: 'https://copart.com/lot/00999' })}`);
  await page.getByRole('button', { name: 'Clear review', exact: true }).click();
  await expect(steps(page).getByRole('link', { name: 'Budget & bid planning', exact: true })).toHaveAttribute('href', '/budget');
  await steps(page).getByRole('link', { name: 'Budget & bid planning', exact: true }).click();
  await expect(page.locator('.journey-reference')).toHaveCount(0);
});


test('photo controls stay disabled until browser handlers can validate selected files', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, baseURL });
  const page = await context.newPage();
  try {
    for (const [path, label] of [['/review', 'Choose vehicle photos'], ['/local-inspection', 'Photos for local analysis']]) {
      await page.goto(path);
      await expect(page.getByLabel(label, { exact: true })).toBeDisabled();
    }
  } finally { await context.close(); }
});
