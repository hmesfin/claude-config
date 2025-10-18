#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude"

echo -e "${GREEN}Claude Config Symlink Setup${NC}"
echo "=============================="
echo "Repository: $REPO_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Backup existing .claude directory if it exists
if [ -d "$TARGET_DIR" ]; then
    BACKUP_DIR="$TARGET_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}⚠️  Existing ~/.claude directory found${NC}"
    echo "Backing up to: $BACKUP_DIR"
    mv "$TARGET_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✅ Backup created${NC}"
    echo ""
fi

# Create .claude directory
echo "Creating ~/.claude directory..."
mkdir -p "$TARGET_DIR"

# Create symlinks
echo "Creating symlinks..."

# Symlink agents directory
if [ -d "$REPO_DIR/agents" ]; then
    ln -sf "$REPO_DIR/agents" "$TARGET_DIR/agents"
    echo -e "${GREEN}✅${NC} Linked: agents/"
else
    echo -e "${YELLOW}⚠️${NC}  Skipped: agents/ (directory not found)"
fi

# Symlink hooks directory
if [ -d "$REPO_DIR/hooks" ]; then
    ln -sf "$REPO_DIR/hooks" "$TARGET_DIR/hooks"
    echo -e "${GREEN}✅${NC} Linked: hooks/"
else
    echo -e "${YELLOW}⚠️${NC}  Skipped: hooks/ (directory not found)"
fi

# Symlink commands directory
if [ -d "$REPO_DIR/commands" ]; then
    ln -sf "$REPO_DIR/commands" "$TARGET_DIR/commands"
    echo -e "${GREEN}✅${NC} Linked: commands/"
else
    echo -e "${YELLOW}⚠️${NC}  Skipped: commands/ (directory not found)"
fi

# Symlink skills directory
if [ -d "$REPO_DIR/skills" ]; then
    ln -sf "$REPO_DIR/skills" "$TARGET_DIR/skills"
    echo -e "${GREEN}✅${NC} Linked: skills/"
else
    echo -e "${YELLOW}⚠️${NC}  Skipped: skills/ (directory not found)"
fi

# Symlink CLAUDE.md (global instructions)
if [ -f "$REPO_DIR/CLAUDE.md" ]; then
    ln -sf "$REPO_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"
    echo -e "${GREEN}✅${NC} Linked: CLAUDE.md"
else
    echo -e "${YELLOW}⚠️${NC}  Skipped: CLAUDE.md (file not found)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Symlink setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "Your ~/.claude/ directory now points to:"
echo "  $REPO_DIR"
echo ""
echo "To update your agents/hooks/commands:"
echo "  cd $REPO_DIR"
echo "  git pull"
echo ""
echo "Changes will instantly reflect in ~/.claude/"
echo ""

# Verify symlinks
echo "Symlink verification:"
ls -la "$TARGET_DIR" | grep -E "agents|hooks|commands|skills|CLAUDE.md"
echo ""
