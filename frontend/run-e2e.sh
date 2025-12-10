#!/bin/bash

echo "🚀 Starting BrandGuard E2E Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if dev server is running
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Dev server is running${NC}"
else
    echo -e "${YELLOW}⚠ Starting dev server...${NC}"
    npm run dev &
    SERVER_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null; then
            echo -e "${GREEN}✓ Server started after ${i}s${NC}"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ Server failed to start within 30 seconds${NC}"
            kill $SERVER_PID 2>/dev/null
            exit 1
        fi
    done
fi

# Run tests
echo -e "${YELLOW}🏃 Running Playwright tests...${NC}"
npx playwright test --reporter=html

TEST_EXIT_CODE=$?

# Kill server if we started it
if [ ! -z "$SERVER_PID" ]; then
    echo -e "${YELLOW}🛑 Stopping dev server...${NC}"
    kill $SERVER_PID 2>/dev/null
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "📊 Report available at: frontend/playwright-report/index.html"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "📊 Report available at: frontend/playwright-report/index.html"
fi

exit $TEST_EXIT_CODE