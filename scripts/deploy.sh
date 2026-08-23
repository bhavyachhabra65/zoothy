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


# ==========================================================
# ENVIRONMENT CONFIGURATION
# ==========================================================

if [ "$ENVIRONMENT" = "production" ]; then

    PROJECT_NAME="zoothy-prod"
    COMPOSE_FILE="docker/compose/docker-compose.prod.yml"
    ENV_FILE=".env"

elif [ "$ENVIRONMENT" = "development" ]; then

    PROJECT_NAME="zoothy-dev"
    COMPOSE_FILE="docker/compose/docker-compose.dev.yml"
    ENV_FILE=".env"

else

    echo "Invalid environment."
    exit 1

fi


# ==========================================================
# CHECK REQUIRED FILES
# ==========================================================

if [ ! -f "$COMPOSE_FILE" ]; then

    echo ""
    echo "ERROR: Compose file not found:"
    echo "$COMPOSE_FILE"
    exit 1

fi


if [ ! -f "$ENV_FILE" ]; then

    echo ""
    echo "ERROR: Environment file not found:"
    echo "$ENV_FILE"
    exit 1

fi


# ==========================================================
# CHECK REQUIRED ENVIRONMENT VARIABLES
# ==========================================================

echo ""
echo "Checking environment configuration..."

if ! grep -q '^POSTGRES_PASSWORD=' "$ENV_FILE"; then

    echo ""
    echo "ERROR: POSTGRES_PASSWORD is not set."
    echo "Check $ENV_FILE"
    exit 1

fi

echo "PostgreSQL password found."


# ==========================================================
# UPDATE CODE
# ==========================================================

echo ""

CURRENT_BRANCH=$(git branch --show-current)

echo "Current branch: $CURRENT_BRANCH"

git fetch origin

git reset --hard "origin/$CURRENT_BRANCH"


# ==========================================================
# VALIDATE DOCKER COMPOSE
# ==========================================================

echo ""
echo "Validating Docker Compose configuration..."

docker compose \
    --project-name "$PROJECT_NAME" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    config >/dev/null

echo "Docker Compose configuration is valid."


# ==========================================================
# BUILD DOCKER IMAGES
# ==========================================================

echo ""
echo "Building Docker Images..."

docker compose \
    --project-name "$PROJECT_NAME" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    build


# ==========================================================
# REMOVE OLD CONTAINERS
# ==========================================================

echo ""
echo "Removing old containers..."

docker compose \
    --project-name "$PROJECT_NAME" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    down --remove-orphans


# ==========================================================
# START CONTAINERS
# ==========================================================

echo ""
echo "Starting Containers..."

docker compose \
    --project-name "$PROJECT_NAME" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    up -d


# ==========================================================
# WAIT FOR APPLICATION
# ==========================================================

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
            --env-file "$ENV_FILE" \
            -f "$COMPOSE_FILE" \
            ps

        echo ""
        echo "Recent application logs:"

        docker compose \
            --project-name "$PROJECT_NAME" \
            --env-file "$ENV_FILE" \
            -f "$COMPOSE_FILE" \
            logs --tail=100 web

        exit 1

    fi

    echo "Waiting... ($RETRY/$MAX_RETRIES)"

    RETRY=$((RETRY + 1))

    sleep 2

done


echo ""
echo "Application is healthy."


# ==========================================================
# RUNNING CONTAINERS
# ==========================================================

echo ""
echo "Running Containers..."

docker compose \
    --project-name "$PROJECT_NAME" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    ps


# ==========================================================
# CLEAN UNUSED IMAGES
# ==========================================================

echo ""
echo "Cleaning unused images..."

docker image prune -f


# ==========================================================
# COMPLETE
# ==========================================================

echo ""
echo "======================================"
echo "Deployment completed successfully."
echo "======================================"