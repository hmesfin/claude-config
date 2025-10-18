# Multi-Machine Setup Guide

**Purpose**: Instructions for using this Claude Code configuration across multiple machines with git sync.

## How It Works

### Architecture

```
Machine A:                          Machine B:
~/claude-config/                    ~/claude-config/
├── agents/                         ├── agents/
├── commands/                       ├── commands/
├── hooks/                          ├── hooks/
├── skills/                         ├── skills/
└── CLAUDE.md                       └── CLAUDE.md
    ↓ (git push)                        ↑ (git pull)
                GitHub/GitLab
    ↑ (git pull)                        ↓ (git push)
~/claude-config/                    ~/claude-config/
```

All machines have symlinks:
```
~/.claude/agents    -> ~/claude-config/agents
~/.claude/commands  -> ~/claude-config/commands
~/.claude/hooks     -> ~/claude-config/hooks
~/.claude/skills    -> ~/claude-config/skills
~/.claude/CLAUDE.md -> ~/claude-config/CLAUDE.md
```

## Setup on New Machine

### Step 1: Clone Repository

```bash
# Clone to ~/claude-config (or your preferred location)
git clone <your-repo-url> ~/claude-config
cd ~/claude-config
```

### Step 2: Run Setup Script

```bash
# The script creates all necessary symlinks
./setup-claude-symlinks.sh
```

**What the script does**:
- Creates `~/.claude/` directory
- Creates symlinks to agents, commands, hooks, skills, CLAUDE.md
- Backs up existing `~/.claude/` if present
- Verifies all symlinks are working

### Step 3: Verify Setup

```bash
# Check symlinks
ls -la ~/.claude/

# Should show:
# agents -> ~/claude-config/agents
# commands -> ~/claude-config/commands
# hooks -> ~/claude-config/hooks
# skills -> ~/claude-config/skills
# CLAUDE.md -> ~/claude-config/CLAUDE.md
```

### Step 4: Test Access

```bash
# Test reading through symlinks
cat ~/.claude/skills/README.md
ls ~/.claude/commands/
ls ~/.claude/agents/
```

## Daily Workflow

### Making Changes

**On Machine A**:
```bash
cd ~/claude-config

# Edit files
vim agents/django-tdd-architect.md
vim skills/DEVELOPMENT_STANDARDS.md

# Commit and push
git add .
git commit -m "Update Django agent patterns"
git push
```

**Changes are immediately reflected** in `~/.claude/` because of symlinks!

### Syncing to Other Machines

**On Machine B**:
```bash
cd ~/claude-config

# Pull latest changes
git pull

# Changes are immediately reflected in ~/.claude/
cat ~/.claude/agents/django-tdd-architect.md  # Shows updated content
```

## What Gets Synced

### ✅ Automatically Synced via Git

- All agent files (`agents/*.md`)
- All command files (`commands/*.md`)
- All hook scripts (`hooks/*.py`)
- All skills documentation (`skills/*.md`)
- Global instructions (`CLAUDE.md`)
- Documentation files (`*.md`)
- Setup scripts (`setup-claude-symlinks.sh`)

### ❌ Not Synced (Machine-Specific)

- `~/.claude/history.jsonl` - Claude Code history
- `~/.claude/settings.json` - Machine-specific settings
- `~/.claude/projects/` - Project-specific data
- `~/.claude/.credentials.json` - API credentials

## Benefits of This Approach

### 1. Single Source of Truth
```bash
# Edit once, available everywhere
vim ~/claude-config/agents/django-tdd-architect.md
git push
# Now available on all machines
```

### 2. Instant Updates
```bash
# On Machine A: Edit file
vim ~/claude-config/skills/TYPESCRIPT_PATTERNS.md

# Changes instantly visible in ~/.claude/ (same machine)
cat ~/.claude/skills/TYPESCRIPT_PATTERNS.md  # Shows new content immediately

# Push to sync with other machines
git push
```

### 3. Version Control
```bash
# See history of all changes
git log --oneline

# Revert if needed
git revert <commit-hash>

# Create branches for experiments
git checkout -b experimental-agents
```

### 4. Easy Backup
```bash
# Your entire configuration is in git
# No special backup needed - just push regularly
git push
```

### 5. Team Collaboration
```bash
# Share configurations with team
git clone <team-repo> ~/claude-config
./setup-claude-symlinks.sh

# Everyone uses same standards
```

## Example Multi-Machine Scenarios

### Scenario 1: Desktop → Laptop

**Desktop (make changes)**:
```bash
cd ~/claude-config

# Add new TypeScript pattern
echo "## Rule 9: New Pattern" >> skills/TYPESCRIPT_PATTERNS.md

# Commit and push
git add skills/TYPESCRIPT_PATTERNS.md
git commit -m "Add new TypeScript pattern"
git push
```

**Laptop (sync changes)**:
```bash
cd ~/claude-config
git pull

# New pattern immediately available
cat ~/.claude/skills/TYPESCRIPT_PATTERNS.md  # Shows Rule 9
```

### Scenario 2: Work → Home

**Work Machine**:
```bash
# Update agent to fix issue
vim ~/claude-config/agents/vue-tdd-architect.md
git add agents/vue-tdd-architect.md
git commit -m "Fix vue-tdd-architect template ref pattern"
git push
```

**Home Machine**:
```bash
# Get the fix
cd ~/claude-config
git pull

# Fix immediately available in Claude Code
# No manual copying needed!
```

### Scenario 3: Multiple Projects

Same configuration across all projects on all machines:
```bash
# Machine A, Project 1
cd ~/project1
claude-code  # Uses ~/.claude/agents/

# Machine A, Project 2
cd ~/project2
claude-code  # Uses same ~/.claude/agents/

# Machine B, Project 1
cd ~/project1
git pull  # In ~/claude-config
claude-code  # Uses synced ~/.claude/agents/
```

## Troubleshooting

### Symlinks Broken After Git Pull

**Problem**: Symlinks point to wrong path after cloning on new machine

**Solution**: Run setup script
```bash
cd ~/claude-config
./setup-claude-symlinks.sh
```

### Changes Not Showing Up

**Problem**: Edited file but changes not visible in `~/.claude/`

**Diagnosis**:
```bash
# Check if symlink is valid
ls -la ~/.claude/agents

# Should show: agents -> /home/username/claude-config/agents
# NOT: agents -> /home/differentuser/claude-config/agents
```

**Solution**: Re-run setup script on that machine
```bash
cd ~/claude-config
./setup-claude-symlinks.sh
```

### Different Usernames Across Machines

**Problem**: Machine A uses `/home/alice/`, Machine B uses `/home/bob/`

**Solution**: This is fine! Symlinks are relative to each machine:
- Machine A: `~/.claude/agents -> /home/alice/claude-config/agents`
- Machine B: `~/.claude/agents -> /home/bob/claude-config/agents`

Both point to `~/claude-config/agents`, which resolves correctly on each machine.

### Git Conflicts

**Problem**: Both machines edited same file

**Solution**: Standard git conflict resolution
```bash
cd ~/claude-config
git pull  # Shows conflict

# Edit conflicted file
vim agents/django-tdd-architect.md

# Resolve conflict markers
git add agents/django-tdd-architect.md
git commit -m "Resolve merge conflict"
git push
```

## Best Practices

### 1. Commit Often
```bash
# Small, focused commits
git add agents/django-tdd-architect.md
git commit -m "Update Django file organization pattern"
git push
```

### 2. Pull Before Editing
```bash
# Always pull latest before making changes
cd ~/claude-config
git pull
# Now edit files
```

### 3. Use Descriptive Commit Messages
```bash
# Good
git commit -m "Add TypeScript null handling pattern to skills/"

# Bad
git commit -m "Update file"
```

### 4. Test Locally First
```bash
# Edit and test on one machine
vim ~/claude-config/agents/django-tdd-architect.md
# Use it with Claude Code to verify
# Then push
git push
```

### 5. Document Major Changes
```bash
# Add notes to commit
git commit -m "Refactor all agents to reference skills/

- Reduced django-tdd-architect by 10%
- Reduced vue-tdd-architect by 31%
- Created new skills/ directory
- Updated 3 of 26 agents

See PHASE2_COMPLETION.md for details"
```

## Current Repository State

As of Phase 2 completion:

```
claude-config/
├── agents/                  # 26 agents (3 updated, 23 ready)
├── commands/                # 6 commands (4 new in Phase 2)
├── hooks/                   # 2 hooks + README
├── skills/                  # 3 skills docs (new in Phase 1-2)
├── CLAUDE.md                # Global instructions
├── setup-claude-symlinks.sh # Setup script (updated)
├── CONFIGURATION_REVIEW.md  # Analysis
├── PHASE1_COMPLETION.md     # Phase 1 summary
├── PHASE2_COMPLETION.md     # Phase 2 summary
├── SYMLINK_STATUS.md        # Symlink documentation
└── MULTI_MACHINE_SETUP.md   # This file
```

All tracked in git and synced across machines.

## Setup Verification Checklist

After setting up on a new machine:

- [ ] Cloned repository to `~/claude-config`
- [ ] Ran `./setup-claude-symlinks.sh`
- [ ] Verified symlinks: `ls -la ~/.claude/`
- [ ] Tested reading: `cat ~/.claude/skills/README.md`
- [ ] Tested commands: `ls ~/.claude/commands/`
- [ ] Tested agents: `ls ~/.claude/agents/`
- [ ] Git configured: `git config --list`
- [ ] Can push: `git push` (test with small change)
- [ ] Can pull: `git pull`

## Quick Reference

```bash
# Setup new machine
git clone <repo> ~/claude-config && cd ~/claude-config && ./setup-claude-symlinks.sh

# Daily workflow
cd ~/claude-config
git pull                    # Get latest
vim agents/some-agent.md    # Edit
git add .                   # Stage
git commit -m "message"     # Commit
git push                    # Sync

# Verify on other machine
cd ~/claude-config
git pull                    # Get changes
cat ~/.claude/agents/some-agent.md  # Verify
```

## Related Documentation

- `setup-claude-symlinks.sh` - Automated setup script
- `SYMLINK_STATUS.md` - Current symlink structure
- `README.md` - Project overview
- `PHASE2_COMPLETION.md` - Recent changes
