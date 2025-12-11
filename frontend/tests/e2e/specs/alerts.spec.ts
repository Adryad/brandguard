import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Alerts System', () => {
  test('should display recent alerts', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigate();
    
    // Verify alerts section
    await expect(dashboardPage.recentAlertsSection).toBeVisible();
    
    // Verify alerts are displayed
    const alerts = page.locator('[data-testid="alert-item"]');
    await expect(alerts).toBeVisible();
    
    // Verify alert content
    await expect(alerts).toContainText('Reputation score dropped');
  });

  test('should show alert severity colors', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigate();
    
    const alertItems = page.locator('[data-testid="alert-item"]');
    const severityIndicator = alertItems.locator('[data-testid="severity-indicator"]');
    
    await expect(severityIndicator).toBeVisible();
    await expect(severityIndicator).toHaveClass(/medium/);
  });

  test('should handle alert interactions', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigate();
    
    const firstAlert = page.locator('[data-testid="alert-item"]').first();
    await expect(firstAlert).toBeVisible();
  });
});