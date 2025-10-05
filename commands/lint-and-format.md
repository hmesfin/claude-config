---
name: lint-and-format
description: Run code linting and formatting for Django/Vue.js projects. Executes Ruff on Python code and ESLint+Prettier on JavaScript/Vue code. Supports auto-fixing issues and generating reports.
---

# /lint-and-format Command

Automated code linting and formatting for Django (Python) and Vue.js (JavaScript/TypeScript) codebases.

## Usage

```bash
/lint-and-format [options]
```

## Options

- `--backend` - Run linting on Django/Python code only
- `--frontend` - Run linting on Vue.js/JavaScript code only
- `--fix` - Automatically fix issues where possible
- `--check` - Check only, don't modify files
- `--report` - Generate detailed report

## Examples

```bash
# Lint and format everything
/lint-and-format --fix

# Check backend only
/lint-and-format --backend --check

# Fix frontend issues
/lint-and-format --frontend --fix

# Generate report
/lint-and-format --report
```

## What It Does

### Backend (Python/Django)

1. **Ruff** - Fast Python linter and formatter
   - Checks code style (PEP 8)
   - Finds bugs and anti-patterns
   - Auto-fixes formatting issues
   - Sorts imports

   ```bash
   docker compose run --rm django ruff check . --fix
   docker compose run --rm django ruff format .
   ```

2. **Import Sorting**
   ```bash
   docker compose run --rm django ruff check . --select I --fix
   ```

### Frontend (JavaScript/Vue.js)

1. **ESLint** - JavaScript/Vue linter
   - Checks code quality
   - Enforces Vue.js best practices
   - Finds potential bugs

   ```bash
   docker compose run --rm frontend npm run lint
   ```

2. **Prettier** - Code formatter
   - Formats JavaScript/TypeScript
   - Formats Vue components
   - Formats CSS/Tailwind

   ```bash
   docker compose run --rm frontend npm run format
   ```

## Configuration Files

The command uses existing project configurations:

**Backend:**
- `pyproject.toml` - Ruff configuration
- `.ruff.toml` - Additional Ruff settings

**Frontend:**
- `.eslintrc.js` - ESLint rules
- `.prettierrc` - Prettier settings

## Output

### Success Output
```
✅ Backend Linting: All checks passed
✅ Backend Formatting: No issues found
✅ Frontend Linting: All checks passed
✅ Frontend Formatting: No issues found

Summary: Code is clean and properly formatted
```

### Issues Found
```
❌ Backend Linting: 5 issues found
  - app/models.py:45:12 - Line too long (120 > 88 characters)
  - app/views.py:23:1 - Missing docstring

🔧 Auto-fixing...
✅ Fixed 3 issues automatically
⚠️  2 issues require manual fix

Frontend Linting: 2 issues found
  - src/components/UserList.vue:34 - Unused variable 'temp'

✅ All auto-fixable issues resolved
```

## Implementation

```python
import subprocess
import sys

def lint_and_format(backend=True, frontend=True, fix=False, check=False, report=False):
    """Run linting and formatting"""

    results = {'backend': None, 'frontend': None}

    if backend:
        print("🔍 Linting backend (Python/Django)...")

        # Ruff check
        ruff_cmd = ['docker', 'compose', 'run', '--rm', 'django', 'ruff', 'check', '.']
        if fix:
            ruff_cmd.append('--fix')

        backend_lint = subprocess.run(ruff_cmd, capture_output=True, text=True)

        # Ruff format
        if not check:
            ruff_format = subprocess.run(
                ['docker', 'compose', 'run', '--rm', 'django', 'ruff', 'format', '.'],
                capture_output=True, text=True
            )

        results['backend'] = {
            'lint': backend_lint.returncode == 0,
            'output': backend_lint.stdout + backend_lint.stderr
        }

        if results['backend']['lint']:
            print("✅ Backend: All checks passed")
        else:
            print(f"❌ Backend: Issues found\n{backend_lint.stdout}")

    if frontend:
        print("\n🔍 Linting frontend (Vue.js/JavaScript)...")

        # ESLint
        eslint_cmd = ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'lint']
        if fix:
            eslint_cmd.append('--', '--fix')

        frontend_lint = subprocess.run(eslint_cmd, capture_output=True, text=True)

        # Prettier
        if not check:
            prettier = subprocess.run(
                ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'format'],
                capture_output=True, text=True
            )

        results['frontend'] = {
            'lint': frontend_lint.returncode == 0,
            'output': frontend_lint.stdout
        }

        if results['frontend']['lint']:
            print("✅ Frontend: All checks passed")
        else:
            print(f"❌ Frontend: Issues found\n{frontend_lint.stdout}")

    # Generate report
    if report:
        generate_lint_report(results)

    # Exit with error if issues found
    all_passed = all(
        r['lint'] for r in results.values() if r is not None
    )
    sys.exit(0 if all_passed else 1)

def generate_lint_report(results):
    """Generate detailed linting report"""
    print("\n" + "="*50)
    print("LINTING REPORT")
    print("="*50)

    for layer, result in results.items():
        if result:
            status = "✅ PASSED" if result['lint'] else "❌ FAILED"
            print(f"\n{layer.upper()}: {status}")
            if result['output']:
                print(result['output'])
```

## Pre-commit Hook Integration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: lint-and-format
        name: Lint and Format
        entry: /lint-and-format --fix
        language: system
        pass_filenames: false
```

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Lint and Format Check
  run: /lint-and-format --check
```

## Notes

- Always run in Docker for consistency
- Auto-fix is safe for formatting, manual review for logic issues
- Integrates with existing project configs
- Runs fast (Ruff is extremely fast)
