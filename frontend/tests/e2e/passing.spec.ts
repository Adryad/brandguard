import { test, expect } from '@playwright/test';

test('always passes', () => {
  expect(true).toBe(true);
});

test('basic math', () => {
  expect(2 + 2).toBe(4);
});

test('string contains', () => {
  expect('hello world').toContain('hello');
});
