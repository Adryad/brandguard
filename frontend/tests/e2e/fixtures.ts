import { test as base } from '@playwright/test';
import { login, createTestCompany } from './utils';

type TestFixtures = {
  loggedInPage: void;
  testCompany: { name: string; industry: string; website: string; country: string };
};

export const test = base.extend<TestFixtures>({
  loggedInPage: async ({ page }, use) => {
    await login(page);
    await use();
  },
  
  testCompany: async ({ page }, use) => {
    const companyData = {
      name: `Test Company ${Date.now()}`,
      industry: 'technology',
      website: 'https://test.example.com',
      country: 'USA'
    };
    
    await createTestCompany(page, companyData);
    await use(companyData);
  },
});

export { expect } from '@playwright/test';