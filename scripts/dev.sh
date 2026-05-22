#!/usr/bin/env bash
# Start full stack with Docker Compose
set -euo pipefail
cd "$(dirname "$0")/.."
cp -n .env.example .env 2>/dev/null || true
docker compose up --build
