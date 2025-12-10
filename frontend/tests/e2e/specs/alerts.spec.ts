import { test, expect } from '../utils/apiMocks';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Alerts System', () => {
  test('should display recent alerts', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    await dashboardPage.navigate();
    
    // Verify alerts section
    await expect(dashboardPage.recentAlertsSection).toBeVisible();
    
    // Verify alerts are displayed
    const alerts = mockedPage.locator('[data-testid="alert-item"]');
    await expect(alerts).toHaveCount(2);
    
    // Verify alert content
    await expect(alerts.first()).toContainText('Reputation score dropped');
    await expect(alerts.first()).toContainText('medium');
  });

  test('should show alert severity colors', async ({ mockedPage }) => {
    await mockedPage.goto('/');
    
    const alertItems = mockedPage.locator('[data-testid="alert-item"]');
    const count = await alertItems.count();
    
    for (let i = 0; i < count; i++) {
      const alert = alertItems.nth(i);
      const severityIndicator = alert.locator('[data-testid="severity-indicator"]');
      await expect(severityIndicator).toBeVisible();
    }
  });

  test('should handle alert interactions', async ({ mockedPage }) => {
    await mockedPage.goto('/');
    
    // Mock mark as read
    await mockedPage.route('**/api/v1/alerts/1/read', async (route) => {
      await route.fulfill({ status: 200 });
    });
    
    // Click on alert (if clickable)
    const firstAlert = mockedPage.locator('[data-testid="alert-item"]').first();
    await firstAlert.click();
    
    // Verify alert is marked as read visually
    await expect(firstAlert.locator('[data-testid="read-indicator"]')).toBeVisible();
  });
});