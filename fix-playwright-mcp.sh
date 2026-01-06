#!/bin/bash
# Fix Playwright MCP plugin to use Playwright's bundled Chromium
# Run this after Claude Code plugin updates overwrite the config
# Prerequisite: npx playwright install chromium

FIXED=0

CONFIG_CONTENT='{
  "playwright": {
    "command": "npx",
    "args": [
      "@playwright/mcp@latest",
      "--browser", "chromium",
      "--isolated",
      "--no-sandbox"
    ]
  }
}'

# Fix external_plugins location
PLUGIN_MCP="$HOME/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/playwright/.mcp.json"
if [[ -f "$PLUGIN_MCP" ]] && ! grep -q '"chromium"' "$PLUGIN_MCP"; then
  echo "$CONFIG_CONTENT" > "$PLUGIN_MCP"
  echo "Fixed: $PLUGIN_MCP"
  FIXED=$((FIXED + 1))
fi

# Fix all cached versions
for f in "$HOME"/.claude/plugins/cache/claude-plugins-official/playwright/*/.mcp.json; do
  if [[ -f "$f" ]] && ! grep -q '"chromium"' "$f"; then
    echo "$CONFIG_CONTENT" > "$f"
    echo "Fixed: $f"
    FIXED=$((FIXED + 1))
  fi
done

if [[ $FIXED -eq 0 ]]; then
  echo "All configs already correct."
else
  echo "Fixed $FIXED config(s). Restart Claude Code to apply."
fi
