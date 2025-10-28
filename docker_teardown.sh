#!/bin/zsh

# --- Configuration ---
# Import variables from .env
set -e
set -a
source scratches/postgres_poc/.env
set +a


YAML=$YML_FILE
CONTAINER_NAME=$DOCKER_PROFILE
VM_NAME=$COLIMA_PROFILE
if 
docker-compose -f "$YAML"
docker rm -f "$CONTAINER_NAME"
colima stop "$VM_NAME"
colima delete -f "$VM_NAME"
echo ""
echo ""

echo "=== Checking docker ps=="
docker ps
echo ""
echo ""

echo "=== Checking colima list=="
colima list
echo ""
echo ""