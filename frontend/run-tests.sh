#!/bin/bash

echo "🚀 Running Playwright tests..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
  npx playwright install chromium
fi

# Run tests with progress reporter
echo "🧪 Running tests..."
npx playwright test --reporter=list

# Generate HTML report
echo "📊 Generating report..."
npx playwright test --reporter=html

echo "✅ Tests completed!"
echo ""
echo "To view the report:"
echo "  npx playwright show-report playwright-report"