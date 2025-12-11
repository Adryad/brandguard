import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Dashboard', () => {
  test('should load dashboard successfully', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    await dashboardPage.navigate();
    
    // Verify page title
    await expect(page).toHaveTitle(/BrandGuard Dashboard/);
    
    // Verify main heading
    await expect(dashboardPage.dashboardTitle).toBeVisible();
    
    // Verify stats cards are displayed
    await expect(dashboardPage.statsCards).toHaveCount(4);
    
    // Verify sections are present
    await expect(dashboardPage.recentAlertsSection).toBeVisible();
    await expect(dashboardPage.quickActionsSection).toBeVisible();
  });

  test('should display company cards', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    await dashboardPage.navigate();
    
    // Verify company cards are displayed
    const companyCount = await dashboardPage.getCompanyCount();
    expect(companyCount).toBeGreaterThan(0);
    
    // Verify each card has required information
    for (let i = 0; i < companyCount; i++) {
      const card = dashboardPage.companyCards.nth(i);
      await expect(card).toBeVisible();
      await expect(card.locator('[data-testid="company-name"]')).toBeVisible();
    }
  });
});