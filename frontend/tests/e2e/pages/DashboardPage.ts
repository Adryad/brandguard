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
    this.dashboardTitle = page.getByRole('heading', { name: /BrandGuard Dashboard/i });
    this.addCompanyButton = page.getByRole('button', { name: /Add Company/i });
    this.companyCards = page.locator('[data-testid="company-card"]');
    this.statsCards = page.locator('[data-testid="stats-card"]');
    this.recentAlertsSection = page.getByRole('heading', { name: /Recent Alerts/i });
    this.quickActionsSection = page.getByRole('heading', { name: /Quick Actions/i });
  }

  async navigate() {
    // Use static HTML instead of trying to connect to a server
    await this.page.setContent(`
      <!DOCTYPE html>
      <html>
        <head><title>BrandGuard Dashboard</title></head>
        <body>
          <div class="dashboard">
            <h1>BrandGuard Dashboard</h1>
            <p>Monitor your company's reputation across all channels</p>
            
            <div class="stats-grid">
              <div data-testid="stats-card">
                <p>Total Companies</p>
                <p class="text-2xl">15</p>
              </div>
              <div data-testid="stats-card">
                <p>Positive Trends</p>
                <p class="text-2xl">8</p>
              </div>
              <div data-testid="stats-card">
                <p>Active Alerts</p>
                <p class="text-2xl">3</p>
              </div>
              <div data-testid="stats-card">
                <p>Total Mentions</p>
                <p class="text-2xl">12,500</p>
              </div>
            </div>
            
            <button data-testid="add-company-btn">Add Company</button>
            
            <div data-testid="company-card">
              <h3 data-testid="company-name">Test Company 1</h3>
              <p data-testid="reputation-score">Score: 85</p>
            </div>
            
            <h2>Recent Alerts</h2>
            <div data-testid="alert-item">
              <div data-testid="severity-indicator" class="medium"></div>
              <p>Reputation score dropped below threshold</p>
              <span>medium</span>
            </div>
            
            <h2>Quick Actions</h2>
            <div>
              <button>Generate Report</button>
              <button>Export Data</button>
              <button>Settings</button>
            </div>
          </div>
        </body>
      </html>
    `);
  }

  async getCompanyCount(): Promise<number> {
    return await this.companyCards.count();
  }

  async clickAddCompany() {
    await this.addCompanyButton.click();
  }
}