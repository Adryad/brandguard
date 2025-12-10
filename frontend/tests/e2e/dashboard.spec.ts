import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('has correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/BrandGuard/);
  });

  test('dashboard loads successfully', async ({ page }) => {
    // Check main heading
    await expect(page.getByRole('heading', { name: 'BrandGuard Dashboard' })).toBeVisible();
    
    // Check stats cards are present
    await expect(page.getByText('Total Companies')).toBeVisible();
    await expect(page.getByText('Positive Trends')).toBeVisible();
    await expect(page.getByText('Active Alerts')).toBeVisible();
    await expect(page.getByText('Total Mentions')).toBeVisible();
  });

  test('navigation works correctly', async ({ page }) => {
    // Click on a company card
    await page.getByTestId('company-card').first().click();
    await expect(page).toHaveURL(/companies/);
    
    // Go back to dashboard
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL('/');
  });

  test('add company modal opens', async ({ page }) => {
    await page.getByRole('button', { name: 'Add Company' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Add New Company' })).toBeVisible();
  });

  test('responsive design works', async ({ page }) => {
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.getByRole('heading', { name: 'BrandGuard Dashboard' })).toBeVisible();
    
    // Verify layout changes for mobile
    await expect(page.locator('.grid')).toHaveClass(/grid-cols-1/);
  });
});