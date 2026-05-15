#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${1:-/opt/folldal-eufy-webcam}

mkdir -p "$APP_DIR"
cp -R . "$APP_DIR"
cd "$APP_DIR"

npm install
npx playwright install --with-deps chromium

mkdir -p state public

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Installed to $APP_DIR"
echo "Edit $APP_DIR/.env before enabling the systemd units."
