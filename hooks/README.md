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
            "command": "~/.claude/hooks/docker-command-guard.py"
          }
        ]
      }
    ]
  }
}
```

**Note**: The `~/.claude/hooks/` path works because hooks are symlinked from `claude-config/hooks/`. This makes the configuration portable across different user accounts.

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

Edit `~/.claude/hooks/docker-command-guard.py` (or `claude-config/hooks/docker-command-guard.py`) to:

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

---

## TypeScript Quality Guard Hook

**Purpose**: Prevent common TypeScript errors BEFORE code is written by warning agents about error-prone patterns.

### What It Does

⚠️ **Provides warnings when writing**:
- Vue components (`.vue` files)
- Test files (`.spec.ts`, `.test.ts`)
- Type definitions (`.types.ts` files)
- Composables (`composables/*.ts`)

### Pattern Warnings

**1. Test Mock Files**
```
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Test File

Common test patterns that cause TypeScript errors:

1. Template Refs - Cast to proper HTML type:
   ✅ (wrapper.find('[data-test="input"]').element as HTMLInputElement).value

2. Component Instance Access - Use 'any' in tests:
   ✅ await (wrapper.vm as any).methodName()

3. Mock Composables - Match real return types:
   ✅ Use computed(() => value) for computed refs, not ref(value)

4. Complete Mocks - Include ALL required properties:
   💡 Hover over type in VSCode to see all required fields

Reference: frontend/TYPESCRIPT_PATTERNS.md
```

**2. Vue Components**
```
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Vue Component

Before writing component code:

1. Run type-check to ensure codebase is clean:
   docker compose run --rm frontend npm run type-check

2. If creating types, ensure unions/enums are COMPLETE:
   ✅ Add ALL possible values upfront to avoid future errors

3. API calls should use generic types:
   ✅ api.get<User>('/users/me/') not api.get('/users/me/')

Reference: /lint-and-format --frontend --categorize --suggest-fixes
```

**3. Type Definitions**
```
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Type Definitions

Type safety checklist:

1. Union types - Include ALL possible values now, not later
2. Interfaces - Mark optional fields with '?'
3. Enums - Add new values as features are created
4. null vs undefined - Be consistent (prefer null)

Common issue: Adding type values after code uses them
✅ Update type FIRST, then use new values in code

Reference: frontend/TYPESCRIPT_PATTERNS.md - Pattern 7
```

**4. Composables**
```
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Composable

Composable type safety:

1. Computed properties - Return ComputedRef<T>, not Ref<T>
2. Refs - Use Ref<T> for mutable state
3. Return types - Explicitly type the return object
4. Generic types - Use <T> for reusable composables

Common issue: Mixing ref() and computed() incorrectly
✅ If logic computes a value, use computed(), not ref()

Reference: frontend/TYPESCRIPT_PATTERNS.md - Pattern 6
```

### Installation

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/docker-command-guard.py"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/typescript-quality-guard.py"
          }
        ]
      }
    ]
  }
}
```

### How It Works

1. **Before every Write/Edit** on frontend/src files
2. **Checks file pattern** (test file, Vue component, etc.)
3. **Shows relevant warnings** about common TypeScript pitfalls
4. **Checks current error count** and warns if errors exist
5. **Allows operation** (non-blocking - just educational)

### Example Output

**When writing test file with existing TypeScript errors:**
```
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Test File

[Pattern warnings shown above]

⚠️  CURRENT TYPESCRIPT ERRORS: 111
   Consider fixing existing errors before adding new code.
   Run: /lint-and-format --frontend --categorize
```

### Why This Hook Matters

**Based on battle-tested learnings from 584 → 111 TypeScript error reduction:**

- **Prevention > Reaction**: Catching patterns before they're written
- **Educational**: Teaches agents about TypeScript best practices
- **Non-blocking**: Warnings don't prevent work, just raise awareness
- **Pattern library**: References actual fixes from real error cleanup

### Battle-Tested Effectiveness

This hook codifies learnings from fixing **473 TypeScript errors** (81% reduction):

- Template ref type casting (45 errors)
- Test mock completeness (24 errors)
- Ref vs ComputedRef (86 errors)
- API client generic types (76 errors)
- Union type completeness (multiple patterns)

**Result**: Agents write TypeScript-clean code from the start, not after CI fails.

### Testing the Hook

```bash
# Test the hook directly
echo '{"tool_name": "Write", "tool_input": {"file_path": "frontend/src/components/Test.spec.ts"}}' | \
  python3 ~/claude-config/hooks/typescript-quality-guard.py

# Should show test file warnings
```

### Customization

Edit `~/.claude/hooks/typescript-quality-guard.py` (or `claude-config/hooks/typescript-quality-guard.py`) to:

- Add more pattern warnings for specific file types
- Customize warning messages based on your patterns
- Adjust error count threshold for warnings

**Example: Add store pattern**
```python
"pinia store": {
    "trigger": r"stores/.*\.ts",
    "warning": """
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Pinia Store

Store type safety:
1. Use defineStore() with setup syntax for type inference
2. Return object should be explicitly typed
3. Actions should have typed parameters
""",
},
```

### Safety

- Hook only shows warnings, never blocks operations
- Hook fails silently on errors (fail-safe)
- Hook only checks frontend/src files
- No file modifications or system changes

### Related Documentation

- `skills/TYPESCRIPT_PATTERNS.md` - Pattern reference library (battle-tested from 584→111 error reduction)
- `/lint-and-format --frontend` - Error categorization tool
- [Claude Code Hooks Guide](https://docs.claude.com/en/docs/claude-code/hooks-guide.md)
- [Claude Code Settings](https://docs.claude.com/en/docs/claude-code/settings)

---

## Auto-Progress Tracking Hook (P0.1)

**Purpose**: Automatically manage GitHub issues when you commit code with issue references.

**Part of**: P0 GitHub Automation (see `docs/P0_IMPLEMENTATION.md`)

### What It Does

✅ **On git commit with issue references**:
- Detects commits with `fixes #N`, `closes #N`, `resolves #N`
- Automatically closes referenced GitHub issue
- Posts progress comment: "15/27 complete (55%)"
- Suggests next sequential open issue

### Files

- `post-tool-use/auto-progress-tracker.py` - Main hook script (PostToolUse)
- `lib/github_automation.py` - GitHub REST API integration

### Installation

1. **Set GitHub Token** environment variable:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="your-github-pat-here"

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

2. **Hook configuration** (in `~/.claude/settings.json`):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/post-tool-use/auto-progress-tracker.py"
          }
        ]
      }
    ]
  }
}
```

3. **Restart Claude Code** for hooks to take effect.

### How It Works

1. **After every Bash git commit**, hook analyzes commit message
2. **Extracts issue references** using regex patterns
3. **Calls GitHub API** to close issues and post comments
4. **Outputs systemMessage** with next issue suggestion

### Usage

```bash
# Working on issue #15
git commit -m "fixes #15: Implement authentication system"

# Hook runs automatically:
# ✅ Closed issue #15
# 📊 Progress: 15/27 (55%) complete
# 🚀 Next issue: #16
```

### Supported Formats

```bash
# Basic reference
git commit -m "fixes #15"

# With description
git commit -m "fixes #15: Add user auth"

# Multiple issues
git commit -m "fixes #15, closes #16"

# Cross-repo reference
git commit -m "fixes owner/repo#15"
```

### Supported Keywords

- `fix` / `fixes`
- `close` / `closes`
- `resolve` / `resolves`

**Note**: Simple `#N` references are detected but NOT auto-closed (only explicit keywords close issues).

### Example Output

**When issue is closed**:
```
✅ Closed issue #15
🚀 Next issue: #16
Tip: You can say 'Show me issue #16' to start working on it
```

**When no more issues**:
```
✅ Closed issue #27
🎉 No more open issues!
```

### Requirements

- Python 3.7+
- `requests` library (install: `pip install requests`)
- `GITHUB_TOKEN` environment variable set to your PAT
- Git repository with GitHub remote

### Testing the Hook

```bash
# Test without committing
echo '{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m \"fixes #999: Test commit\""
  }
}' | ~/.claude/hooks/post-tool-use/auto-progress-tracker.py
```

### Troubleshooting

**Hook not running:**
- Check `GITHUB_TOKEN` is set: `echo $GITHUB_TOKEN`
- Verify hook is executable: `ls -l ~/.claude/hooks/post-tool-use/auto-progress-tracker.py`
- Check settings.json has PostToolUse configuration
- Restart Claude Code

**GitHub API errors:**
```bash
# Test GitHub API access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**Issues not closing:**
- Verify commit message uses keywords: `fixes`, `closes`, `resolves`
- Check issue number exists in repository
- Verify repository remote is GitHub

### Safety

- Hook never fails git commit (exits 0 even on errors)
- Only closes issues with explicit keywords
- Read-only access to repository info
- No file modifications or system changes

### GitHub API Library

**Location**: `lib/github_automation.py`

**Features**:
- Direct GitHub REST API integration
- Issue management (list, get, update, comment)
- Progress calculation
- Next issue suggestion

**Usage** (in other hooks):
```python
from lib.github_automation import GitHubAPI

api = GitHubAPI()  # Uses GITHUB_TOKEN from environment

# Close issue
api.update_issue('owner', 'repo', 15, state='closed')

# Add comment
api.add_comment('owner', 'repo', 15, 'Progress update')

# Calculate progress
progress = api.calculate_progress('owner', 'repo')
# Returns: {'total': 27, 'closed': 15, 'open': 12, 'percentage': 55.5}
```

### Related

- **Test Coverage Guardian**: See `github-actions/coverage-guardian/`
- **Complete Documentation**: `docs/P0_IMPLEMENTATION.md`
- **Enhancement Ideas**: `docs/GH_MCP_IDEAS.md`
