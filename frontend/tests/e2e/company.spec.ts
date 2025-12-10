import { test, expect } from '@playwright/test';

test.describe('Company Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel('Email').fill('admin@example.com');
    await page.getByLabel('Password').fill('admin123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await page.goto('/companies');
  });

  test('create new company', async ({ page }) => {
    await page.getByRole('button', { name: 'Add Company' }).click();
    
    // Fill company form
    await page.getByLabel('Company Name').fill('Test Corp');
    await page.getByLabel('Industry').selectOption('technology');
    await page.getByLabel('Website').fill('https://testcorp.com');
    await page.getByLabel('Country').fill('USA');
    
    // Submit
    await page.getByRole('button', { name: 'Create Company' }).click();
    
    // Should show success message
    await expect(page.getByText('Company created successfully')).toBeVisible();
    
    // New company should appear in list
    await expect(page.getByText('Test Corp')).toBeVisible();
  });

  test('edit company details', async ({ page }) => {
    // Click edit button on first company
    await page.getByTestId('company-card').first().hover();
    await page.getByRole('button', { name: 'Edit' }).click();
    
    // Update company name
    await page.getByLabel('Company Name').fill('Updated Company Name');
    await page.getByRole('button', { name: 'Save Changes' }).click();
    
    // Should show success message
    await expect(page.getByText('Company updated successfully')).toBeVisible();
  });

  test('delete company', async ({ page }) => {
    // Create a test company first
    await page.getByRole('button', { name: 'Add Company' }).click();
    await page.getByLabel('Company Name').fill('To Delete');
    await page.getByRole('button', { name: 'Create Company' }).click();
    
    // Delete the company
    await page.getByText('To Delete').hover();
    await page.getByRole('button', { name: 'Delete' }).click();
    
    // Confirm deletion
    await page.getByRole('button', { name: 'Confirm Delete' }).click();
    
    // Should show success message
    await expect(page.getByText('Company deleted successfully')).toBeVisible();
  });
});