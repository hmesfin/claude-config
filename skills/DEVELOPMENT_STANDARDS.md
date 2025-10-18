# Development Standards for Claude Code

**Purpose**: This document codifies the mandatory development standards that Claude Code MUST follow across all projects. These standards are enforced by specialized agents, slash commands, and hooks.

## Table of Contents

1. [Core TDD Philosophy](#core-tdd-philosophy)
2. [File Organization Rules](#file-organization-rules)
3. [TypeScript Quality Standards](#typescript-quality-standards)
4. [Docker Workflow Requirements](#docker-workflow-requirements)
5. [Code Quality Gates](#code-quality-gates)
6. [Testing Standards](#testing-standards)
7. [Git Commit Standards](#git-commit-standards)

---

## Core TDD Philosophy

**The cardinal rule**: No code exists until there's a test that needs it.

### RED-GREEN-REFACTOR Cycle (Immutable Sequence)

1. **RED**: Write failing tests FIRST
2. **GREEN**: Write minimal code to pass tests
3. **REFACTOR**: Improve code while keeping tests green
4. **REPEAT**: Next feature or edge case

### You Will Be FIRED If You

- Write implementation before tests
- Skip edge case testing
- Ignore test coverage (minimum 85%)
- Commit code with failing tests
- Create files with >500 lines of code

### Test Coverage Requirements

| Layer | Minimum Coverage |
|-------|------------------|
| Models / Data | 90% |
| Serializers / API | 85% |
| Views / Components | 85% |
| Services / Business Logic | 85% |
| Utilities | 80% |
| **Overall** | **85%** |

### Special Requirements

- **Security code**: 95% coverage minimum
- **Data transformations**: 90% coverage minimum
- **Payment/financial code**: 100% coverage required

---

## File Organization Rules

**MANDATORY**: No file shall exceed 500 lines of code.

### File Splitting Triggers

✅ **Split immediately when**:

- File approaches 500 lines
- Component has >3 responsibilities
- Module has 3+ related views
- Logic used by 3+ modules

### Django Backend Structure

```
app/
├── models/              # Split by domain/aggregate
│   ├── __init__.py
│   ├── user.py
│   ├── profile.py
│   └── organization.py
├── serializers/         # Split by domain
│   ├── __init__.py
│   ├── user_serializers.py
│   └── organization_serializers.py
├── views/              # Split by resource
│   ├── __init__.py
│   ├── user_views.py
│   └── organization_views.py
├── services/           # Split by business logic domain
│   ├── __init__.py
│   ├── email_service.py
│   └── notification_service.py
├── tests/              # Mirror source structure
│   ├── models/
│   ├── views/
│   ├── serializers/
│   └── services/
└── migrations/
```

### Vue.js Frontend Structure

```
frontend/src/
├── modules/                    # Feature modules
│   ├── blog/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── views/
│   │   │   ├── dashboard/     # Protected routes
│   │   │   └── public/        # Public routes
│   │   └── routes.ts          # Exports blogRoutes.dashboard, blogRoutes.public
│   └── user/
├── shared/                     # Shared across 3+ modules
│   ├── components/
│   ├── composables/
│   └── utils/
├── components/                 # Global components
├── composables/               # Global composables
├── stores/                    # Global state
├── router/
│   └── index.ts              # Composes module routes by layout
└── layouts/
    ├── DashboardLayout.vue
    ├── AuthLayout.vue
    └── DefaultLayout.vue
```

### React Native Mobile Structure

```
src/
├── features/                  # Feature-based modules
│   ├── chat/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── screens/
│   │   ├── services/
│   │   ├── store/
│   │   └── types/
│   └── auth/
├── components/               # Shared components
├── navigation/              # Navigation config
│   ├── AuthNavigator.tsx
│   ├── AppNavigator.tsx
│   └── PublicNavigator.tsx
├── hooks/                   # Global hooks
├── services/                # Global services
└── utils/                   # Global utilities
```

### When to Create a Module/Feature

✅ **Create module when**:

- Feature has 3+ related views/screens
- Feature has dedicated API endpoints
- Feature has its own state management needs
- Feature can be developed/tested independently

❌ **Don't create module for**:

- Single view pages
- Simple utility functions
- Shared UI components
- Global application state

---

## TypeScript Quality Standards

**Battle-tested from 584 → 111 error reduction journey.**

### Rule 1: Type-Check FIRST, Before Any Commit

```bash
# ALWAYS run before committing
docker compose run --rm frontend npm run type-check

# Expected: "Found 0 errors"
# If errors exist, FIX THEM FIRST before writing new code
```

### Rule 2: Test Mocks Must Match Real Types

```typescript
// ❌ WRONG: Incomplete mock
const mockAgent: AgentProfile = {
  public_id: '123',
  slug: 'test',
  // Missing is_top_agent - causes errors!
}

// ✅ CORRECT: Complete mock
const mockAgent: AgentProfile = {
  public_id: '123',
  slug: 'test',
  is_top_agent: false,  // ALL required fields
}
```

### Rule 3: Template Refs Need Type Casting

```typescript
// ❌ WRONG
expect(wrapper.find('[data-test="input"]').element.value).toBe('test')

// ✅ CORRECT
expect((wrapper.find('[data-test="input"]').element as HTMLInputElement).value).toBe('test')
```

### Rule 4: Component Instance Access in Tests

```typescript
// ❌ WRONG
await wrapper.vm.goToStep(1)

// ✅ CORRECT (tests only!)
await (wrapper.vm as any).goToStep(1)
```

### Rule 5: Ref vs ComputedRef in Composables

```typescript
// ❌ WRONG: Using ref() for computed values
const createMockComposable = () => ({
  isComplete: ref(false),  // Should be computed!
})

// ✅ CORRECT
const createMockComposable = () => ({
  isComplete: computed(() => false),  // Match real composable
})
```

### Rule 6: API Client Generic Types

```typescript
// ✅ ALWAYS use generics
const user = await api.get<User>('/users/me/')
const response = await api.post<LoginResponse>('/auth/login/', credentials)
```

### Rule 7: Enum/Union Type Completeness

```typescript
// ❌ WRONG: Adding values later
export type LeadSource = 'blog' | 'social' | 'email'
// Later: LeadSource = 'mortgage_calculator'  ← ERROR!

// ✅ CORRECT: Add ALL values upfront
export type LeadSource =
  | 'blog'
  | 'social'
  | 'email'
  | 'mortgage_calculator'
  | 'net_proceeds_calculator'
  | 'rent_vs_buy_calculator'
```

### Rule 8: null vs undefined Handling

```typescript
// ❌ WRONG: Mixing null and undefined
formData.recurrence = pattern  // pattern could be undefined

// ✅ CORRECT: Convert undefined to null
formData.recurrence = pattern ?? null
```

### TypeScript Pre-Commit Checklist

Before committing ANY code:

1. Run type-check: `docker compose run --rm frontend npm run type-check`
2. If errors found:
   - Categorize: `npm run type-check 2>&1 | grep "error TS" | cut -d: -f3- | sort | uniq -c | sort -rn | head -10`
   - Fix highest-count errors first
   - Reference: `frontend/TYPESCRIPT_PATTERNS.md`
3. Run tests: `docker compose run --rm frontend npm run test:unit`
4. Run build: `docker compose run --rm frontend npm run build-only`
5. Only commit if ALL pass: TypeScript 0 errors ✅ Tests passing ✅ Build success ✅

---

## Docker Workflow Requirements

**Services run in Docker via `docker compose up`. A PreToolUse hook enforces this.**

### ❌ NEVER Run Locally (Hook Blocks These)

- `npm run dev` / `yarn dev` / `vite` - Frontend dev server (already running)
- `python manage.py runserver` - Django dev server (already running)
- `python manage.py migrate` - Postgres is in Docker
- `python manage.py makemigrations` - Postgres is in Docker
- `python manage.py shell` - Postgres is in Docker
- `python manage.py <any command except startapp>` - Postgres is in Docker
- `uvicorn` / `gunicorn` - ASGI servers (already running)
- `celery worker` - Background workers (already running)

### ✅ ONLY Django Command That Runs Locally

```bash
# Creates files with local user ownership (not root)
python manage.py startapp <app_name>
```

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

---

## Code Quality Gates

**Enforced via `/lint-and-format --gate` command**

### Quality Gate Sequence (ALL Must Pass)

Frontend Quality Gate:

1. TypeScript type-check (BLOCKER)
2. ESLint (BLOCKER)
3. Unit tests (BLOCKER)
4. Build check (BLOCKER)

Backend Quality Gate:

1. Ruff linting (BLOCKER)
2. Django system check (BLOCKER)

### Usage

```bash
# During development (find issues early)
/lint-and-format --frontend --fix --categorize --suggest-fixes

# Before committing (full quality check)
/lint-and-format --gate --frontend

# Track progress over time
/lint-and-format --trend
```

### Error Categorization

The `/lint-and-format` command categorizes errors by frequency:

```bash
# Show top 10 error patterns
/lint-and-format --frontend --categorize

# Get fix suggestions from pattern library
/lint-and-format --frontend --suggest-fixes
```

### Success Metrics

- TypeScript: 0 errors ✅
- ESLint: 0 errors ✅
- Tests: All passing ✅
- Build: Success ✅
- Coverage: 85%+ ✅

---

## Testing Standards

### Test Categories (All Required)

1. **Unit Tests**: Individual functions/methods
2. **Integration Tests**: API endpoints, database interactions
3. **Security Tests**: Authentication, authorization, injection attacks
4. **Performance Tests**: N+1 queries, load testing
5. **Edge Cases**: Null values, boundary conditions, race conditions

### Test Organization

```
tests/
├── unit/
│   ├── components/
│   ├── composables/
│   └── stores/
├── integration/
│   ├── api/
│   └── database/
├── security/
│   ├── permissions/
│   └── rbac/
└── performance/
    └── queries/
```

### Django Test Patterns

```python
# FIRST: Write tests
@pytest.mark.django_db
class TestProjectAPI:
    def test_list_projects_returns_paginated_results(self):
        # Test implementation
        pass

    def test_create_project_requires_authentication(self):
        # Security test
        pass

    def test_project_list_avoids_n_plus_1_queries(self):
        # Performance test
        with self.assertNumQueries(3):
            response = self.client.get('/api/v1/projects/')
```

### Vue.js Test Patterns

```typescript
// FIRST: Write tests
describe('UserProfile', () => {
  it('renders user information when loaded', async () => {
    // Test implementation
  })

  it('validates email format before submitting', async () => {
    // Validation test
  })

  it('handles API errors gracefully', async () => {
    // Error handling test
  })
})
```

### React Native Test Patterns

```typescript
// FIRST: Write tests
describe('ChatScreen', () => {
  it('renders message list', () => {
    // Rendering test
  })

  it('sends message on submit', async () => {
    // Interaction test
  })

  it('handles offline mode gracefully', async () => {
    // Offline-first test
  })
})
```

---

## Git Commit Standards

### Commit Format

```
type(scope): description

Longer description if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding tests
- `docs`: Documentation
- `style`: Formatting
- `perf`: Performance improvement
- `chore`: Build/tooling changes

### Git Safety Protocol

- NEVER update git config
- NEVER run destructive commands (push --force, hard reset) unless explicitly requested
- NEVER skip hooks (--no-verify, --no-gpg-sign)
- NEVER force push to main/master
- Avoid `git commit --amend` (only use when user requests OR adding pre-commit hook edits)

### Commit Process

1. Run `git status` to see untracked files
2. Run `git diff` to see staged/unstaged changes
3. Run `git log` to see recent commit messages (follow style)
4. Analyze changes and draft commit message
5. Add relevant files to staging
6. Create commit with proper format
7. Run `git status` after commit to verify

### DO NOT

- Push to remote unless user explicitly asks
- Create empty commits when no changes exist
- Use `git -i` commands (interactive mode not supported)
- Run additional commands to explore code (only git commands)

---

## Enforcement Mechanisms

### 1. Specialized Agents

26 specialized agents enforce these standards:

- `django-tdd-architect` - Django TDD enforcement
- `vue-tdd-architect` - Vue.js TDD enforcement
- `react-native-tdd-architect` - React Native TDD enforcement
- `tdd-test-specialist` - Overall TDD enforcement
- `security-tdd-architect` - Security testing enforcement
- And 21 more specialized agents

### 2. Slash Commands

- `/lint-and-format` - Code quality enforcement
- `/generate-legal` - Legal document generation

### 3. Hooks

- `docker-command-guard.py` - Enforces Docker workflow
- `typescript-quality-guard.py` - Prevents TypeScript errors before writing

### 4. Documentation

- `TYPESCRIPT_PATTERNS.md` - Battle-tested TypeScript patterns
- `DOCKER_WORKFLOW.md` - Docker workflow guide
- Agent-specific guides in `agents/` directory

---

## Quick Reference

### Before Starting Any Task

1. Understand requirements clearly
2. Plan TDD approach (tests first!)
3. Check file size limits
4. Verify Docker services running
5. Run type-check if frontend work

### Before Committing

```bash
# Frontend
docker compose run --rm frontend npm run type-check
docker compose run --rm frontend npm run test:unit
docker compose run --rm frontend npm run build-only

# Backend
docker compose run --rm django ruff check .
docker compose run --rm django pytest
docker compose run --rm django python manage.py check

# Quality gate (runs all)
/lint-and-format --gate
```

### When Stuck

1. Reference agent documentation in `agents/`
2. Check `TYPESCRIPT_PATTERNS.md` for frontend issues
3. Check `DOCKER_WORKFLOW.md` for Docker questions
4. Use `/lint-and-format --categorize --suggest-fixes` for errors
5. Ask user for clarification

---

## Success Criteria

Every task you complete must have:

- ✅ Tests written BEFORE implementation
- ✅ All tests passing (green)
- ✅ 85%+ code coverage
- ✅ TypeScript: 0 errors (frontend)
- ✅ No files exceeding 500 lines
- ✅ Proper file organization
- ✅ Security tests included
- ✅ Performance tests for queries
- ✅ Edge cases covered
- ✅ Git commit follows standards
- ✅ Quality gates passed

**Remember**: Code without tests is code that doesn't exist. Tests are not optional—they are the foundation.
