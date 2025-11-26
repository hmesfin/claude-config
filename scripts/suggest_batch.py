#!/usr/bin/env python3
"""
Smart Batching Suggestions

Analyzes project dependency graph and suggests optimal batches for parallel work:
- Parses dependency markers (UNLOCKS, BLOCKS, DEPENDS ON, BLOCKED BY)
- Identifies ready issues (no blockers)
- Categorizes by complexity (Copilot-friendly vs Complex)
- Generates optimal batches based on capacity

Usage:
    python suggest_batch.py
    python suggest_batch.py --json           # Output as JSON
    python suggest_batch.py --capacity 5     # Custom batch size
    python suggest_batch.py --copilot-only   # Show only Copilot-friendly issues
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from pm_utils import (
    get_repo_info,
    fetch_issues,
    parse_date,
    extract_labels,
    get_priority,
    get_complexity,
    print_header,
    print_section,
)


# Dependency patterns to search for in issue bodies
DEPENDENCY_PATTERNS = {
    "unlocks": [
        r"UNLOCKS?:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
        r"ENABLES?:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
    ],
    "blocks": [
        r"BLOCKS?:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
    ],
    "depends_on": [
        r"DEPENDS?\s+ON:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
        r"REQUIRES?:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
    ],
    "blocked_by": [
        r"BLOCKED\s+BY:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
        r"WAITING\s+ON:\s*#?(\d+(?:\s*,\s*#?\d+)*)",
    ],
}

# Labels indicating Copilot-friendly issues
COPILOT_FRIENDLY_LABELS = [
    "crud", "simple", "standard", "ui-only", "docs", "documentation",
    "good-first-issue", "beginner", "straightforward"
]

# Labels indicating complex issues requiring human expertise
COMPLEX_LABELS = [
    "complex", "architecture", "security", "performance", "migration",
    "breaking-change", "critical", "expert"
]


def extract_issue_numbers(text: str) -> list[int]:
    """Extract issue numbers from a comma-separated string."""
    numbers = re.findall(r"#?(\d+)", text)
    return [int(n) for n in numbers]


def parse_dependencies(issue: dict) -> dict:
    """Parse dependency markers from issue body."""
    body = issue.get("body", "") or ""
    dependencies = {
        "unlocks": [],
        "blocks": [],
        "depends_on": [],
        "blocked_by": [],
    }

    for dep_type, patterns in DEPENDENCY_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                numbers = extract_issue_numbers(match)
                dependencies[dep_type].extend(numbers)

    # Remove duplicates
    for key in dependencies:
        dependencies[key] = list(set(dependencies[key]))

    return dependencies


def build_dependency_graph(issues: list[dict]) -> dict:
    """Build a dependency graph from all issues."""
    graph = {}
    issue_map = {issue["number"]: issue for issue in issues}

    for issue in issues:
        number = issue["number"]
        deps = parse_dependencies(issue)

        graph[number] = {
            "issue": issue,
            "dependencies": deps,
            "state": issue.get("state", "OPEN"),
        }

    return graph, issue_map


def get_blocking_issues(graph: dict, issue_number: int) -> list[int]:
    """Get all issues blocking a given issue."""
    node = graph.get(issue_number, {})
    deps = node.get("dependencies", {})

    blockers = []
    blockers.extend(deps.get("depends_on", []))
    blockers.extend(deps.get("blocked_by", []))

    return blockers


def is_issue_ready(graph: dict, issue_number: int) -> bool:
    """Check if an issue is ready (all blockers resolved)."""
    blockers = get_blocking_issues(graph, issue_number)

    for blocker in blockers:
        blocker_node = graph.get(blocker)
        if blocker_node and blocker_node.get("state") == "OPEN":
            return False

    return True


def categorize_issue(issue: dict) -> str:
    """Categorize issue as copilot-friendly, complex, or medium."""
    labels = [l.lower() for l in extract_labels(issue)]
    body = issue.get("body", "") or ""

    # Check for explicit complexity labels
    if any(label in labels for label in COPILOT_FRIENDLY_LABELS):
        return "copilot"

    if any(label in labels for label in COMPLEX_LABELS):
        return "complex"

    # Check body for hints
    complexity = get_complexity(extract_labels(issue), body)
    if complexity == "simple":
        return "copilot"
    elif complexity == "complex":
        return "complex"

    return "medium"


def calculate_unlocking_power(graph: dict, issue_number: int) -> int:
    """Calculate how many issues this issue unlocks (directly or transitively)."""
    node = graph.get(issue_number, {})
    deps = node.get("dependencies", {})

    direct_unlocks = len(deps.get("unlocks", []))
    direct_blocks = len(deps.get("blocks", []))

    return direct_unlocks + direct_blocks


def identify_critical_path(graph: dict) -> list[int]:
    """Identify issues on the critical path (high unlocking power)."""
    critical = []

    for number, node in graph.items():
        if node.get("state") == "OPEN":
            unlocking_power = calculate_unlocking_power(graph, number)
            if unlocking_power >= 2:  # Unlocks 2+ issues
                critical.append({
                    "number": number,
                    "unlocking_power": unlocking_power,
                    "title": node["issue"].get("title", ""),
                })

    # Sort by unlocking power
    critical.sort(key=lambda x: x["unlocking_power"], reverse=True)
    return critical


def find_parallel_safe_groups(
    ready_issues: list[dict],
    issue_map: dict,
) -> list[list[dict]]:
    """Group ready issues that can be worked on in parallel."""
    # Simple heuristic: group by different label categories
    groups = defaultdict(list)

    for issue in ready_issues:
        labels = extract_labels(issue)

        # Determine primary domain
        domain = "other"
        for label in labels:
            label_lower = label.lower()
            if any(d in label_lower for d in ["backend", "api", "database"]):
                domain = "backend"
                break
            elif any(d in label_lower for d in ["frontend", "ui", "component"]):
                domain = "frontend"
                break
            elif any(d in label_lower for d in ["mobile", "ios", "android"]):
                domain = "mobile"
                break
            elif any(d in label_lower for d in ["infra", "devops", "deploy"]):
                domain = "infra"
                break

        groups[domain].append(issue)

    return dict(groups)


def generate_batch_suggestions(
    owner: str,
    repo: str,
    capacity: int = 4,
    output_json: bool = False,
    copilot_only: bool = False,
) -> dict:
    """Generate batch suggestions."""
    issues = fetch_issues(owner, repo, state="all")

    if not issues:
        print("No issues found.")
        return {}

    # Build dependency graph
    graph, issue_map = build_dependency_graph(issues)

    # Find ready issues (open with no open blockers)
    open_issues = [i for i in issues if i.get("state") == "OPEN"]
    ready_issues = [
        i for i in open_issues
        if is_issue_ready(graph, i["number"])
    ]

    # Categorize ready issues
    categorized = {
        "copilot": [],
        "complex": [],
        "medium": [],
    }

    for issue in ready_issues:
        category = categorize_issue(issue)
        issue_data = {
            "number": issue["number"],
            "title": issue.get("title", ""),
            "category": category,
            "priority": get_priority(extract_labels(issue)),
            "labels": extract_labels(issue),
            "unlocking_power": calculate_unlocking_power(graph, issue["number"]),
            "assignees": [a.get("login", "") for a in issue.get("assignees", [])],
        }
        categorized[category].append(issue_data)

    # Sort each category by priority then unlocking power
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    for category in categorized:
        categorized[category].sort(
            key=lambda x: (priority_order.get(x["priority"], 2), -x["unlocking_power"])
        )

    # Find critical path issues
    critical_path = identify_critical_path(graph)

    # Find parallel groups
    parallel_groups = find_parallel_safe_groups(ready_issues, issue_map)

    # Generate recommended batch
    batch = {
        "copilot": categorized["copilot"][:capacity],
        "manual": [],
        "sequential": [],
    }

    # Add complex issues to manual
    for issue in categorized["complex"][:2]:
        batch["manual"].append(issue)

    # Identify blocked issues
    blocked_issues = []
    for issue in open_issues:
        if not is_issue_ready(graph, issue["number"]):
            blockers = get_blocking_issues(graph, issue["number"])
            open_blockers = [b for b in blockers if graph.get(b, {}).get("state") == "OPEN"]
            if open_blockers:
                blocked_issues.append({
                    "number": issue["number"],
                    "title": issue.get("title", ""),
                    "blocked_by": open_blockers,
                })

    # Build report
    report = {
        "generated": datetime.now().isoformat(),
        "repository": f"{owner}/{repo}",
        "summary": {
            "total_open": len(open_issues),
            "ready": len(ready_issues),
            "blocked": len(blocked_issues),
            "copilot_friendly": len(categorized["copilot"]),
            "complex": len(categorized["complex"]),
        },
        "ready_issues": categorized,
        "critical_path": critical_path[:5],
        "parallel_groups": {k: len(v) for k, v in parallel_groups.items()},
        "blocked_issues": blocked_issues[:10],
        "recommended_batch": batch,
    }

    if output_json:
        import json
        print(json.dumps(report, indent=2, default=str))
    else:
        print_batch_report(report, owner, repo, copilot_only)

    return report


def print_batch_report(report: dict, owner: str, repo: str, copilot_only: bool) -> None:
    """Print formatted batch suggestions."""
    print_header(f"Smart Batch Suggestions: {owner}/{repo}")

    summary = report["summary"]

    # Summary
    print_section("📊 Dependency Overview")
    print(f"**Open Issues**: {summary['total_open']}")
    print(f"**Ready to Work**: {summary['ready']} ({summary['copilot_friendly']} Copilot-friendly, {summary['complex']} complex)")
    print(f"**Blocked**: {summary['blocked']} issues waiting on dependencies")

    # Critical Path
    if report["critical_path"]:
        print_section("🔥 Critical Path (High Unlocking Power)")
        for item in report["critical_path"]:
            print(f"- **#{item['number']}**: {item['title'][:50]}... → Unlocks {item['unlocking_power']} issues")

    # Parallel Opportunities
    print_section("🔀 Parallel Opportunities")
    for domain, count in report["parallel_groups"].items():
        if count > 0:
            print(f"- **{domain.title()}**: {count} issues can be parallelized")

    # Recommended Batch
    batch = report["recommended_batch"]

    print_section("🎯 Recommended Batch")

    if batch["copilot"]:
        print("\n### 🤖 Assign to Copilot (parallel)")
        for issue in batch["copilot"]:
            unassigned = " ⚠️ Unassigned" if not issue["assignees"] else ""
            unlocks = f" → Unlocks {issue['unlocking_power']}" if issue["unlocking_power"] > 0 else ""
            print(f"- **#{issue['number']}**: {issue['title'][:45]}... [{issue['priority']}]{unlocks}{unassigned}")

    if not copilot_only and batch["manual"]:
        print("\n### 🧠 Manual Work (complex)")
        for issue in batch["manual"]:
            print(f"- **#{issue['number']}**: {issue['title'][:45]}... [{issue['priority']}]")
            if issue["labels"]:
                print(f"  Labels: {', '.join(issue['labels'][:5])}")

    # Medium complexity issues
    medium = report["ready_issues"]["medium"][:5]
    if not copilot_only and medium:
        print("\n### ⚖️ Medium Complexity")
        for issue in medium:
            print(f"- #{issue['number']}: {issue['title'][:50]}...")

    # Blocked Issues
    if report["blocked_issues"]:
        print_section("🚧 Blocked Issues")
        for issue in report["blocked_issues"][:5]:
            blockers = ", ".join(f"#{b}" for b in issue["blocked_by"])
            print(f"- #{issue['number']}: {issue['title'][:40]}... (blocked by {blockers})")

    # Expected Outcomes
    print_section("📈 Expected Outcomes")
    total_batch = len(batch["copilot"]) + len(batch["manual"])
    total_unlocks = sum(i["unlocking_power"] for i in batch["copilot"])
    total_unlocks += sum(i["unlocking_power"] for i in batch["manual"])

    print(f"**If batch completes**:")
    print(f"- ✅ {total_batch} issues closed")
    print(f"- 🔓 Up to {total_unlocks} additional issues unblocked")

    # Action Items
    print_section("🔧 Action Items")

    if batch["copilot"]:
        print("\n**Assign Copilot Issues**:")
        for issue in batch["copilot"]:
            print(f"  gh issue edit {issue['number']} --add-assignee @me")

    print("\n" + "=" * 60)
    print("🚀 Run `/suggest-batch` weekly for optimal planning")
    print("📊 Combine with `/velocity` and `/risk-check` for full visibility")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate smart batch suggestions for parallel work",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--capacity",
        type=int,
        default=4,
        help="Maximum batch size (default: 4)",
    )
    parser.add_argument(
        "--copilot-only",
        action="store_true",
        help="Show only Copilot-friendly issues",
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

    generate_batch_suggestions(
        owner,
        repo,
        args.capacity,
        args.json,
        args.copilot_only,
    )


if __name__ == "__main__":
    main()
