#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Read version from package.json
VERSION=$(node -p "require('${REPO_ROOT}/package.json').version")

if [ -z "$VERSION" ]; then
  echo "Error: could not read version from package.json" >&2
  exit 1
fi

TAG="v${VERSION}"

echo "Version: ${VERSION}"
echo "Tag: ${TAG}"

# Check if tag already exists locally
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag ${TAG} already exists locally, skipping."
  exit 0
fi

# Check if tag already exists on remote
if git ls-remote --tags origin "$TAG" | grep -q "$TAG"; then
  echo "Tag ${TAG} already exists on remote, skipping."
  exit 0
fi

# Ensure package.json changes are committed before tagging
if git diff --name-only | grep -q 'package.json' || git diff --cached --name-only | grep -q 'package.json'; then
  echo "Error: package.json has uncommitted changes. Please commit before tagging." >&2
  exit 1
fi

# Ensure current branch is pushed to remote before tagging
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse "origin/${CURRENT_BRANCH}" 2>/dev/null || echo "")
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
  echo "Error: local branch '${CURRENT_BRANCH}' is not in sync with remote. Please push your commits first." >&2
  exit 1
fi

# Create and push tag
git tag "$TAG"
git push origin "$TAG"

echo "Successfully created and pushed tag ${TAG}"
