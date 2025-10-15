# My Personal Development Preferences

## Coding Style (All Projects)

- Use 2-space indentation
- Prefer functional components with hooks (React/Vue)
- Always use `const` or `let`, never `var`
- Write self-documenting code - comments only when necessary
- Use TypeScript/Python type hints everywhere
- **CRITICAL**: No file shall exceed 500 lines of code - split into directories when needed

## File Organization (MANDATORY)

### Django Backend
- Split models into `models/` directory by domain/aggregate
- Split serializers into `serializers/` by domain
- Split views into `views/` by resource
- Split services into `services/` by business logic domain
- Keep migrations focused (one schema change per file)

### Vue.js Frontend
- Use modular architecture with `modules/` directory
- Each module has its own: components, composables, services, stores, types, views
- Split routes by layout: `dashboard`, `public`
- Shared components go in `shared/` directory
- Global utilities in top-level `utils/`, `composables/`, `stores/`

### React Native Mobile
- Use feature-based modules in `src/features/<feature>/`
- Each feature has: components, hooks, screens, services, store, types
- Split native modules by platform: `ios/`, `android/`, `js/`
- Shared components in `src/components/`
- Platform-specific code: `Component.ios.tsx`, `Component.android.tsx`

### File Splitting Triggers
- File approaching 500 lines → Split immediately
- Component has >3 responsibilities → Extract sub-components
- Module has 3+ related views → Create feature module
- Logic used by 3+ modules → Move to `shared/`

## Behavioral Rules

- **NEVER** say "you're absolutely right" or "this project is now production ready"
- Ask clarifying questions before making assumptions
- If I ask a question, only answer the question - don't edit code
- Criticize my ideas constructively
- Get straight to the point - no fluff

## Docker Workflows (I develop in Docker)

**Services run in Docker via `docker compose up`. A PreToolUse hook enforces this.**

### ❌ NEVER Run Locally (Hook will block these)
- `npm run dev` / `yarn dev` / `vite` - Frontend dev server (already running)
- `python manage.py runserver` - Django dev server (already running)
- `python manage.py migrate` - Postgres is in Docker
- `python manage.py makemigrations` - Postgres is in Docker
- `python manage.py shell` - Postgres is in Docker
- `python manage.py <any command except startapp>` - Postgres is in Docker
- `uvicorn` / `gunicorn` - ASGI servers (already running)
- `celery worker` - Background workers (already running)

### ✅ ONLY Django Command That Runs Locally
- `python manage.py startapp <name>` - Creates files with local user ownership (not root)

### ✅ Allowed Local Commands
- `npm run build` - Build operations
- `npm run test` - Frontend tests
- `npm install` - Package installation
- `docker compose <anything>` - All Docker commands

### ✅ Correct Way to Run Django Commands
```bash
# Database operations
docker compose run --rm django python manage.py makemigrations
docker compose run --rm django python manage.py migrate

# Interactive shells
docker compose run --rm django python manage.py shell
docker compose run --rm django python manage.py dbshell

# User management
docker compose run --rm django python manage.py createsuperuser

# Testing
docker compose run --rm django pytest

# Custom management commands
docker compose run --rm django python manage.py <command>
```

### View Logs / Restart Services
```bash
# View logs
docker compose logs -f django
docker compose logs -f frontend
docker compose logs -f celery

# Restart services
docker compose restart django
docker compose restart frontend
```

## Git Preferences

- Commit frequently with descriptive messages
- Use conventional commits format: `type(scope): description`
- Always run tests before committing

## Tools I Use

- Formatter: Black (Python), Prettier (JS/Vue/React Native)
- Linter: Ruff (Python), ESLint (JS/Vue/React Native)
- Testing: Pytest (Python), Vitest (Vue), Jest (React Native)

## Architecture Patterns

### Django/Vue.js Stack
- **Backend**: Django REST Framework with TDD-first approach
- **Frontend**: Vue 3 Composition API + Pinia + Tailwind CSS
- **Database**: PostgreSQL (in Docker)
- **Async Tasks**: Celery (in Docker)
- **Real-time**: Django Channels + WebSockets

### React Native Mobile Stack
- **Framework**: React Native with Expo or bare workflow
- **State**: Redux Toolkit, Zustand, or React Context
- **Navigation**: React Navigation
- **Testing**: Jest + React Native Testing Library
- **Data**: AsyncStorage, MMKV, WatermelonDB, React Query
- **Real-time**: Socket.io or native WebSockets
- **Offline-First**: Always assume network unavailability

### Test-Driven Development (TDD)
- **RED-GREEN-REFACTOR** cycle is non-negotiable
- Write tests FIRST, implementation SECOND
- Minimum 85% code coverage (90% for data, 95% for security)
- No code exists until there's a test that needs it

### Module Pattern (Vue.js)
- Feature modules in `src/modules/<feature>/`
- Each module exports routes grouped by layout (dashboard, public, auth)
- Self-contained: components, composables, services, stores, types, views
- Example: `modules/blog/routes.ts` exports `blogRoutes.dashboard` and `blogRoutes.public`

### Module Pattern (React Native)
- Feature modules in `src/features/<feature>/`
- Each feature is self-contained: components, hooks, screens, services, store, types
- Platform-specific code uses `.ios.tsx`/`.android.tsx` extensions
- Navigation organized by flow: authenticated, public, onboarding
- Example: `features/chat/` contains all chat-related code in one place

## Related Documentation

- Docker workflow guide: `~/.claude/DOCKER_WORKFLOW.md`
- Hook system: `~/.claude/hooks/README.md`
- Specialized agents: `~/.claude/agents/`


# Agent Management Commands

## /backend
Disable all mobile agents and enable backend agents:
- Disable: mobile-data-architect, mobile-performance-optimizer, mobile-realtime-architect, mobile-security-architect, react-native-tdd-architect, native-module-tdd-engineer, expo-deployment-agent
- Keep enabled: fastapi-tdd-architect, django-tdd-architect, data-tdd-architect, security-tdd-architect, async-tdd-architect, devops-tdd-engineer, project-orchestrator, tdd-test-specialist

## /mobile
Disable all backend framework agents and enable mobile agents:
- Disable: fastapi-tdd-architect, fastapi-data-architect, fastapi-security-architect, fastapi-vue-staging-agent, django-tdd-architect, django-data-architect, django-security-architect, django-vue-staging-agent, vue-tdd-architect
- Keep enabled: mobile-data-architect, mobile-performance-optimizer, mobile-realtime-architect, mobile-security-architect, react-native-tdd-architect, native-module-tdd-engineer, expo-deployment-agent, project-orchestrator, tdd-test-specialist

## /fastapi
Configure for FastAPI projects:
- Disable: django-tdd-architect, django-data-architect, django-security-architect, django-vue-staging-agent, all mobile agents
- Enable: fastapi-tdd-architect, fastapi-data-architect, fastapi-security-architect, async-tdd-architect

## /django
Configure for Django projects:
- Disable: fastapi-tdd-architect, fastapi-data-architect, fastapi-security-architect, fastapi-vue-staging-agent, all mobile agents
- Enable: django-tdd-architect, django-data-architect, django-security-architect, async-tdd-architect