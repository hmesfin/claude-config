---
name: backend
description: Configure Claude Code for backend development (Django/FastAPI). Disables mobile agents, enables backend framework agents.
---

# /backend Command

Configures Claude Code's specialized agents for backend development.

## Quick Start

```bash
# Apply backend profile
python scripts/agent-config.py --profile backend
```

## What This Does

**Disables Mobile Agents** (7 agents):
- mobile-data-architect
- mobile-performance-optimizer
- mobile-realtime-architect
- mobile-security-architect
- react-native-tdd-architect
- native-module-tdd-engineer
- expo-deployment-agent

**Keeps Enabled** (19 agents):
- django-tdd-architect
- fastapi-tdd-architect
- django-data-architect, fastapi-data-architect
- django-security-architect, fastapi-security-architect
- data-tdd-architect
- security-tdd-architect
- async-tdd-architect
- devops-tdd-engineer
- project-orchestrator
- tdd-test-specialist
- vue-tdd-architect (for full-stack projects)
- And more...

## Usage

When this command runs, execute:

```bash
python scripts/agent-config.py --profile backend
```

This automatically updates `.claude/settings.json` with:

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
    ],
    "profile": "backend"
  }
}
```

## When to Use

Use this command when:
- Starting a new Django or FastAPI backend project
- Working on existing backend-only project
- Switching from mobile development to backend work
- Full-stack project focusing on backend tasks

## Related Commands

- `/mobile` - Switch to mobile development configuration
- `/django` - Django-specific configuration (more restrictive)
- `/fastapi` - FastAPI-specific configuration (more restrictive)

## Verification

After running, verify configuration:

```bash
python scripts/agent-config.py --current
```

Expected output:
```
Active Profile: backend
Agents: 19 enabled, 7 disabled

Disabled Agents (7):
  - mobile-data-architect
  - mobile-performance-optimizer
  ...
```

## Reset to Full-Stack

To re-enable all agents:

```bash
python scripts/agent-config.py --reset
```

## Standards Reference

All enabled agents follow standards defined in:
- `skills/DEVELOPMENT_STANDARDS.md` - Complete development standards
- `skills/TYPESCRIPT_PATTERNS.md` - TypeScript quality patterns (for full-stack)
