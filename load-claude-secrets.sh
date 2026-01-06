#!/bin/bash
# Load Claude Code secrets from Bitwarden
# Source this in your .zshrc: source ~/claude-config/load-claude-secrets.sh

# Check if bw is available
if ! command -v bw &> /dev/null; then
  echo "Bitwarden CLI not found" >&2
  return 1
fi

# Check if session is unlocked
BW_STATUS=$(bw status 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [[ "$BW_STATUS" != "unlocked" ]]; then
  # Silently skip if locked - user can unlock manually when needed
  return 0
fi

# Fetch secrets from Bitwarden
SECRETS_JSON=$(bw get item "claude_code_secrets" 2>/dev/null)
if [[ -z "$SECRETS_JSON" ]]; then
  echo "Failed to fetch claude_code_secrets from Bitwarden" >&2
  return 1
fi

# Extract and export secrets
export CONTEXT7_API_KEY=$(echo "$SECRETS_JSON" | jq -r '.fields[] | select(.name=="context7_api_key") | .value')
export GITHUB_PERSONAL_ACCESS_TOKEN=$(echo "$SECRETS_JSON" | jq -r '.fields[] | select(.name=="gh_pat") | .value')
