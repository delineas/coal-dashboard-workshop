// End-to-end test: runs the real frontend and backend in a browser, as a user does.
// It protects the main path: overview -> country search -> country page.
import { expect, test } from '@playwright/test'

test('the search opens a country page', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Countries').fill('spain')
  await page.getByLabel('Countries').press('Enter')

  await expect(page).toHaveURL(/\/country\/Spain$/)
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Spain')
})
