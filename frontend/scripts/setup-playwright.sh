#!/bin/bash

echo "🔧 Setting up Playwright for E2E testing..."

# Install Playwright
npm install --save-dev @playwright/test

# Install browsers
npx playwright install --with-deps

# Create test directory structure
mkdir -p tests/e2e/specs
mkdir -p tests/e2e/fixtures
mkdir -p tests/e2e/pages
mkdir -p tests/e2e/utils

echo "✅ Playwright setup complete!"
echo ""
echo "Available commands:"
echo "  npm run test:e2e           - Run all E2E tests"
echo "  npm run test:e2e:ui        - Run tests with UI mode"
echo "  npm run test:e2e:debug     - Run tests in debug mode"
echo "  npm run test:e2e:chromium  - Run tests only in Chrome"
echo "  npm run test:e2e:install   - Install browsers"
echo "  npm run test:e2e:codegen   - Generate tests with CodeGen"