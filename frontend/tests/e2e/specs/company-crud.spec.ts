import { test, expect } from '../utils/apiMocks';
import { DashboardPage } from '../pages/DashboardPage';
import { CompanyModal } from '../pages/CompanyModal';
import { testCompanies } from '../utils/testData';

test.describe('Company CRUD Operations', () => {
  test.beforeEach(async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    await dashboardPage.navigate();
  });

  test('should open add company modal', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    const companyModal = new CompanyModal(mockedPage);
    
    await dashboardPage.clickAddCompany();
    
    // Verify modal opens
    await expect(companyModal.modalTitle).toBeVisible();
    await expect(companyModal.nameInput).toBeVisible();
    await expect(companyModal.submitButton).toBeVisible();
    await expect(companyModal.cancelButton).toBeVisible();
  });

  test('should add a new company successfully', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    const companyModal = new CompanyModal(mockedPage);
    
    await dashboardPage.clickAddCompany();
    await companyModal.fillCompanyDetails(testCompanies.validCompany);
    await companyModal.submit();
    
    // Verify modal closes
    await expect(companyModal.modalTitle).not.toBeVisible();
    
    // Verify success message (if implemented)
    // await expect(mockedPage.getByText('Company added successfully')).toBeVisible();
    
    // Verify company appears in list
    await expect(mockedPage.getByText(testCompanies.validCompany.name)).toBeVisible();
  });

  test('should show validation errors for invalid input', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    const companyModal = new CompanyModal(mockedPage);
    
    await dashboardPage.clickAddCompany();
    await companyModal.fillCompanyDetails(testCompanies.invalidCompany);
    await companyModal.submit();
    
    // Verify validation errors are shown
    await expect(companyModal.errorMessages).toHaveCount(4);
    await expect(companyModal.errorMessages.first()).toContainText('required');
  });

  test('should handle edge case inputs', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    const companyModal = new CompanyModal(mockedPage);
    
    await dashboardPage.clickAddCompany();
    await companyModal.fillCompanyDetails(testCompanies.edgeCaseCompany);
    await companyModal.submit();
    
    // Verify long inputs are handled
    await expect(companyModal.errorMessages).toHaveCount(0);
  });

  test('should cancel adding a company', async ({ mockedPage }) => {
    const dashboardPage = new DashboardPage(mockedPage);
    const companyModal = new CompanyModal(mockedPage);
    
    await dashboardPage.clickAddCompany();
    await companyModal.fillCompanyDetails(testCompanies.validCompany);
    await companyModal.cancel();
    
    // Verify modal closes
    await expect(companyModal.modalTitle).not.toBeVisible();
    
    // Verify no new company was added
    await expect(mockedPage.getByText(testCompanies.validCompany.name)).not.toBeVisible();
  });

  test('should navigate to company details', async ({ mockedPage }) => {
    // Click on first company card
    await mockedPage.locator('[data-testid="company-card"]').first().click();
    
    // Verify navigation to company details page
    await expect(mockedPage).toHaveURL(/\/companies\/\d+/);
    await expect(mockedPage.getByTestId('company-details-title')).toBeVisible();
  });
});