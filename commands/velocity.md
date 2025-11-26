---
description: "Generate velocity dashboard with project metrics, burndown, and completion projections"
---

# Velocity Dashboard Command

Generate a comprehensive project velocity report with real-time metrics.

## Quick Start

```bash
# Generate velocity dashboard
python scripts/velocity.py

# Output as JSON
python scripts/velocity.py --json

# Save to history for trend tracking
python scripts/velocity.py --save

# Specify repository (if not in git repo)
python scripts/velocity.py --repo owner/repo
```

## Implementation

**Script**: `scripts/velocity.py` (with `scripts/pm_utils.py` utilities)

The implementation uses GitHub CLI (`gh`) to fetch issues and calculate metrics.

## Instructions

1. **Detect Repository**:
   - Get current git repository (owner/repo) from `git remote get-url origin`
   - Parse GitHub URL to extract owner and repo name

2. **Fetch All Issues**:
   - Use GitHub MCP: `list_issues(owner, repo, state='all')`
   - Filter out pull requests (issues with `pull_request` key)
   - Separate into open and closed issues

3. **Calculate Velocity Metrics**:

   **Completion Rate**:
   - Total issues: count of all issues
   - Closed issues: count of closed issues
   - Open issues: count of open issues
   - Completion percentage: (closed / total) * 100

   **Velocity (Issues/Week)**:
   - Get closed issues with `closed_at` dates
   - Group by week
   - Calculate rolling 2-week average
   - Formula: `velocity = issues_closed_last_2_weeks / 2`

   **Projected Completion**:
   - Remaining issues: count of open issues
   - Weeks remaining: `remaining / velocity`
   - Projected date: current date + weeks remaining

4. **Phase Breakdown** (if labels exist):
   - Look for phase labels: `Phase 1`, `Phase 2`, etc.
   - Count completed vs total for each phase
   - Generate status emoji: ✅ (complete), 🟡 (in progress), ⚪ (not started)

5. **Milestone Progress** (if milestones exist):
   - Group issues by milestone
   - Calculate completion % for each milestone
   - Show milestone due dates if available

6. **Generate Report**:
   - Use markdown formatting with progress bars
   - Include emojis for visual appeal
   - Show trend indicators (↑ velocity increasing, → steady, ↓ decreasing)

## Output Format

```markdown
# 📊 Velocity Dashboard: [Project Name]

**Generated**: [Current Date & Time]
**Repository**: [owner/repo]

---

## 🎯 Overall Progress

**Completed**: X/Y issues (Z%)

[████████░░░░░░░░░░░░] Z%

**Status**: [On Track 🟢 | At Risk 🟡 | Delayed 🔴]

---

## 📈 Velocity Metrics

**Current Velocity**: X.X issues/week (2-week average)
**Trend**: [↑ Increasing | → Steady | ↓ Decreasing]

**Last 4 Weeks**:
- Week 1: X issues
- Week 2: Y issues
- Week 3: Z issues
- Week 4: W issues

---

## 🔮 Projections

**Remaining Issues**: X
**Estimated Completion**: [Date] (in X weeks)
**Working Days Remaining**: X days

**Velocity Scenarios**:
- Best case (current + 20%): X weeks
- Likely case (current velocity): Y weeks
- Conservative (current - 20%): Z weeks

---

## 🏗️ Phase Breakdown

**Phase 1: [Name]** ✅ Complete (X/X issues)
[████████████████████] 100%

**Phase 2: [Name]** 🟡 In Progress (X/Y issues)
[████████░░░░░░░░░░░░] Z%

**Phase 3: [Name]** ⚪ Not Started (0/Y issues)
[░░░░░░░░░░░░░░░░░░░░] 0%

---

## 🎯 Milestones

**Milestone 1: [Name]** - Due: [Date]
- Progress: X/Y issues (Z%)
- Status: [On Track | At Risk | Overdue]

**Milestone 2: [Name]** - Due: [Date]
- Progress: X/Y issues (Z%)
- Status: [On Track | At Risk | Overdue]

---

## 📊 Quality Metrics

**Average Time to Close**: X days
**Oldest Open Issue**: X days (#N)
**Recently Closed**: X issues this week

---

## 💡 Insights

- [Insight 1: e.g., "Velocity increased 20% this week"]
- [Insight 2: e.g., "Phase 2 at risk - only 30% complete with deadline in 2 weeks"]
- [Insight 3: e.g., "5 issues open >30 days - consider reviewing priorities"]

---

## 🚀 Recommendations

1. [Action item based on metrics]
2. [Suggestion to maintain/improve velocity]
3. [Warning if any issues need attention]

---

*📅 Next Update: Run `/velocity` anytime for latest metrics*
```

## Progress Bar Helper

For generating text progress bars:
- Total width: 20 characters
- Use `█` for completed, `░` for remaining
- Formula: `filled = int((percentage / 100) * 20)`
- Example: 65% → `[█████████████░░░░░░░] 65%`

## Trend Calculation

Compare last 2 weeks vs previous 2 weeks:
- If increase >15%: ↑ Increasing
- If change <15%: → Steady
- If decrease >15%: ↓ Decreasing

## Status Indicators

Overall project status:
- 🟢 On Track: Velocity matches or exceeds needed rate
- 🟡 At Risk: Velocity is 80-100% of needed rate
- 🔴 Delayed: Velocity is <80% of needed rate

## Error Handling

If GitHub MCP fails or no issues found:
- Show helpful error message
- Suggest checking repository exists
- Verify GitHub MCP is connected

## Example Usage

```
/velocity
```

Generates full dashboard for current repository.

## Notes

- This command reads only - no issues are modified
- All calculations are real-time based on current issue state
- Rerun anytime to see updated metrics
- Works best with labeled issues for phase tracking
