---
name: mobile
description: Configure Claude Code for mobile development (React Native). Disables backend framework agents, enables mobile agents.
---

# /mobile Command

Configures Claude Code's specialized agents for React Native mobile development.

## Quick Start

```bash
# Apply mobile profile
python scripts/agent-config.py --profile mobile
```

## What This Does

**Disables Backend Framework Agents** (9 agents):
- django-tdd-architect
- django-data-architect
- django-security-architect
- django-vue-staging-agent
- fastapi-tdd-architect
- fastapi-data-architect
- fastapi-security-architect
- fastapi-vue-staging-agent
- vue-tdd-architect

**Keeps Enabled** (17 agents):
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
- realtime-tdd-architect (for WebSocket patterns)
- e2e-tdd-architect (for Detox testing)
- performance-tdd-optimizer
- devops-tdd-engineer (for deployment)
- observability-tdd-engineer

## Usage

When this command runs, execute:

```bash
python scripts/agent-config.py --profile mobile
```

This automatically updates `.claude/settings.json` with the mobile profile.

## When to Use

Use this command when:
- Starting a new React Native mobile project
- Working on existing mobile-only project
- Switching from backend development to mobile work
- Building mobile apps with Expo or bare React Native

## Mobile-Specific Agents

### react-native-tdd-architect
- Component development with React Native Testing Library
- Navigation patterns (React Navigation)
- State management (Redux Toolkit, Zustand)
- Platform-specific code (.ios.tsx, .android.tsx)

### mobile-data-architect
- Offline-first data architecture
- AsyncStorage, MMKV, WatermelonDB
- React Query patterns
- Sync strategies

### mobile-security-architect
- Biometric authentication
- Secure storage (Keychain/Keystore)
- JWT token management
- Certificate pinning

### mobile-performance-optimizer
- App startup optimization
- Frame rate monitoring (60 FPS target)
- Memory management
- Bundle size optimization (<50MB)

### mobile-realtime-architect
- Socket.io reconnection patterns
- Mobile-specific challenges (battery, app state)
- Background handling
- Push notification integration

### native-module-tdd-engineer
- iOS Swift/Obj-C bridge code
- Android Kotlin/Java bridge code
- TurboModules
- Third-party SDK integration

### expo-deployment-agent
- EAS Build configuration
- OTA updates
- App store submissions
- Environment management

## Related Commands

- `/backend` - Switch to backend development configuration
- `/django` - Django-specific configuration
- `/fastapi` - FastAPI-specific configuration

## Verification

After running, verify configuration:

```bash
python scripts/agent-config.py --current
```

Expected output:
```
Active Profile: mobile
Agents: 17 enabled, 9 disabled
```

## React Native Patterns

### Feature-Based Module Structure
```
src/features/<feature>/
├── components/
├── hooks/
├── screens/
├── services/
├── store/
└── types/
```

### Platform-Specific Code
```typescript
// Component.ios.tsx - iOS-specific
// Component.android.tsx - Android-specific
// Component.tsx - Shared
```

### Offline-First Architecture
```typescript
// Always assume network unavailability
const data = useQuery({
  queryKey: ['items'],
  queryFn: fetchItems,
  staleTime: 5 * 60 * 1000,
  cacheTime: 24 * 60 * 60 * 1000,
});
```

## Reset to Full-Stack

To re-enable all agents:

```bash
python scripts/agent-config.py --reset
```

## Standards Reference

All enabled agents follow standards defined in:
- `skills/DEVELOPMENT_STANDARDS.md` - Complete development standards including React Native patterns
- Mobile-specific file organization (feature-based modules in `src/features/`)
- Offline-first data architecture
- Platform-specific code patterns (.ios.tsx, .android.tsx)
- 85% test coverage minimum (95% for security code)
