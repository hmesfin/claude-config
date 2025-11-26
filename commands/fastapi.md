---
name: fastapi
description: Configure Claude Code for FastAPI projects. Disables Django and mobile agents, enables FastAPI-specific agents.
---

# /fastapi Command

Configures Claude Code's specialized agents specifically for FastAPI projects.

## Quick Start

```bash
# Apply FastAPI profile
python scripts/agent-config.py --profile fastapi
```

## What This Does

**Disables** (11 agents):
- django-tdd-architect
- django-data-architect
- django-security-architect
- django-vue-staging-agent
- mobile-data-architect
- mobile-performance-optimizer
- mobile-realtime-architect
- mobile-security-architect
- react-native-tdd-architect
- native-module-tdd-engineer
- expo-deployment-agent

**Enables** (15 agents):
- fastapi-tdd-architect
- fastapi-data-architect
- fastapi-security-architect
- fastapi-vue-staging-agent
- vue-tdd-architect (for full-stack FastAPI+Vue.js)
- data-tdd-architect
- security-tdd-architect
- async-tdd-architect (for async endpoints and background tasks)
- realtime-tdd-architect (for WebSocket endpoints)
- e2e-tdd-architect
- performance-tdd-optimizer
- devops-tdd-engineer
- observability-tdd-engineer
- project-orchestrator
- tdd-test-specialist

## Usage

When this command runs, execute:

```bash
python scripts/agent-config.py --profile fastapi
```

This automatically updates `.claude/settings.json` with the FastAPI profile.

## When to Use

Use this command when:
- Starting a new FastAPI project
- Working on existing FastAPI-only project
- Building async REST APIs
- Full-stack FastAPI + Vue.js project
- High-performance API development

## FastAPI-Specific Agents

### fastapi-tdd-architect
- Async FastAPI endpoints
- Pydantic schemas and validation
- Dependency injection patterns
- OpenAPI/Swagger documentation

### fastapi-data-architect
- SQLAlchemy 2.0 async models
- Alembic migrations
- Async database sessions
- Query optimization with asyncio

### fastapi-security-architect
- FastAPI dependency-based RBAC
- OAuth2/JWT authentication
- Async authorization middleware
- Security dependencies

### fastapi-vue-staging-agent
- Traefik deployment configuration
- Docker compose for staging
- Nginx configuration for FastAPI+Vue.js

## Related Commands

- `/backend` - General backend configuration (Django + FastAPI)
- `/django` - Django-specific configuration
- `/mobile` - Switch to mobile development

## Docker Integration

All FastAPI commands run through Docker:

```bash
# Run server (already running via docker compose up)
docker compose logs -f fastapi

# Testing
docker compose run --rm fastapi pytest

# Alembic migrations
docker compose run --rm fastapi alembic revision --autogenerate -m "description"
docker compose run --rm fastapi alembic upgrade head

# Shell
docker compose run --rm fastapi python
```

## FastAPI Patterns

### Async-First Architecture
```python
# All endpoints are async
@app.get("/users/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Dependency Injection
```python
# Security dependencies
@app.get("/protected/")
async def protected_route(
    current_user: User = Depends(get_current_user),
    has_permission: bool = Depends(require_permission("admin"))
):
    return {"user": current_user}
```

## Verification

After running, verify configuration:

```bash
python scripts/agent-config.py --current
```

Expected output:
```
Active Profile: fastapi
Agents: 15 enabled, 11 disabled
```

## Standards Reference

FastAPI agents follow:
- `skills/DEVELOPMENT_STANDARDS.md` - File organization, TDD workflow
- 500-line file limit enforced
- Routers split by resource
- Schemas split by domain
- Dependencies split by purpose
- 85% test coverage minimum
