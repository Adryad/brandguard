import { Locator, Page } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly dashboardTitle: Locator;
  readonly addCompanyButton: Locator;
  readonly companyCards: Locator;
  readonly statsCards: Locator;
  readonly recentAlertsSection: Locator;
  readonly quickActionsSection: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dashboardTitle = page.getByRole('heading', { name: 'BrandGuard Dashboard' });
    this.addCompanyButton = page.getByRole('button', { name: /Add Company/i });
    this.companyCards = page.locator('[data-testid="company-card"]');
    this.statsCards = page.locator('[data-testid="stats-card"]');
    this.recentAlertsSection = page.locator('h2', { hasText: 'Recent Alerts' });
    this.quickActionsSection = page.locator('h2', { hasText: 'Quick Actions' });
  }

  async navigate() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async getCompanyCount(): Promise<number> {
    return await this.companyCards.count();
  }

  async clickAddCompany() {
    await this.addCompanyButton.click();
  }

  async getStatValue(statName: string): Promise<string> {
    const statCard = this.page.locator(`[data-testid="stats-card"]:has-text("${statName}")`);
    const value = statCard.locator('.text-2xl');
    return await value.textContent() || '';
  }
}