#!/bin/bash
# brandguard/scripts/health-check.sh

SERVICES=("backend:8000" "frontend:3000" "postgres:5432" "redis:6379")
TIMEOUT=300
SLEEP=10

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    echo "🔍 Checking $name..."
    count=0
    until curl -sf "localhost:$port/health" > /dev/null; do
        count=$((count + 1))
        if [ $count -gt $((TIMEOUT / SLEEP)) ]; then
            echo "❌ $name failed health check!"
            exit 1
        fi
        echo "⏳ Waiting for $name... ($count/$((TIMEOUT / SLEEP)))"
        sleep $SLEEP
    done
    echo "✅ $name is healthy!"
done

echo "🎉 All services are healthy!"