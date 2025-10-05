# Docker-First Development Workflow

This document explains the Docker-first development approach and how Claude Code hooks enforce it.

## Philosophy

**All services run in Docker containers.** Commands should be executed via `docker compose run --rm <service> <command>` unless there's a specific reason to run locally.

## What Runs Where

### ✅ Always in Docker

**Development Servers** (already running via `docker compose up`):
- Frontend: `npm run dev` / `yarn dev` / `vite`
- Django: `python manage.py runserver`
- ASGI servers: `uvicorn` / `gunicorn` / `daphne`
- Background workers: `celery worker`

**Most Commands**:
```bash
# Testing
docker compose run --rm django pytest
docker compose run --rm frontend npm run test

# Database operations
docker compose run --rm django python manage.py migrate
docker compose run --rm django python manage.py dbshell

# Package installation
docker compose run --rm frontend npm install
docker compose run --rm django pip install -r requirements.txt
```

### ✅ Sometimes Local

**Django: ONLY startapp** (file ownership - this is the ONLY Django command that runs locally):
```bash
# Creates files you need to edit with proper ownership
python manage.py startapp blog
```

**Frontend: Build operations** (often faster locally):
```bash
# Frontend production build
npm run build

# Frontend tests
npm run test
```

**One-time Setup**:
```bash
# Initial project setup (before Docker)
django-admin startproject myproject
npm create vue@latest
```

## The Hook System

Claude Code has a **PreToolUse hook** that intercepts Bash commands before execution.

### Blocked Commands

When an agent tries to run a blocked command, they'll see:

```
❌ BLOCKED: npm run dev

This command is already running in Docker.

✅ Instead use:
  - View logs: docker compose logs -f frontend
  - Restart: docker compose restart frontend
  - Build: docker compose run --rm frontend npm run build
```

### Allowed Commands

Commands that pass the hook execute normally:

```bash
✅ python manage.py startapp blog
✅ npm run build
✅ docker compose run --rm django pytest
```

## Common Patterns

### Pattern 1: Create Django App

```bash
# ❌ WRONG: Files owned by root (can't edit)
docker compose run --rm django python manage.py startapp blog

# ✅ CORRECT: Files owned by you
python manage.py startapp blog
```

### Pattern 2: Run Tests

```bash
# ✅ CORRECT: Always run in Docker for consistency
docker compose run --rm django pytest
docker compose run --rm frontend npm run test
```

### Pattern 3: Database Migrations (Always Docker - Postgres is in Docker!)

```bash
# ❌ WRONG: Can't connect to Postgres locally
python manage.py makemigrations
python manage.py migrate

# ✅ CORRECT: Always in Docker
docker compose run --rm django python manage.py makemigrations
docker compose run --rm django python manage.py migrate
docker compose run --rm django python manage.py shell
docker compose run --rm django python manage.py createsuperuser
```

### Pattern 4: Install Packages

```bash
# ✅ CORRECT: Install in Docker, update requirements file
docker compose run --rm django pip install django-rest-framework
echo "djangorestframework==3.14.0" >> backend/requirements.txt

# ✅ CORRECT: Frontend packages
docker compose run --rm frontend npm install axios
```

### Pattern 5: View Logs

```bash
# ✅ View running service logs
docker compose logs -f django
docker compose logs -f frontend
docker compose logs -f celery

# ✅ View all logs
docker compose logs -f
```

### Pattern 6: Build Frontend

```bash
# ✅ CORRECT: Build locally (faster, better error messages)
npm run build

# ✅ ALTERNATIVE: Build in Docker (if local env issues)
docker compose run --rm frontend npm run build
```

## Hook Configuration

The hook is defined in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/home/hamel/.claude/hooks/docker-command-guard.py"
          }
        ]
      }
    ]
  }
}
```

## Customizing the Hook

Edit `~/.claude/hooks/docker-command-guard.py` to modify behavior:

### Block Additional Commands

```python
BLOCKED_PATTERNS = [
    # ... existing patterns ...
    r'\bjest\s+--watch\b',  # Block jest watch mode
    r'\bwebpack\s+serve\b',  # Block webpack dev server
]
```

### Allow Additional Commands

```python
ALLOWED_PATTERNS = [
    # ... existing patterns ...
    r'\bpython\s+manage\.py\s+loaddata\b',  # Allow loading fixtures
    r'\bnpm\s+run\s+storybook\b',           # Allow Storybook
]
```

### Customize Help Messages

```python
HELP_MESSAGES = {
    'npm_dev': '''
❌ BLOCKED: npm run dev

Your custom message here...
''',
}
```

## Testing the Hook

```bash
# Test blocked command
echo '{"tool_input": {"command": "npm run dev"}}' | \
  python3 ~/.claude/hooks/docker-command-guard.py
# Exit code: 2 (blocked)

# Test allowed command
echo '{"tool_input": {"command": "npm run build"}}' | \
  python3 ~/.claude/hooks/docker-command-guard.py
# Exit code: 0 (allowed)
```

## Benefits

1. **Consistency**: Same environment across all developers
2. **No "works on my machine"**: Everything runs in standardized containers
3. **Easy onboarding**: New developers just run `docker compose up`
4. **Prevents mistakes**: Hook catches common errors automatically
5. **Clear guidance**: Helpful error messages show the right way

## Troubleshooting

### Hook not working

1. Check settings: `cat ~/.claude/settings.json`
2. Verify hook is executable: `ls -l ~/.claude/hooks/docker-command-guard.py`
3. Restart Claude Code
4. Test hook manually (see above)

### Hook blocking too much

- Add pattern to `ALLOWED_PATTERNS` in hook script
- Test with manual command
- Restart Claude Code

### Services not running

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## Related Documentation

- [Claude Code Hooks](~/.claude/hooks/README.md)
- [Django Best Practices](https://docs.djangoproject.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
