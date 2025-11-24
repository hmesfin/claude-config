---
description: "AI-powered contractor assignment suggestions based on skills, workload, and performance"
---

# Contractor Assignment Intelligence Command

Suggests optimal contractor assignments based on skill matching, workload balancing, and historical performance.

## Instructions

1. **Load Contractor Profiles**:

   Look for `.contractors.yml` in:
   - Project root (`./.contractors.yml`)
   - Claude config (`~/.claude/.contractors.yml`)
   - Example template (`~/.claude-config/.contractors.example.yml`)

   If not found, show error:
   ```
   ❌ No contractor profiles found!

   Create .contractors.yml in your project root:
   cp ~/.claude-config/.contractors.example.yml ./.contractors.yml

   Then customize with your team's skills and preferences.
   ```

2. **Detect Repository**:
   - Get current git repository (owner/repo) from `git remote get-url origin`
   - Parse GitHub URL to extract owner and repo name

3. **Fetch Open Issues**:
   - Use GitHub MCP: `list_issues(owner, repo, state='open')`
   - Filter out pull requests
   - Separate into:
     - **Unassigned**: No assignee yet
     - **Assigned**: Already has assignee (for workload calculation)

4. **Analyze Current Workload**:

   For each contractor:
   ```python
   current_issues = [i for i in assigned_issues if i.assignee == contractor.github_username]

   workload = {
       'contractor': contractor.name,
       'current_issues': len(current_issues),
       'capacity': contractor.preferences.max_concurrent_issues,
       'available_capacity': capacity - len(current_issues),
       'issues': current_issues,
   }
   ```

5. **Extract Issue Requirements**:

   For each unassigned issue:
   ```python
   requirements = {
       'labels': issue.labels,  # Extract skill requirements
       'complexity': estimate_complexity(issue),
       'priority': extract_priority(issue.labels),
       'estimated_hours': extract_estimate(issue.body),
       'domain': identify_domain(issue.labels),  # backend, frontend, mobile, etc.
       'has_risk': 'RISK:' in issue.body,
   }
   ```

   **Complexity Estimation**:
   - **Simple**: Labels include 'simple', 'crud', 'ui-only', or body mentions <200 lines
   - **Medium**: No complexity labels, standard business logic
   - **Complex**: Labels include 'complex', 'architecture', 'security', or >500 lines

6. **Calculate Assignment Scores**:

   For each (issue, contractor) pair:

   **A. Skill Match Score (0-100)**:
   ```python
   issue_skills = set(issue.labels)
   contractor_skills = set(contractor.skills)

   # Direct matches
   matches = issue_skills & contractor_skills
   skill_match_ratio = len(matches) / max(len(issue_skills), 1)

   # Bonus for specialty match
   if issue.domain == contractor.specialty:
       specialty_bonus = 20
   else:
       specialty_bonus = 0

   # Penalty for avoid labels
   avoid_penalty = 0
   if any(label in contractor.preferences.avoid_labels for label in issue.labels):
       avoid_penalty = -30

   skill_score = (skill_match_ratio * 80) + specialty_bonus + avoid_penalty
   skill_score = max(0, min(100, skill_score))
   ```

   **B. Availability Score (0-100)**:
   ```python
   available = contractor.workload.available_capacity
   max_capacity = contractor.preferences.max_concurrent_issues

   if available <= 0:
       availability_score = 0  # Fully loaded
   elif available == max_capacity:
       availability_score = 100  # Completely free
   else:
       availability_score = (available / max_capacity) * 100
   ```

   **C. Velocity Score (0-100)**:
   ```python
   # Normalize velocity to 0-100 scale
   # Higher velocity = higher score (but consider issue complexity)

   if issue.complexity == 'complex':
       # For complex issues, slower but thorough contractors score higher
       if contractor.velocity.avg_time_to_complete > 5:
           velocity_score = 90  # Prefer thorough approach
       else:
           velocity_score = 60  # Fast contractors may rush
   else:
       # For simple/medium issues, faster is better
       issues_per_week = contractor.velocity.issues_per_week
       velocity_score = min(issues_per_week * 40, 100)
   ```

   **D. Performance Score (0-100)**:
   ```python
   # Weighted average of quality, reliability, communication
   quality = contractor.performance.quality_score * 10
   reliability = contractor.performance.reliability_score * 10
   communication = contractor.performance.communication_score * 10

   performance_score = (quality * 0.5 + reliability * 0.3 + communication * 0.2)
   ```

   **E. Complexity Match Score (0-100)**:
   ```python
   if issue.complexity == 'complex':
       if contractor.preferences.get('prefers_complex', False):
           complexity_match = 100
       else:
           complexity_match = 40
   elif issue.complexity == 'simple':
       if contractor.preferences.get('prefers_simple', False):
           complexity_match = 100
       else:
           complexity_match = 60
   else:  # medium
       complexity_match = 80  # Most contractors ok with medium
   ```

   **F. Total Score (Weighted)**:
   ```python
   weights = team.weights  # From config

   total_score = (
       skill_score * weights.skill_match +
       availability_score * weights.availability +
       velocity_score * weights.velocity +
       complexity_match * weights.specialty_match
   )

   # Adjust for performance (multiplier)
   performance_multiplier = performance_score / 100
   final_score = total_score * performance_multiplier
   ```

7. **Rank and Suggest**:

   For each unassigned issue:
   - Calculate scores for all contractors
   - Sort by final_score (highest first)
   - Filter contractors with available_capacity > 0
   - Filter scores above min_score_threshold (default 70)

8. **Generate Report**:

   ```markdown
   # 🎯 Contractor Assignment Suggestions

   **Generated**: [Date & Time]
   **Repository**: [owner/repo]
   **Unassigned Issues**: X
   **Available Contractors**: Y (Z with capacity)

   ---

   ## 📊 Current Workload

   **Contractor A (Alex Chen)**:
   - Current: 2/2 issues (at capacity)
   - In Progress: #45, #67
   - Available: ❌ No capacity

   **Contractor B (Maria Rodriguez)**:
   - Current: 1/3 issues (33% capacity)
   - In Progress: #89
   - Available: ✅ 2 slots

   **Contractor C (Jordan Kim)**:
   - Current: 0/1 issues (0% capacity)
   - In Progress: None
   - Available: ✅ 1 slot

   ---

   ## 🎯 Assignment Recommendations

   ### Issue #123: Implement real-time WebSocket notifications

   **Top Match: Contractor A - Alex Chen** (Score: 92/100)
   - ✅ **Skills**: Perfect match (websockets, real-time, backend)
   - ⚠️ **Availability**: At capacity (2/2 issues) - wait for slot
   - ✅ **Velocity**: 1.5 issues/week (good for complex work)
   - ✅ **Specialty**: Backend (matches issue domain)
   - ✅ **Performance**: 9.5/10 quality, 9.0/10 reliability

   **Why this match**:
   - Expert in WebSockets and real-time systems
   - Has completed 3 similar issues with 9.5/10 quality
   - Prefers complex backend work
   - **Recommendation**: Wait for slot or assign if urgent

   **Alternative: Contractor B - Maria Rodriguez** (Score: 58/100)
   - ⚠️ **Skills**: Partial match (javascript, frontend)
   - ✅ **Availability**: 2 slots available (1/3 capacity)
   - ✅ **Velocity**: 2.0 issues/week (faster)
   - ❌ **Specialty**: Mobile (not backend)
   - ✅ **Performance**: 8.5/10 quality, 9.5/10 reliability

   **Why lower score**:
   - Missing key skills (websockets, real-time backend)
   - Specialty mismatch (mobile vs backend)
   - Could complete faster but may lack expertise

   ---

   ### Issue #156: Mobile calendar UI component

   **Top Match: Contractor B - Maria Rodriguez** (Score: 95/100) ⭐
   - ✅ **Skills**: Perfect match (react-native, mobile, ui)
   - ✅ **Availability**: 2 slots available
   - ✅ **Velocity**: 2.0 issues/week (fast for simple work)
   - ✅ **Specialty**: Mobile (exact match!)
   - ✅ **Performance**: 8.5/10 quality, 9.5/10 reliability

   **Why this match**:
   - Mobile specialist with UI expertise
   - Has completed 15 mobile issues with avg 1.8 review iterations
   - Available immediately (2 open slots)
   - Fast velocity for simple UI work
   - **Recommendation**: ✅ ASSIGN NOW

   **Action**:
   ```bash
   gh issue edit 156 --add-assignee mariarodriguez
   ```

   ---

   ### Issue #201: Security audit and RBAC implementation

   **Top Match: Contractor C - Jordan Kim** (Score: 98/100) ⭐⭐
   - ✅ **Skills**: Perfect match (security, rbac, authentication)
   - ✅ **Availability**: 1 slot available (0/1 capacity)
   - ✅ **Velocity**: 1.0 issues/week (thorough for complex)
   - ✅ **Specialty**: Security (exact match!)
   - ✅ **Performance**: 10.0/10 quality, 8.0/10 reliability

   **Why this match**:
   - Security specialist with perfect quality record
   - Prefers complex, high-stakes work
   - Available immediately
   - Slower but exceptional thoroughness
   - **Recommendation**: ✅ ASSIGN NOW (critical work)

   **Action**:
   ```bash
   gh issue edit 201 --add-assignee jordankim
   ```

   **Special Note**:
   - This is high-risk work - worth waiting for specialist
   - Jordan's 10/10 quality ensures secure implementation

   ---

   ## 📋 Quick Assignment Summary

   | Issue | Title | Best Match | Score | Available | Action |
   |-------|-------|------------|-------|-----------|--------|
   | #123 | WebSocket notifications | Alex Chen | 92 | ❌ | Wait |
   | #156 | Calendar UI | Maria Rodriguez | 95 | ✅ | Assign |
   | #201 | Security RBAC | Jordan Kim | 98 | ✅ | Assign |
   | #178 | API endpoints | Alex Chen | 88 | ❌ | Wait |
   | #190 | Settings page | Maria Rodriguez | 91 | ✅ | Assign |

   ---

   ## 💡 Workload Optimization

   **Immediate Actions** (contractors with capacity):
   - ✅ Assign #156 to Maria Rodriguez (mobile)
   - ✅ Assign #201 to Jordan Kim (security)
   - ✅ Assign #190 to Maria Rodriguez (ui)

   **Queued for Later** (wait for capacity):
   - ⏳ #123 for Alex Chen (when slot opens)
   - ⏳ #178 for Alex Chen (backend work)

   **Expected Completion**:
   - Maria: 2 issues @ 2/week = ~1 week
   - Jordan: 1 issue @ 1/week = ~1 week
   - Alex: Available in ~3 days (current velocity)

   **Capacity Utilization**:
   - Current: 3/6 slots (50%)
   - After assignments: 6/6 slots (100% - optimal!)

   ---

   ## 🎯 Strategic Recommendations

   **Balance Check**: 🟢 Good
   - All contractors will have work
   - Capacity fully utilized
   - Skill-to-task matching is excellent

   **Bottleneck Alert**: 🟡 Backend
   - 2 backend issues waiting for Alex Chen
   - Consider: Cross-train Maria on backend OR hire backend specialist

   **Velocity Forecast**:
   - With current assignments: 4 issues complete in 1 week
   - Matches team capacity (4.5 issues/week)

   ---

   ## 🔧 Auto-Assignment Actions

   To auto-assign the recommended contractors:

   ```bash
   # Option 1: Auto-assign all recommendations
   gh issue edit 156 --add-assignee mariarodriguez
   gh issue edit 201 --add-assignee jordankim
   gh issue edit 190 --add-assignee mariarodriguez

   # Option 2: One at a time
   gh issue edit 156 --add-assignee mariarodriguez
   # ... (assign others after first completes)
   ```

   Or run: `/assign-contractor --auto` (if enabled in config)

   ---

   *🎯 Run `/assign-contractor` weekly for optimal team utilization*
   *📊 Update .contractors.yml with actual velocity data for better matching*
   ```

9. **Detailed Explanations**:

   For each recommendation, explain:
   - **Skill Match**: Which skills align, which are missing
   - **Availability**: Current workload, time to availability
   - **Velocity Match**: Why this contractor's pace fits the issue
   - **Specialty Bonus**: If issue matches their expertise
   - **Performance History**: Track record on similar issues
   - **Risk Assessment**: Any concerns with this match

10. **Alternative Suggestions**:

    Show 2nd and 3rd best matches with lower scores and why they're less ideal

11. **Capacity Planning**:

    ```markdown
    ## 📊 Team Capacity Analysis

    **Current Utilization**: 50% (3/6 slots)
    **After Assignments**: 100% (6/6 slots)

    **Velocity Forecast** (next 2 weeks):
    - Week 1: 4.5 issues complete (Maria: 2, Alex: 1.5, Jordan: 1)
    - Week 2: 4.5 issues complete (same pace)

    **Bottlenecks**:
    - Backend: 2 issues queued for Alex
    - Mobile: No bottleneck (Maria has capacity)
    - Security: No bottleneck (Jordan available)

    **Recommendations**:
    1. Assign Maria to #156, #190 immediately
    2. Assign Jordan to #201 immediately
    3. Queue #123, #178 for Alex (3-day wait)
    4. Consider: Hire additional backend contractor for faster backend velocity
    ```

## Configuration

### Contractor Profile (.contractors.yml)

Required fields:
```yaml
contractors:
  contractor_id:
    name: "Full Name"
    github_username: "username"
    skills: [list, of, skills]
    specialty: "primary_domain"
    velocity:
      issues_per_week: 1.5
    preferences:
      max_concurrent_issues: 2
    performance:
      quality_score: 9.0
      reliability_score: 8.5
```

### Customization

Edit `.contractors.yml`:

**Add Contractor**:
```yaml
contractors:
  new_contractor:
    name: "New Person"
    # ... full profile
```

**Update Skills**:
```yaml
skills:
  - python
  - django
  - new-skill  # Add here
```

**Adjust Weights**:
```yaml
team:
  weights:
    skill_match: 0.50      # Increase for skill-first matching
    availability: 0.20     # Decrease if skills matter more than availability
```

## Error Handling

- **No contractor profiles**: Show setup instructions
- **No unassigned issues**: "All issues assigned! Run `/risk-check` to monitor."
- **All contractors at capacity**: Show queued assignments with wait times
- **No good matches**: Show all contractors with explanation of why scores are low

## Example Usage

```
/assign-contractor

# Analyzes all unassigned issues
# Shows optimal assignments
# Provides workload analysis
```

**With auto-assignment** (if enabled):
```
/assign-contractor --auto

# Same analysis + automatically assigns via GitHub
```

## Integration

Works seamlessly with:
- `/suggest-batch` - Get batch, then use this to assign optimally
- `/risk-check` - Identify issues needing urgent assignment
- `/velocity` - Track if assignments match actual capacity

**Workflow**:
```bash
# Monday planning
/suggest-batch          # Get weekly batch
/assign-contractor      # Assign to optimal contractors
gh issue edit X --add-assignee username  # Execute assignments

# During week
/risk-check             # Monitor progress

# Friday review
/velocity               # Verify completion rates
```

## Notes

- **Read-only by default**: No auto-assignments unless `--auto` flag used
- **Learning system**: Update profiles quarterly with actual velocity data
- **Skill evolution**: Add new skills as contractors learn
- **Fair distribution**: Algorithm balances workload while optimizing matches
