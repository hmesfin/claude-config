"""
GitHub Automation Library
Direct GitHub API integration for hooks.
"""

import os
import requests
from typing import Optional, List, Dict


class GitHubAPI:
    """Simple GitHub API client for hooks."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def list_issues(self, owner: str, repo: str, state: str = 'all') -> List[Dict]:
        """List issues in a repository."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        params = {'state': state, 'per_page': 100}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Optional[Dict]:
        """Get a single issue."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}'

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def update_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> bool:
        """Update an issue (close, change labels, etc.)."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}'

        try:
            response = requests.patch(url, headers=self.headers, json=kwargs, timeout=10)
            response.raise_for_status()
            return True
        except Exception:
            return False

    def add_comment(self, owner: str, repo: str, issue_number: int, body: str) -> bool:
        """Add a comment to an issue."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments'

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={'body': body},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def calculate_progress(self, owner: str, repo: str) -> Dict:
        """Calculate project progress."""
        issues = self.list_issues(owner, repo, state='all')

        # Filter out pull requests
        issues = [i for i in issues if 'pull_request' not in i]

        total = len(issues)
        closed = sum(1 for i in issues if i.get('state') == 'closed')

        return {
            'total': total,
            'closed': closed,
            'open': total - closed,
            'percentage': (closed / total * 100) if total > 0 else 0
        }

    def get_next_open_issue(self, owner: str, repo: str, after_number: int) -> Optional[int]:
        """Find next sequential open issue after a given number."""
        issues = self.list_issues(owner, repo, state='open')

        # Filter out pull requests
        issues = [i for i in issues if 'pull_request' not in i]

        # Find next issue number after current
        for issue in sorted(issues, key=lambda x: x['number']):
            if issue['number'] > after_number:
                return issue['number']

        return None

    def add_labels(self, owner: str, repo: str, issue_number: int, labels: List[str]) -> bool:
        """Add labels to an issue."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels'

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={'labels': labels},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def get_issue_labels(self, owner: str, repo: str, issue_number: int) -> List[str]:
        """Get labels for an issue."""
        issue = self.get_issue(owner, repo, issue_number)
        if issue and 'labels' in issue:
            return [label['name'] for label in issue['labels']]
        return []
