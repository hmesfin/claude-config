#!/usr/bin/env python3
"""
Project Management Utilities

Shared utilities for project management commands:
- /velocity
- /risk-check
- /suggest-batch
- /assign-contractor

These utilities handle GitHub data fetching, date calculations,
and common formatting functions.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def get_repo_info() -> tuple[str, str]:
    """Get owner and repo from git remote URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()

        # Parse GitHub URL (handles both HTTPS and SSH)
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        if "github.com" in url:
            if url.startswith("git@"):
                # SSH format
                path = url.split(":")[-1]
            else:
                # HTTPS format
                path = url.split("github.com/")[-1]

            # Remove .git suffix if present
            path = path.rstrip(".git")
            parts = path.split("/")

            if len(parts) >= 2:
                return parts[0], parts[1]

        print("Error: Could not parse GitHub URL from git remote")
        sys.exit(1)

    except subprocess.CalledProcessError:
        print("Error: Not a git repository or no remote configured")
        sys.exit(1)


def run_gh_command(args: list[str]) -> dict | list | None:
    """Run a GitHub CLI command and return JSON result."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except subprocess.CalledProcessError as e:
        print(f"GitHub CLI error: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not parse GitHub response")
        return None


def fetch_issues(
    owner: str,
    repo: str,
    state: str = "all",
    labels: Optional[list[str]] = None,
    limit: int = 500,
) -> list[dict]:
    """Fetch issues from GitHub repository."""
    args = [
        "issue",
        "list",
        "--repo",
        f"{owner}/{repo}",
        "--state",
        state,
        "--json",
        "number,title,state,labels,assignees,milestone,createdAt,updatedAt,closedAt,body,comments",
        "--limit",
        str(limit),
    ]

    if labels:
        args.extend(["--label", ",".join(labels)])

    result = run_gh_command(args)
    return result if result else []


def fetch_prs(
    owner: str,
    repo: str,
    state: str = "all",
    limit: int = 100,
) -> list[dict]:
    """Fetch pull requests from GitHub repository."""
    args = [
        "pr",
        "list",
        "--repo",
        f"{owner}/{repo}",
        "--state",
        state,
        "--json",
        "number,title,state,author,createdAt,updatedAt,closedAt,mergedAt,additions,deletions,changedFiles,labels",
        "--limit",
        str(limit),
    ]

    result = run_gh_command(args)
    return result if result else []


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse ISO date string to datetime."""
    if not date_str:
        return None
    try:
        # Handle various ISO formats
        date_str = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date2 - date1).days)


def days_ago(date: datetime) -> int:
    """Calculate days since a date."""
    now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
    return (now - date).days


def format_progress_bar(percentage: float, width: int = 20) -> str:
    """Generate a text progress bar."""
    filled = int((percentage / 100) * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {percentage:.0f}%"


def get_week_number(date: datetime) -> str:
    """Get ISO week number as string."""
    return date.strftime("%Y-W%W")


def group_by_week(items: list[dict], date_field: str) -> dict[str, list[dict]]:
    """Group items by week based on a date field."""
    weeks = {}
    for item in items:
        date = parse_date(item.get(date_field, ""))
        if date:
            week = get_week_number(date)
            if week not in weeks:
                weeks[week] = []
            weeks[week].append(item)
    return weeks


def extract_labels(issue: dict) -> list[str]:
    """Extract label names from issue."""
    labels = issue.get("labels", [])
    if isinstance(labels, list):
        return [
            label.get("name", label) if isinstance(label, dict) else str(label)
            for label in labels
        ]
    return []


def get_priority(labels: list[str]) -> str:
    """Determine priority from labels."""
    label_lower = [l.lower() for l in labels]

    if any(p in label_lower for p in ["p0", "critical", "urgent", "blocker"]):
        return "P0"
    elif any(p in label_lower for p in ["p1", "high", "important"]):
        return "P1"
    elif any(p in label_lower for p in ["p2", "medium", "normal"]):
        return "P2"
    elif any(p in label_lower for p in ["p3", "low", "nice-to-have"]):
        return "P3"
    return "P2"  # Default to medium


def get_complexity(labels: list[str], body: str = "") -> str:
    """Determine complexity from labels and body."""
    label_lower = [l.lower() for l in labels]

    # Check for explicit complexity labels
    if any(c in label_lower for c in ["complex", "architecture", "security", "migration"]):
        return "complex"
    elif any(c in label_lower for c in ["simple", "crud", "ui-only", "docs", "standard"]):
        return "simple"

    # Check body for size hints
    if body:
        body_lower = body.lower()
        if ">500 lines" in body_lower or "large" in body_lower:
            return "complex"
        elif "<200 lines" in body_lower or "small" in body_lower:
            return "simple"

    return "medium"


def load_json_file(filepath: str) -> dict:
    """Load JSON file if it exists."""
    path = Path(filepath)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_json_file(filepath: str, data: dict) -> None:
    """Save data to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def print_header(title: str, char: str = "=") -> None:
    """Print a formatted header."""
    width = 60
    print(f"\n{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}\n")


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n## {title}\n")


def format_issue_link(owner: str, repo: str, number: int) -> str:
    """Format a GitHub issue link."""
    return f"https://github.com/{owner}/{repo}/issues/{number}"


def format_pr_link(owner: str, repo: str, number: int) -> str:
    """Format a GitHub PR link."""
    return f"https://github.com/{owner}/{repo}/pull/{number}"


# Constants for risk calculation
PRIORITY_THRESHOLDS = {
    "P0": 3,   # Critical issues risky after 3 days
    "P1": 7,   # High priority risky after 7 days
    "P2": 14,  # Medium priority risky after 14 days
    "P3": 21,  # Low priority risky after 21 days
}

# Risk score weights
RISK_WEIGHTS = {
    "days_open": 30,      # Max points for being open too long
    "risk_marker": 30,    # Points for explicit RISK: marker
    "stale": 20,          # Max points for no recent updates
    "no_comments": 15,    # Points for no engagement
    "deadline": 20,       # Max points for approaching deadline
    "blocked": 15,        # Points for being blocked
}
