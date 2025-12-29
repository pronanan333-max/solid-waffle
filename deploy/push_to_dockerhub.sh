#!/usr/bin/env bash
# Helper: build and push image to Docker Hub (local helper; expects DOCKERHUB_USERNAME and DOCKERHUB_TOKEN env vars)
set -euo pipefail

IMAGE_NAME="${DOCKERHUB_USERNAME:-yourusername}/musker"
TAG=${1:-latest}

docker build -t "${IMAGE_NAME}:${TAG}" .

echo "Logging in to Docker Hub..."
if [ -z "${DOCKERHUB_USERNAME:-}" ] || [ -z "${DOCKERHUB_TOKEN:-}" ]; then
  echo "Please export DOCKERHUB_USERNAME and DOCKERHUB_TOKEN"
  exit 1
fi

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

docker push "${IMAGE_NAME}:${TAG}"

echo "Pushed ${IMAGE_NAME}:${TAG}"
