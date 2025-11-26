#!/usr/bin/env python3
"""
Velocity Dashboard Generator

Generates comprehensive project velocity metrics including:
- Overall progress (issues completed vs total)
- Velocity calculation (issues per week, rolling average)
- Phase breakdown with progress bars
- Milestone tracking
- Completion projections

Usage:
    python velocity.py
    python velocity.py --json           # Output as JSON
    python velocity.py --save           # Save to .claude/velocity-history.json
"""

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# Add scripts directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from pm_utils import (
    get_repo_info,
    fetch_issues,
    parse_date,
    days_ago,
    format_progress_bar,
    group_by_week,
    extract_labels,
    print_header,
    print_section,
    save_json_file,
    load_json_file,
)


def calculate_velocity(closed_issues: list[dict], weeks: int = 2) -> float:
    """Calculate velocity as issues closed per week (rolling average)."""
    cutoff = datetime.now() - timedelta(weeks=weeks)

    recent_closed = [
        issue
        for issue in closed_issues
        if parse_date(issue.get("closedAt", ""))
        and parse_date(issue["closedAt"]) > cutoff
    ]

    return len(recent_closed) / weeks if weeks > 0 else 0


def get_weekly_breakdown(closed_issues: list[dict], weeks: int = 4) -> list[dict]:
    """Get issues closed per week for the last N weeks."""
    now = datetime.now()
    weekly_data = []

    for i in range(weeks):
        week_start = now - timedelta(weeks=i + 1)
        week_end = now - timedelta(weeks=i)

        count = sum(
            1
            for issue in closed_issues
            if parse_date(issue.get("closedAt", ""))
            and week_start <= parse_date(issue["closedAt"]) < week_end
        )

        weekly_data.append(
            {
                "week": i + 1,
                "start": week_start.strftime("%Y-%m-%d"),
                "end": week_end.strftime("%Y-%m-%d"),
                "count": count,
            }
        )

    return list(reversed(weekly_data))


def calculate_trend(weekly_data: list[dict]) -> str:
    """Calculate velocity trend from weekly data."""
    if len(weekly_data) < 4:
        return "→"  # Not enough data

    # Compare last 2 weeks vs previous 2 weeks
    recent = sum(w["count"] for w in weekly_data[-2:])
    previous = sum(w["count"] for w in weekly_data[-4:-2])

    if previous == 0:
        return "↑" if recent > 0 else "→"

    change = (recent - previous) / previous * 100

    if change > 15:
        return "↑"
    elif change < -15:
        return "↓"
    return "→"


def get_phase_breakdown(issues: list[dict]) -> dict[str, dict]:
    """Break down issues by phase labels."""
    phases = defaultdict(lambda: {"total": 0, "closed": 0})

    for issue in issues:
        labels = extract_labels(issue)
        phase_labels = [l for l in labels if l.lower().startswith("phase")]

        if phase_labels:
            for phase in phase_labels:
                phases[phase]["total"] += 1
                if issue.get("state") == "CLOSED":
                    phases[phase]["closed"] += 1
        else:
            # No phase label - count in "Other"
            phases["Other"]["total"] += 1
            if issue.get("state") == "CLOSED":
                phases["Other"]["closed"] += 1

    return dict(phases)


def get_milestone_progress(issues: list[dict]) -> dict[str, dict]:
    """Get progress by milestone."""
    milestones = defaultdict(lambda: {"total": 0, "closed": 0, "due_on": None})

    for issue in issues:
        milestone = issue.get("milestone")
        if milestone:
            name = milestone.get("title", "Unknown")
            milestones[name]["total"] += 1
            if issue.get("state") == "CLOSED":
                milestones[name]["closed"] += 1
            if milestone.get("dueOn"):
                milestones[name]["due_on"] = milestone["dueOn"]

    return dict(milestones)


def calculate_projections(
    open_count: int, velocity: float
) -> dict[str, str]:
    """Calculate completion projections."""
    if velocity <= 0:
        return {
            "best_case": "Unknown",
            "likely": "Unknown",
            "conservative": "Unknown",
        }

    now = datetime.now()

    # Best case: 20% faster
    best_weeks = open_count / (velocity * 1.2)
    best_date = now + timedelta(weeks=best_weeks)

    # Likely: current velocity
    likely_weeks = open_count / velocity
    likely_date = now + timedelta(weeks=likely_weeks)

    # Conservative: 20% slower
    conservative_weeks = open_count / (velocity * 0.8)
    conservative_date = now + timedelta(weeks=conservative_weeks)

    return {
        "best_case": f"{best_date.strftime('%Y-%m-%d')} ({best_weeks:.1f} weeks)",
        "likely": f"{likely_date.strftime('%Y-%m-%d')} ({likely_weeks:.1f} weeks)",
        "conservative": f"{conservative_date.strftime('%Y-%m-%d')} ({conservative_weeks:.1f} weeks)",
    }


def get_quality_metrics(issues: list[dict]) -> dict:
    """Calculate quality metrics."""
    closed_issues = [i for i in issues if i.get("state") == "CLOSED"]
    open_issues = [i for i in issues if i.get("state") == "OPEN"]

    # Average time to close
    close_times = []
    for issue in closed_issues:
        created = parse_date(issue.get("createdAt", ""))
        closed = parse_date(issue.get("closedAt", ""))
        if created and closed:
            close_times.append((closed - created).days)

    avg_close_time = sum(close_times) / len(close_times) if close_times else 0

    # Oldest open issue
    oldest_days = 0
    oldest_number = None
    for issue in open_issues:
        created = parse_date(issue.get("createdAt", ""))
        if created:
            age = days_ago(created)
            if age > oldest_days:
                oldest_days = age
                oldest_number = issue.get("number")

    # Recently closed (this week)
    week_ago = datetime.now() - timedelta(days=7)
    recently_closed = sum(
        1
        for issue in closed_issues
        if parse_date(issue.get("closedAt", ""))
        and parse_date(issue["closedAt"]) > week_ago
    )

    return {
        "avg_close_time": avg_close_time,
        "oldest_open_days": oldest_days,
        "oldest_open_number": oldest_number,
        "recently_closed": recently_closed,
    }


def determine_status(completion_pct: float, velocity: float, open_count: int) -> str:
    """Determine overall project status."""
    if open_count == 0:
        return "🟢 Complete"

    # Calculate if we're on track based on typical project timeline
    # This is a simplified heuristic
    if velocity >= 2 and completion_pct >= 50:
        return "🟢 On Track"
    elif velocity >= 1 or completion_pct >= 30:
        return "🟡 At Risk"
    else:
        return "🔴 Delayed"


def generate_velocity_report(
    owner: str,
    repo: str,
    output_json: bool = False,
    save_history: bool = False,
) -> dict:
    """Generate the velocity report."""
    # Fetch all issues
    issues = fetch_issues(owner, repo, state="all")

    if not issues:
        print("No issues found in repository.")
        return {}

    # Separate by state
    open_issues = [i for i in issues if i.get("state") == "OPEN"]
    closed_issues = [i for i in issues if i.get("state") == "CLOSED"]

    # Calculate metrics
    total = len(issues)
    closed_count = len(closed_issues)
    open_count = len(open_issues)
    completion_pct = (closed_count / total * 100) if total > 0 else 0

    velocity = calculate_velocity(closed_issues)
    weekly_data = get_weekly_breakdown(closed_issues)
    trend = calculate_trend(weekly_data)
    phases = get_phase_breakdown(issues)
    milestones = get_milestone_progress(issues)
    projections = calculate_projections(open_count, velocity)
    quality = get_quality_metrics(issues)
    status = determine_status(completion_pct, velocity, open_count)

    # Build report data
    report = {
        "generated": datetime.now().isoformat(),
        "repository": f"{owner}/{repo}",
        "summary": {
            "total_issues": total,
            "closed": closed_count,
            "open": open_count,
            "completion_percentage": round(completion_pct, 1),
            "status": status,
        },
        "velocity": {
            "current": round(velocity, 2),
            "trend": trend,
            "weekly_breakdown": weekly_data,
        },
        "projections": projections,
        "phases": phases,
        "milestones": milestones,
        "quality": quality,
    }

    # Save history if requested
    if save_history:
        history_file = ".claude/velocity-history.json"
        history = load_json_file(history_file)
        if "entries" not in history:
            history["entries"] = []
        history["entries"].append(
            {
                "timestamp": report["generated"],
                "velocity": velocity,
                "completion_pct": completion_pct,
                "open": open_count,
                "closed": closed_count,
            }
        )
        # Keep last 100 entries
        history["entries"] = history["entries"][-100:]
        save_json_file(history_file, history)

    if output_json:
        import json

        print(json.dumps(report, indent=2, default=str))
    else:
        print_report(report, owner, repo)

    return report


def print_report(report: dict, owner: str, repo: str) -> None:
    """Print formatted velocity report."""
    print_header(f"Velocity Dashboard: {owner}/{repo}")

    summary = report["summary"]
    velocity_data = report["velocity"]
    projections = report["projections"]
    quality = report["quality"]

    # Overall Progress
    print_section("🎯 Overall Progress")
    print(f"**Completed**: {summary['closed']}/{summary['total']} issues ({summary['completion_percentage']}%)")
    print(f"\n{format_progress_bar(summary['completion_percentage'])}")
    print(f"\n**Status**: {summary['status']}")

    # Velocity Metrics
    print_section("📈 Velocity Metrics")
    print(f"**Current Velocity**: {velocity_data['current']:.1f} issues/week (2-week average)")
    print(f"**Trend**: {velocity_data['trend']} {'Increasing' if velocity_data['trend'] == '↑' else 'Decreasing' if velocity_data['trend'] == '↓' else 'Steady'}")

    print("\n**Last 4 Weeks**:")
    for week in velocity_data["weekly_breakdown"]:
        print(f"  Week {week['week']}: {week['count']} issues")

    # Projections
    print_section("🔮 Projections")
    print(f"**Remaining Issues**: {summary['open']}")
    print(f"\n**Estimated Completion**:")
    print(f"  - Best case (+20% velocity): {projections['best_case']}")
    print(f"  - Likely (current velocity): {projections['likely']}")
    print(f"  - Conservative (-20% velocity): {projections['conservative']}")

    # Phase Breakdown
    if report["phases"]:
        print_section("🏗️ Phase Breakdown")
        for phase, data in sorted(report["phases"].items()):
            pct = (data["closed"] / data["total"] * 100) if data["total"] > 0 else 0
            status_emoji = "✅" if pct == 100 else "🟡" if pct > 0 else "⚪"
            print(f"\n**{phase}** {status_emoji} ({data['closed']}/{data['total']} issues)")
            print(format_progress_bar(pct))

    # Milestones
    if report["milestones"]:
        print_section("🎯 Milestones")
        for name, data in report["milestones"].items():
            pct = (data["closed"] / data["total"] * 100) if data["total"] > 0 else 0
            due_str = ""
            if data["due_on"]:
                due_date = parse_date(data["due_on"])
                if due_date:
                    days_until = (due_date - datetime.now(due_date.tzinfo)).days
                    if days_until < 0:
                        due_str = f" - ⚠️ Overdue by {abs(days_until)} days"
                    elif days_until <= 7:
                        due_str = f" - ⚠️ Due in {days_until} days"
                    else:
                        due_str = f" - Due: {due_date.strftime('%Y-%m-%d')}"

            print(f"\n**{name}**{due_str}")
            print(f"  Progress: {data['closed']}/{data['total']} ({pct:.0f}%)")

    # Quality Metrics
    print_section("📊 Quality Metrics")
    print(f"**Average Time to Close**: {quality['avg_close_time']:.1f} days")
    if quality["oldest_open_number"]:
        print(f"**Oldest Open Issue**: {quality['oldest_open_days']} days (#{quality['oldest_open_number']})")
    print(f"**Recently Closed**: {quality['recently_closed']} issues this week")

    # Footer
    print("\n" + "=" * 60)
    print("📅 Run `/velocity` anytime for latest metrics")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate project velocity dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save velocity data to history file",
    )
    parser.add_argument(
        "--repo",
        help="Repository in owner/repo format (auto-detected if not provided)",
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

    generate_velocity_report(owner, repo, args.json, args.save)


if __name__ == "__main__":
    main()
