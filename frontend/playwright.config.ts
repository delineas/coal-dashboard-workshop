import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: 'e2e',
  testMatch: '**/*.e2e.ts',
  use: {
    baseURL: 'http://localhost:5173',
    // PW_CHANNEL=chrome uses the installed Google Chrome where Playwright cannot download Chromium (for example macOS 13).
    channel: process.env.PW_CHANNEL,
  },
  webServer: [
    {
      command: '../.venv/bin/uvicorn app.main:app --port 8000',
      cwd: '../backend',
      url: 'http://localhost:8000/api/countries',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev -- --port 5173 --strictPort',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
    },
  ],
})
