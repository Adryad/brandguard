import { test as base } from '@playwright/test';
import { Page } from '@playwright/test';

export const mockApiResponses = (page: Page) => {
  // Mock companies API
  page.route('**/api/v1/companies*', async (route) => {
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
            },
            {
              id: 2,
              name: 'Mock Company 2',
              industry: 'finance',
              reputation_score: 65,
              total_mentions: 850,
              trend: 'down'
            }
          ],
          total_count: 2
        })
      });
    } else if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 3,
          name: 'New Company',
          industry: 'healthcare',
          reputation_score: 75,
          total_mentions: 0,
          trend: 'neutral'
        })
      });
    }
  });

  // Mock alerts API
  page.route('**/api/v1/alerts*', async (route) => {
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
        },
        {
          id: 2,
          title: 'New positive article detected',
          severity: 'low',
          created_at: '2024-01-15T09:15:00Z',
          is_read: true
        }
      ])
    });
  });

  // Mock stats API
  page.route('**/api/v1/dashboard/stats*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_companies: 15,
        positive_trends: 8,
        active_alerts: 3,
        total_mentions: 12500
      })
    });
  });
};

// Custom fixture with mocked APIs
export const test = base.extend<{ mockedPage: Page }>({
  mockedPage: async ({ page }, use) => {
    mockApiResponses(page);
    await use(page);
  },
});

export { expect } from '@playwright/test';