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
- Split routes by layout: `dashboard`, `public`, `auth`
- Shared components go in `shared/` directory
- Global utilities in top-level `utils/`, `composables/`, `stores/`

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

- Formatter: Black (Python), Prettier (JS/Vue)
- Linter: Ruff (Python), ESLint (JS/Vue)
- Testing: Pytest (Python), Vitest (Vue)

## Architecture Patterns

### Django/Vue.js Stack
- **Backend**: Django REST Framework with TDD-first approach
- **Frontend**: Vue 3 Composition API + Pinia + Tailwind CSS
- **Database**: PostgreSQL (in Docker)
- **Async Tasks**: Celery (in Docker)
- **Real-time**: Django Channels + WebSockets

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

## Related Documentation

- Docker workflow guide: `~/.claude/DOCKER_WORKFLOW.md`
- Hook system: `~/.claude/hooks/README.md`
- Specialized agents: `~/.claude/agents/`
