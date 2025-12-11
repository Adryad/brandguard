import { test, expect } from '@playwright/test';

test.describe('Setup Verification', () => {
  test('Playwright is working', async ({ page }) => {
    // Test basic Playwright functionality
    await page.setContent('<h1>Test Page</h1>');
    await expect(page.locator('h1')).toHaveText('Test Page');
  });

  test('Assertions work', () => {
    expect(1 + 1).toBe(2);
    expect('hello').toContain('hell');
  });

  test('Page interactions work', async ({ page }) => {
    await page.setContent(`
      <button onclick="this.textContent='Clicked'">Click me</button>
    `);
    
    const button = page.locator('button');
    await button.click();
    await expect(button).toHaveText('Clicked');
  });
});