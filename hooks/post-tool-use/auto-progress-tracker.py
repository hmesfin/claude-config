#!/usr/bin/env python3
"""
Auto-Progress Tracking Hook (P0.1 + P1.2)
Automatically manages GitHub issues based on git commit messages.

Triggers: After git commit with issue references (fixes #N, closes #N, resolves #N)
Actions:
  1. Close referenced GitHub issue
  2. Post progress comment
  3. Detect and unlock dependent issues (P1.2)
  4. Suggest next sequential issue
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

# Add hooks lib to path
sys.path.insert(0, str(Path.home() / '.claude' / 'hooks'))

from lib.github_automation import GitHubAPI


def extract_issue_refs(commit_message: str) -> List[Tuple[str, str, int]]:
    """
    Extract issue references from commit message.

    Patterns: "fixes #15", "closes #15", "resolves #15", "fix #15", etc.
    Returns: List of (keyword, owner/repo, issue_number) tuples
    """
    # Pattern: (fixes|closes|resolves|fix|close|resolve) owner/repo#number or #number
    patterns = [
        r'(fix(?:es)?|close(?:s)?|resolve(?:s)?)\s+([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)?#(\d+)',
        r'#(\d+)',  # Simple #N reference
    ]

    refs = []
    for pattern in patterns:
        matches = re.finditer(pattern, commit_message, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3:
                keyword, repo, number = match.groups()
                refs.append((keyword, repo or '', int(number)))
            else:
                # Simple #N reference - assume current repo
                refs.append(('reference', '', int(match.group(1))))

    return refs


def get_current_repo() -> Optional[str]:
    """Get current GitHub repository (owner/repo) from git remote."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse GitHub URL: git@github.com:owner/repo.git or https://github.com/owner/repo.git
            match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', url)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
    except Exception as e:
        print(f"Error getting repo: {e}", file=sys.stderr)

    return None


def parse_dependencies(issue_body: str) -> List[int]:
    """
    Parse dependency declarations from issue body.

    Supported formats:
    - UNLOCKS: #15, #16, #17
    - BLOCKS: #20
    - Depends on: #10

    Returns: List of issue numbers that are unlocked/blocked by this issue
    """
    if not issue_body:
        return []

    dependencies = []

    # Patterns for dependency declarations
    patterns = [
        r'UNLOCKS?:\s*#?(\d+(?:\s*,\s*#?\d+)*)',  # UNLOCKS: #15, #16
        r'BLOCKS?:\s*#?(\d+(?:\s*,\s*#?\d+)*)',    # BLOCKS: #20
        r'ENABLES?:\s*#?(\d+(?:\s*,\s*#?\d+)*)',   # ENABLES: #15
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, issue_body, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Extract all numbers from the matched string
            numbers = re.findall(r'\d+', match.group(1))
            dependencies.extend([int(num) for num in numbers])

    return list(set(dependencies))  # Remove duplicates


def unlock_dependent_issues(
    api: GitHubAPI,
    owner: str,
    repo: str,
    closed_issue_number: int,
    dependent_issues: List[int]
) -> List[int]:
    """
    Unlock dependent issues by adding 'ready' label and posting comment.

    Returns: List of successfully unlocked issue numbers
    """
    unlocked = []

    for dep_issue_num in dependent_issues:
        try:
            # Check if issue exists and is open
            issue = api.get_issue(owner, repo, dep_issue_num)
            if not issue or issue.get('state') != 'open':
                continue

            # Add 'ready' label
            current_labels = api.get_issue_labels(owner, repo, dep_issue_num)
            if 'ready' not in current_labels:
                api.add_labels(owner, repo, dep_issue_num, ['ready'])

            # Post comment
            comment = (
                f"✅ **Dependency Resolved**\n\n"
                f"Issue #{closed_issue_number} has been completed.\n"
                f"This issue is now unblocked and ready to start! 🚀"
            )
            api.add_comment(owner, repo, dep_issue_num, comment)

            unlocked.append(dep_issue_num)

        except Exception as e:
            print(f"Error unlocking issue #{dep_issue_num}: {e}", file=sys.stderr)

    return unlocked


def close_issue_with_comment(api: GitHubAPI, owner: str, repo: str, issue_number: int) -> bool:
    """Close GitHub issue and post progress comment."""
    try:
        # Calculate progress
        progress = api.calculate_progress(owner, repo)

        # Post progress comment
        comment_body = (
            f"✅ **Issue closed via commit**\n\n"
            f"📊 **Progress**: {progress['closed']}/{progress['total']} "
            f"({progress['percentage']:.0f}%) complete\n"
            f"🚀 {progress['open']} issues remaining"
        )

        # Add comment
        api.add_comment(owner, repo, issue_number, comment_body)

        # Close issue
        return api.update_issue(owner, repo, issue_number, state='closed')

    except Exception as e:
        print(f"Error closing issue: {e}", file=sys.stderr)
        return False


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        # Only process Bash tool calls
        if hook_input.get('tool_name') != 'Bash':
            sys.exit(0)

        # Get the bash command
        command = hook_input.get('tool_input', {}).get('command', '')

        # Check if this is a git commit command
        if not re.search(r'git\s+commit', command, re.IGNORECASE):
            sys.exit(0)

        # Extract commit message from command
        # Handle both -m "message" and --message="message" formats
        message_match = re.search(r'(?:-m|--message[=\s]+)["\']([^"\']+)["\']', command)
        if not message_match:
            sys.exit(0)

        commit_message = message_match.group(1)

        # Extract issue references
        issue_refs = extract_issue_refs(commit_message)
        if not issue_refs:
            sys.exit(0)

        # Get current repository
        current_repo = get_current_repo()
        if not current_repo:
            print("⚠️ Could not determine GitHub repository", file=sys.stderr)
            sys.exit(0)

        owner, repo = current_repo.split('/')

        # Initialize GitHub API
        api = GitHubAPI()

        # Process each issue reference
        closed_issues = []
        for keyword, ref_repo, issue_number in issue_refs:
            # Only auto-close on explicit keywords
            if keyword.lower() in ['fix', 'fixes', 'close', 'closes', 'resolve', 'resolves']:
                target_owner, target_repo = (ref_repo.split('/') if ref_repo else (owner, repo))

                if close_issue_with_comment(api, target_owner, target_repo, issue_number):
                    closed_issues.append(issue_number)

                    # P1.2: Check for dependencies and unlock dependent issues
                    issue_data = api.get_issue(target_owner, target_repo, issue_number)
                    if issue_data and issue_data.get('body'):
                        dependencies = parse_dependencies(issue_data['body'])
                        if dependencies:
                            unlocked = unlock_dependent_issues(
                                api, target_owner, target_repo, issue_number, dependencies
                            )
                            if unlocked:
                                dep_msg = f"\n🔓 Unlocked issues: {', '.join(f'#{n}' for n in unlocked)}"
                            else:
                                dep_msg = ""
                        else:
                            dep_msg = ""
                    else:
                        dep_msg = ""

                    # Suggest next issue
                    next_issue = api.get_next_open_issue(target_owner, target_repo, issue_number)
                    if next_issue:
                        print(json.dumps({
                            "systemMessage": f"✅ Closed issue #{issue_number}{dep_msg}\n"
                                           f"🚀 Next issue: #{next_issue}\n"
                                           f"Tip: You can say 'Show me issue #{next_issue}' to start working on it"
                        }))
                    else:
                        print(json.dumps({
                            "systemMessage": f"✅ Closed issue #{issue_number}{dep_msg}\n"
                                           f"🎉 No more open issues!"
                        }))

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Never fail the tool call


if __name__ == '__main__':
    main()
