import { Locator, Page } from '@playwright/test';

export class CompanyModal {
  readonly page: Page;
  readonly modalTitle: Locator;
  readonly nameInput: Locator;
  readonly industrySelect: Locator;
  readonly countryInput: Locator;
  readonly websiteInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly errorMessages: Locator;

  constructor(page: Page) {
    this.page = page;
    this.modalTitle = page.getByRole('heading', { name: /Add Company|Edit Company/i });
    this.nameInput = page.getByLabel('Company Name');
    this.industrySelect = page.getByLabel('Industry');
    this.countryInput = page.getByLabel('Country');
    this.websiteInput = page.getByLabel('Website');
    this.submitButton = page.getByRole('button', { name: /Save|Add Company/i });
    this.cancelButton = page.getByRole('button', { name: 'Cancel' });
    this.errorMessages = page.locator('[data-testid="error-message"]');
  }

  async isVisible(): Promise<boolean> {
    return await this.modalTitle.isVisible();
  }

  async fillCompanyDetails(data: {
    name: string;
    industry: string;
    country: string;
    website: string;
  }) {
    await this.nameInput.fill(data.name);
    await this.industrySelect.selectOption(data.industry);
    await this.countryInput.fill(data.country);
    await this.websiteInput.fill(data.website);
  }

  async submit() {
    await this.submitButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }
}