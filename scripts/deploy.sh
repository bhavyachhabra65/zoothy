#!/bin/bash

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage:"
    echo "bash scripts/deploy.sh production"
    echo "bash scripts/deploy.sh development"
    exit 1
fi

echo ""
echo "======================================"
echo "Deploying Zoothy ($ENVIRONMENT)"
echo "======================================"

if [ "$ENVIRONMENT" = "production" ]; then

    PROJECT_NAME="zoothy-prod"
    COMPOSE_FILE="docker/compose/docker-compose.prod.yml"

elif [ "$ENVIRONMENT" = "development" ]; then

    PROJECT_NAME="zoothy-dev"
    COMPOSE_FILE="docker/compose/docker-compose.dev.yml"

else

    echo "Invalid environment."
    exit 1

fi

echo ""
CURRENT_BRANCH=$(git branch --show-current)

echo "Current branch: $CURRENT_BRANCH"

git fetch origin

git reset --hard origin/$CURRENT_BRANCH

echo ""
echo "Building Docker Images..."

docker compose \
    --project-name "$PROJECT_NAME" \
    -f "$COMPOSE_FILE" \
    build

echo ""
echo "Restarting Containers..."

docker compose \
    --project-name "$PROJECT_NAME" \
    -f "$COMPOSE_FILE" \
    up -d

echo ""
echo "Waiting for application to become healthy..."

if [ "$ENVIRONMENT" = "production" ]; then

    HEALTH_URL="https://localhost/health"
    CURL_OPTIONS="-k"

else

    HEALTH_URL="http://localhost:5000/health"
    CURL_OPTIONS=""

fi

MAX_RETRIES=30
RETRY=1

until curl $CURL_OPTIONS -fs "$HEALTH_URL" >/dev/null; do

    if [ $RETRY -ge $MAX_RETRIES ]; then

        echo ""
        echo "Health check failed."
        echo ""

        docker compose \
            --project-name "$PROJECT_NAME" \
            -f "$COMPOSE_FILE" \
            ps

        exit 1

    fi

    echo "Waiting... ($RETRY/$MAX_RETRIES)"

    RETRY=$((RETRY + 1))

    sleep 2

done

echo "Application is healthy."

echo ""
echo "Running Containers..."

docker compose \
    --project-name "$PROJECT_NAME" \
    -f "$COMPOSE_FILE" \
    ps

echo ""
echo "Cleaning unused images..."

docker image prune -f

echo ""
echo "Deployment completed successfully."