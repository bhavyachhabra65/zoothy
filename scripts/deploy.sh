#!/bin/bash

set -e

echo ""
echo "=================================="
echo "     Deploying Zoothy"
echo "=================================="
echo ""

echo "Fetching latest code..."
git fetch origin

echo "Checking out main branch..."
git checkout main

echo "Resetting to origin/main..."
git reset --hard origin/main

echo ""
echo "Building Docker images..."
docker compose -f docker/compose/docker-compose.prod.yml build

echo ""
echo "Starting containers..."
docker compose -f docker/compose/docker-compose.prod.yml up -d

echo ""
echo "Cleaning unused Docker images..."
docker image prune -f

echo ""
echo "Waiting for application..."
sleep 5

# echo "Performing health check..."
# curl -f https://zoothy.com/health

echo ""
echo "=================================="
echo " Deployment Successful ✅"
echo "=================================="
echo ""