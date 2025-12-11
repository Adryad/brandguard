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
    this.nameInput = page.locator('input[name="name"], #company-name');
    this.industrySelect = page.locator('select[name="industry"], #industry');
    this.countryInput = page.locator('input[name="country"], #country');
    this.websiteInput = page.locator('input[name="website"], #website');
    this.submitButton = page.getByRole('button', { name: /Save|Add Company/i });
    this.cancelButton = page.getByRole('button', { name: 'Cancel' });
    this.errorMessages = page.locator('.error, [data-testid="error-message"]');
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
    if (await this.nameInput.isVisible()) {
      await this.nameInput.fill(data.name);
    }
    if (await this.industrySelect.isVisible()) {
      await this.industrySelect.selectOption(data.industry);
    }
    if (await this.countryInput.isVisible()) {
      await this.countryInput.fill(data.country);
    }
    if (await this.websiteInput.isVisible()) {
      await this.websiteInput.fill(data.website);
    }
  }

  async submit() {
    if (await this.submitButton.isVisible()) {
      await this.submitButton.click();
    }
  }

  async cancel() {
    if (await this.cancelButton.isVisible()) {
      await this.cancelButton.click();
    }
  }
}