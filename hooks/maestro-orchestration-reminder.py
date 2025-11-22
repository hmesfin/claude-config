#!/usr/bin/env python3
"""
PreToolUse hook: Remind about MAESTRO orchestration when attempting direct implementation

Triggers when Claude tries to use Edit/Write tools for feature implementation
without explicit user instruction to do so.
"""
import json
import sys


def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # If we can't parse input, allow the tool to proceed
        print(json.dumps({"action": "allow"}))
        return

    tool_name = hook_input.get("tool", "")
    conversation = hook_input.get("conversation", [])

    # Only check Edit/Write tools
    if tool_name not in ["Edit", "Write"]:
        print(json.dumps({"action": "allow"}))
        return

    # Get the last user message
    user_messages = [msg for msg in conversation if msg.get("role") == "user"]
    if not user_messages:
        print(json.dumps({"action": "allow"}))
        return

    last_user_msg = user_messages[-1].get("content", "").lower()

    # Detect implementation requests
    implementation_keywords = [
        "implement", "add feature", "create component", "add component",
        "build", "add endpoint", "create api", "add model", "create model",
        "refactor", "add service", "create service", "new feature"
    ]

    has_implementation_request = any(
        keyword in last_user_msg for keyword in implementation_keywords
    )

    if has_implementation_request:
        # Check if user explicitly said "write" or "edit"
        explicit_instructions = [
            "write", "edit", "modify", "update file", "change file",
            "create file", "add to file"
        ]
        is_explicit = any(instr in last_user_msg for instr in explicit_instructions)

        if not is_explicit:
            # Warn about MAESTRO orchestration
            print(json.dumps({
                "action": "warn",
                "message": """⚠️ **MAESTRO Orchestration Reminder**

You're about to implement code directly, but the user requested a feature/component.

**MAESTRO Principle:** Orchestrate specialized agents, don't implement yourself.

**Should you be using the Task tool instead?**

Available specialized agents:
- Backend: `django-tdd-architect`, `fastapi-tdd-architect`
- Frontend: `vue-tdd-architect`
- Mobile: `react-native-tdd-architect`
- Data: `django-data-architect`, `fastapi-data-architect`, `mobile-data-architect`
- Security: `django-security-architect`, `fastapi-security-architect`

**Only implement directly if:**
- Tiny fix (<10 lines) explicitly requested
- User said "write [filename]" or "edit [filename]"
- Documentation update explicitly requested

**If proceeding anyway:**
- Ensure you follow TDD strictly (RED-GREEN-REFACTOR)
- Run type-checking before claiming DONE
- Show verification evidence

See: ~/.claude/skills/MAESTRO_ORCHESTRATION.md"""
            }))
            return

    # Allow the tool to proceed
    print(json.dumps({"action": "allow"}))


if __name__ == "__main__":
    main()
