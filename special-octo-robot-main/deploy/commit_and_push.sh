#!/usr/bin/env bash
set -euo pipefail

BRANCH=${1:-deploy/digitalocean}

echo "Creating branch: $BRANCH"
git checkout -b "$BRANCH"

echo "Staging deployment files"
git add Procfile Dockerfile docker-compose*.yml .env.example .github README.md deploy .dockerignore requirements.txt || true

echo "Committing"
git commit -m "chore: add deployment configs for DigitalOcean (Docker, Procfile, CI)" || echo "No changes to commit"

echo "Pushing branch to origin"
git push -u origin "$BRANCH"

echo "Done. Open a PR from $BRANCH to main/master when ready."
