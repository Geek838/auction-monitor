import { expect, test, type Page, type Route } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
const copart = 'https://copart.com/lot/00012345';
const model = 'test-vision:latest';
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAFAAAAA8CAIAAAB+RarbAAAALnRFWHRQcml2YXRlUmVzZWFyY2hOb3RlAE5FVkVSX1VQTE9BRF9USElTX01FVEFEQVRBBPm1kgAAAGRJREFUeJztz0ERwCAAwDDAIx9E4P85F9tdlyho575n/Mn6OuBthusM1xmuM1xnuM5wneE6w3WG6wzXGa4zXGe4znCd4TrDdYbrDNcZrjNcZ7jOcJ3hOsN1husM1xmuM1xnuO4BWc0BlUPWoXEAAAAASUVORK5CYII=', 'base64');
const systems = ['Structural integrity', 'SRS and airbags', 'ADAS', 'Cooling', 'Suspension', 'Mechanical condition'];
const hostileText = '<img src=x onerror="window.__localInjected=true">';

async function selectPhoto(page: Page) {
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill(copart);
  await page.getByLabel('Photos for local analysis', { exact: true }).setInputFiles({ name: 'private-local-image.png', mimeType: 'image/png', buffer: png });
  await expect(page.getByRole('img', { name: 'Image 1 — selected local evidence', exact: true })).toBeVisible();
}

async function readyConsumer(page: Page) {
  // This status is a consumer-boundary fixture. No installed model is implied.
  await page.route('**/api/v1/local-vision/status', route => route.fulfill({ json: { enabled: true, available: true, reason_code: 'READY', message: 'Controlled UI test status; not real runtime availability.', model } }));
  await page.goto('/local-inspection');
  await expect(page.getByText('Local vision model ready', { exact: true })).toBeVisible();
}

async function controlledReport(route: Route) {
  // Preserve the real API's parsed reference, replacing only its disabled report
  // for explicit consumer behavior coverage. Backend transport tests cover pixels.
  const response = await route.fetch();
  expect(response.ok()).toBe(true);
  const blocked = await response.json();
  const input = route.request().postDataJSON();
  const images = input.images.map((image: { image_id: string; label: string; sha256: string }) => ({ image_id: image.image_id, label: image.label, source_sha256: image.sha256, inference_sha256: image.sha256, width: 80, height: 60 }));
  const report = {
    ...blocked, outcome: 'COMPLETED', reason_code: 'CONTROLLED_CONSUMER_FIXTURE', reasons: ['This browser response is a test double, not real model output.'],
    images, findings: [{ classification: 'OBSERVED', component: 'Engineering pattern', region: 'Test square', description: hostileText, rationale: 'Consumer escaping test only.', confirmation: 'Requires real evidence review.', image_ids: [images[0].image_id], confidence: null }],
    checks: systems.map(system => ({ system, status: 'UNKNOWN', recommendation: 'Qualified physical review is still needed.' })),
    limitations: ['Controlled browser fixture; no model accuracy or vehicle condition is established.'],
    provenance: { mode: 'LOCAL_MODEL', model, model_digest: 'a'.repeat(64), adapter_version: 'ollama-local-v1', prompt_version: 'visible-evidence-v1', schema_version: 'local-inspection-v1', image_digests: Object.fromEntries(images.map((image: { image_id: string; inference_sha256: string }) => [image.image_id, image.inference_sha256])), generated_at: new Date().toISOString(), elapsed_ms: 1 },
  };
  return { response, input, report };
}

test.beforeEach(async ({ request }) => {
  expect((await (await request.get('/api/v1/health')).json()).provider_context.id).toBe(mode);
});

test('default-disabled local inference never sends selected pixels or invents findings', async ({ page }) => {
  const inferenceRequests: string[] = [];
  page.on('request', request => { if (request.url().endsWith('/api/v1/local-inspections')) inferenceRequests.push(request.url()); });
  await page.goto('/local-inspection');
  await expect(page.getByText('Local vision is not ready', { exact: true })).toBeVisible();
  await selectPhoto(page);
  await page.getByLabel('I have permission to process these photos with the local model.', { exact: true }).check();
  await expect(page.getByRole('button', { name: 'Analyze with local model', exact: true })).toBeDisabled();
  await expect(page.getByRole('heading', { name: 'Local model review', exact: true })).toHaveCount(0);
  expect(inferenceRequests).toEqual([]);
  await page.getByRole('button', { name: 'Clear local analysis', exact: true }).click();
  await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue('');
  await expect(page.getByRole('img')).toHaveCount(0);
});

if (mode === 'fixture') {
  test('explicit local-analysis action transmits prepared pixels and renders unreviewed data safely', async ({ page }, info) => {
    if (info.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
    await readyConsumer(page);
    await selectPhoto(page);
    const posts: unknown[] = [];
    let returned: unknown;
    await page.route('**/api/v1/local-inspections', async route => {
      const { response, input, report } = await controlledReport(route);
      posts.push(input); returned = report;
      const bytes = Buffer.from(input.images[0].content_base64, 'base64');
      expect(bytes.subarray(0, 2)).toEqual(Buffer.from([255, 216]));
      expect(bytes.includes(Buffer.from('NEVER_UPLOAD_THIS_METADATA'))).toBe(false);
      expect(createHash('sha256').update(bytes).digest('hex')).toBe(input.images[0].sha256);
      expect(JSON.stringify(input)).not.toContain('private-local-image');
      expect(input.local_processing_permission).toBe(true);
      await route.fulfill({ response, json: report });
    });
    await expect(page.getByRole('button', { name: 'Analyze with local model', exact: true })).toBeDisabled();
    expect(posts).toEqual([]);
    await page.getByLabel('I have permission to process these photos with the local model.', { exact: true }).check();
    await page.getByRole('button', { name: 'Analyze with local model', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Local model review', exact: true })).toBeVisible();
    expect(posts).toHaveLength(1);
    await expect(page.getByText('EXPERIMENTAL / UNREVIEWED · IDENTITY UNVERIFIED', { exact: true })).toBeVisible();
    await expect(page.getByText(hostileText, { exact: true })).toBeVisible();
    await expect(page.locator('img[src="x"]')).toHaveCount(0);
    expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__localInjected)).toBeUndefined();
    await expect(page.getByRole('heading', { name: 'Physical checks still needed', exact: true })).toBeVisible();
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download local analysis JSON', exact: true }).click();
    const file = await (await downloadPromise).path();
    expect(JSON.parse(await readFile(file!, 'utf8'))).toEqual(returned);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: path.resolve(__dirname, `../../../.cache/qa/v1/local-${info.project.name}.png`), fullPage: true });
  });

  test('a model response bound to different photo bytes cannot attach to the review', async ({ page }) => {
    await readyConsumer(page); await selectPhoto(page);
    await page.getByLabel('I have permission to process these photos with the local model.', { exact: true }).check();
    await page.route('**/api/v1/local-inspections', async route => {
      const { response, report } = await controlledReport(route);
      report.images[0].source_sha256 = '0'.repeat(64);
      await route.fulfill({ response, json: report });
    });
    await page.getByRole('button', { name: 'Analyze with local model', exact: true }).click();
    await expect(page.getByRole('main').getByRole('alert')).toContainText('The response could not be bound to your selected photos.');
    await expect(page.getByRole('heading', { name: 'Local model review', exact: true })).toHaveCount(0);
  });

  test('an old local-model result is discarded when the reference changes', async ({ page }) => {
    await readyConsumer(page); await selectPhoto(page);
    await page.getByLabel('I have permission to process these photos with the local model.', { exact: true }).check();
    let release!: () => void; let intercepted!: () => void;
    const held = new Promise<void>(done => { release = done; });
    const ready = new Promise<void>(done => { intercepted = done; });
    await page.route('**/api/v1/local-inspections', async route => {
      const { response, report } = await controlledReport(route); intercepted(); await held;
      try { await route.fulfill({ response, json: report }); } catch { /* Previous fetch is aborted. */ }
    });
    await page.getByRole('button', { name: 'Analyze with local model', exact: true }).click();
    await ready;
    await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill('https://iaai.com/VehicleDetail/41000001~US');
    release();
    await expect(page.getByRole('heading', { name: 'Local model review', exact: true })).toHaveCount(0);
  });
}
