# How We Work Together

1. **Ask questions before assuming** - If unclear, ask. Don't guess.
2. **Collaborate, don't automate** - Work with me, not around me.
3. **One change at a time** - Verify it works before moving on.
4. **Read your context** - Check CLAUDE.md and SKILL.md before acting.
5. **If stuck after 2 attempts, STOP and ask** - I have context you don't.

## Behavioral Rules

- Be a genuine thinking partner rather than just an echo chamber or validation machine
- If I ask a question, answer it - don't edit code
- Criticize my ideas constructively
- Get straight to the point - no fluff

## Coding Style

- 2-space indentation
- TypeScript/Python type hints everywhere
- No file over 500 lines - split when needed
- All imports at top (no inline imports)

## Docker Workflow

Services run via `docker compose up`. Use `docker compose run --rm <service>` for commands.

```bash
# Django commands
docker compose run --rm django python manage.py makemigrations
docker compose run --rm django python manage.py migrate
docker compose run --rm django pytest

# Frontend commands
docker compose run --rm frontend npm run test:run
docker compose run --rm frontend npm run type-check
```

**Exception:** `python manage.py startapp <name>` runs locally (for file ownership).

## Tools

- **Python:** Black, Ruff, Pytest, uv
- **JS/Vue/React Native:** Prettier, ESLint, Vitest/Jest, npm
- **Git:** Conventional commits (`type(scope): description`)

## TDD

Write tests first, implementation second. No exceptions.
