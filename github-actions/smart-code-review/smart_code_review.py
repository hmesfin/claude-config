#!/usr/bin/env python3
"""
Smart Code Review Agent
AI-powered code review with static analysis and anti-pattern detection.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Anti-patterns to check for
ANTI_PATTERNS = {
    'python': {
        'n_plus_one': r'for\s+\w+\s+in\s+\w+.*\.get\(',
        'bare_except': r'except\s*:',
        'sql_injection': r'f["\'].*SELECT.*{.*}.*["\']',
        'missing_error_handling': r'requests\.\w+\(.*\)(?!\s*\.raise_for_status)',
    },
    'javascript': {
        'console_log': r'console\.(log|debug|info)',
        'var_usage': r'\bvar\s+\w+',
        'eval_usage': r'\beval\s*\(',
        'unvalidated_input': r'innerHTML\s*=',
    },
    'typescript': {
        'any_type': r':\s*any\b',
        'non_null_assertion': r'!\s*[;\)]',
        'type_assertion': r'as\s+\w+',
    }
}


def run_ruff(file_paths: List[str]) -> List[Dict]:
    """Run ruff linter on Python files."""
    issues = []
    python_files = [f for f in file_paths if f.endswith('.py')]

    if not python_files:
        return issues

    try:
        result = subprocess.run(
            ['ruff', 'check', '--output-format=json'] + python_files,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.stdout:
            ruff_issues = json.loads(result.stdout)
            for issue in ruff_issues:
                issues.append({
                    'tool': 'ruff',
                    'file': issue.get('filename', ''),
                    'line': issue.get('location', {}).get('row', 0),
                    'message': issue.get('message', ''),
                    'code': issue.get('code', ''),
                    'severity': 'error' if issue.get('severity') == 'error' else 'warning'
                })
    except Exception as e:
        print(f"Error running ruff: {e}", file=sys.stderr)

    return issues


def run_eslint(file_paths: List[str]) -> List[Dict]:
    """Run ESLint on JavaScript/TypeScript files."""
    issues = []
    js_files = [f for f in file_paths if f.endswith(('.js', '.ts', '.tsx', '.jsx'))]

    if not js_files:
        return issues

    try:
        result = subprocess.run(
            ['eslint', '--format=json'] + js_files,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.stdout:
            eslint_results = json.loads(result.stdout)
            for file_result in eslint_results:
                for message in file_result.get('messages', []):
                    issues.append({
                        'tool': 'eslint',
                        'file': file_result.get('filePath', ''),
                        'line': message.get('line', 0),
                        'message': message.get('message', ''),
                        'code': message.get('ruleId', ''),
                        'severity': 'error' if message.get('severity') == 2 else 'warning'
                    })
    except Exception as e:
        print(f"Error running eslint: {e}", file=sys.stderr)

    return issues


def check_anti_patterns(diff_content: str, file_path: str) -> List[Dict]:
    """Check for anti-patterns in code diff."""
    issues = []

    # Determine language from file extension
    lang = None
    if file_path.endswith('.py'):
        lang = 'python'
    elif file_path.endswith(('.js', '.jsx')):
        lang = 'javascript'
    elif file_path.endswith(('.ts', '.tsx')):
        lang = 'typescript'

    if not lang or lang not in ANTI_PATTERNS:
        return issues

    # Check each anti-pattern
    for pattern_name, pattern_regex in ANTI_PATTERNS[lang].items():
        matches = re.finditer(pattern_regex, diff_content, re.MULTILINE)
        for match in matches:
            # Get line number
            line_num = diff_content[:match.start()].count('\n') + 1

            issues.append({
                'tool': 'anti-pattern',
                'file': file_path,
                'line': line_num,
                'message': f'Potential {pattern_name.replace("_", " ")} detected',
                'code': pattern_name,
                'severity': 'warning'
            })

    return issues


def get_pr_files() -> List[str]:
    """Get list of files changed in PR."""
    try:
        with open('pr_diff.txt', 'r') as f:
            diff_content = f.read()

        # Extract file paths from diff
        file_pattern = r'diff --git a/(.*?) b/'
        files = re.findall(file_pattern, diff_content)
        return [f for f in files if Path(f).exists()]
    except Exception as e:
        print(f"Error getting PR files: {e}", file=sys.stderr)
        return []


def analyze_with_claude(issues: List[Dict], diff_content: str) -> Optional[str]:
    """Use Claude to analyze issues and provide insights."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return None

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Prepare prompt
        issues_summary = "\n".join([
            f"- {issue['file']}:{issue['line']} - {issue['message']} ({issue['tool']})"
            for issue in issues[:20]  # Limit to avoid token limits
        ])

        prompt = f"""Analyze this code review and provide insights:

Static Analysis Issues Found:
{issues_summary}

Code Diff (first 5000 chars):
{diff_content[:5000]}

Provide:
1. Overall code quality assessment
2. Critical issues that must be fixed
3. Suggestions for improvement
4. Praise for good practices (if any)

Keep response concise and actionable."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    except Exception as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        return None


def format_review_comment(issues: List[Dict], ai_insights: Optional[str] = None) -> str:
    """Generate formatted markdown review comment."""
    # Count issues by severity
    errors = [i for i in issues if i['severity'] == 'error']
    warnings = [i for i in issues if i['severity'] == 'warning']

    # Determine overall status
    if len(errors) == 0 and len(warnings) <= 3:
        header = "✅ **Smart Code Review - PASSED**"
        status_emoji = "🟢"
    elif len(errors) == 0:
        header = "⚠️ **Smart Code Review - WARNINGS**"
        status_emoji = "🟡"
    else:
        header = "❌ **Smart Code Review - ISSUES FOUND**"
        status_emoji = "🔴"

    comment = f"""## {header}

**Status**: {status_emoji} {len(errors)} errors, {len(warnings)} warnings

---

"""

    # Add AI insights if available
    if ai_insights:
        comment += f"""### 🤖 AI Analysis

{ai_insights}

---

"""

    # Errors section
    if errors:
        comment += "### ❌ Errors (Must Fix)\n\n"
        for issue in errors[:10]:  # Limit display
            comment += f"**{issue['file']}:{issue['line']}**\n"
            comment += f"- {issue['message']} (`{issue['code']}`)\n\n"

    # Warnings section
    if warnings:
        comment += "### ⚠️ Warnings\n\n"
        for issue in warnings[:10]:
            comment += f"**{issue['file']}:{issue['line']}**\n"
            comment += f"- {issue['message']} (`{issue['code']}`)\n\n"

    # Summary
    if len(issues) == 0:
        comment += """### 🎉 Excellent!

No issues found. Code looks clean! ✨

"""

    comment += "\n---\n*🤖 Generated by Smart Code Review Agent*"

    return comment


def main():
    """Main entry point."""
    print("🔍 Running Smart Code Review...")

    # Get PR files
    files = get_pr_files()
    if not files:
        print("No files to review")
        sys.exit(0)

    print(f"Reviewing {len(files)} files...")

    # Run static analysis
    issues = []
    issues.extend(run_ruff(files))
    issues.extend(run_eslint(files))

    # Check anti-patterns in diff
    try:
        with open('pr_diff.txt', 'r') as f:
            diff_content = f.read()

        for file_path in files:
            issues.extend(check_anti_patterns(diff_content, file_path))
    except Exception as e:
        print(f"Error checking anti-patterns: {e}", file=sys.stderr)
        diff_content = ""

    # Analyze with Claude
    ai_insights = analyze_with_claude(issues, diff_content)

    # Generate review comment
    comment = format_review_comment(issues, ai_insights)

    # Determine if approved
    errors = [i for i in issues if i['severity'] == 'error']
    approved = len(errors) == 0 and len(issues) <= 5

    # Write report
    report = {
        'approved': approved,
        'total_issues': len(issues),
        'errors': len(errors),
        'warnings': len([i for i in issues if i['severity'] == 'warning']),
        'comment': comment
    }

    with open('review_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Set GitHub Action output
    print(f"::set-output name=approved::{str(approved).lower()}")
    print(f"::set-output name=total_issues::{len(issues)}")

    # Print summary
    if approved:
        print(f"✅ Review passed: {len(issues)} minor issues")
        sys.exit(0)
    else:
        print(f"❌ Review failed: {len(errors)} errors, {len(issues) - len(errors)} warnings")
        sys.exit(0)  # Don't fail workflow, just report


if __name__ == '__main__':
    main()
