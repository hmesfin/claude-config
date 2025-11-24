---
description: "Auto-generate release notes from closed issues and PRs in a milestone"
---

# Release Notes Generator Command

Generate comprehensive, well-formatted release notes from GitHub issues and pull requests.

## Instructions

1. **Detect Repository**:
   - Get current git repository (owner/repo) from `git remote get-url origin`
   - Parse GitHub URL to extract owner and repo name

2. **Get Target Scope**:
   - **If milestone specified**: Use that milestone
   - **If no milestone**: Ask user which milestone or date range
   - **Options to present**:
     - List available milestones: `list_issues(state='all')` and extract unique milestones
     - "Last 7 days"
     - "Last 30 days"
     - "Since last release"
     - "All unreleased issues"

3. **Fetch Issues and PRs**:
   - Use GitHub MCP: `list_issues(owner, repo, state='closed', milestone=milestone_number)`
   - If date range: filter by `closed_at` date
   - Include both issues and pull requests
   - Get issue details including labels, assignees, linked PRs

4. **Categorize Changes**:

   **Group by labels** (priority order):
   - 🚀 **New Features**: `enhancement`, `feature`, `feat`
   - 🐛 **Bug Fixes**: `bug`, `fix`, `bugfix`
   - 🔒 **Security**: `security`, `vulnerability`
   - ⚡ **Performance**: `performance`, `optimization`
   - 📚 **Documentation**: `documentation`, `docs`
   - 🔧 **Maintenance**: `maintenance`, `chore`, `refactor`
   - 💥 **Breaking Changes**: `breaking`, `breaking-change`
   - 🎨 **UI/UX**: `ui`, `ux`, `design`
   - ✅ **Tests**: `test`, `testing`
   - 🏗️ **Infrastructure**: `infrastructure`, `ci`, `deployment`
   - 📦 **Dependencies**: `dependencies`, `deps`
   - 🔀 **Other**: Everything else

5. **Extract Metrics**:
   - **Issues closed**: Count total issues (not PRs)
   - **PRs merged**: Count total PRs
   - **Contributors**: Extract unique assignees and PR authors
   - **Files changed**: Sum from PR data if available
   - **Lines changed**: Sum additions + deletions from PR data
   - **Time span**: First closed date → last closed date

6. **Format Release Notes**:

   **Structure**:
   ```markdown
   # [Milestone/Version Name] - Release Notes

   **Released**: [Date]
   **Milestone**: [Milestone link if exists]

   ---

   ## 🎯 Highlights

   [Auto-generate 2-3 sentence summary of major changes]

   ---

   ## 💥 Breaking Changes

   [List breaking changes first if any exist]

   ---

   ## 🚀 New Features

   - [#123](link) Feature title - brief description @contributor
   - [#124](link) Another feature @contributor

   ---

   ## 🐛 Bug Fixes

   - [#125](link) Bug fix title @contributor

   ---

   ## ⚡ Performance Improvements

   - [#126](link) Performance improvement @contributor

   ---

   ## 📚 Documentation

   - [#127](link) Doc improvement @contributor

   ---

   ## 🔧 Maintenance

   - [#128](link) Chore @contributor

   ---

   ## 📊 Release Statistics

   - **Issues Closed**: X
   - **PRs Merged**: Y
   - **Contributors**: @user1, @user2, @user3
   - **Files Changed**: Z files
   - **Lines Changed**: +A, -B
   - **Milestone Duration**: X days

   ---

   ## 🙏 Contributors

   Thank you to all contributors who made this release possible!

   @user1, @user2, @user3, @user4

   ---

   🤖 *Generated with Claude Code - [Edit on GitHub](link to releases)*
   ```

7. **Smart Summaries**:

   For the **Highlights** section, analyze the changes and generate:
   - Focus on user-facing changes
   - Mention major features or architectural changes
   - Note any critical bug fixes
   - Keep it 2-3 sentences max

   Example:
   > "This release introduces real-time collaboration features with WebSocket support,
   > fixes critical memory leaks in the data sync layer, and improves overall
   > performance by 40%. We've also added comprehensive E2E test coverage."

8. **Create GitHub Release** (Optional):

   After generating notes, ask user:
   ```
   Would you like me to:
   1. Just show release notes (copy/paste yourself)
   2. Create draft GitHub release (you can edit before publishing)
   3. Create and publish GitHub release immediately
   ```

   If option 2 or 3:
   - Use GitHub MCP to create release
   - Tag format: Detect from existing tags or ask (e.g., `v1.2.0`, `release-2024-11`)
   - Set as draft if option 2
   - Publish if option 3

9. **Formatting Guidelines**:

   - **Issue/PR links**: Always link to GitHub (use issue/PR number)
   - **Contributors**: Use @ mentions (extracts from assignees/authors)
   - **Descriptions**:
     - Use issue title as default
     - Truncate if >80 chars
     - Remove conventional commit prefixes (`feat:`, `fix:`, etc.)
   - **Emojis**: Use consistently for visual scanning
   - **Sections**: Only include categories that have items

10. **Edge Cases**:

    - **No closed issues in scope**: Show message "No closed issues found for [scope]"
    - **No milestone exists**: Offer date range instead
    - **Multiple labels**: Use highest priority label (Features > Bugs > etc.)
    - **No labels**: Put in "Other" section
    - **Large releases** (>50 items): Offer to summarize by showing only highlights
    - **No PRs linked**: Just show issue numbers

## Output Format Options

### Compact (for small releases <10 items):
```markdown
# Release v1.2.0

**New Features**
- #123 Feature A @user1
- #124 Feature B @user2

**Bug Fixes**
- #125 Fix critical bug @user3

**Contributors**: @user1, @user2, @user3
```

### Standard (default, 10-50 items):
Full format as shown in step 6

### Detailed (for major releases >50 items):
Same as standard but includes:
- Extended descriptions (first line of issue body)
- PR links for each issue
- Commit count per PR

## Example Usage

```
/release-notes

# User prompted for scope:
# - Milestone "v1.2.0"
# - Last 30 days
# - Since last release

# Generates full release notes
# Asks if user wants to create GitHub release
```

## Error Handling

- **No git repo**: "Not in a git repository. Please run from project root."
- **No GitHub remote**: "No GitHub remote found. Is this a GitHub repository?"
- **No closed issues**: "No closed issues found for [scope]. Try a different milestone or date range."
- **GitHub MCP error**: Show helpful error and suggest checking connection

## Notes

- **Read-only by default**: No changes until user confirms GitHub release creation
- **Smart defaults**: If only one milestone exists in last 90 days, suggest it
- **Template customization**: Users can edit this file to change formatting
- **Changelog append**: Optionally offer to append to CHANGELOG.md
