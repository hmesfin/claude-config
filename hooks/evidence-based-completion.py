#!/usr/bin/env python3
"""
PostToolUse hook: Check for evidence when claiming work is "DONE" or "FIXED"

Triggers when Claude claims completion without showing verification evidence.
"""
import json
import sys
import re


def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # If we can't parse input, allow
        print(json.dumps({"action": "allow"}))
        return

    # Get the last assistant message
    conversation = hook_input.get("conversation", [])
    assistant_messages = [msg for msg in conversation if msg.get("role") == "assistant"]

    if not assistant_messages:
        print(json.dumps({"action": "allow"}))
        return

    last_message = assistant_messages[-1].get("content", "")
    last_message_lower = last_message.lower()

    # Check for completion claims
    completion_patterns = [
        r'\bdone\b', r'\bfixed\b', r'\bcompleted\b', r'\bworking\b',
        r'\bpasses\b', r'\bsuccessful\b', r'\bready\b',
        r"i've implemented", r"i've added", r"i've created",
        r"implementation complete", r"feature complete"
    ]

    has_completion_claim = any(
        re.search(pattern, last_message_lower) for pattern in completion_patterns
    )

    if has_completion_claim:
        # Check for evidence markers
        evidence_patterns = [
            r'✅.*test.*\d+.*passing',  # Test results with checkmark
            r'✅.*type-check.*0 errors',  # Type-check with checkmark
            r'```[\s\S]*?(PASSED|passed|OK)[\s\S]*?```',  # Test output in code blocks
            r'```[\s\S]*?0 errors[\s\S]*?```',  # Type-check output in code blocks
            r'docker compose run.*pytest',  # Test command execution
            r'docker compose run.*mypy',  # Type-check command execution
            r'npm run test',  # Frontend test command
            r'npm run type-check',  # Frontend type-check command
            r'\d+/\d+ passing',  # Test count format
            r'manual test:',  # Manual testing description
        ]

        has_evidence = any(
            re.search(pattern, last_message, re.IGNORECASE | re.DOTALL)
            for pattern in evidence_patterns
        )

        if not has_evidence:
            # Check if this is a question/exploration (not implementation)
            question_indicators = [
                'should i', 'would you like', 'do you want',
                'let me know', 'which approach', '?'
            ]
            is_question = any(indicator in last_message_lower for indicator in question_indicators)

            # Only warn if claiming completion on implementation work
            if not is_question:
                print(json.dumps({
                    "action": "warn",
                    "message": """⚠️ **Evidence Required for Completion**

You claimed work is "DONE" or "FIXED" but didn't show verification evidence.

**Required before claiming DONE:**

```bash
✅ Tests: X/Y passing (show actual output)
✅ Type-check: 0 errors (show actual output)
✅ Manual test: [describe what you tested]

DONE ← Only after showing evidence
```

**FORBIDDEN without evidence:**
❌ "This should work"
❌ "I've fixed X"
❌ "Tests will pass"
❌ "Everything is working"

**Run verification commands and show output:**

Django/Backend:
- docker compose run --rm django pytest
- docker compose run --rm django mypy apps

Vue.js/Frontend:
- docker compose run --rm frontend npm run test:run
- docker compose run --rm frontend npm run type-check

React Native/Mobile:
- docker compose run --rm mobile npm run test:run
- docker compose run --rm mobile npm run type-check

See: ~/.claude/skills/RESPONSE_QUALITY_STANDARDS.md"""
                }))
                return

    # Allow if no completion claim or evidence is present
    print(json.dumps({"action": "allow"}))


if __name__ == "__main__":
    main()
