#!/usr/bin/env python3
"""
TypeScript Quality Guard Hook
Prevents common TypeScript errors BEFORE code is written.

This hook runs before Write/Edit tools and warns agents about:
- Writing Vue components without running type-check first
- Common TypeScript patterns that historically caused errors
- Test mock patterns that need type safety

Based on battle-tested learnings from 584 → 111 TypeScript error reduction.
"""

import json
import sys
import re
import subprocess
from pathlib import Path


# Pattern warnings from TYPESCRIPT_PATTERNS.md
PATTERN_WARNINGS = {
    "test mock": {
        "trigger": r"\.spec\.ts|\.test\.ts",
        "warning": """
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
""",
    },
    "vue component": {
        "trigger": r"\.vue$",
        "warning": """
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Vue Component

Before writing component code:

1. Run type-check to ensure codebase is clean:
   docker compose run --rm frontend npm run type-check

2. If creating types, ensure unions/enums are COMPLETE:
   ✅ Add ALL possible values upfront to avoid future errors

3. API calls should use generic types:
   ✅ api.get<User>('/users/me/') not api.get('/users/me/')

Reference: /lint-and-format --frontend --categorize --suggest-fixes
""",
    },
    "typescript types": {
        "trigger": r"\.types\.ts|types/.*\.ts",
        "warning": """
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Type Definitions

Type safety checklist:

1. Union types - Include ALL possible values now, not later
2. Interfaces - Mark optional fields with '?'
3. Enums - Add new values as features are created
4. null vs undefined - Be consistent (prefer null)

Common issue: Adding type values after code uses them
✅ Update type FIRST, then use new values in code

Reference: frontend/TYPESCRIPT_PATTERNS.md - Pattern 7
""",
    },
    "composable": {
        "trigger": r"composables/.*\.ts",
        "warning": """
⚠️  TYPESCRIPT QUALITY REMINDER: Writing Composable

Composable type safety:

1. Computed properties - Return ComputedRef<T>, not Ref<T>
2. Refs - Use Ref<T> for mutable state
3. Return types - Explicitly type the return object
4. Generic types - Use <T> for reusable composables

Common issue: Mixing ref() and computed() incorrectly
✅ If logic computes a value, use computed(), not ref()

Reference: frontend/TYPESCRIPT_PATTERNS.md - Pattern 6
""",
    },
}


def check_typescript_error_count():
    """Check current TypeScript error count"""
    try:
        # Check if we're in a project with frontend
        frontend_path = Path.cwd() / "frontend"
        if not frontend_path.exists():
            return None

        # Run type-check to see current error count
        result = subprocess.run(
            ["docker", "compose", "run", "--rm", "frontend", "npm", "run", "type-check"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Count errors
        error_count = len(re.findall(r"error TS\d+:", result.stderr))

        return error_count
    except Exception:
        # If check fails, don't block - just skip
        return None


def get_pattern_warning(file_path):
    """Get warning for file pattern if applicable"""
    for pattern_name, pattern_info in PATTERN_WARNINGS.items():
        if re.search(pattern_info["trigger"], file_path, re.IGNORECASE):
            return pattern_info["warning"]

    return None


def main():
    """Main hook entry point"""
    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Extract tool input
        tool_input = hook_input.get("tool_input", {})
        tool_name = hook_input.get("tool_name", "")

        # Only process Write and Edit tools
        if tool_name not in ["Write", "Edit"]:
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        if not file_path:
            sys.exit(0)

        # Check if file is in frontend/src
        if not ("frontend/src" in file_path or "frontend\\src" in file_path):
            sys.exit(0)

        # Get pattern warning if applicable
        warning = get_pattern_warning(file_path)

        if warning:
            # Check current TypeScript error count
            error_count = check_typescript_error_count()

            output = warning

            if error_count is not None and error_count > 0:
                output += f"\n⚠️  CURRENT TYPESCRIPT ERRORS: {error_count}\n"
                output += "   Consider fixing existing errors before adding new code.\n"
                output += "   Run: /lint-and-format --frontend --categorize\n"

            # Output warning to agent (not blocking, just informational)
            print(output, file=sys.stderr)

        # Allow the operation (this is a warning hook, not a blocker)
        sys.exit(0)

    except Exception as e:
        # On error, log but don't block
        print(f"TypeScript Quality Guard hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
