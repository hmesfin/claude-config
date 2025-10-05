# Claude Code Hooks

Custom hooks for Claude Code to enforce Docker-first development workflow.

## Docker Command Guard Hook

**Purpose**: Prevent agents from running development servers that are already running in Docker, while allowing necessary build and management commands.

### What It Blocks

❌ **Blocked commands** (already running in Docker or require Docker DB):
- `npm run dev` / `npm run serve` - Frontend dev server
- `yarn dev` / `pnpm dev` - Alternative package managers
- `python manage.py runserver` - Django dev server
- `python manage.py migrate` - Requires Postgres in Docker
- `python manage.py makemigrations` - Requires Postgres in Docker
- `python manage.py shell` - Requires Postgres in Docker
- `python manage.py <any command except startapp>` - Requires Postgres in Docker
- `uvicorn` / `gunicorn` - ASGI/WSGI servers
- `celery -A app worker` - Celery workers

### What It Allows

✅ **Allowed commands** (need local execution):
- `npm run build` / `npm run test` - Build and test operations
- `python manage.py startapp <name>` - **ONLY Django command allowed locally** (needs local file ownership)
- `docker compose run --rm django python manage.py <command>` - All other Django commands
- `docker compose <command>` - All Docker commands
- `npm install` / `pip install` - Package installation

### Why This Matters

**Problem 1**: Agents try to run development servers locally, not realizing they're already running in Docker.

**Problem 2**: Agents try to run Django management commands locally, but Postgres is in Docker.

**Django startapp - The ONLY exception**:
```bash
# ❌ Running in Docker creates files owned by root
docker compose run --rm django python manage.py startapp blog
# Result: Can't edit files (permission denied)

# ✅ Running locally creates files owned by your user
python manage.py startapp blog
# Result: Files are editable
```

**All other Django commands need Docker**:
```bash
# ❌ WRONG: Can't connect to Postgres (it's in Docker)
python manage.py migrate

# ✅ CORRECT: Runs in Docker with access to Postgres
docker compose run --rm django python manage.py migrate
```

### Installation

1. **Create settings file** (if it doesn't exist):
```bash
mkdir -p ~/.claude
```

2. **Add hook configuration** to `~/.claude/settings.json`:
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

3. **Restart Claude Code** for hooks to take effect.

### How It Works

1. **Before every Bash command**, Claude Code calls the hook
2. **Hook analyzes the command** using regex patterns
3. **If blocked**: Hook exits with code 2 and shows helpful message
4. **If allowed**: Hook exits with code 0 and command proceeds

### Example Blocked Commands

**When agent tries `npm run dev`**:
```
❌ BLOCKED: npm run dev

This command is already running in Docker.

✅ Instead use:
  - View logs: docker compose logs -f frontend
  - Restart: docker compose restart frontend
  - Build: docker compose run --rm frontend npm run build
```

**When agent tries `python manage.py migrate`**:
```
❌ BLOCKED: python manage.py migrate

Django management commands require the Postgres database running in Docker.

✅ Instead use:
  - Migrations: docker compose run --rm django python manage.py makemigrations
  - Migrate: docker compose run --rm django python manage.py migrate
  - Shell: docker compose run --rm django python manage.py shell
  - Create superuser: docker compose run --rm django python manage.py createsuperuser
  - Custom commands: docker compose run --rm django python manage.py <command>

⚠️  EXCEPTION: Only 'startapp' runs locally (for file ownership):
  - Create app: python manage.py startapp <app_name>
```

### Example Allowed Commands

**When agent runs `python manage.py startapp blog`**:
```
✅ ALLOWED: Creating Django app locally for proper file permissions
```

**When agent runs `docker compose run --rm django python manage.py migrate`**:
```
✅ ALLOWED: Running Django management command in Docker with DB access
```

### Customization

Edit `/home/hamel/.claude/hooks/docker-command-guard.py` to:

- Add more blocked patterns to `BLOCKED_PATTERNS`
- Add more allowed patterns to `ALLOWED_PATTERNS`
- Customize help messages in `HELP_MESSAGES`

**Example: Block additional commands**
```python
BLOCKED_PATTERNS = [
    # ... existing patterns ...
    r'\bjest\s+--watch\b',  # Block jest watch mode
    r'\bwebpack\s+serve\b',  # Block webpack dev server
]
```

**Example: Allow additional commands**
```python
ALLOWED_PATTERNS = [
    # ... existing patterns ...
    r'\bpython\s+manage\.py\s+loaddata\b',  # Allow loading fixtures
    r'\bnpm\s+run\s+storybook\b',           # Allow Storybook
]
```

### Testing the Hook

```bash
# Test the hook directly
echo '{"tool_input": {"command": "npm run dev"}}' | python3 ~/.claude/hooks/docker-command-guard.py
# Should exit with code 2 (blocked)

echo '{"tool_input": {"command": "npm run build"}}' | python3 ~/.claude/hooks/docker-command-guard.py
# Should exit with code 0 (allowed)
```

### Troubleshooting

**Hook not triggering:**
- Check `~/.claude/settings.json` has correct hook configuration
- Restart Claude Code
- Verify hook script is executable: `ls -l ~/.claude/hooks/docker-command-guard.py`

**Hook blocking too much:**
- Add pattern to `ALLOWED_PATTERNS` in the hook script
- Test with echo command above

**Hook not blocking enough:**
- Add pattern to `BLOCKED_PATTERNS` in the hook script
- Test with echo command above

### Safety

- Hook only affects Bash tool commands
- Hook never modifies files or system
- On error, hook allows command (fail-safe)
- Hook is local to your machine only

### Related Documentation

- [Claude Code Hooks Guide](https://docs.claude.com/en/docs/claude-code/hooks-guide.md)
- [Claude Code Settings](https://docs.claude.com/en/docs/claude-code/settings)
