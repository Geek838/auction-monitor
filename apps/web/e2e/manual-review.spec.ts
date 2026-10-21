import { expect, test, type Page } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

// Project-generated 80x60 solid-color engineering PNG, with an ancillary text marker.
// It is not a vehicle photograph, vehicle evidence, or a damage-analysis fixture.
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAFAAAAA8CAIAAAB+RarbAAAALnRFWHRQcml2YXRlUmVzZWFyY2hOb3RlAE5FVkVSX1VQTE9BRF9USElTX01FVEFEQVRBBPm1kgAAAGRJREFUeJztz0ERwCAAwDDAIx9E4P85F9tdlyho575n/Mn6OuBthusM1xmuM1xnuM5wneE6w3WG6wzXGa4zXGe4znCd4TrDdYbrDNcZrjNcZ7jOcJ3hOsN1husM1xmuM1xnuO4BWc0BlUPWoXEAAAAASUVORK5CYII=', 'base64');
const copart = 'https://copart.com/lot/00012345';
const iaai = 'https://iaai.com:443/VehicleDetail/41000001~US';
const mode = process.env.E2E_PROVIDER_MODE ?? 'fixture';

async function addPhoto(page: Page) {
  await page.getByLabel('Choose vehicle photos', { exact: true }).setInputFiles({ name: 'private-original-name.png', mimeType: 'image/png', buffer: png });
  await expect(page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true }).first()).toBeVisible();
  await page.getByLabel('I have permission to use these photos for this local review.', { exact: true }).check();
}

async function prepare(page: Page, url = copart) {
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill(url);
  await page.getByLabel('Make (optional)', { exact: true }).fill('Engineering');
  await page.getByLabel('Model (optional)', { exact: true }).fill('Test case');
}

async function build(page: Page) {
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/v1/manual-reviews') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Build my review', exact: true }).click();
  const response = await responsePromise;
  expect(response.ok()).toBe(true);
  const request = response.request().postDataJSON();
  const report = await response.json();
  await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toBeVisible();
  return { report, request };
}

test.beforeEach(async ({ page, request }) => {
  expect((await (await request.get('/api/v1/health')).json()).provider_context.id).toBe(mode);
  await page.goto('/review');
});

test('local evidence compiles an unverified report without uploading pixels or metadata', async ({ page }, info) => {
  if (info.project.name === 'mobile-chromium') await page.setViewportSize({ width: 320, height: 800 });
  await page.goto('/');
  await page.getByRole('link', { name: 'Review your own evidence', exact: true }).click();
  await expect(page).toHaveURL(/\/review$/);
  const nonlocal: string[] = [];
  page.on('request', request => { if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(page.url()).origin) nonlocal.push(request.url()); });
  await prepare(page);
  await addPhoto(page);
  const image = page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true }).first();
  const normalized = await image.evaluate(async node => {
    const data = new Uint8Array(await (await fetch((node as HTMLImageElement).src)).arrayBuffer());
    return { content: Array.from(data), src: (node as HTMLImageElement).src };
  });
  expect(normalized.src.startsWith('blob:')).toBe(true);
  const normalizedBytes = Buffer.from(normalized.content);
  expect(normalizedBytes.includes(Buffer.from('NEVER_UPLOAD_THIS_METADATA'))).toBe(false);
  await page.getByRole('button', { name: 'Add a finding', exact: true }).click();
  await page.getByLabel('Finding 1 category', { exact: true }).selectOption('OBSERVED');
  await page.getByLabel('Finding 1 photo', { exact: true }).selectOption({ label: 'Photo 1' });
  await page.getByLabel('Finding 1 component', { exact: true }).fill('Painted test square');
  await page.getByLabel('Finding 1 description', { exact: true }).fill('I entered this test observation manually.');
  const { report, request } = await build(page);
  expect(report.source_kind).toBe('USER_SUPPLIED_UNVERIFIED');
  expect(report.canonical_claim.lot_or_stock_number).toBe('00012345');
  expect(report.findings[0].source_kind).toBe('USER_REPORTED');
  expect(report.photos[0].verification_status).toBe('CLIENT_DECLARED_NOT_SERVER_VERIFIED');
  expect(request.photos[0].sha256).toBe(createHash('sha256').update(normalizedBytes).digest('hex'));
  expect(request.photos[0].width).toBe(80);
  expect(request.photos[0].height).toBe(60);
  expect(Object.keys(request.photos[0]).sort()).toEqual(['height', 'label', 'photo_id', 'sha256', 'width']);
  const serialized = JSON.stringify(request);
  expect(serialized).not.toContain('NEVER_UPLOAD_THIS_METADATA');
  expect(serialized).not.toContain('private-original-name');
  expect(serialized).not.toContain('data:image');
  expect(serialized).not.toContain(png.toString('base64'));
  expect(report.checks).toHaveLength(6);
  expect(report.checks.every((item: { status: string }) => item.status === 'UNKNOWN')).toBe(true);
  await expect(page.getByText('USER-SUPPLIED · UNVERIFIED', { exact: true }).first()).toBeVisible();
  expect(nonlocal).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: path.resolve(__dirname, `../../../.cache/qa/sprint4/${mode}-${info.project.name}.png`), fullPage: true });
  if (info.project.name === 'mobile-chromium' && mode === 'fixture') {
    await page.getByRole('heading', { name: 'Your local evidence', exact: true }).scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.resolve(__dirname, '../../../.cache/qa/sprint4/gallery-mobile.png') });
  }
});

test('IAAI page and claimed stock stay separate, including a facts-only report', async ({ page }) => {
  await prepare(page, iaai);
  await page.getByLabel('IAAI stock number (optional)', { exact: true }).fill('00098765');
  const { report } = await build(page);
  expect(report.reference.page_id).toBe('41000001');
  expect(report.reference.country).toBe('US');
  expect(report.reference.stock_number).toBeNull();
  expect(report.canonical_claim.lot_or_stock_number).toBe('00098765');
  expect(report.canonical_claim.verification_status).toBe('UNVERIFIED');
  expect(report.findings).toEqual([]);
  expect(report.photos).toEqual([]);
});

test('JSON export is honest metadata and the print action uses the browser', async ({ page }) => {
  await prepare(page);
  const { report } = await build(page);
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download review JSON', exact: true }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.json$/);
  const file = await download.path();
  expect(file).not.toBeNull();
  expect(JSON.parse(await readFile(file!, 'utf8'))).toEqual(report);
  await page.evaluate(() => { window.print = () => { (window as unknown as Record<string, unknown>).__manualPrinted = true; }; });
  const print = page.getByRole('button', { name: 'Print review', exact: true });
  await print.focus(); await print.press('Enter');
  expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__manualPrinted)).toBe(true);
  await page.emulateMedia({ media: 'print' });
  await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Build my review', exact: true })).toBeHidden();
});

test('editing a completed review clears it before another request', async ({ page }) => {
  await prepare(page);
  await build(page);
  await page.getByLabel('Review notes (optional)', { exact: true }).fill('Changed facts need a new report.');
  await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Download review JSON', exact: true })).toHaveCount(0);
});

test('a late report cannot appear under edited evidence', async ({ page }) => {
  await prepare(page);
  let release!: () => void;
  let intercepted!: () => void;
  const held = new Promise<void>(done => { release = done; });
  const ready = new Promise<void>(done => { intercepted = done; });
  await page.route('**/api/v1/manual-reviews', async route => {
    const response = await route.fetch(); intercepted(); await held;
    try { await route.fulfill({ response }); } catch { /* Old fetch is aborted when evidence changes. */ }
  });
  await page.getByRole('button', { name: 'Build my review', exact: true }).click();
  await ready;
  await page.getByLabel('Copart or IAAI listing URL', { exact: true }).fill(iaai);
  release();
  await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Build my review', exact: true })).toBeEnabled();
});

test('invalid image bytes cannot become local evidence', async ({ page }) => {
  await page.getByLabel('Choose vehicle photos', { exact: true }).setInputFiles({ name: 'not-a-photo.png', mimeType: 'image/png', buffer: Buffer.from('not a PNG') });
  await expect(page.getByRole('main').getByRole('alert')).toContainText(/valid.*PNG|PNG or JPEG/);
  await expect(page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true })).toHaveCount(0);
});

test('user notes render hostile markup literally without executing it', async ({ page }) => {
  await prepare(page);
  const note = '<img src=x onerror="window.__manualInjected=true">';
  await page.getByLabel('Review notes (optional)', { exact: true }).fill(note);
  const { report } = await build(page);
  expect(report.notes).toBe(note);
  await expect(page.getByText(note, { exact: true }).first()).toBeVisible();
  await expect(page.locator('img[src="x"]')).toHaveCount(0);
  expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__manualInjected)).toBeUndefined();
});

test('clearing a review releases local photos and resets fields, findings and report', async ({ page }) => {
  await prepare(page);
  await addPhoto(page);
  const photoUrl = await page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true }).first().getAttribute('src');
  await page.getByLabel('Review notes (optional)', { exact: true }).fill('A private temporary note.');
  await page.getByRole('button', { name: 'Add a finding', exact: true }).click();
  await page.getByLabel('Finding 1 category', { exact: true }).selectOption('UNKNOWN');
  await page.getByLabel('Finding 1 component', { exact: true }).fill('Underside');
  await page.getByLabel('Finding 1 description', { exact: true }).fill('Not shown.');
  await build(page);
  await page.getByRole('button', { name: 'Clear review', exact: true }).click();
  await expect(page.getByLabel('Copart or IAAI listing URL', { exact: true })).toHaveValue('');
  await expect(page.getByLabel('Make (optional)', { exact: true })).toHaveValue('');
  await expect(page.getByLabel('Review notes (optional)', { exact: true })).toHaveValue('');
  await expect(page.getByLabel('Finding 1 component', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true })).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toHaveCount(0);
  expect(await page.evaluate(async url => { try { await fetch(url!); return true; } catch { return false; } }, photoUrl)).toBe(false);
});

test('forged Copart lot or IAAI page in the returned report is rejected', async ({ page }) => {
  for (const url of [copart, iaai]) {
    await page.goto('/review');
    await prepare(page, url);
    if (url === iaai) await page.getByLabel('IAAI stock number (optional)', { exact: true }).fill('00098765');
    await page.route('**/api/v1/manual-reviews', async route => {
      const response = await route.fetch();
      const report = await response.json();
      if (url === copart) report.reference.lot_number = '999';
      else report.reference.page_id = '999';
      await route.fulfill({ response, json: report });
    });
    const response = page.waitForResponse(response => response.url().endsWith('/api/v1/manual-reviews'));
    await page.getByRole('button', { name: 'Build my review', exact: true }).click();
    await response;
    await expect(page.getByRole('main').getByRole('alert')).toContainText('The review response could not be verified.');
    await expect(page.getByRole('heading', { name: 'Your evidence review', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Download review JSON', exact: true })).toHaveCount(0);
    await page.unroute('**/api/v1/manual-reviews');
  }
});


if (mode === 'fixture') {
  test('JPEG orientation is decoded and private EXIF is stripped before metadata-only submission', async ({ page }) => {
    // Generated solid-color 80x60 JPEG, EXIF orientation 6 and a private description marker.
    const jpeg = Buffer.from('/9j/4AAQSkZJRgABAQAAAQABAAD/4QBKRXhpZgAATU0AKgAAAAgAAgEOAAIAAAAbAAAAJgESAAMAAAABAAYAAAAAAABORVZFUl9VUExPQURfVEhJU19NRVRBREFUQQAA/9sAQwAIBgYHBgUIBwcHCQkICgwUDQwLCwwZEhMPFB0aHx4dGhwcICQuJyAiLCMcHCg3KSwwMTQ0NB8nOT04MjwuMzQy/9sAQwEJCQkMCwwYDQ0YMiEcITIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy/8AAEQgAPABQAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8Aw6KKKyOUKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/Z', 'base64');
    expect(jpeg.includes(Buffer.from('NEVER_UPLOAD_THIS_METADATA'))).toBe(true);
    await prepare(page);
    await page.getByLabel('Choose vehicle photos', { exact: true }).setInputFiles({ name: 'private-jpeg.jpg', mimeType: 'image/jpeg', buffer: jpeg });
    const image = page.getByRole('img', { name: 'Photo 1 — local review evidence', exact: true }).first();
    await expect(image).toBeVisible();
    const pixels = await image.evaluate(async node => Array.from(new Uint8Array(await (await fetch((node as HTMLImageElement).src)).arrayBuffer())));
    const normalized = Buffer.from(pixels);
    expect(normalized.subarray(0, 8)).toEqual(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
    expect(normalized.includes(Buffer.from('NEVER_UPLOAD_THIS_METADATA'))).toBe(false);
    await page.getByLabel('I have permission to use these photos for this local review.', { exact: true }).check();
    const { request, report } = await build(page);
    expect(request.photos[0].width).toBe(60);
    expect(request.photos[0].height).toBe(80);
    expect(request.photos[0].sha256).toBe(createHash('sha256').update(normalized).digest('hex'));
    expect(report.photos[0].verification_status).toBe('CLIENT_DECLARED_NOT_SERVER_VERIFIED');
    expect(JSON.stringify(request)).not.toContain('NEVER_UPLOAD_THIS_METADATA');
    expect(JSON.stringify(request)).not.toContain(jpeg.toString('base64'));
    expect(JSON.stringify(request)).not.toContain('private-jpeg');
  });
}
