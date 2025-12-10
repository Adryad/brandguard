import { Page } from '@playwright/test';

export async function login(page: Page, email: string = 'test@example.com', password: string = 'password123') {
  await page.goto('/login');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/');
}

export async function createTestCompany(page: Page, companyData: {
  name: string;
  industry: string;
  website: string;
  country: string;
}) {
  await page.getByRole('button', { name: 'Add Company' }).click();
  await page.getByLabel('Company Name').fill(companyData.name);
  await page.getByLabel('Industry').selectOption(companyData.industry);
  await page.getByLabel('Website').fill(companyData.website);
  await page.getByLabel('Country').fill(companyData.country);
  await page.getByRole('button', { name: 'Create Company' }).click();
  await expect(page.getByText('Company created successfully')).toBeVisible();
}

export async function waitForAPIResponse(page: Page) {
  await page.waitForResponse(response => 
    response.url().includes('/api/') && response.status() === 200
  );
}