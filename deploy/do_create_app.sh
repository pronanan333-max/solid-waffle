#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DO_API_TOKEN:-}" ]; then
  echo "Please export DO_API_TOKEN (DigitalOcean API token)"
  exit 1
fi
if [ -z "${DOCKERHUB_USERNAME:-}" ]; then
  echo "Please export DOCKERHUB_USERNAME"
  exit 1
fi
TAG=${1:-latest}
IMAGE="${DOCKERHUB_USERNAME}/musker:${TAG}"

echo "Using image: $IMAGE"

tmp_spec=$(mktemp)
sed -e "s|__IMAGE__|$IMAGE|g" "$(dirname "$0")/app.yaml" > "$tmp_spec"

# Authenticate doctl
if ! command -v doctl >/dev/null 2>&1; then
  echo "doctl not found. Install from https://github.com/digitalocean/doctl or 'brew install doctl'"
  exit 1
fi

echo "$DO_API_TOKEN" | doctl auth init --access-token

# Create the app from the spec
echo "Creating DigitalOcean App from spec..."
DO_OUTPUT=$(doctl apps create --spec "$tmp_spec" --no-header 2>&1)
ret=$?
if [ $ret -ne 0 ]; then
  echo "doctl failed:"
  echo "$DO_OUTPUT"
  exit $ret
fi

echo "$DO_OUTPUT"

echo "App created. Save the App ID for future updates."
rm -f "$tmp_spec"
