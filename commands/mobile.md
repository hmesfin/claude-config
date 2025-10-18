---
name: mobile
description: Configure Claude Code for mobile development (React Native). Disables backend framework agents, enables mobile agents.
---

# /mobile Command

Configures Claude Code's specialized agents for React Native mobile development.

## What This Does

**Disables Backend Framework Agents**:
- django-tdd-architect
- django-data-architect
- django-security-architect
- django-vue-staging-agent
- fastapi-tdd-architect
- fastapi-data-architect
- fastapi-security-architect
- fastapi-vue-staging-agent
- vue-tdd-architect

**Keeps Enabled**:
- react-native-tdd-architect
- mobile-data-architect
- mobile-performance-optimizer
- mobile-realtime-architect
- mobile-security-architect
- native-module-tdd-engineer
- expo-deployment-agent
- project-orchestrator
- tdd-test-specialist
- data-tdd-architect (for shared data patterns)
- security-tdd-architect (for shared security patterns)
- async-tdd-architect (for background tasks)
- devops-tdd-engineer (for deployment)

## Usage

```bash
/mobile
```

## When to Use

Use this command when:
- Starting a new React Native mobile project
- Working on existing mobile-only project
- Switching from backend development to mobile work
- Building mobile apps with Expo or bare React Native

## Related Commands

- `/backend` - Switch to backend development configuration
- `/django` - Django-specific configuration
- `/fastapi` - FastAPI-specific configuration

## Implementation

This command updates your agent configuration to optimize for mobile development. Backend framework agents (Django/FastAPI/Vue.js) are disabled to focus on React Native patterns.

**Note**: This is a configuration command. The actual agent enabling/disabling is managed through your Claude Code settings. Currently, you need to manually disable agents in settings. A future version may automate this.

## Manual Steps (Until Automated)

1. Open Claude Code settings
2. Navigate to Agents section
3. Disable the backend framework agents listed above
4. Ensure mobile agents are enabled
5. Restart Claude Code if needed

## Future Enhancement

A script could automate agent management by updating `.claude/settings.json`:

```json
{
  "agents": {
    "disabled": [
      "django-tdd-architect",
      "django-data-architect",
      "django-security-architect",
      "django-vue-staging-agent",
      "fastapi-tdd-architect",
      "fastapi-data-architect",
      "fastapi-security-architect",
      "fastapi-vue-staging-agent",
      "vue-tdd-architect"
    ]
  }
}
```

## Standards Reference

All enabled agents follow standards defined in:
- `skills/DEVELOPMENT_STANDARDS.md` - Complete development standards including React Native patterns
- Mobile-specific file organization (feature-based modules in `src/features/`)
- Offline-first data architecture
- Platform-specific code patterns (.ios.tsx, .android.tsx)
