#!/usr/bin/env python3
"""
PreToolUse hook: Prevent autonomous code writing without explicit user instruction

Blocks Edit/Write tools when user asked a question but Claude tries to write code.
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

    # Check for explicit file editing instructions
    explicit_instructions = [
        "write", "edit", "modify", "update file", "change file",
        "create file", "add to file", "fix in", "update in",
        "change in", "modify in"
    ]

    # Also allow if user mentioned a specific file path
    has_file_path = "/" in last_user_msg or ".py" in last_user_msg or ".ts" in last_user_msg or ".vue" in last_user_msg

    has_explicit_instruction = (
        any(instr in last_user_msg for instr in explicit_instructions) or
        has_file_path
    )

    if not has_explicit_instruction:
        # Check if this is a question or exploration task
        question_indicators = [
            "what", "how", "why", "when", "where", "which",
            "explain", "show me", "tell me", "describe",
            "can you", "could you", "would you",
            "is there", "are there", "does", "do you",
            "?", "help me understand"
        ]
        is_question = any(q in last_user_msg for q in question_indicators)

        if is_question:
            # Block autonomous code writing for questions
            print(json.dumps({
                "action": "block",
                "message": """🚫 **Autonomous Code Writing Blocked**

The user asked a QUESTION, but you're trying to write code!

**User asked:** Exploration/understanding question
**You're doing:** Writing/editing code

**What you should do instead:**
1. Answer the question
2. Explain the concept
3. Show examples if helpful
4. Wait for explicit instruction to write code

**To write code, user must explicitly say:**
- "write [filename]"
- "edit [filename]"
- "create file [path]"
- "modify [specific file]"

**Remember:** Be proactive with UNDERSTANDING, not with CODE.

See: ~/.claude/skills/MAESTRO_ORCHESTRATION.md"""
            }))
            return

    # Allow the tool to proceed if explicit instruction given
    print(json.dumps({"action": "allow"}))


if __name__ == "__main__":
    main()
