---
name: django
description: Configure Claude Code for Django projects. Disables FastAPI and mobile agents, enables Django-specific agents.
---

# /django Command

Configures Claude Code's specialized agents specifically for Django projects.

## Quick Start

```bash
# Apply Django profile
python scripts/agent-config.py --profile django
```

## What This Does

**Disables** (11 agents):
- fastapi-tdd-architect
- fastapi-data-architect
- fastapi-security-architect
- fastapi-vue-staging-agent
- mobile-data-architect
- mobile-performance-optimizer
- mobile-realtime-architect
- mobile-security-architect
- react-native-tdd-architect
- native-module-tdd-engineer
- expo-deployment-agent

**Enables** (15 agents):
- django-tdd-architect
- django-data-architect
- django-security-architect
- django-vue-staging-agent
- vue-tdd-architect (for full-stack Django+Vue.js)
- data-tdd-architect
- security-tdd-architect
- async-tdd-architect (for Celery tasks)
- realtime-tdd-architect (for Django Channels)
- e2e-tdd-architect
- performance-tdd-optimizer
- devops-tdd-engineer
- observability-tdd-engineer
- project-orchestrator
- tdd-test-specialist

## Usage

When this command runs, execute:

```bash
python scripts/agent-config.py --profile django
```

This automatically updates `.claude/settings.json` with the Django profile.

## When to Use

Use this command when:
- Starting a new Django project
- Working on existing Django-only project
- Building Django REST Framework APIs
- Full-stack Django + Vue.js project
- Django with Celery background tasks

## Django-Specific Agents

### django-tdd-architect
- Django REST Framework APIs
- Database models and migrations
- ViewSets and serializers
- Query optimization

### django-data-architect
- Database schema design
- Django ORM patterns
- PostgreSQL optimization
- Data migrations

### django-security-architect
- Django RBAC (permissions, groups)
- DRF authentication
- Custom permission classes
- Security middleware

### django-vue-staging-agent
- Traefik deployment configuration
- Docker compose for staging
- Nginx configuration for Django+Vue.js

## Related Commands

- `/backend` - General backend configuration (Django + FastAPI)
- `/fastapi` - FastAPI-specific configuration
- `/mobile` - Switch to mobile development

## Docker Integration

All Django commands run through Docker:

```bash
# Migrations
docker compose run --rm django python manage.py makemigrations
docker compose run --rm django python manage.py migrate

# Testing
docker compose run --rm django pytest

# Shell
docker compose run --rm django python manage.py shell
```

**Exception**: `python manage.py startapp <name>` runs locally for proper file ownership.

## Verification

After running, verify configuration:

```bash
python scripts/agent-config.py --current
```

Expected output:
```
Active Profile: django
Agents: 15 enabled, 11 disabled
```

## Standards Reference

Django agents follow:
- `skills/DEVELOPMENT_STANDARDS.md` - Django file organization, TDD workflow
- 500-line file limit enforced
- Models split into models/ directory
- Serializers split by domain
- Views split by resource
- 85% test coverage minimum (90% for models)
