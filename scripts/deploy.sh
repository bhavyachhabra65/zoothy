#!/bin/bash

set -e

echo ""
echo "=================================="
echo " Deploying Zoothy"
echo "=================================="
echo ""

echo "Updating repository..."
git pull

echo ""
echo "Building containers..."
docker compose -f docker/compose/docker-compose.prod.yml build

echo ""
echo "Starting containers..."
docker compose -f docker/compose/docker-compose.prod.yml up -d

echo ""
echo "Cleaning unused images..."
docker image prune -f

echo ""
echo "Deployment completed successfully."