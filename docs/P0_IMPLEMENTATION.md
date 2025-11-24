# P0 Implementation Guide: Auto-Progress Tracking & Test Coverage Guardian

**Status**: ✅ **Implemented**
**Date**: 2025-11-24
**Priority**: P0 (Critical - Highest ROI)

## Overview

This document describes the implementation of the two P0 (Priority 0) enhancements from `GH_MCP_IDEAS.md`:

1. **Auto-Progress Tracking** - Automates GitHub issue lifecycle based on git commits
2. **Test Coverage Guardian** - Enforces test coverage requirements on pull requests

Both features are now fully implemented and ready for testing.

---

## 🎯 P0.1: Auto-Progress Tracking

### What It Does

Automatically manages GitHub issues when you commit code with issue references:

- **Detects**: Git commits with `fixes #N`, `closes #N`, or `resolves #N`
- **Closes**: Referenced GitHub issue automatically
- **Comments**: Posts progress update with project statistics
- **Suggests**: Next sequential open issue to work on

### Implementation Details

**Location**: `~/.claude/hooks/post-tool-use/auto-progress-tracker.py`

**Trigger**: PostToolUse hook (after Bash tool executes git commit)

**Components**:
1. **Hook Script** (`auto-progress-tracker.py`):
   - Parses git commit messages
   - Extracts issue references
   - Calls GitHub API to manage issues

2. **GitHub API Library** (`~/.claude/hooks/lib/github_automation.py`):
   - Direct GitHub REST API integration
   - Issue management functions
   - Progress calculation

**Requirements**:
- Python 3.7+
- `requests` library (already installed)
- `GITHUB_TOKEN` environment variable (set from your PAT)

### How to Use

#### 1. Set GitHub Token

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export GITHUB_TOKEN="your-github-personal-access-token-here"
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

#### 2. Commit with Issue Reference

When you're done with work on an issue, commit with a keyword:

```bash
git commit -m "fixes #15: Implement user authentication"
```

**Supported keywords**:
- `fix #N` / `fixes #N`
- `close #N` / `closes #N`
- `resolve #N` / `resolves #N`

#### 3. Automatic Actions

The hook will:
1. ✅ Close issue #15 on GitHub
2. 📊 Post progress comment: "14/27 (52%) complete"
3. 🚀 Suggest next issue: "Next issue: #16"

#### 4. View Suggestion

Claude Code will display:
```
✅ Closed issue #15
🚀 Next issue: #16
Tip: You can say 'Show me issue #16' to start working on it
```

### Supported Formats

```bash
# Basic reference
git commit -m "fixes #15"

# With description
git commit -m "fixes #15: Add user auth"

# Multiple issues
git commit -m "fixes #15, closes #16"

# Cross-repo reference
git commit -m "fixes owner/repo#15"
```

### Example Workflow

```bash
# 1. Working on issue #15
git add .
git commit -m "fixes #15: Implement authentication system"

# Hook runs automatically:
# ✅ Closed issue #15
# 📊 Progress: 15/27 (55%) complete
# 🚀 Next issue: #16

# 2. Start next issue
# Say to Claude: "Show me issue #16"
```

### Testing the Hook

Test without actually committing:

```bash
cd ~/projects/sp-mcp

# Create test input
echo '{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m \"fixes #999: Test commit\""
  }
}' | ~/.claude/hooks/post-tool-use/auto-progress-tracker.py
```

---

## 🛡️ P0.2: Test Coverage Guardian

### What It Does

Automatically enforces test coverage requirements on every pull request:

- **Runs**: Coverage check on every PR
- **Enforces**: Minimum 85% overall coverage
- **Strict**: 95% coverage for security-related files
- **Blocks**: Merge if coverage is too low
- **Reports**: Detailed coverage breakdown in PR comments

### Implementation Details

**Location**: `.github/workflows/coverage-guardian.yml`

**Trigger**: Pull request events (opened, synchronize, reopened)

**Components**:
1. **GitHub Action Workflow** (`coverage-guardian.yml`):
   - Runs on every PR
   - Executes pytest with coverage
   - Calls coverage check script

2. **Coverage Check Script** (`.github/scripts/check_coverage.py`):
   - Analyzes pytest coverage JSON output
   - Enforces thresholds
   - Generates PR comment
   - Fails workflow if below threshold

**Thresholds**:
- **Minimum Coverage**: 85%
- **Security Files**: 95%

**Security File Patterns**:
- Files containing: `auth`, `security`, `permission`, `token`, `password`, `encryption`, `crypto`

### How to Use

#### 1. Push Configuration to Repo

The GitHub Action is already set up in your sp-mcp repository:
```bash
cd ~/projects/sp-mcp
git add .github/
git commit -m "Add Test Coverage Guardian workflow"
git push
```

#### 2. Create a Pull Request

Coverage Guardian runs automatically on every PR:

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... write code ...

# Commit and push
git add .
git commit -m "Add new feature"
git push -u origin feature/my-feature

# Create PR via GitHub or CLI
gh pr create --title "Add my feature" --body "Description"
```

#### 3. Review Coverage Report

The workflow will:
1. ✅ Run all tests with coverage
2. 📊 Generate coverage report
3. 💬 Comment on PR with results
4. ❌ Block merge if below threshold

#### Example PR Comment

```markdown
✅ **Test Coverage Report - PASSED**

📊 **Overall Coverage**: 93.2% (target: 85%)

**Summary:**
- Total Files: 12
- Files Below Threshold: 0
- Security Files Below Threshold: 0

---
🤖 Generated by Test Coverage Guardian
```

Or if failed:

```markdown
❌ **Test Coverage Report - FAILED**

📊 **Overall Coverage**: 82.5% (target: 85%)

**Summary:**
- Total Files: 12
- Files Below Threshold: 3
- Security Files Below Threshold: 1

## ⚠️ Files Below Coverage Threshold

| File | Coverage | Missing Lines | Target |
|------|----------|--------------|--------|
| `src/models.py` | 78.3% | 15 | 85% |
| `src/server.py` | 81.2% | 8 | 85% |

## 🔒 Security Files Requiring Higher Coverage

| File | Coverage | Required |
|------|----------|----------|
| `src/auth.py` | 92.1% | 95% |

## 📝 Action Required

- Add tests to increase coverage for files listed above
- Security-related files require >95% coverage
- Coverage check will block merge until requirements are met
```

### Local Testing

Test coverage locally before pushing:

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term --cov-report=json

# Check coverage manually
python .github/scripts/check_coverage.py
```

### Customizing Thresholds

Edit `.github/scripts/check_coverage.py`:

```python
# Coverage thresholds
MINIMUM_COVERAGE = 85.0  # Change to your preferred minimum
SECURITY_COVERAGE = 95.0  # Change security threshold

# Security-related file patterns
SECURITY_PATTERNS = [
    'auth',
    'security',
    # Add more patterns
]
```

---

## 🚀 Combined Workflow Example

Here's how both P0 features work together:

### Scenario: Working on Issue #15

**1. Start Work**
```bash
# Checkout feature branch
git checkout -b fix/issue-15
```

**2. Develop & Test**
```bash
# Write code
vim src/feature.py

# Write tests (Coverage Guardian will check these!)
vim tests/test_feature.py

# Run tests locally
pytest --cov=src
```

**3. Commit & Push**
```bash
git add .
git commit -m "fixes #15: Implement new feature with 95% coverage"

# Auto-Progress Tracker runs:
# ✅ Closed issue #15
# 📊 Progress: 15/27 (55%)
# 🚀 Next: #16

git push -u origin fix/issue-15
```

**4. Create PR**
```bash
gh pr create --title "Fix issue #15" --body "Closes #15"

# Coverage Guardian runs:
# ✅ Checks coverage
# 💬 Comments on PR
# ✅ Passes (93% coverage)
```

**5. Merge**
```bash
# Coverage passed, safe to merge!
gh pr merge
```

**6. Continue**
```bash
# Start next issue suggested by Auto-Progress Tracker
git checkout main
git pull
git checkout -b fix/issue-16
```

---

## 📊 Success Metrics

Track the impact of P0 features:

| Feature | Metric | Target | Actual |
|---------|--------|--------|--------|
| Auto-Progress | Time saved per issue | 2+ min | TBD |
| Auto-Progress | Manual updates avoided | 100% | TBD |
| Coverage Guardian | Coverage maintained | >85% | TBD |
| Coverage Guardian | Bad PRs blocked | 100% | TBD |

Update after 1 week of usage.

---

## 🔧 Troubleshooting

### Auto-Progress Tracker

**Issue**: Hook not running
```bash
# Check hook is executable
ls -la ~/.claude/hooks/post-tool-use/auto-progress-tracker.py

# Should show: -rwxr-xr-x

# Fix if needed
chmod +x ~/.claude/hooks/post-tool-use/auto-progress-tracker.py
```

**Issue**: GitHub API errors
```bash
# Verify token is set
echo $GITHUB_TOKEN

# Test GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

**Issue**: Hook not detecting commits
```bash
# Check commit message format
git log -1 --pretty=%B

# Must contain: fixes #N, closes #N, or resolves #N
```

### Coverage Guardian

**Issue**: Workflow not running
- Check `.github/workflows/coverage-guardian.yml` exists in repo
- Verify it's pushed to GitHub
- Check GitHub Actions tab for errors

**Issue**: Coverage always fails
```bash
# Run locally to debug
pytest --cov=src --cov-report=term

# Check coverage.json exists
ls -la coverage.json

# Run check script manually
python .github/scripts/check_coverage.py
```

**Issue**: Security files flagged incorrectly
- Edit `.github/scripts/check_coverage.py`
- Modify `SECURITY_PATTERNS` list

---

## 🎉 Next Steps

Now that P0 is implemented:

1. **Test on Real Workflow**:
   - Create a test issue
   - Make changes
   - Commit with `fixes #N`
   - Create PR and watch Coverage Guardian

2. **Monitor & Iterate**:
   - Track metrics
   - Adjust thresholds if needed
   - Add more automation based on learnings

3. **Move to P1** (from GH_MCP_IDEAS.md):
   - Smart Code Review Agent
   - Velocity Dashboard
   - Dependency Automation

---

## 📚 Files Created

```
Desktop (HMDESKTOP):
├── ~/.claude/hooks/
│   ├── lib/
│   │   ├── __init__.py
│   │   └── github_automation.py
│   └── post-tool-use/
│       └── auto-progress-tracker.py
└── ~/projects/sp-mcp/
    ├── .github/
    │   ├── workflows/
    │   │   └── coverage-guardian.yml
    │   └── scripts/
    │       └── check_coverage.py
    └── P0_IMPLEMENTATION.md (this file)
```

---

## 🤖 Summary

**P0.1: Auto-Progress Tracking** ✅
- Hook automatically closes GitHub issues on commit
- Posts progress updates
- Suggests next issue
- Saves 2-3 minutes per issue

**P0.2: Test Coverage Guardian** ✅
- GitHub Action enforces 85% coverage
- Security files require 95% coverage
- Blocks low-quality PRs
- Detailed coverage reports

**Total Implementation Time**: ~2 hours
**Expected Time Savings**: 54-81 minutes over 27 issues
**Quality Improvement**: Maintains >85% test coverage

---

**Let's build the future of AI-powered project management!** 🚀🤖
