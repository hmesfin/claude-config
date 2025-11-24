---
description: "AI-powered batch suggestions for optimal parallel work and maximum velocity"
---

# Smart Batching Suggestions Command

Analyzes your project's dependency graph and suggests optimal batches of parallel work to maximize velocity.

## Instructions

1. **Detect Repository**:
   - Get current git repository (owner/repo) from `git remote get-url origin`
   - Parse GitHub URL to extract owner and repo name

2. **Fetch All Open Issues**:
   - Use GitHub MCP: `list_issues(owner, repo, state='open')`
   - Filter out pull requests (issues with `pull_request` key)
   - Get full details for each issue (labels, body, assignee, comments)

3. **Parse Dependency Graph**:

   For each issue, extract dependencies from body:

   ```
   UNLOCKS: #15, #16, #17
   BLOCKS: #20
   ENABLES: #21
   DEPENDS ON: #10, #11
   BLOCKED BY: #5
   ```

   Build graph structure:
   ```python
   graph = {
       issue_number: {
           'unlocks': [15, 16, 17],      # Issues this unblocks
           'blocks': [20],                # Issues this blocks
           'depends_on': [10, 11],        # Issues this depends on
           'blocked_by': [5],             # Issues blocking this
       }
   }
   ```

4. **Identify Ready Issues**:

   An issue is "ready" if:
   - ✅ Has no open blockers (all `depends_on` issues are closed)
   - ✅ Has no `BLOCKED BY:` marker pointing to open issues
   - ✅ Not already assigned (or assigned to you)
   - ✅ Has 'ready' label (from dependency automation)

   ```python
   ready_issues = []
   for issue in open_issues:
       blockers = get_dependencies(issue, 'blocked_by')

       # Check if all blockers are closed
       all_blockers_resolved = all(
           is_issue_closed(blocker) for blocker in blockers
       )

       if all_blockers_resolved and not issue.assignee:
           ready_issues.append(issue)
   ```

5. **Categorize Issues**:

   **A. By Complexity** (for assignment):

   - **🤖 Copilot-Friendly** (good for automation):
     - Labels: `crud`, `simple`, `standard`, `ui-only`, `docs`
     - No "complex" or "architecture" labels
     - <300 lines estimated (from issue description)
     - Clear acceptance criteria

   - **🧠 Complex** (needs human expertise):
     - Labels: `complex`, `architecture`, `security`, `performance`
     - Has "RISK:" in description
     - >500 lines estimated
     - Touches critical systems

   - **⚖️ Medium** (can go either way):
     - Everything else
     - 300-500 lines estimated
     - Standard business logic

   **B. By Phase** (for grouping):

   - Extract phase from labels: `Phase 1`, `Phase 2`, etc.
   - Group by milestone if no phase labels
   - Group by feature area if no milestone

   **C. By Parallel Safety**:

   - **✅ Parallel-Safe** (can work simultaneously):
     - Different feature areas
     - Different files/modules
     - No shared dependencies

   - **⚠️ Sequential** (must be done in order):
     - Same feature area
     - Dependency chain
     - Shared critical files

6. **Analyze Current Capacity**:

   ```python
   # Check velocity from /velocity command
   velocity = calculate_velocity()  # issues per week

   # Check current workload
   assigned_issues = [i for i in open_issues if i.assignee]
   in_progress = [i for i in open_issues if 'in-progress' in labels]

   # Calculate available capacity
   available_capacity = velocity - len(in_progress)
   ```

7. **Generate Optimal Batches**:

   **Strategy**:
   - Maximize parallel work (different people, different areas)
   - Balance Copilot vs manual work
   - Stay within capacity
   - Prioritize critical path (P0 > P1 > P2)
   - Group by phase/milestone

   **Batch Structure**:
   ```python
   batch = {
       'copilot': [  # Assign to Copilot/automation
           {'issue': #17, 'title': '...', 'reason': 'Simple CRUD, clear spec'},
           {'issue': #19, 'title': '...', 'reason': 'UI-only, no business logic'},
       ],
       'self': [  # Work on yourself
           {'issue': #13, 'title': '...', 'reason': 'Complex UI interactions'},
       ],
       'contractor_a': [  # If contractors available
           {'issue': #21, 'title': '...', 'reason': 'Backend API, matches skills'},
       ],
       'sequential': [  # Must wait for others
           {'issue': #25, 'title': '...', 'blocked_by': [#13]},
       ]
   }
   ```

8. **Calculate Expected Outcomes**:

   ```python
   # Parallel work estimation
   if copilot + contractor work happens simultaneously:
       expected_prs = len(copilot) + len(contractor) + len(self)
       expected_days = max(
           estimate_days(copilot),
           estimate_days(contractor),
           estimate_days(self)
       )
   ```

9. **Generate Report**:

   ```markdown
   # 🚀 Smart Batch Suggestions: [Project Name]

   **Generated**: [Date & Time]
   **Repository**: [owner/repo]
   **Ready Issues**: X issues (Y Copilot-friendly, Z complex)
   **Current Capacity**: N issues this week

   ---

   ## 📊 Dependency Overview

   **Critical Path** (must finish first):
   - Issue #10 → Unlocks #15, #16, #17 (3 issues)
   - Issue #15 → Unlocks #20, #21 (2 issues)

   **Parallel Opportunities**:
   - 5 issues can be worked simultaneously
   - 2 feature areas with no shared dependencies

   **Blocked Issues**: X issues waiting on dependencies

   ---

   ## 🎯 Recommended Batch (This Week)

   ### 🤖 Assign to Copilot (3 issues, parallel)

   **Issue #17: Mobile App Setup**
   - **Why Copilot**: Standard React Native setup, clear patterns
   - **Estimate**: 2-3 days
   - **Parallel with**: #19, #14
   - **Unlocks**: #22, #23

   **Issue #19: Mobile Calendar UI**
   - **Why Copilot**: UI-only, standard calendar component
   - **Estimate**: 2 days
   - **Parallel with**: #17, #14

   **Issue #14: Web Shopping List**
   - **Why Copilot**: Simple CRUD operations, existing patterns
   - **Estimate**: 2-3 days
   - **Parallel with**: #17, #19

   ---

   ### 🧠 Work on Yourself (1 issue)

   **Issue #13: Web Task Management (Complex)**
   - **Why Manual**: Complex state management, real-time sync
   - **Estimate**: 3-4 days
   - **Parallel with**: All Copilot issues
   - **Risk**: Architecture decisions needed
   - **Unlocks**: #18, #24

   ---

   ### 📅 Next Batch (After Current)

   **Ready after #13 completes**:
   - Issue #18: Task notifications
   - Issue #24: Task sharing

   **Ready after #17 completes**:
   - Issue #22: Mobile push notifications
   - Issue #23: Mobile offline sync

   ---

   ## 📈 Expected Outcomes

   **If all batches complete in parallel**:
   - ✅ 4 PRs ready by end of week
   - ✅ 7 additional issues unblocked
   - ✅ 40% progress toward milestone "v1.0"
   - ⏱️ Velocity: 4 issues/week (current: 2.5)

   **Timeline**:
   ```
   Week 1 (Now):
   ┌─ Copilot: #17, #19, #14 (parallel) ─┐
   │                                      ├─> 4 PRs done
   └─ You: #13 (parallel) ───────────────┘

   Week 2 (Next):
   ┌─ Copilot: #22, #23 (parallel) ──────┐
   │                                      ├─> 4 more PRs
   └─ You: #18, #24 (parallel) ──────────┘
   ```

   ---

   ## 💡 Optimization Insights

   **Parallelization Opportunity**: 🟢 High
   - 75% of ready issues can be done in parallel
   - No shared file conflicts detected

   **Copilot Efficiency**: 🟢 Excellent
   - 3/4 issues are Copilot-friendly
   - Clear specs and patterns available

   **Critical Path Risk**: 🟡 Medium
   - Issue #13 blocks 2 important issues
   - Consider starting #13 first or breaking down

   **Capacity Utilization**: 🟢 Optimal
   - Batch size (4) matches velocity (4/week)
   - Good balance of Copilot vs manual work

   ---

   ## 🎯 Alternative Strategies

   ### Strategy A: Focus on Critical Path
   **Do first**: #13 (manual)
   **Then**: #18, #24 (unblocked by #13)
   **Result**: Maximum unlocking, but slower start

   ### Strategy B: Maximize Copilot (Recommended)
   **Do first**: #17, #19, #14 (Copilot parallel)
   **Then**: #13 (manual while Copilot works)
   **Result**: Fastest total velocity, balanced work

   ### Strategy C: Risk-First
   **Do first**: #13 (complex, risky)
   **While**: #17, #19 (simple Copilot work)
   **Result**: De-risk early, parallel simple work

   **🏆 Recommended**: Strategy B (current batch suggestion)

   ---

   ## 🔧 Action Items

   1. **Assign Copilot Issues**:
      ```bash
      gh issue edit 17 --add-assignee copilot
      gh issue edit 19 --add-assignee copilot
      gh issue edit 14 --add-assignee copilot
      ```

   2. **Start Your Work**:
      ```bash
      git checkout -b feature/task-management
      # Work on #13
      ```

   3. **Monitor Progress**:
      - Daily: Check Copilot PR status
      - Mid-week: Run `/risk-check` for blockers
      - End-week: Run `/velocity` to verify velocity

   4. **Prepare Next Batch**:
      - Review issues #18, #22, #23, #24
      - Add any missing specs
      - Label appropriately

   ---

   ## 📋 Batch Summary Table

   | Issue | Title | Type | Estimate | Parallel | Unlocks |
   |-------|-------|------|----------|----------|---------|
   | #17 | Mobile Setup | 🤖 Copilot | 2-3d | ✅ | 2 issues |
   | #19 | Calendar UI | 🤖 Copilot | 2d | ✅ | 0 issues |
   | #14 | Shopping List | 🤖 Copilot | 2-3d | ✅ | 0 issues |
   | #13 | Task Mgmt | 🧠 Manual | 3-4d | ✅ | 2 issues |

   **Total**: 4 issues, 9-12 days work, 3-4 days elapsed (if parallel)

   ---

   *🚀 Run `/suggest-batch` weekly to optimize your workflow*
   *📊 Combine with `/velocity` and `/risk-check` for full visibility*
   ```

10. **Smart Recommendations**:

    Based on project state, add context-aware tips:

    **If velocity is low**:
    > 💡 **Tip**: Your velocity is 2.5 issues/week but capacity allows 4.
    > Consider assigning more Copilot work to increase throughput.

    **If many blockers**:
    > ⚠️ **Warning**: 40% of issues are blocked by just 2 issues (#10, #15).
    > Prioritize these to unblock 8 downstream issues.

    **If no parallel work**:
    > 🔄 **Suggestion**: All ready issues are in same feature area.
    > Consider breaking down into parallel sub-tasks.

    **If over-capacity**:
    > ⏸️ **Caution**: Batch size (6) exceeds velocity (4/week).
    > Reduce scope or extend timeline to avoid burnout.

11. **Integration with Other Commands**:

    ```markdown
    ## 🔗 Related Commands

    - `/velocity` - Check current velocity and capacity
    - `/risk-check` - Identify blockers in suggested batch
    - `/release-notes` - Generate notes after batch completes

    **Workflow**:
    1. Run `/velocity` to check capacity
    2. Run `/suggest-batch` to get weekly plan
    3. Assign and start work
    4. Run `/risk-check` daily to monitor
    5. Run `/release-notes` when batch completes
    ```

## Configuration

Customize batching logic by editing this file:

```markdown
## Customization Options

**Copilot Classification**:
- Add labels to `copilot_friendly`: ['crud', 'simple', 'ui-only', 'docs']
- Add labels to `manual_required`: ['complex', 'architecture', 'security']

**Batch Size**:
- Default: Match velocity (from /velocity)
- Custom: Set max issues per batch (e.g., 5)

**Parallel Safety**:
- Aggressive: Allow more parallel work (faster, more risk)
- Conservative: Less parallel work (slower, safer)

**Priority Order**:
- Default: P0 > P1 > P2 > unlocking power
- Custom: Adjust priority weights
```

## Error Handling

- **No dependencies found**: Suggest all ready issues without dependency analysis
- **All issues blocked**: Show top blockers and recommend unblocking strategy
- **No ready issues**: Show what needs to close to unblock work
- **Over-capacity**: Warn and suggest prioritization

## Example Usage

```
/suggest-batch

# Analyzes project
# Shows optimal weekly batch
# Provides assignment recommendations
```

## Notes

- **Read-only**: No automatic assignments, just recommendations
- **AI-powered**: Uses dependency analysis + heuristics
- **Weekly cadence**: Run at sprint planning or weekly planning
- **Integrates with**: /velocity, /risk-check, dependency automation
