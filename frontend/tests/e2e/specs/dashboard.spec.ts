import { test, expect } from '../utils/apiMocks';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Dashboard', () => {
  test('should load dashboard successfully', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    
    await dashboardPage.navigate();
    
    // Verify page title
    await expect(dashboardPage.dashboardTitle).toBeVisible();
    
    // Verify stats cards are displayed
    await expect(dashboardPage.statsCards).toHaveCount(4);
    
    // Verify sections are present
    await expect(dashboardPage.recentAlertsSection).toBeVisible();
    await expect(dashboardPage.quickActionsSection).toBeVisible();
  });

  test('should display company cards', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    
    await dashboardPage.navigate();
    
    // Verify company cards are displayed
    const companyCount = await dashboardPage.getCompanyCount();
    expect(companyCount).toBeGreaterThan(0);
    
    // Verify each card has required information
    for (let i = 0; i < companyCount; i++) {
      const card = dashboardPage.companyCards.nth(i);
      await expect(card).toBeVisible();
      await expect(card.locator('[data-testid="company-name"]')).toBeVisible();
      await expect(card.locator('[data-testid="reputation-score"]')).toBeVisible();
    }
  });

  test('should update stats correctly', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    
    await dashboardPage.navigate();
    
    // Verify stats values
    const totalCompanies = await dashboardPage.getStatValue('Total Companies');
    const positiveTrends = await dashboardPage.getStatValue('Positive Trends');
    const activeAlerts = await dashboardPage.getStatValue('Active Alerts');
    
    expect(parseInt(totalCompanies)).toBeGreaterThan(0);
    expect(parseInt(positiveTrends)).toBeGreaterThanOrEqual(0);
    expect(parseInt(activeAlerts)).toBeGreaterThanOrEqual(0);
  });

  test('should handle empty state', async ({ page }) => {
    // Mock empty companies response
    await page.route('**/api/v1/companies*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          companies: [],
          total_count: 0
        })
      });
    });
    
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigate();
    
    // Verify empty state message
    await expect(page.getByText('No companies monitored yet')).toBeVisible();
    await expect(page.getByText('Add your first company to start monitoring')).toBeVisible();
  });

  test('should be responsive on different screen sizes', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    
    // Test mobile view
    await mockedPage.setViewportSize({ width: 375, height: 667 });
    await dashboardPage.navigate();
    
    // Verify layout adjusts for mobile
    await expect(dashboardPage.companyCards.first()).toBeVisible();
    
    // Test tablet view
    await mockedPage.setViewportSize({ width: 768, height: 1024 });
    await dashboardPage.navigate();
    
    // Test desktop view
    await mockedPage.setViewportSize({ width: 1440, height: 900 });
    await dashboardPage.navigate();
  });
});