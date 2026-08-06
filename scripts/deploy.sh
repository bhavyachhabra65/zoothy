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

    BRANCH="main"
    COMPOSE_FILE="docker/compose/docker-compose.prod.yml"

elif [ "$ENVIRONMENT" = "development" ]; then

    BRANCH="develop"
    COMPOSE_FILE="docker/compose/docker-compose.dev.yml"

else

    echo "Invalid environment."

    exit 1

fi

echo ""
echo "Checking out $BRANCH..."

git fetch origin

git checkout $BRANCH

git reset --hard origin/$BRANCH

echo ""
echo "Building Docker Images..."

docker compose -f $COMPOSE_FILE build

echo ""
echo "Restarting Containers..."

docker compose -f $COMPOSE_FILE up -d

echo ""
echo "Cleaning unused images..."

docker image prune -f

echo ""
echo "Deployment completed successfully."