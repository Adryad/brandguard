#!/bin/bash

echo "🔧 Setting up E2E tests..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing npm dependencies..."
  npm install
fi

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install chromium

# Create test directory structure
echo "📁 Creating test structure..."
mkdir -p tests/e2e/specs tests/e2e/pages tests/e2e/utils

echo "✅ Setup complete!"
echo ""
echo "To run tests:"
echo "  npm run test:e2e"
echo ""
echo "To run tests with UI:"
echo "  npm run test:e2e:ui"