#!/usr/bin/env python3
"""
Risk Alert System

Proactively identifies issues at risk of causing delays by calculating
risk scores based on:
- Days open vs priority threshold
- Explicit RISK: markers in issue body
- Stale issues (no recent updates)
- No comments/engagement
- Approaching milestone deadlines
- Blocked status

Usage:
    python risk_check.py
    python risk_check.py --json           # Output as JSON
    python risk_check.py --critical-only  # Show only critical issues
    python risk_check.py --post-alerts    # Post warning comments to issues
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from pm_utils import (
    get_repo_info,
    fetch_issues,
    fetch_prs,
    parse_date,
    days_ago,
    extract_labels,
    get_priority,
    print_header,
    print_section,
    run_gh_command,
    PRIORITY_THRESHOLDS,
    RISK_WEIGHTS,
)


def calculate_days_open_score(issue: dict, priority: str) -> tuple[int, str]:
    """Calculate risk score based on days open vs priority threshold."""
    created = parse_date(issue.get("createdAt", ""))
    if not created:
        return 0, ""

    days_open = days_ago(created)
    threshold = PRIORITY_THRESHOLDS.get(priority, 21)

    if days_open <= threshold:
        return 0, ""

    # Calculate points: 2 points per day over threshold, max 30
    excess_days = days_open - threshold
    points = min(excess_days * 2, RISK_WEIGHTS["days_open"])

    reason = f"Open {days_open} days ({priority} threshold: {threshold} days)"
    return points, reason


def calculate_risk_marker_score(issue: dict) -> tuple[int, str]:
    """Check for explicit RISK: marker in issue body."""
    body = issue.get("body", "") or ""

    # Look for RISK: marker (case insensitive)
    risk_match = re.search(r"RISK:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)

    if risk_match:
        risk_description = risk_match.group(1).strip()[:50]  # Truncate
        return RISK_WEIGHTS["risk_marker"], f"Marked with RISK: {risk_description}"

    return 0, ""


def calculate_stale_score(issue: dict) -> tuple[int, str]:
    """Calculate risk score for stale issues."""
    updated = parse_date(issue.get("updatedAt", ""))
    if not updated:
        return 0, ""

    days_since_update = days_ago(updated)

    if days_since_update < 7:
        return 0, ""

    # 2 points per day stale, max 20
    points = min(days_since_update * 2, RISK_WEIGHTS["stale"])
    return points, f"No activity in {days_since_update} days"


def calculate_no_comments_score(issue: dict) -> tuple[int, str]:
    """Calculate risk score for issues with no comments."""
    comments = issue.get("comments", 0)
    created = parse_date(issue.get("createdAt", ""))

    if not created:
        return 0, ""

    days_open = days_ago(created)

    # Only penalize if open > 2 days with no comments
    if comments == 0 and days_open > 2:
        return RISK_WEIGHTS["no_comments"], f"No comments after {days_open} days"

    return 0, ""


def calculate_deadline_score(issue: dict) -> tuple[int, str]:
    """Calculate risk score for approaching milestone deadline."""
    milestone = issue.get("milestone")
    if not milestone or not milestone.get("dueOn"):
        return 0, ""

    due_date = parse_date(milestone["dueOn"])
    if not due_date:
        return 0, ""

    now = datetime.now(due_date.tzinfo) if due_date.tzinfo else datetime.now()
    days_until_due = (due_date - now).days

    if days_until_due < 0:
        return RISK_WEIGHTS["deadline"], f"Milestone overdue by {abs(days_until_due)} days"
    elif days_until_due <= 3:
        return RISK_WEIGHTS["deadline"], f"Milestone due in {days_until_due} days"
    elif days_until_due <= 7:
        return 15, f"Milestone due in {days_until_due} days"
    elif days_until_due <= 14:
        return 10, f"Milestone due in {days_until_due} days"

    return 0, ""


def calculate_blocked_score(issue: dict) -> tuple[int, str]:
    """Calculate risk score for blocked issues."""
    labels = extract_labels(issue)
    body = issue.get("body", "") or ""

    # Check for blocked label
    if any("blocked" in l.lower() for l in labels):
        return RISK_WEIGHTS["blocked"], "Has 'blocked' label"

    # Check for BLOCKED: marker in body
    if re.search(r"BLOCKED:", body, re.IGNORECASE):
        blocked_match = re.search(r"BLOCKED:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
        if blocked_match:
            blocker = blocked_match.group(1).strip()[:30]
            return RISK_WEIGHTS["blocked"], f"Blocked by: {blocker}"

    return 0, ""


def calculate_risk_score(issue: dict) -> dict:
    """Calculate total risk score for an issue."""
    labels = extract_labels(issue)
    priority = get_priority(labels)

    # Calculate each component
    components = []

    days_score, days_reason = calculate_days_open_score(issue, priority)
    if days_score > 0:
        components.append({"factor": "days_open", "points": days_score, "reason": days_reason})

    risk_score, risk_reason = calculate_risk_marker_score(issue)
    if risk_score > 0:
        components.append({"factor": "risk_marker", "points": risk_score, "reason": risk_reason})

    stale_score, stale_reason = calculate_stale_score(issue)
    if stale_score > 0:
        components.append({"factor": "stale", "points": stale_score, "reason": stale_reason})

    comments_score, comments_reason = calculate_no_comments_score(issue)
    if comments_score > 0:
        components.append({"factor": "no_comments", "points": comments_score, "reason": comments_reason})

    deadline_score, deadline_reason = calculate_deadline_score(issue)
    if deadline_score > 0:
        components.append({"factor": "deadline", "points": deadline_score, "reason": deadline_reason})

    blocked_score, blocked_reason = calculate_blocked_score(issue)
    if blocked_score > 0:
        components.append({"factor": "blocked", "points": blocked_score, "reason": blocked_reason})

    # Calculate total (max theoretical is 130, normalize to 0-100)
    raw_total = sum(c["points"] for c in components)
    max_possible = sum(RISK_WEIGHTS.values())
    normalized_score = min(int((raw_total / max_possible) * 100), 100)

    # Determine risk level
    if normalized_score >= 70:
        level = "CRITICAL"
        emoji = "🔴"
    elif normalized_score >= 50:
        level = "HIGH"
        emoji = "🟠"
    elif normalized_score >= 30:
        level = "MEDIUM"
        emoji = "🟡"
    else:
        level = "LOW"
        emoji = "🟢"

    return {
        "number": issue.get("number"),
        "title": issue.get("title", ""),
        "priority": priority,
        "score": normalized_score,
        "level": level,
        "emoji": emoji,
        "components": components,
        "assignees": [a.get("login", "") for a in issue.get("assignees", [])],
        "labels": labels,
        "created_at": issue.get("createdAt"),
        "updated_at": issue.get("updatedAt"),
    }


def get_recommendations(risk_data: dict) -> list[str]:
    """Generate recommendations based on risk factors."""
    recommendations = []
    components = {c["factor"]: c for c in risk_data["components"]}

    if "days_open" in components:
        recommendations.append("Review and prioritize - open longer than expected for priority level")

    if "risk_marker" in components:
        recommendations.append("Address documented risk immediately")

    if "stale" in components:
        recommendations.append("Request status update from assignee or reassign")

    if "no_comments" in components:
        recommendations.append("Add clarifying comments or acceptance criteria")

    if "deadline" in components:
        recommendations.append("Milestone at risk - consider scope reduction or deadline extension")

    if "blocked" in components:
        recommendations.append("Resolve blocker or find alternative approach")

    if not risk_data["assignees"]:
        recommendations.append("Assign to team member")

    return recommendations


def analyze_pr_risks(owner: str, repo: str) -> list[dict]:
    """Analyze open PRs for risk factors."""
    prs = fetch_prs(owner, repo, state="open")
    risky_prs = []

    for pr in prs:
        risk_factors = []

        # Large PR
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions

        if total_changes > 500:
            risk_factors.append(f"Large PR: {total_changes} lines changed")

        # Stale PR
        updated = parse_date(pr.get("updatedAt", ""))
        if updated and days_ago(updated) > 7:
            risk_factors.append(f"Stale: no activity in {days_ago(updated)} days")

        # Many files
        files_changed = pr.get("changedFiles", 0)
        if files_changed > 15:
            risk_factors.append(f"Touches {files_changed} files")

        # Check labels for complexity
        labels = [l.get("name", "") for l in pr.get("labels", [])]
        if any("complex" in l.lower() for l in labels):
            risk_factors.append("Marked as complex")

        if risk_factors:
            risky_prs.append({
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "author": pr.get("author", {}).get("login", "unknown"),
                "changes": total_changes,
                "files": files_changed,
                "risk_factors": risk_factors,
            })

    return risky_prs


def generate_risk_report(
    owner: str,
    repo: str,
    output_json: bool = False,
    critical_only: bool = False,
    post_alerts: bool = False,
) -> dict:
    """Generate the risk report."""
    issues = fetch_issues(owner, repo, state="open")

    if not issues:
        print("No open issues found.")
        return {}

    # Calculate risk for each issue
    risk_results = [calculate_risk_score(issue) for issue in issues]

    # Sort by score (highest first)
    risk_results.sort(key=lambda x: x["score"], reverse=True)

    # Categorize by level
    categorized = defaultdict(list)
    for result in risk_results:
        categorized[result["level"]].append(result)

    # Get PR risks
    pr_risks = analyze_pr_risks(owner, repo)

    # Determine overall health
    critical_count = len(categorized["CRITICAL"])
    high_count = len(categorized["HIGH"])

    if critical_count > 0:
        health = "🔴 CRITICAL"
    elif high_count > 3:
        health = "🟠 AT RISK"
    elif high_count > 0:
        health = "🟡 NEEDS ATTENTION"
    else:
        health = "🟢 GOOD"

    report = {
        "generated": datetime.now().isoformat(),
        "repository": f"{owner}/{repo}",
        "health": health,
        "summary": {
            "total_analyzed": len(issues),
            "critical": critical_count,
            "high": high_count,
            "medium": len(categorized["MEDIUM"]),
            "low": len(categorized["LOW"]),
        },
        "issues": {
            "critical": categorized["CRITICAL"],
            "high": categorized["HIGH"],
            "medium": categorized["MEDIUM"],
            "low": categorized["LOW"],
        },
        "pr_risks": pr_risks,
    }

    # Add recommendations to each issue
    for level in ["critical", "high", "medium"]:
        for issue in report["issues"][level]:
            issue["recommendations"] = get_recommendations(issue)

    if output_json:
        import json
        print(json.dumps(report, indent=2, default=str))
    else:
        print_risk_report(report, owner, repo, critical_only)

    # Post alerts if requested
    if post_alerts and categorized["CRITICAL"]:
        post_risk_alerts(owner, repo, categorized["CRITICAL"])

    return report


def print_risk_report(report: dict, owner: str, repo: str, critical_only: bool) -> None:
    """Print formatted risk report."""
    print_header(f"Risk Alert Report: {owner}/{repo}")

    summary = report["summary"]

    # Summary
    print_section("📊 Risk Summary")
    print(f"- 🔴 **CRITICAL**: {summary['critical']} issues")
    print(f"- 🟠 **HIGH**: {summary['high']} issues")
    print(f"- 🟡 **MEDIUM**: {summary['medium']} issues")
    print(f"- 🟢 **LOW**: {summary['low']} issues")
    print(f"\n**Overall Project Health**: {report['health']}")

    # Critical Issues
    if report["issues"]["critical"]:
        print_section("🔴 CRITICAL Risk Issues")
        for issue in report["issues"]["critical"]:
            print_issue_risk(issue, owner, repo)

    # High Issues
    if not critical_only and report["issues"]["high"]:
        print_section("🟠 HIGH Risk Issues")
        for issue in report["issues"]["high"]:
            print_issue_risk(issue, owner, repo)

    # Medium Issues (brief)
    if not critical_only and report["issues"]["medium"]:
        print_section("🟡 MEDIUM Risk Issues")
        for issue in report["issues"]["medium"][:5]:  # Top 5 only
            print(f"- #{issue['number']}: {issue['title'][:50]}... (Score: {issue['score']})")
        if len(report["issues"]["medium"]) > 5:
            print(f"  ... and {len(report['issues']['medium']) - 5} more")

    # PR Risks
    if report["pr_risks"]:
        print_section("🔧 PR Risks")
        for pr in report["pr_risks"][:5]:
            print(f"\n**PR #{pr['number']}**: {pr['title'][:50]}")
            print(f"  Author: @{pr['author']} | {pr['changes']} lines | {pr['files']} files")
            for factor in pr["risk_factors"]:
                print(f"  ⚠️ {factor}")

    # Action Items
    print_section("🎯 Immediate Action Items")
    critical = report["issues"]["critical"]
    high = report["issues"]["high"]

    if critical:
        print(f"\n1. **Triage CRITICAL issues within 24 hours**")
        print(f"   Issues: {', '.join(f'#{i[\"number\"]}' for i in critical)}")

    if high:
        print(f"\n2. **Review HIGH risk issues this week**")
        print(f"   Issues: {', '.join(f'#{i[\"number\"]}' for i in high[:5])}")

    print("\n" + "=" * 60)
    print("🚨 Run `/risk-check` daily to stay ahead of problems")
    print("=" * 60)


def print_issue_risk(issue: dict, owner: str, repo: str) -> None:
    """Print detailed risk info for a single issue."""
    print(f"\n### Issue #{issue['number']}: {issue['title'][:50]}")
    print(f"**Risk Score**: {issue['score']}/100 | **Priority**: {issue['priority']}")

    if issue["assignees"]:
        print(f"**Assignees**: {', '.join(f'@{a}' for a in issue['assignees'])}")
    else:
        print("**Assignees**: ⚠️ Unassigned")

    print("\n**Why it's risky**:")
    for component in issue["components"]:
        print(f"  - {component['reason']} (+{component['points']} pts)")

    if issue.get("recommendations"):
        print("\n**Recommended Actions**:")
        for i, rec in enumerate(issue["recommendations"], 1):
            print(f"  {i}. {rec}")

    print(f"\n[View Issue](https://github.com/{owner}/{repo}/issues/{issue['number']})")


def post_risk_alerts(owner: str, repo: str, critical_issues: list[dict]) -> None:
    """Post warning comments on critical issues."""
    print("\n📢 Posting alerts to critical issues...")

    for issue in critical_issues:
        comment = f"""🚨 **Risk Alert**

This issue has been identified as **CRITICAL** risk (score: {issue['score']}/100).

**Risk Factors**:
"""
        for comp in issue["components"]:
            comment += f"- {comp['reason']}\n"

        comment += "\n**Recommended Actions**:\n"
        for i, rec in enumerate(issue.get("recommendations", []), 1):
            comment += f"{i}. {rec}\n"

        comment += "\n---\n🤖 Generated by Risk Alert System - `/risk-check`"

        # Post comment via gh CLI
        result = run_gh_command([
            "issue", "comment", str(issue["number"]),
            "--repo", f"{owner}/{repo}",
            "--body", comment,
        ])

        if result is not None:
            print(f"  ✅ Posted alert to #{issue['number']}")
        else:
            print(f"  ❌ Failed to post alert to #{issue['number']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate risk alert report for project issues",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Show only critical issues",
    )
    parser.add_argument(
        "--post-alerts",
        action="store_true",
        help="Post warning comments to critical issues",
    )
    parser.add_argument(
        "--repo",
        help="Repository in owner/repo format",
    )

    args = parser.parse_args()

    if args.repo:
        parts = args.repo.split("/")
        if len(parts) != 2:
            print("Error: Repository must be in owner/repo format")
            sys.exit(1)
        owner, repo = parts
    else:
        owner, repo = get_repo_info()

    generate_risk_report(
        owner,
        repo,
        args.json,
        args.critical_only,
        args.post_alerts,
    )


if __name__ == "__main__":
    main()
