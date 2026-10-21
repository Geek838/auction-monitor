import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';

const providerMode = process.env.E2E_PROVIDER_MODE ?? 'fixture';
if (!['fixture', 'simulation', 'bidcars'].includes(providerMode)) {
  throw new Error('E2E_PROVIDER_MODE must be fixture, simulation, or bidcars.');
}
const apiPort = process.env.E2E_API_PORT ?? '8000';
const webPort = process.env.E2E_WEB_PORT ?? '3000';
if (![apiPort, webPort].every(port => /^\d+$/.test(port) && Number(port) >= 1 && Number(port) <= 65535)) {
  throw new Error('E2E_API_PORT and E2E_WEB_PORT must be valid TCP ports.');
}
// A quoted absolute executable supports PowerShell/cmd paths and spaces.
const python = path.resolve(__dirname, '../../.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const apiUrl = `http://127.0.0.1:${apiPort}`;
const webUrl = `http://127.0.0.1:${webPort}`;

export default defineConfig({
  testDir: './e2e',
  testIgnore: providerMode === 'fixture' ? '**/provider-modes.spec.ts' : '**/resolver.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: {
    baseURL: webUrl,
    trace: 'retain-on-failure',
    launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
      ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH }
      : {},
  },
  projects: [
    { name: 'desktop-chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    {
      command: `"${python}" -m uvicorn app.main:app --app-dir ../../services/api --host 127.0.0.1 --port ${apiPort}`,
      url: `${apiUrl}/api/v1/health`,
      // Explicit opt-in prevents silently testing a running server in another mode.
      reuseExistingServer: process.env.E2E_REUSE_SERVERS === '1' && !process.env.CI,
      env: { AUCTION_PROVIDER: providerMode },
    },
    {
      command: `npm run dev -- --hostname 127.0.0.1 --port ${webPort}`,
      url: webUrl,
      reuseExistingServer: process.env.E2E_REUSE_SERVERS === '1' && !process.env.CI,
      env: { API_BASE_URL: apiUrl },
    },
  ],
});
