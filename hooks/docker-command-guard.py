#!/usr/bin/env python3
"""
Docker Command Guard Hook
Blocks development server commands that conflict with Docker services,
while allowing build commands and ONLY 'startapp' for Django.

This hook prevents agents from running:
- npm run dev / npm run serve (frontend already running in Docker)
- python manage.py runserver (Django already running in Docker)
- python manage.py <any command except startapp> (Postgres is in Docker)
- uvicorn / gunicorn dev commands (services already running)

But ALLOWS necessary commands:
- npm run build / npm run test (build operations)
- python manage.py startapp (ONLY Django command that runs locally - needs file ownership)
- docker compose commands (ALL Django commands should use this)
"""

import json
import sys
import re


# Commands that are BLOCKED (already running in Docker or need Docker DB)
BLOCKED_PATTERNS = [
    # Frontend dev servers
    r'\bnpm\s+run\s+(dev|serve)\b',
    r'\byarn\s+(dev|serve)\b',
    r'\bpnpm\s+(dev|serve)\b',
    # Invoking the vite binary directly, without a `build` subcommand.
    # Patterns are matched with re.IGNORECASE, so this must not fire on the
    # string "vite" appearing as anything other than a command word: it has to
    # sit at the start of the command or after a shell operator or a runner,
    # and be followed by whitespace or end-of-string. Without those guards it
    # blocked `cat vite.config.ts` and even the word "Vite" inside a comment
    # being written into a heredoc.
    r'(?:^|[;&|]\s*|\bnpx\s+|\byarn\s+|\bpnpm\s+(?:exec\s+)?)vite(?!\S)(?!.*\bbuild\b)',

    # Django dev server
    r'\bpython\s+manage\.py\s+runserver\b',
    r'\b\.\/manage\.py\s+runserver\b',

    # Django management commands (ALL require Docker DB except startapp)
    # This blocks everything, then ALLOWED_PATTERNS explicitly allows startapp
    r'\bpython\s+manage\.py\s+(?!startapp\b)\w+',
    r'\b\.\/manage\.py\s+(?!startapp\b)\w+',

    # ASGI/WSGI dev servers
    r'\buvicorn\b(?!.*--help)',  # uvicorn without --help
    r'\bgunicorn\b(?!.*--help)',  # gunicorn without --help
    r'\bdaphne\b(?!.*--help)',   # daphne without --help

    # Celery worker (if running in Docker)
    r'\bcelery\s+-A\s+\w+\s+worker\b',
]

# Commands that are ALLOWED (need local execution)
ALLOWED_PATTERNS = [
    # Build commands
    r'\bnpm\s+run\s+build\b',
    r'\bnpm\s+run\s+test\b',
    r'\byarn\s+build\b',
    r'\bvite\s+build\b',

    # Django: ONLY startapp (needs local file ownership)
    r'\bpython\s+manage\.py\s+startapp\b',
    r'\b\.\/manage\.py\s+startapp\b',

    # Docker commands (always allowed - this is how to run Django commands)
    r'\bdocker\s+compose\b',
    r'\bdocker-compose\b',
    r'\bdocker\s+',

    # Package management
    r'\bnpm\s+(install|ci|update)\b',
    r'\bpip\s+install\b',
]

# Help messages for blocked commands
HELP_MESSAGES = {
    'npm_dev': """
BLOCKED: npm run dev

Already running in Docker.

Instead:
  - Logs:    docker compose logs -f frontend
  - Restart: docker compose restart frontend
  - Build:   docker compose exec -T frontend npm run build
""",
    'django_runserver': """
BLOCKED: python manage.py runserver

Already running in Docker.

Instead:
  - Logs:    docker compose logs -f django
  - Restart: docker compose restart django
  - Shell:   docker compose exec django /entrypoint python manage.py shell
""",
    'django_management': """
BLOCKED: python manage.py <command>

Django management commands need the Postgres running in Docker.

Instead:
  - Migrations:  docker compose exec -T django /entrypoint python manage.py makemigrations
  - Migrate:     docker compose exec -T django /entrypoint python manage.py migrate
  - Shell:       docker compose exec django /entrypoint python manage.py shell
  - Superuser:   docker compose exec django /entrypoint python manage.py createsuperuser
  - Anything:    docker compose exec -T django /entrypoint python manage.py <command>

The /entrypoint prefix builds DATABASE_URL and cd's to /app/backend. Without it
you get a missing DATABASE_URL or the wrong working directory. Drop -T for
interactive commands like shell and dbshell.

If the service isn't running: docker compose up -d django, then retry. Don't
fall back to `run --rm` silently -- it costs ~13s per call against ~2.5s.

EXCEPTION: startapp runs locally, for file ownership:
  python manage.py startapp <app_name>
""",
    'uvicorn': """
BLOCKED: uvicorn/gunicorn/daphne dev server

Already running in Docker.

Instead:
  - Logs:    docker compose logs -f backend
  - Restart: docker compose restart backend
  - Run:     docker compose exec -T backend /entrypoint <command>
""",
    'celery_worker': """
BLOCKED: celery worker

Already running in Docker.

Instead:
  - Logs:    docker compose logs -f celery
  - Restart: docker compose restart celery
  - Inspect: docker compose exec -T celery celery -A <app> inspect active
""",
}


def get_help_message(command):
    """Get appropriate help message for blocked command"""
    if re.search(r'\bnpm\s+run\s+(dev|serve)\b', command):
        return HELP_MESSAGES['npm_dev']
    elif re.search(r'\bpython\s+manage\.py\s+runserver\b', command):
        return HELP_MESSAGES['django_runserver']
    elif re.search(r'\bpython\s+manage\.py\s+(?!startapp\b)\w+', command):
        return HELP_MESSAGES['django_management']
    elif re.search(r'\b(uvicorn|gunicorn|daphne)\b', command):
        return HELP_MESSAGES['uvicorn']
    elif re.search(r'\bcelery\s+-A\s+\w+\s+worker\b', command):
        return HELP_MESSAGES['celery_worker']
    else:
        return "This command conflicts with Docker services already running."


def should_block_command(command):
    """
    Determine if command should be blocked.
    Returns (should_block: bool, reason: str)
    """
    # First check if explicitly allowed
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, ""

    # Then check if blocked
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, get_help_message(command)

    # Default: allow
    return False, ""


def main():
    """Main hook entry point"""
    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Extract command from Bash tool input
        tool_input = hook_input.get('tool_input', {})
        command = tool_input.get('command', '')

        if not command:
            # No command to check, allow
            sys.exit(0)

        # Check if command should be blocked
        should_block, reason = should_block_command(command)

        if should_block:
            # Output context message to Claude
            print(reason, file=sys.stderr)

            # Exit with code 2 to block the command
            # Claude will show the stderr message to the user
            sys.exit(2)
        else:
            # Allow the command
            sys.exit(0)

    except Exception as e:
        # On error, log but don't block
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
