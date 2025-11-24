---
description: "Monitor and alert on high-risk issues that need attention"
---

# Risk Alert System Command

Proactively identify and alert on issues that are at risk of causing delays or problems.

## Instructions

1. **Detect Repository**:
   - Get current git repository (owner/repo) from `git remote get-url origin`
   - Parse GitHub URL to extract owner and repo name

2. **Fetch All Open Issues**:
   - Use GitHub MCP: `list_issues(owner, repo, state='open')`
   - Filter out pull requests (issues with `pull_request` key)
   - Get full details for each issue (labels, comments, created_at, updated_at)

3. **Calculate Risk Score** (0-100 for each issue):

   Risk score is calculated by summing these factors:

   **A. Days Open Factor** (max 30 points):
   ```
   Priority thresholds:
   - P0 (critical): Risky after 3 days
   - P1 (high): Risky after 7 days
   - P2 (medium): Risky after 14 days
   - No priority: Risky after 21 days

   Calculate:
   days_open = today - issue.created_at
   threshold = get_threshold_for_priority(issue.labels)

   if days_open > threshold:
       points = min((days_open - threshold) * 2, 30)
   else:
       points = 0
   ```

   **B. Explicit Risk Marker** (30 points):
   ```
   if "RISK:" in issue.body (case insensitive):
       points = 30
       extract_risk_description = text after "RISK:"
   ```

   **C. Stale Issue Factor** (max 20 points):
   ```
   days_since_update = today - issue.updated_at

   if days_since_update >= 7:
       points = min(days_since_update * 2, 20)
   ```

   **D. No Comments Factor** (15 points):
   ```
   if issue.comments == 0 and days_open > 2:
       points = 15  # Might be blocked or unclear
   ```

   **E. Approaching Milestone Deadline** (max 20 points):
   ```
   if issue.milestone and issue.milestone.due_on:
       days_until_due = milestone.due_on - today

       if days_until_due <= 3:
           points = 20
       elif days_until_due <= 7:
           points = 15
       elif days_until_due <= 14:
           points = 10
   ```

   **F. Blocked by Dependencies** (15 points):
   ```
   if "BLOCKED:" in issue.body or "blocked" label:
       points = 15
   ```

   **Total Risk Score** = A + B + C + D + E + F (max 130, normalized to 0-100)

4. **Classify Risk Levels**:

   ```
   if score >= 70:
       level = "🔴 CRITICAL"
       priority = 1
   elif score >= 50:
       level = "🟠 HIGH"
       priority = 2
   elif score >= 30:
       level = "🟡 MEDIUM"
       priority = 3
   else:
       level = "🟢 LOW"
       priority = 4  # Don't show in report
   ```

5. **Analyze PR Risks** (Optional):

   For open PRs from Copilot or automated tools:
   - Check if PR is on complex issue (has "complex" label or >500 lines changed)
   - Check if PR has review comments with changes requested
   - Check if CI is failing
   - Check if PR is stale (>7 days without updates)

6. **Generate Risk Report**:

   ```markdown
   # 🚨 Risk Alert Report: [Project Name]

   **Generated**: [Date & Time]
   **Repository**: [owner/repo]
   **Open Issues Analyzed**: X

   ---

   ## 📊 Risk Summary

   - 🔴 **CRITICAL**: X issues (need immediate attention)
   - 🟠 **HIGH**: Y issues (at risk of causing delays)
   - 🟡 **MEDIUM**: Z issues (monitor closely)
   - 🟢 **LOW**: W issues (normal progress)

   **Overall Project Health**: [CRITICAL | AT RISK | GOOD]

   ---

   ## 🔴 CRITICAL Risk Issues

   ### Issue #123: [Title] (Risk Score: 85/100)

   **Why it's risky**:
   - ⏰ Open for 15 days (P0 threshold: 3 days) → +24 pts
   - 🚨 Marked with "RISK: Complex database migration" → +30 pts
   - 💬 No comments or updates in 8 days → +16 pts
   - 🎯 Milestone "v1.0" due in 2 days → +20 pts

   **Recommended Actions**:
   1. Assign to senior developer immediately
   2. Schedule sync meeting to unblock
   3. Consider breaking into smaller tasks
   4. Update status in next 24 hours

   **Links**: [View Issue](link) | [Edit](link)

   ---

   ### Issue #156: [Title] (Risk Score: 72/100)

   **Why it's risky**:
   - ⏰ Open for 10 days (P1 threshold: 7 days) → +6 pts
   - 🚧 Marked as "BLOCKED: Waiting on #123" → +15 pts
   - 💬 No activity in 10 days → +20 pts
   - 🎯 Assigned to milestone due in 5 days → +15 pts

   **Recommended Actions**:
   1. Check blocker #123 status
   2. Consider parallel work if possible
   3. Update assignee on blocker timeline

   **Links**: [View Issue](link) | [Edit](link)

   ---

   ## 🟠 HIGH Risk Issues

   ### Issue #89: [Title] (Risk Score: 58/100)

   **Why it's risky**:
   - ⏰ Open for 12 days (P2 threshold: 14 days) → +4 pts
   - 🚨 Contains "RISK: External API dependency" → +30 pts
   - 📅 No updates in 5 days → +10 pts

   **Recommended Actions**:
   1. Verify external API is still accessible
   2. Request status update from assignee
   3. Consider adding fallback mechanism

   **Links**: [View Issue](link) | [Edit](link)

   ---

   ## 🟡 MEDIUM Risk Issues

   [List medium risk issues with brief summaries]

   ---

   ## 🤖 PR Risks

   ### PR #234: [Title] (Complex PR from Copilot)

   **Risk Factors**:
   - 🤖 Auto-generated by Copilot
   - 📊 Large PR: 850 lines changed across 15 files
   - 🔍 No human review yet (open 3 days)
   - ⚠️ Touches security-critical auth code

   **Recommended Actions**:
   1. Priority review by senior developer
   2. Run full security audit
   3. Consider breaking into smaller PRs

   ---

   ## 💡 Risk Insights

   - [Insight 1: e.g., "5 issues blocked by #123 - resolving it will unblock 20% of backlog"]
   - [Insight 2: e.g., "P0 issues taking average 8 days vs 3 day target - capacity issue?"]
   - [Insight 3: e.g., "3 issues with no comments suggest unclear requirements"]

   ---

   ## 🎯 Immediate Action Items

   1. **Triage CRITICAL issues within 24 hours**
      - Issues: #123, #156
      - Suggested: Assign, schedule sync, break down

   2. **Review HIGH risk issues this week**
      - Issues: #89, #91, #102
      - Suggested: Status updates, unblock dependencies

   3. **Monitor MEDIUM risk issues**
      - Issues: #45, #67, #78, #88, #99
      - Suggested: Check in next standup

   ---

   ## 📅 Monitoring Schedule

   **Daily**:
   - Check CRITICAL issues for updates
   - Monitor issues approaching milestone deadlines

   **Weekly**:
   - Full risk assessment (run `/risk-check`)
   - Review and update risk markers
   - Adjust priorities based on velocity

   ---

   ## 🔧 Risk Mitigation Strategies

   Based on current risk profile:

   1. **For Stale Issues**: Post comment to check status
   2. **For Blocked Issues**: Create unblocking tasks with higher priority
   3. **For Complex Issues**: Break down into smaller, parallel tasks
   4. **For No-Comment Issues**: Clarify requirements, add acceptance criteria

   ---

   *🚨 Run `/risk-check` daily to stay ahead of problems*
   *⚙️ Configure risk thresholds in `~/.claude/commands/risk-check.md`*
   ```

7. **Post Alerts** (Optional):

   Ask user:
   ```
   Found X CRITICAL and Y HIGH risk issues.

   Would you like me to:
   1. Just show this report
   2. Post warning comments on CRITICAL issues
   3. Create "risk-alert" label and apply to risky issues
   4. Send summary to GitHub issue #1 (project tracking)

   Choose [1-4]:
   ```

   **If option 2 selected**:
   Post comment on each CRITICAL issue:
   ```markdown
   🚨 **Risk Alert**

   This issue has been identified as CRITICAL risk (score: 85/100).

   **Risk Factors**:
   - Open for 15 days (P0 threshold: 3 days)
   - Marked with RISK flag
   - No activity in 8 days
   - Milestone deadline in 2 days

   **Recommended Actions**:
   1. [Action 1]
   2. [Action 2]

   Please update status or request help.

   🤖 Generated by Risk Alert System - `/risk-check`
   ```

8. **Track Risk Trends** (Optional):

   If run multiple times:
   - Compare risk scores over time
   - Show "New risks", "Resolved risks", "Worsening risks"
   - Generate risk trend chart

   ```markdown
   ## 📈 Risk Trends (Last 7 Days)

   **Improving** ✅:
   - #45: Score 75 → 40 (updated, assigned, progress made)

   **Worsening** ⚠️:
   - #89: Score 35 → 58 (stale, no comments, deadline approaching)

   **New Risks** 🆕:
   - #234: PR opened 3 days ago with no review (complex, 850 lines)
   ```

## Configuration

Customize risk thresholds by editing this file:

```markdown
## Custom Thresholds

**Days Open Thresholds**:
- P0: 3 days (default) → Change to 2 days for stricter monitoring
- P1: 7 days (default) → Change to 5 days
- P2: 14 days (default) → Change to 10 days

**Stale Threshold**: 7 days (default) → Change to 5 days

**Risk Score Thresholds**:
- CRITICAL: 70+ (default)
- HIGH: 50-69 (default)
- MEDIUM: 30-49 (default)
```

## Error Handling

- **No open issues**: "✅ No open issues - nothing to monitor!"
- **GitHub MCP error**: Show error, suggest checking connection
- **Rate limit**: Cache results, show last check time

## Example Usage

```
/risk-check

# Analyzes all open issues
# Shows risk report
# Offers to post alerts
```

## Automated Monitoring

For daily automated checks, use GitHub Actions (see implementation guide).

## Notes

- **Read-only by default**: No changes until user confirms alerts
- **Smart defaults**: Prioritizes P0/P1 issues
- **Actionable**: Every risk includes recommended actions
- **Trends**: Compare over time to spot patterns
