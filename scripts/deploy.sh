#!/bin/bash
# brandguard/scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
COMMIT_SHA=${GIT_COMMIT:-latest}

echo "🚀 Deploying to $ENVIRONMENT..."

# Login to registry
docker login ghcr.io -u $GITHUB_ACTOR -p $GITHUB_TOKEN

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Database migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Restart services
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Health checks
./scripts/health-check.sh

# Notify Slack
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-type: application/json' \
  --data '{"text":"BrandGuard deployed to '$ENVIRONMENT' successfully!"}'

echo "✅ Deployment complete!"