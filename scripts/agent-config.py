#!/usr/bin/env python3
"""
Agent Configuration Manager for Claude Code

This script manages which specialized agents are enabled/disabled
by updating .claude/settings.json with the appropriate configuration.

Usage:
    python agent-config.py --profile backend
    python agent-config.py --profile django
    python agent-config.py --profile fastapi
    python agent-config.py --profile mobile
    python agent-config.py --list
    python agent-config.py --reset
"""

import argparse
import json
import sys
from pathlib import Path

# Agent profiles define which agents to DISABLE for each development context
AGENT_PROFILES = {
    "backend": {
        "description": "Backend development (Django + FastAPI). Disables mobile agents.",
        "disabled": [
            "mobile-data-architect",
            "mobile-performance-optimizer",
            "mobile-realtime-architect",
            "mobile-security-architect",
            "react-native-tdd-architect",
            "native-module-tdd-engineer",
            "expo-deployment-agent",
        ],
    },
    "django": {
        "description": "Django-specific development. Disables FastAPI and mobile agents.",
        "disabled": [
            "fastapi-tdd-architect",
            "fastapi-data-architect",
            "fastapi-security-architect",
            "fastapi-vue-staging-agent",
            "mobile-data-architect",
            "mobile-performance-optimizer",
            "mobile-realtime-architect",
            "mobile-security-architect",
            "react-native-tdd-architect",
            "native-module-tdd-engineer",
            "expo-deployment-agent",
        ],
    },
    "fastapi": {
        "description": "FastAPI-specific development. Disables Django and mobile agents.",
        "disabled": [
            "django-tdd-architect",
            "django-data-architect",
            "django-security-architect",
            "django-vue-staging-agent",
            "mobile-data-architect",
            "mobile-performance-optimizer",
            "mobile-realtime-architect",
            "mobile-security-architect",
            "react-native-tdd-architect",
            "native-module-tdd-engineer",
            "expo-deployment-agent",
        ],
    },
    "mobile": {
        "description": "React Native mobile development. Disables backend framework agents.",
        "disabled": [
            "django-tdd-architect",
            "django-data-architect",
            "django-security-architect",
            "django-vue-staging-agent",
            "fastapi-tdd-architect",
            "fastapi-data-architect",
            "fastapi-security-architect",
            "fastapi-vue-staging-agent",
            "vue-tdd-architect",
        ],
    },
    "full-stack": {
        "description": "Full-stack development. All agents enabled.",
        "disabled": [],
    },
}

# All available agents in the ecosystem
ALL_AGENTS = [
    # Backend - Django
    "django-tdd-architect",
    "django-data-architect",
    "django-security-architect",
    "django-vue-staging-agent",
    # Backend - FastAPI
    "fastapi-tdd-architect",
    "fastapi-data-architect",
    "fastapi-security-architect",
    "fastapi-vue-staging-agent",
    # Frontend
    "vue-tdd-architect",
    # Mobile
    "react-native-tdd-architect",
    "mobile-data-architect",
    "mobile-performance-optimizer",
    "mobile-realtime-architect",
    "mobile-security-architect",
    "native-module-tdd-engineer",
    "expo-deployment-agent",
    # Cross-cutting
    "data-tdd-architect",
    "security-tdd-architect",
    "async-tdd-architect",
    "realtime-tdd-architect",
    "e2e-tdd-architect",
    "performance-tdd-optimizer",
    # Infrastructure
    "devops-tdd-engineer",
    "observability-tdd-engineer",
    # Meta
    "project-orchestrator",
    "tdd-test-specialist",
]


def find_settings_file() -> Path:
    """Find the .claude/settings.json file in the project."""
    # Check current directory first
    cwd = Path.cwd()
    settings_path = cwd / ".claude" / "settings.json"

    if settings_path.exists():
        return settings_path

    # Check for claude-config directory
    config_path = Path.home() / "claude-config" / ".claude" / "settings.json"
    if config_path.exists():
        return config_path

    # Fallback: create in current directory
    settings_dir = cwd / ".claude"
    settings_dir.mkdir(exist_ok=True)
    return settings_dir / "settings.json"


def load_settings(settings_path: Path) -> dict:
    """Load existing settings or return empty dict."""
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}


def save_settings(settings_path: Path, settings: dict) -> None:
    """Save settings to file."""
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print(f"Updated: {settings_path}")


def apply_profile(profile_name: str) -> None:
    """Apply an agent profile to disable specified agents."""
    if profile_name not in AGENT_PROFILES:
        print(f"Unknown profile: {profile_name}")
        print(f"Available profiles: {', '.join(AGENT_PROFILES.keys())}")
        sys.exit(1)

    profile = AGENT_PROFILES[profile_name]
    settings_path = find_settings_file()
    settings = load_settings(settings_path)

    # Update or create agents section
    if "agents" not in settings:
        settings["agents"] = {}

    settings["agents"]["disabled"] = profile["disabled"]
    settings["agents"]["profile"] = profile_name

    save_settings(settings_path, settings)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"Agent Profile: {profile_name.upper()}")
    print(f"{'=' * 60}")
    print(f"\nDescription: {profile['description']}")

    disabled_count = len(profile["disabled"])
    enabled_count = len(ALL_AGENTS) - disabled_count

    print(f"\nAgents: {enabled_count} enabled, {disabled_count} disabled")

    if profile["disabled"]:
        print("\nDisabled agents:")
        for agent in profile["disabled"]:
            print(f"  - {agent}")

    print(f"\n{'=' * 60}")
    print("Configuration applied successfully!")
    print(f"{'=' * 60}\n")


def list_profiles() -> None:
    """List all available profiles."""
    print("\nAvailable Agent Profiles:")
    print("=" * 60)

    for name, profile in AGENT_PROFILES.items():
        disabled_count = len(profile["disabled"])
        enabled_count = len(ALL_AGENTS) - disabled_count
        print(f"\n{name}:")
        print(f"  Description: {profile['description']}")
        print(f"  Agents: {enabled_count} enabled, {disabled_count} disabled")

    print(f"\n{'=' * 60}")
    print("\nUsage: python agent-config.py --profile <profile_name>")


def show_current() -> None:
    """Show current agent configuration."""
    settings_path = find_settings_file()
    settings = load_settings(settings_path)

    print("\nCurrent Agent Configuration:")
    print("=" * 60)

    agents_config = settings.get("agents", {})
    current_profile = agents_config.get("profile", "none")
    disabled = agents_config.get("disabled", [])

    print(f"\nActive Profile: {current_profile}")
    print(f"Settings File: {settings_path}")

    if disabled:
        print(f"\nDisabled Agents ({len(disabled)}):")
        for agent in disabled:
            print(f"  - {agent}")

        enabled = [a for a in ALL_AGENTS if a not in disabled]
        print(f"\nEnabled Agents ({len(enabled)}):")
        for agent in enabled:
            print(f"  + {agent}")
    else:
        print("\nAll agents are enabled.")

    print(f"\n{'=' * 60}")


def reset_agents() -> None:
    """Reset to enable all agents."""
    apply_profile("full-stack")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude Code agent configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent-config.py --profile django    # Configure for Django development
  python agent-config.py --profile mobile    # Configure for React Native
  python agent-config.py --list              # Show available profiles
  python agent-config.py --current           # Show current configuration
  python agent-config.py --reset             # Enable all agents
        """,
    )

    parser.add_argument(
        "--profile",
        "-p",
        choices=list(AGENT_PROFILES.keys()),
        help="Apply agent profile",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available profiles",
    )
    parser.add_argument(
        "--current",
        "-c",
        action="store_true",
        help="Show current configuration",
    )
    parser.add_argument(
        "--reset",
        "-r",
        action="store_true",
        help="Reset to enable all agents",
    )

    args = parser.parse_args()

    if args.list:
        list_profiles()
    elif args.current:
        show_current()
    elif args.reset:
        reset_agents()
    elif args.profile:
        apply_profile(args.profile)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
