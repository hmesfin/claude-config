---
name: backend
description: Configure Claude Code for backend development (Django/FastAPI). Disables mobile agents, enables backend framework agents.
---

# /backend Command

Configures Claude Code's specialized agents for backend development.

## What This Does

**Disables Mobile Agents**:
- mobile-data-architect
- mobile-performance-optimizer
- mobile-realtime-architect
- mobile-security-architect
- react-native-tdd-architect
- native-module-tdd-engineer
- expo-deployment-agent

**Keeps Enabled**:
- django-tdd-architect
- fastapi-tdd-architect
- data-tdd-architect
- security-tdd-architect
- async-tdd-architect
- devops-tdd-engineer
- project-orchestrator
- tdd-test-specialist
- vue-tdd-architect (for full-stack projects)

## Usage

```bash
/backend
```

## When to Use

Use this command when:
- Starting a new Django or FastAPI backend project
- Working on existing backend-only project
- Switching from mobile development to backend work
- Full-stack project focusing on backend tasks

## Related Commands

- `/mobile` - Switch to mobile development configuration
- `/django` - Django-specific configuration
- `/fastapi` - FastAPI-specific configuration

## Implementation

This command updates your agent configuration to optimize for backend development. Mobile-specific agents are disabled to reduce noise and improve Claude Code's focus on backend tasks.

**Note**: This is a configuration command. The actual agent enabling/disabling is managed through your Claude Code settings. Currently, you need to manually disable agents in settings. A future version may automate this.

## Manual Steps (Until Automated)

1. Open Claude Code settings
2. Navigate to Agents section
3. Disable the mobile agents listed above
4. Ensure backend agents are enabled
5. Restart Claude Code if needed

## Future Enhancement

A script could automate agent management by updating `.claude/settings.json`:

```json
{
  "agents": {
    "disabled": [
      "mobile-data-architect",
      "mobile-performance-optimizer",
      "mobile-realtime-architect",
      "mobile-security-architect",
      "react-native-tdd-architect",
      "native-module-tdd-engineer",
      "expo-deployment-agent"
    ]
  }
}
```

## Standards Reference

All enabled agents follow standards defined in:
- `skills/DEVELOPMENT_STANDARDS.md` - Complete development standards
- `skills/TYPESCRIPT_PATTERNS.md` - TypeScript quality patterns (for full-stack)
