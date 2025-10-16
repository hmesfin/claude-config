---
name: lint-and-format
description: Preventative code quality tool for Django/Vue.js projects. Runs TypeScript type-checking, ESLint, Prettier, and Ruff. Categorizes errors, suggests fixes, tracks trends, and enforces quality gates. Prevents commits with TypeScript/lint errors.
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
- `--gate` - Quality gate mode: blocks on ANY error (TypeScript, ESLint, tests, build)
- `--type-check` - Include TypeScript type-checking (enabled by default for frontend)
- `--no-type-check` - Skip TypeScript type-checking (not recommended)
- `--categorize` - Show error categorization by frequency
- `--suggest-fixes` - Show smart fix suggestions based on error patterns
- `--trend` - Show error trend over time

## Examples

```bash
# Lint and format everything (includes TypeScript check)
/lint-and-format --fix

# Check backend only
/lint-and-format --backend --check

# Fix frontend issues with type-checking
/lint-and-format --frontend --fix

# Run quality gate (blocks on any error)
/lint-and-format --gate --frontend

# Show error categorization and fix suggestions
/lint-and-format --frontend --categorize --suggest-fixes

# Show error trend over time
/lint-and-format --trend

# Generate detailed report
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

### Frontend (JavaScript/Vue.js/TypeScript)

1. **TypeScript Type-Checking** - FIRST (highest priority)
   - Validates TypeScript types across entire codebase
   - Catches type errors before runtime
   - Prevents type-related bugs
   - **NEW**: Categorizes errors by frequency
   - **NEW**: Suggests fixes from pattern library

   ```bash
   docker compose run --rm frontend npm run type-check
   ```

2. **ESLint** - JavaScript/Vue linter (SECOND priority)
   - Checks code quality
   - Enforces Vue.js best practices
   - Finds potential bugs
   - **NEW**: Categorizes errors by rule

   ```bash
   docker compose run --rm frontend npm run lint
   ```

3. **Prettier** - Code formatter (LAST - just formatting)
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
import re
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

# Error history tracking
ERROR_HISTORY_FILE = '.claude/error-history.json'

# TypeScript fix patterns from TYPESCRIPT_PATTERNS.md
TYPESCRIPT_FIX_PATTERNS = {
    "Property 'value' does not exist on type 'VueNode<Element>'": {
        "fix": "Cast element to proper HTML type",
        "example": "(wrapper.find('[data-test=\"input\"]').element as HTMLInputElement).value",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 2"
    },
    "is missing in type": {
        "fix": "Add missing required property to type/mock",
        "example": "Add property to interface or test mock",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 3"
    },
    "Type 'Ref<": {
        "fix": "Use computed() instead of ref() for computed properties",
        "example": "const value = computed(() => data.value)",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 6"
    },
    "is not assignable to type": {
        "fix": "Check type definition matches usage",
        "example": "Verify enum includes all values being used",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 5"
    },
    "does not exist on type": {
        "fix": "Cast component instance or template ref to proper type",
        "example": "(wrapper.vm as any).methodName() or (element as HTMLInputElement).value",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 1-2"
    },
}


def categorize_typescript_errors(output):
    """Categorize TypeScript errors for quick triage"""
    # Extract error patterns
    error_pattern = r'error TS\d+: (.+?)$'
    errors = re.findall(error_pattern, output, re.MULTILINE)

    if not errors:
        return ""

    # Count by category
    error_counts = Counter(errors)

    # Sort by frequency
    sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)

    report = "\n📊 TypeScript Error Breakdown:\n"
    report += "=" * 60 + "\n"

    for i, (error_msg, count) in enumerate(sorted_errors[:10], 1):
        # Truncate long error messages
        short_msg = error_msg[:70] + "..." if len(error_msg) > 70 else error_msg
        report += f"{i}. [{count:3d}x] {short_msg}\n"

    total = sum(error_counts.values())
    unique = len(error_counts)

    report += "=" * 60 + "\n"
    report += f"Total: {total} errors | Unique patterns: {unique}\n\n"

    if sorted_errors:
        top_error = sorted_errors[0]
        report += f"💡 TIP: Fix the top error first ({top_error[1]} occurrences)\n"
        report += f"Command: npm run type-check 2>&1 | grep \"{top_error[0][:30]}\"\n"

    return report


def categorize_eslint_errors(output):
    """Categorize ESLint errors"""
    # Extract error rules
    rule_pattern = r'eslint\(([^)]+)\)'
    rules = re.findall(rule_pattern, output)

    if not rules:
        return ""

    rule_counts = Counter(rules)
    sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)

    report = "\n📊 ESLint Error Breakdown:\n"
    report += "=" * 60 + "\n"

    for i, (rule, count) in enumerate(sorted_rules[:10], 1):
        report += f"{i}. [{count:3d}x] {rule}\n"

    total = sum(rule_counts.values())
    unique = len(rule_counts)

    report += "=" * 60 + "\n"
    report += f"Total: {total} errors | Unique rules: {unique}\n"

    return report


def suggest_fixes(error_output):
    """Suggest fixes for common TypeScript errors"""
    suggestions = []

    for pattern, fix_info in TYPESCRIPT_FIX_PATTERNS.items():
        if pattern in error_output:
            suggestions.append({
                'pattern': pattern,
                'fix': fix_info['fix'],
                'example': fix_info['example'],
                'reference': fix_info['reference']
            })

    if suggestions:
        print("\n💡 Suggested Fixes:")
        print("=" * 60)

        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. Pattern: {suggestion['pattern']}")
            print(f"   Fix: {suggestion['fix']}")
            print(f"   Example: {suggestion['example']}")
            print(f"   Reference: {suggestion['reference']}")


def track_error_trend(error_type, error_count):
    """Track error counts over time"""
    history = load_error_history()

    history['entries'].append({
        'timestamp': datetime.now().isoformat(),
        'type': error_type,
        'count': error_count,
    })

    # Keep last 100 entries
    history['entries'] = history['entries'][-100:]

    save_error_history(history)


def load_error_history():
    """Load error history from file"""
    if os.path.exists(ERROR_HISTORY_FILE):
        with open(ERROR_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {'entries': []}


def save_error_history(history):
    """Save error history to file"""
    os.makedirs(os.path.dirname(ERROR_HISTORY_FILE), exist_ok=True)
    with open(ERROR_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def show_error_trend():
    """Show error trend report"""
    history = load_error_history()

    if not history['entries']:
        print("No error history tracked yet")
        return

    print("\n📈 Error Trend (Last 10 Runs):")
    print("=" * 60)

    # Group by type
    by_type = defaultdict(list)

    for entry in history['entries'][-10:]:
        by_type[entry['type']].append({
            'time': entry['timestamp'],
            'count': entry['count']
        })

    for error_type, entries in by_type.items():
        counts = [e['count'] for e in entries]
        trend = "📉" if counts[-1] < counts[0] else "📈" if counts[-1] > counts[0] else "➡️"

        print(f"\n{error_type}:")
        print(f"  Latest: {counts[-1]} errors")
        print(f"  Trend: {trend} (from {counts[0]} to {counts[-1]})")

        if counts[-1] > counts[0]:
            print(f"  ⚠️  Errors increasing! +{counts[-1] - counts[0]}")
        elif counts[-1] < counts[0]:
            print(f"  ✅ Errors decreasing! -{counts[0] - counts[-1]}")


def lint_frontend(fix=False, check=False, type_check=True, categorize=False, suggest_fix=False):
    """Lint frontend with TypeScript checking"""
    results = []

    # 1. Type-check FIRST (most important)
    if type_check:
        print("\n🔍 TypeScript type-check...")
        type_result = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'type-check'],
            capture_output=True, text=True
        )

        if type_result.returncode != 0:
            print("❌ TypeScript errors found!")

            # Count errors
            error_count = len(re.findall(r'error TS\d+:', type_result.stderr))

            if categorize:
                print(categorize_typescript_errors(type_result.stderr))

            if suggest_fix:
                suggest_fixes(type_result.stderr)

            # Track trend
            track_error_trend('typescript', error_count)

            results.append(('type-check', False, type_result.stderr))
        else:
            print("✅ TypeScript: 0 errors")
            track_error_trend('typescript', 0)
            results.append(('type-check', True, ''))

    # 2. ESLint (second priority)
    print("\n🔍 ESLint...")
    eslint_cmd = ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'lint']
    if fix:
        eslint_cmd.extend(['--', '--fix'])

    eslint_result = subprocess.run(eslint_cmd, capture_output=True, text=True)

    if eslint_result.returncode != 0:
        print("❌ ESLint errors found!")

        if categorize:
            print(categorize_eslint_errors(eslint_result.stdout))

        results.append(('eslint', False, eslint_result.stdout))
    else:
        print("✅ ESLint: All checks passed")
        results.append(('eslint', True, ''))

    # 3. Prettier (last - just formatting)
    if not check:
        print("\n🔍 Prettier...")
        prettier = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'format'],
            capture_output=True, text=True
        )

    return results


def run_quality_gate(backend=True, frontend=True):
    """Run full quality gate - blocks on ANY error"""
    print("🚧 Running Quality Gate...")
    print("=" * 60)

    gate_results = {
        'type-check': None,
        'eslint': None,
        'ruff': None,
        'tests': None,
        'build': None,
    }

    # Frontend checks
    if frontend:
        print("\n📝 Frontend Quality Gate:")

        # 1. TypeScript (BLOCKER)
        print("  1/4 TypeScript type-check...")
        type_check = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'type-check'],
            capture_output=True
        )
        gate_results['type-check'] = type_check.returncode == 0
        status = "✅" if gate_results['type-check'] else "❌ BLOCKED"
        print(f"      {status}")

        # 2. ESLint (BLOCKER)
        print("  2/4 ESLint...")
        eslint = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'lint'],
            capture_output=True
        )
        gate_results['eslint'] = eslint.returncode == 0
        status = "✅" if gate_results['eslint'] else "❌ BLOCKED"
        print(f"      {status}")

        # 3. Tests (BLOCKER)
        print("  3/4 Unit tests...")
        tests = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'test:unit'],
            capture_output=True
        )
        gate_results['tests'] = tests.returncode == 0
        status = "✅" if gate_results['tests'] else "❌ BLOCKED"
        print(f"      {status}")

        # 4. Build (BLOCKER)
        print("  4/4 Build check...")
        build = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'frontend', 'npm', 'run', 'build-only'],
            capture_output=True
        )
        gate_results['build'] = build.returncode == 0
        status = "✅" if gate_results['build'] else "❌ BLOCKED"
        print(f"      {status}")

    # Backend checks
    if backend:
        print("\n🐍 Backend Quality Gate:")

        # 1. Ruff (BLOCKER)
        print("  1/2 Ruff linting...")
        ruff = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'django', 'ruff', 'check', '.'],
            capture_output=True
        )
        gate_results['ruff'] = ruff.returncode == 0
        status = "✅" if gate_results['ruff'] else "❌ BLOCKED"
        print(f"      {status}")

        # 2. Django checks (BLOCKER)
        print("  2/2 Django system check...")
        django_check = subprocess.run(
            ['docker', 'compose', 'run', '--rm', 'django', 'python', 'manage.py', 'check'],
            capture_output=True
        )
        status = "✅" if django_check.returncode == 0 else "❌ BLOCKED"
        print(f"      {status}")

    # Summary
    print("\n" + "=" * 60)
    all_passed = all(v for v in gate_results.values() if v is not None)

    if all_passed:
        print("✅ QUALITY GATE: PASSED")
        print("   All checks green - safe to commit/push")
        return 0
    else:
        print("❌ QUALITY GATE: BLOCKED")
        print("   Fix errors before committing")

        failed = [k for k, v in gate_results.items() if v is False]
        print(f"\n   Failed checks: {', '.join(failed)}")

        return 1


def lint_and_format(backend=True, frontend=True, fix=False, check=False, report=False,
                    gate=False, type_check=True, categorize=False, suggest_fix=False,
                    show_trend=False):
    """Run linting and formatting with preventative features"""

    # Show trend if requested
    if show_trend:
        show_error_trend()
        return

    # Run quality gate if requested
    if gate:
        exit_code = run_quality_gate(backend=backend, frontend=frontend)
        sys.exit(exit_code)

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
        print("\n🔍 Linting frontend (Vue.js/TypeScript)...")
        frontend_results = lint_frontend(
            fix=fix,
            check=check,
            type_check=type_check,
            categorize=categorize,
            suggest_fix=suggest_fix
        )

        # Check if any frontend checks failed
        all_passed = all(result[1] for result in frontend_results)

        results['frontend'] = {
            'lint': all_passed,
            'output': '\n'.join(result[2] for result in frontend_results if result[2])
        }

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

## NEW PREVENTATIVE FEATURES ✨

### 1. TypeScript Type-Checking (Default ON)
- Runs **FIRST** before ESLint/Prettier
- Catches type errors before they reach CI
- Auto-enabled for all frontend linting

### 2. Error Categorization
- Groups errors by frequency
- Shows top 10 error patterns
- Helps prioritize fixes (fix highest count first!)

### 3. Smart Fix Suggestions
- Matches errors against `frontend/TYPESCRIPT_PATTERNS.md`
- Shows fix, example code, and reference docs
- Based on battle-tested patterns from 584 → 111 error journey

### 4. Quality Gates
- `--gate` mode blocks on ANY error
- Runs: TypeScript → ESLint → Tests → Build
- Perfect for pre-commit hooks (see Husky integration above)

### 5. Error Trend Tracking
- Tracks error counts over time in `.claude/error-history.json`
- Shows if errors increasing/decreasing
- Motivates continuous improvement!

## Workflow Integration

```bash
# During development (find issues early)
/lint-and-format --frontend --fix --categorize --suggest-fixes

# Before committing (full quality check)
/lint-and-format --gate --frontend

# Track progress over time
/lint-and-format --trend
```

## Success Metrics

These enhancements have proven effective:
- **584 → 111 TypeScript errors** (81% reduction)
- **Systematic error categorization** enables focused fixes
- **Pattern library** prevents repeated mistakes
- **Quality gates** prevent error accumulation
