#!/usr/bin/env python3
"""
Risk Alert System - Automated Issue Risk Monitoring

Analyzes open issues and PRs for risk factors and posts alerts.
"""

import os
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from github import Github


# Configuration
RISK_THRESHOLDS = {
    'critical': 70,
    'high': 50,
    'medium': 30,
    'low': 0,
}

DAYS_OPEN_THRESHOLDS = {
    'P0': 3,
    'P1': 7,
    'P2': 14,
    'default': 21,
}

STALE_THRESHOLD_DAYS = 7
POST_COMMENTS = True  # Set to False to disable auto-commenting


def get_priority_label(labels: List) -> str:
    """Extract priority label from issue labels."""
    label_names = [label.name.lower() for label in labels]

    if any('p0' in name or 'critical' in name for name in label_names):
        return 'P0'
    elif any('p1' in name or 'high' in name for name in label_names):
        return 'P1'
    elif any('p2' in name or 'medium' in name for name in label_names):
        return 'P2'

    return 'default'


def is_blocked(issue) -> bool:
    """Check if issue is blocked."""
    body = issue.body or ''
    labels = [label.name.lower() for label in issue.labels]

    return 'BLOCKED:' in body.upper() or 'blocked' in labels


def extract_risk_description(issue) -> str:
    """Extract RISK: description from issue body."""
    body = issue.body or ''
    match = re.search(r'RISK:\s*(.+?)(?:\n|$)', body, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return ''


def calculate_risk_score(issue, now: datetime) -> Tuple[int, Dict]:
    """
    Calculate risk score (0-100) for an issue.
    Returns (score, factors) where factors explains the score.
    """
    factors = {}
    total_score = 0

    # A. Days Open Factor (max 30 points)
    created_at = issue.created_at.replace(tzinfo=timezone.utc)
    days_open = (now - created_at).days

    priority = get_priority_label(issue.labels)
    threshold = DAYS_OPEN_THRESHOLDS[priority]

    if days_open > threshold:
        days_over = days_open - threshold
        points = min(days_over * 2, 30)
        total_score += points
        factors['days_open'] = {
            'points': points,
            'days': days_open,
            'threshold': threshold,
            'priority': priority,
        }

    # B. Explicit Risk Marker (30 points)
    risk_desc = extract_risk_description(issue)
    if risk_desc:
        total_score += 30
        factors['explicit_risk'] = {
            'points': 30,
            'description': risk_desc,
        }

    # C. Stale Issue Factor (max 20 points)
    updated_at = issue.updated_at.replace(tzinfo=timezone.utc)
    days_since_update = (now - updated_at).days

    if days_since_update >= STALE_THRESHOLD_DAYS:
        points = min(days_since_update * 2, 20)
        total_score += points
        factors['stale'] = {
            'points': points,
            'days': days_since_update,
        }

    # D. No Comments Factor (15 points)
    if issue.comments == 0 and days_open > 2:
        total_score += 15
        factors['no_comments'] = {
            'points': 15,
        }

    # E. Milestone Deadline (max 20 points)
    if issue.milestone and issue.milestone.due_on:
        due_date = issue.milestone.due_on.replace(tzinfo=timezone.utc)
        days_until_due = (due_date - now).days

        if days_until_due <= 3:
            points = 20
        elif days_until_due <= 7:
            points = 15
        elif days_until_due <= 14:
            points = 10
        else:
            points = 0

        if points > 0:
            total_score += points
            factors['milestone_deadline'] = {
                'points': points,
                'milestone': issue.milestone.title,
                'days_until_due': days_until_due,
            }

    # F. Blocked (15 points)
    if is_blocked(issue):
        total_score += 15
        factors['blocked'] = {
            'points': 15,
        }

    # Normalize to 0-100 (max possible is 130)
    normalized_score = min(int((total_score / 130) * 100), 100)

    return normalized_score, factors


def classify_risk_level(score: int) -> Tuple[str, str]:
    """Return (emoji, level) for risk score."""
    if score >= RISK_THRESHOLDS['critical']:
        return '🔴', 'CRITICAL'
    elif score >= RISK_THRESHOLDS['high']:
        return '🟠', 'HIGH'
    elif score >= RISK_THRESHOLDS['medium']:
        return '🟡', 'MEDIUM'
    else:
        return '🟢', 'LOW'


def format_risk_factors(factors: Dict) -> str:
    """Format risk factors as markdown bullet points."""
    lines = []

    if 'days_open' in factors:
        f = factors['days_open']
        lines.append(
            f"⏰ Open for {f['days']} days "
            f"({f['priority']} threshold: {f['threshold']} days) "
            f"→ +{f['points']} pts"
        )

    if 'explicit_risk' in factors:
        f = factors['explicit_risk']
        lines.append(f"🚨 Marked with \"RISK: {f['description']}\" → +{f['points']} pts")

    if 'stale' in factors:
        f = factors['stale']
        lines.append(f"📅 No activity in {f['days']} days → +{f['points']} pts")

    if 'no_comments' in factors:
        f = factors['no_comments']
        lines.append(f"💬 No comments (might be blocked or unclear) → +{f['points']} pts")

    if 'milestone_deadline' in factors:
        f = factors['milestone_deadline']
        lines.append(
            f"🎯 Milestone \"{f['milestone']}\" due in {f['days_until_due']} days "
            f"→ +{f['points']} pts"
        )

    if 'blocked' in factors:
        f = factors['blocked']
        lines.append(f"🚧 Issue is blocked → +{f['points']} pts")

    return '\n'.join(f'- {line}' for line in lines)


def generate_recommendations(issue, factors: Dict) -> List[str]:
    """Generate actionable recommendations based on risk factors."""
    recommendations = []

    if 'days_open' in factors and factors['days_open']['priority'] == 'P0':
        recommendations.append('Assign to senior developer immediately')
        recommendations.append('Schedule sync meeting to unblock')

    if 'explicit_risk' in factors:
        recommendations.append('Review risk mitigation strategy')
        recommendations.append('Consider breaking into smaller, safer tasks')

    if 'stale' in factors:
        recommendations.append('Request status update from assignee')
        recommendations.append('Check if issue is still relevant')

    if 'no_comments' in factors:
        recommendations.append('Clarify requirements and acceptance criteria')
        recommendations.append('Add implementation guidance')

    if 'milestone_deadline' in factors:
        recommendations.append('Escalate if not on track for deadline')
        recommendations.append('Consider moving to next milestone if needed')

    if 'blocked' in factors:
        recommendations.append('Identify and prioritize blocker resolution')
        recommendations.append('Look for parallel work opportunities')

    if not recommendations:
        recommendations.append('Monitor progress in next standup')
        recommendations.append('Update issue status if any blockers arise')

    return recommendations


def post_risk_alert_comment(issue, score: int, emoji: str, level: str, factors: Dict):
    """Post a risk alert comment on the issue."""
    recommendations = generate_recommendations(issue, factors)

    comment_body = f"""🚨 **Risk Alert: {emoji} {level} Risk**

This issue has been identified as **{level}** risk (score: {score}/100).

**Risk Factors**:
{format_risk_factors(factors)}

**Recommended Actions**:
{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))}

Please update status or request help if needed.

---
🤖 *Generated by Risk Alert System - Run `/risk-check` for full report*
"""

    # Check if we already posted a risk alert recently
    existing_comments = list(issue.get_comments())

    for comment in existing_comments[-5:]:  # Check last 5 comments
        if '🚨 **Risk Alert:' in comment.body:
            # Already has recent alert, don't spam
            print(f"  ℹ️  Issue #{issue.number} already has risk alert, skipping")
            return

    # Post the comment
    issue.create_comment(comment_body)
    print(f"  ✅ Posted risk alert on issue #{issue.number}")


def analyze_repository(repo, now: datetime):
    """Analyze all open issues in repository."""
    print(f"🔍 Analyzing repository: {repo.full_name}")

    # Fetch all open issues
    open_issues = list(repo.get_issues(state='open'))

    # Filter out PRs
    issues_only = [issue for issue in open_issues if not issue.pull_request]

    print(f"📊 Found {len(issues_only)} open issues")

    # Analyze each issue
    risk_issues = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': [],
    }

    for issue in issues_only:
        score, factors = calculate_risk_score(issue, now)
        emoji, level = classify_risk_level(score)

        risk_data = {
            'issue': issue,
            'number': issue.number,
            'title': issue.title,
            'score': score,
            'emoji': emoji,
            'level': level,
            'factors': factors,
            'url': issue.html_url,
        }

        if level == 'CRITICAL':
            risk_issues['critical'].append(risk_data)
        elif level == 'HIGH':
            risk_issues['high'].append(risk_data)
        elif level == 'MEDIUM':
            risk_issues['medium'].append(risk_data)
        else:
            risk_issues['low'].append(risk_data)

    # Sort by score (highest first)
    for level in risk_issues:
        risk_issues[level].sort(key=lambda x: x['score'], reverse=True)

    return risk_issues


def generate_summary_report(risk_issues: Dict) -> str:
    """Generate markdown summary report."""
    critical_count = len(risk_issues['critical'])
    high_count = len(risk_issues['high'])
    medium_count = len(risk_issues['medium'])
    low_count = len(risk_issues['low'])

    total = critical_count + high_count + medium_count + low_count

    lines = [
        f"# 🚨 Risk Alert Summary",
        f"",
        f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Open Issues Analyzed**: {total}",
        f"",
        f"## 📊 Risk Breakdown",
        f"",
        f"- 🔴 **CRITICAL**: {critical_count} issues (need immediate attention)",
        f"- 🟠 **HIGH**: {high_count} issues (at risk of causing delays)",
        f"- 🟡 **MEDIUM**: {medium_count} issues (monitor closely)",
        f"- 🟢 **LOW**: {low_count} issues (normal progress)",
        f"",
    ]

    # Overall health
    if critical_count > 0:
        health = "🔴 CRITICAL - Immediate action required"
    elif high_count > 3:
        health = "🟠 AT RISK - Multiple issues need attention"
    elif high_count > 0 or medium_count > 5:
        health = "🟡 MONITOR - Some issues need attention"
    else:
        health = "🟢 GOOD - All issues progressing normally"

    lines.append(f"**Overall Project Health**: {health}")
    lines.append("")

    # List critical issues
    if critical_count > 0:
        lines.append("## 🔴 CRITICAL Issues")
        lines.append("")

        for risk_data in risk_issues['critical'][:5]:  # Top 5
            lines.append(f"### Issue #{risk_data['number']}: {risk_data['title']}")
            lines.append(f"**Risk Score**: {risk_data['score']}/100")
            lines.append("")
            lines.append("**Risk Factors**:")
            lines.append(format_risk_factors(risk_data['factors']))
            lines.append("")
            lines.append(f"**Links**: [View Issue]({risk_data['url']})")
            lines.append("")

    # List high issues (summary)
    if high_count > 0:
        lines.append("## 🟠 HIGH Risk Issues")
        lines.append("")

        for risk_data in risk_issues['high'][:3]:  # Top 3
            lines.append(
                f"- [#{risk_data['number']}]({risk_data['url']}): "
                f"{risk_data['title']} (Score: {risk_data['score']}/100)"
            )

        if high_count > 3:
            lines.append(f"- ...and {high_count - 3} more")

        lines.append("")

    lines.append("---")
    lines.append("🤖 *Run `/risk-check` in Claude Code for full report*")

    return '\n'.join(lines)


def main():
    """Main execution."""
    # Get environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    repository = os.environ.get('REPOSITORY')

    if not github_token or not repository:
        print("❌ Error: GITHUB_TOKEN and REPOSITORY environment variables required")
        return 1

    # Initialize GitHub API
    g = Github(github_token)
    repo = g.get_repo(repository)

    now = datetime.now(timezone.utc)

    # Analyze repository
    risk_issues = analyze_repository(repo, now)

    # Generate summary
    summary = generate_summary_report(risk_issues)

    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60 + "\n")

    # Post alerts on critical issues
    if POST_COMMENTS:
        critical_issues = risk_issues['critical']

        if critical_issues:
            print(f"\n📬 Posting alerts on {len(critical_issues)} critical issues...")

            for risk_data in critical_issues:
                post_risk_alert_comment(
                    risk_data['issue'],
                    risk_data['score'],
                    risk_data['emoji'],
                    risk_data['level'],
                    risk_data['factors'],
                )
        else:
            print("\n✅ No critical issues found - no alerts to post")

    # Save report as JSON artifact
    report_data = {
        'generated_at': now.isoformat(),
        'repository': repository,
        'summary': {
            'critical': len(risk_issues['critical']),
            'high': len(risk_issues['high']),
            'medium': len(risk_issues['medium']),
            'low': len(risk_issues['low']),
        },
        'critical_issues': [
            {
                'number': r['number'],
                'title': r['title'],
                'score': r['score'],
                'url': r['url'],
                'factors': r['factors'],
            }
            for r in risk_issues['critical']
        ],
        'high_issues': [
            {
                'number': r['number'],
                'title': r['title'],
                'score': r['score'],
                'url': r['url'],
            }
            for r in risk_issues['high']
        ],
    }

    with open('risk_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)

    print("\n💾 Risk report saved to risk_report.json")

    # Exit with error code if critical issues found
    if risk_issues['critical']:
        print(f"\n⚠️  WARNING: {len(risk_issues['critical'])} CRITICAL issues require attention!")
        return 1  # Fail the workflow to draw attention

    return 0


if __name__ == '__main__':
    exit(main())
