#!/bin/bash
set -euo pipefail

# Publishes github-templates/ to the public hmesfin/.github repo, where GitHub
# applies them as default community health files to every hmesfin/* repo that
# has no equivalent file of its own.
#
# pre-commit-snippet.yaml and README.md are local-only and never published.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/github-templates"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

[ -d "$SRC" ] || { echo -e "${RED}missing $SRC${NC}"; exit 1; }

echo "Cloning hmesfin/.github..."
gh repo clone hmesfin/.github "$WORK/dotgithub" -- -q

cd "$WORK/dotgithub"
rm -rf .github/ISSUE_TEMPLATE .github/PULL_REQUEST_TEMPLATE.md
mkdir -p .github
cp "$SRC/PULL_REQUEST_TEMPLATE.md" .github/
cp -r "$SRC/ISSUE_TEMPLATE" .github/

# Guard: local-only files must never reach the public repo.
for f in pre-commit-snippet.yaml README.md; do
  if [ -e ".github/$f" ]; then
    echo -e "${RED}refusing to publish .github/$f${NC}"; exit 1
  fi
done

# Guard: no internal identifiers in a world-readable repo.
if grep -rqniE 'gojjo|realgig|rentkee|famapp|hetzner|traefik' .github/; then
  echo -e "${RED}internal identifier found in templates - refusing to publish${NC}"
  grep -rniE 'gojjo|realgig|rentkee|famapp|hetzner|traefik' .github/
  exit 1
fi

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi

git add -A
git commit -q -m "chore: sync templates from claude-config"
git push -q
echo -e "${GREEN}Published.${NC}"
