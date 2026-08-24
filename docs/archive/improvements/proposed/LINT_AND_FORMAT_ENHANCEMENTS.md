# Lint-and-Format Command - Prevention Enhancements

**Proposed by:** Ham Dog & TC
**Date:** 2025-10-16
**Battle-Tested From:** 584 → 111 TypeScript error journey

---

## 🎯 Problem Statement

Current `/lint-and-format` command is **reactive** - it catches issues AFTER they're written.

**What it does NOW:**
- ✅ Lints Python (Ruff)
- ✅ Lints JavaScript/Vue (ESLint)
- ✅ Formats code (Prettier)
- ❌ Doesn't check TypeScript types
- ❌ Doesn't prevent commits with errors
- ❌ Doesn't categorize errors by severity
- ❌ Doesn't track error trends

**Result:** TypeScript errors accumulate, CI fails, manual cleanup needed.

---

## 💡 Proposed Enhancements

### Enhancement 1: Add TypeScript Type-Checking

**NEW Option:** `--type-check` (enabled by default for frontend)

```bash
# Run type-check as part of lint
/lint-and-format --frontend --fix

# Now includes:
# 1. ESLint
# 2. Prettier
# 3. TypeScript type-check ← NEW
```

**Implementation:**

```python
def lint_frontend(fix=False, check=False, type_check=True):
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
            print(categorize_typescript_errors(type_result.stderr))
            results.append(('type-check', False, type_result.stderr))
        else:
            print("✅ TypeScript: 0 errors")
            results.append(('type-check', True, ''))

    # 2. ESLint (second priority)
    print("\n🔍 ESLint...")
    # ... existing ESLint code ...

    # 3. Prettier (last - just formatting)
    print("\n🔍 Prettier...")
    # ... existing Prettier code ...

    return results
```

### Enhancement 2: Error Categorization

**NEW Function:** Categorize errors by severity and count

```python
def categorize_typescript_errors(output):
    """Categorize TypeScript errors for quick triage"""
    import re
    from collections import Counter

    # Extract error patterns
    error_pattern = r'error TS\d+: (.+?)$'
    errors = re.findall(error_pattern, output, re.MULTILINE)

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
    import re
    from collections import Counter

    # Extract error rules
    rule_pattern = r'eslint\(([^)]+)\)'
    rules = re.findall(rule_pattern, output)

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
```

### Enhancement 3: Quality Gates

**NEW Option:** `--gate` (blocks on any errors)

```python
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
```

### Enhancement 4: Error Trend Tracking

**NEW Feature:** Track error count over time

```python
import json
import os
from datetime import datetime

ERROR_HISTORY_FILE = '.claude/error-history.json'

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
    from collections import defaultdict
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
```

### Enhancement 5: Smart Fix Suggestions

**NEW Feature:** Suggest fixes based on error patterns

```python
TYPESCRIPT_FIX_PATTERNS = {
    "Property 'value' does not exist on type 'VueNode<Element>'": {
        "fix": "Cast element to proper HTML type",
        "example": "(wrapper.find('[data-test=\"input\"]').element as HTMLInputElement).value",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 2"
    },
    "is missing in type": {
        "fix": "Add missing required property to type/mock",
        "example": "Add property to interface or test mock",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 1"
    },
    "Type 'Ref<": {
        "fix": "Use computed() instead of ref() for computed properties",
        "example": "const value = computed(() => data.value)",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 4"
    },
    "is not assignable to type": {
        "fix": "Check type definition matches usage",
        "example": "Verify enum includes all values being used",
        "reference": "frontend/TYPESCRIPT_PATTERNS.md - Pattern 6"
    },
}

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
```

---

## 🔄 Enhanced Command Options

### NEW Options

```bash
# Run full quality gate (blocks on any error)
/lint-and-format --gate

# Show error trends
/lint-and-format --trend

# Run with TypeScript check
/lint-and-format --frontend --type-check

# Skip TypeScript check (not recommended)
/lint-and-format --frontend --no-type-check

# Categorize errors (don't fix)
/lint-and-format --frontend --categorize

# Get fix suggestions
/lint-and-format --frontend --suggest-fixes
```

### Updated Command Flow

```
OLD:
/lint-and-format --fix
  → ESLint
  → Prettier
  → Done

NEW:
/lint-and-format --fix
  → TypeScript type-check (FIRST - most critical)
     ├─ Errors found → Categorize → Suggest fixes
     └─ Pass → Continue
  → ESLint (SECOND)
     ├─ Errors found → Categorize → Auto-fix
     └─ Pass → Continue
  → Prettier (LAST - just formatting)
  → Track error trends
  → Summary report
```

---

## 📋 Updated Description

**CHANGE lines 3-4 to:**

```markdown
description: Preventative code quality tool for Django/Vue.js projects. Runs TypeScript type-checking, ESLint, Prettier, and Ruff. Categorizes errors, suggests fixes, tracks trends, and enforces quality gates. Prevents commits with TypeScript/lint errors.
```

---

## 🎯 Integration with Pre-Commit Hook

**Enhanced `.husky/pre-commit`:**

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "🚧 Running pre-commit quality gate..."

# Run quality gate
/lint-and-format --gate --frontend

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Quality gate FAILED - commit blocked"
  echo ""
  echo "💡 Quick fixes:"
  echo "   1. Run: npm run type-check"
  echo "   2. Fix highest-count errors first"
  echo "   3. Reference: frontend/TYPESCRIPT_PATTERNS.md"
  echo ""
  exit 1
fi

echo "✅ Quality gate passed - proceeding with commit"
```

---

## 📊 New Output Format

### Before Enhancement:
```
🔍 Linting frontend (Vue.js/JavaScript)...
❌ Frontend: Issues found
  /path/to/file.ts(45,12): error TS2339: Property 'foo' does not exist
  /path/to/file.ts(67,8): error TS2339: Property 'bar' does not exist
  ... (200+ more lines)
```

### After Enhancement:
```
🚧 Running Quality Gate...
============================================================

📝 Frontend Quality Gate:
  1/4 TypeScript type-check...
      ❌ BLOCKED

📊 TypeScript Error Breakdown:
============================================================
1. [ 45x] Property 'value' does not exist on type 'VueNode<Element>'
2. [ 23x] is missing in type ... but required in type
3. [ 18x] Type 'Ref<boolean>' is missing properties from ComputedRef
4. [ 12x] Cannot find module '../types'
5. [  8x] Type 'string | undefined' not assignable to 'string'
============================================================
Total: 106 errors | Unique patterns: 15

💡 TIP: Fix the top error first (45 occurrences)
Command: npm run type-check 2>&1 | grep "Property 'value'"

💡 Suggested Fixes:
============================================================
1. Pattern: Property 'value' does not exist on type 'VueNode<Element>'
   Fix: Cast element to proper HTML type
   Example: (wrapper.find('[data-test="input"]').element as HTMLInputElement).value
   Reference: frontend/TYPESCRIPT_PATTERNS.md - Pattern 2

============================================================
❌ QUALITY GATE: BLOCKED
   Fix errors before committing
   Failed checks: type-check
```

---

## ✅ Success Criteria

**Prevention effectiveness:**
- [ ] Blocks commits with TypeScript errors
- [ ] Categorizes errors for quick triage
- [ ] Suggests fixes from pattern library
- [ ] Tracks error trends over time
- [ ] Reduces manual error hunting time by 80%

**Developer experience:**
- [ ] Runs in <30 seconds for type-check
- [ ] Clear, actionable error messages
- [ ] Links to fix documentation
- [ ] Shows progress toward zero errors

---

## 🔄 Implementation Plan

### Phase 1: Core Enhancement
- [ ] Add TypeScript type-checking
- [ ] Add error categorization
- [ ] Add quality gate mode

### Phase 2: Intelligence
- [ ] Add fix suggestions
- [ ] Add error trend tracking
- [ ] Integrate with TYPESCRIPT_PATTERNS.md

### Phase 3: Automation
- [ ] Update pre-commit hook
- [ ] Add CI/CD integration
- [ ] Create error trend dashboard

---

## 💭 Ham Dog's Decision

**Option A:** Implement all enhancements (full prevention system)
**Option B:** Phase 1 only first (core features, add intelligence later)
**Option C:** Specific modifications (tell me what to change)
**Option D:** Keep current command (manual vigilance)

**What's your call?** 🎯
