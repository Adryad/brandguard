import { Page } from '@playwright/test';

export const mockApiResponses = async (page: Page) => {
  // Mock companies API
  await page.route('**/api/v1/companies*', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          companies: [
            {
              id: 1,
              name: 'Mock Company 1',
              industry: 'technology',
              reputation_score: 85,
              total_mentions: 1250,
              trend: 'up'
            }
          ],
          total_count: 1
        })
      });
    } else if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 123,
          name: 'New Company',
          success: true
        })
      });
    }
  });

  // Mock alerts API
  await page.route('**/api/v1/alerts*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 1,
          title: 'Reputation score dropped below threshold',
          severity: 'medium',
          created_at: '2024-01-15T10:30:00Z',
          is_read: false
        }
      ])
    });
  });
};

// Simple test utility
export const setupTestPage = async (page: Page) => {
  await mockApiResponses(page);
  return page;
};