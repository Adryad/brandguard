import { test, expect } from '@playwright/test';

test.describe('Authentication E2E Tests', () => {
  test('login flow works', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Welcome back')).toBeVisible();
  });

  test('protected routes require authentication', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL(/login/);
  });

  test('logout works', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Logout
    await page.getByRole('button', { name: 'User menu' }).click();
    await page.getByRole('menuitem', { name: 'Sign out' }).click();
    
    // Should redirect to login
    await expect(page).toHaveURL(/login/);
  });
});