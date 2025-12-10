import { test, expect } from '@playwright/test';

test('always passes', () => {
  expect(1 + 1).toBe(2);
});

test('Playwright works', async ({ page }) => {
  await page.goto('https://example.com');
  const title = await page.title();
  expect(title).toContain('Example');
});
