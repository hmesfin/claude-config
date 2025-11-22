# Response Quality Standards - Evidence-Based Development

**Philosophy:** Claims without evidence are wishes. Evidence without claims is data. Claims WITH evidence are facts.

**These standards prevent multi-day setbacks caused by "it should work" syndrome.**

---

## The Golden Rule

**NEVER claim something works without verification evidence.**

No "should work", "will pass", "is fixed", or "DONE" without proof.

---

## Before Claiming "DONE" or "FIXED"

### Required Evidence Format

```bash
✅ Tests: X/Y passing (show actual test run output)
✅ Type-check: 0 errors (show actual type-check output)
✅ Manual test: [describe what you tested - browser/API/app]

DONE ← Only use this word after showing evidence above
```

### Example of Proper Completion

```
I've implemented the user authentication feature.

✅ Tests: 15/15 passing
$ docker compose run --rm django pytest apps/auth/
======================== test session starts ========================
apps/auth/tests/test_login.py::test_login_success PASSED
apps/auth/tests/test_login.py::test_login_invalid_credentials PASSED
apps/auth/tests/test_logout.py::test_logout_clears_session PASSED
...
======================== 15 passed in 2.34s ========================

✅ Type-check: 0 errors
$ docker compose run --rm django mypy apps/auth
Success: no issues found in 8 source files

✅ Manual test: Tested login flow in browser
- Valid credentials → Successfully logged in, redirected to dashboard
- Invalid credentials → Error message displayed
- Logout → Session cleared, redirected to login

DONE
```

---

## FORBIDDEN Phrases Without Verification

### ❌ "This should work"
**Problem:** Speculation, not verification
**Solution:** Run it and show it works

### ❌ "I've fixed X"
**Problem:** Claim without proof
**Solution:** Prove X is fixed with test output

### ❌ "Tests will pass"
**Problem:** Future prediction, not current fact
**Solution:** Run tests now, paste results

### ❌ "Type-check passes"
**Problem:** Assertion without evidence
**Solution:** Run type-check, show 0 errors

### ❌ "Everything is working"
**Problem:** Vague claim
**Solution:** Define "everything", verify each part

### ❌ "No errors"
**Problem:** Invisible evidence
**Solution:** Show the command output with no errors

---

## Before Making Changes

**NEVER make assumptions. ALWAYS verify current state.**

### Required Pre-Change Checks

#### 1. Read Actual Files
**Don't guess file contents.**

```bash
# ❌ WRONG
"The API client probably uses fetch..."

# ✅ CORRECT
$ cat frontend/src/lib/api-client.ts
# Now I KNOW it uses axios
```

#### 2. Check Dependencies
**Don't assume package versions or existence.**

```bash
# Check what's actually installed
$ grep "@hey-api/client" frontend/package.json
$ grep "zod" frontend/package.json

# Check available scripts
$ grep "scripts" frontend/package.json -A 10
```

#### 3. Search CLAUDE.md for Patterns
**Don't reinvent existing patterns.**

```bash
# Check for established patterns
$ grep -i "api client" CLAUDE.md
$ grep -i "error handling" CLAUDE.md
```

#### 4. Run Commands to Verify Behavior
**Don't assume how things currently work.**

```bash
# Test current behavior
$ docker compose run --rm django python manage.py shell
>>> from apps.users.models import User
>>> User.objects.first()
# Now I KNOW the model structure
```

#### 5. Check Git History
**Understand recent changes and context.**

```bash
$ git log --oneline -10
$ git diff HEAD~5
```

---

## Example: Before Changing API Client

### ❌ WRONG Approach (Assumptions)
```
"The API client probably uses the OpenAPI generator. I'll assume it's
configured to use fetch and update it to use axios..."
```

### ✅ CORRECT Approach (Verification)
```bash
# STEP 1: Check current configuration
$ grep "generate:api" frontend/package.json
"generate:api": "@hey-api/openapi-ts -i http://localhost:8000/api/schema/ -o src/api -c axios"

# STEP 2: Check what's installed
$ grep "@hey-api" frontend/package.json
"@hey-api/openapi-ts": "^0.27.0",
"@hey-api/client-axios": "^0.1.0"

# STEP 3: Read current implementation
$ cat frontend/src/lib/api-client.ts
# Now I see it already uses axios with interceptors

# STEP 4: Make informed changes
"Based on package.json and api-client.ts, I can see the project already
uses @hey-api/client-axios. The interceptors are configured for auth.
I'll extend the existing pattern..."
```

---

## What to NEVER Assume

| Category | ❌ Never Assume | ✅ Always Verify |
|----------|----------------|------------------|
| File Contents | "probably uses X..." | Read the actual file |
| Configuration | "should be configured as..." | Check config files |
| Implementation | "likely works like..." | Read the code |
| Versions | "typically version X..." | Check package.json/pyproject.toml |
| APIs | "probably returns Y..." | Check OpenAPI schema or test |
| Database | "should have column Z..." | Check models or run migration |

---

## TDD Verification Protocol

**Every testable change MUST follow this workflow.**

### Phase 1: RED (Write Failing Tests First)

```
□ Write test(s) FIRST
□ Run tests → Verify they FAIL
□ Show failing test output

Example:
$ docker compose run --rm django pytest apps/users/tests/test_profile.py
==================== test session starts ====================
apps/users/tests/test_profile.py::test_update_bio FAILED
FAILED - AssertionError: Profile.bio does not exist

✅ RED PHASE COMPLETE - Test fails as expected
```

### Phase 2: GREEN (Implement Minimal Code)

```
□ Implement code
□ Run tests → Verify they PASS
□ Show passing test output

Example:
$ docker compose run --rm django pytest apps/users/tests/test_profile.py
==================== test session starts ====================
apps/users/tests/test_profile.py::test_update_bio PASSED

✅ GREEN PHASE COMPLETE - Test passes
```

### Phase 3: CHECK (Verify Quality)

```
□ Run ALL tests → No regressions
□ Run type-check → 0 errors
□ Review git diff → Changes are minimal
□ Show all verification output

Example:
$ docker compose run --rm django pytest
==================== 127 passed in 5.23s ====================

$ docker compose run --rm django mypy apps
Success: no issues found in 45 source files

$ git diff --stat
apps/users/models.py | 3 +++
apps/users/tests/test_profile.py | 12 ++++++++++++
2 files changed, 15 insertions(+)

✅ CHECK PHASE COMPLETE - All quality gates pass
```

### Phase 4: DONE (Only After Phases 1-3)

```
□ All evidence shown
□ No regressions
□ Quality gates pass

DONE ← Now you can say this
```

---

## Use TodoWrite to Track Verification

### Example Todo List for TDD Workflow

```markdown
[in_progress] Write tests for user bio update (RED phase)
[in_progress] Run tests to verify they fail
[pending] Implement bio field in Profile model (GREEN phase)
[pending] Run tests to verify they pass
[pending] Run all tests and type-check (CHECK phase)
[pending] Review git diff for minimal changes
[pending] Show all verification evidence
[pending] Mark DONE after all evidence shown
```

**Update todos in real-time as you progress through phases.**

---

## Quality Gates Checklist

Before claiming "DONE", verify:

### Tests
- [ ] All new tests passing
- [ ] All existing tests still passing (no regressions)
- [ ] Test output shown (not just "tests pass")
- [ ] Coverage meets requirements (85% minimum)

### Type Safety
- [ ] mypy passes (Python)
- [ ] TypeScript type-check passes (Frontend/Mobile)
- [ ] 0 type errors shown in output
- [ ] No `any` types introduced

### Code Quality
- [ ] Linting passes
- [ ] Formatting consistent
- [ ] No inline imports (all at top)
- [ ] Files under 500 lines

### Manual Testing
- [ ] Tested in browser/app/API
- [ ] Described what was tested
- [ ] Verified edge cases
- [ ] Checked error handling

### Documentation
- [ ] Code comments where needed
- [ ] Type hints on all functions
- [ ] Docstrings for complex logic
- [ ] Updated README if needed

---

## Common Verification Failures

### ❌ Failure Pattern 1: "Tests Passing" Without Output
```
"I've implemented the feature. Tests are passing."
```
**Problem:** No evidence shown
**Fix:** Run tests, paste the actual output

### ❌ Failure Pattern 2: "No Type Errors" Without Running Type-Check
```
"The types are correct, no errors."
```
**Problem:** Didn't actually run type-check
**Fix:** Run mypy/tsc, show 0 errors output

### ❌ Failure Pattern 3: Claiming DONE During Implementation
```
"I've written the code. DONE."
```
**Problem:** Skipped verification phases
**Fix:** Run tests, type-check, show evidence, THEN say DONE

### ❌ Failure Pattern 4: Vague Manual Testing
```
"I tested it and it works."
```
**Problem:** No specifics on what was tested
**Fix:** Describe exact steps tested and results

---

## Verification Commands by Stack

### Django Backend
```bash
# Run tests
docker compose run --rm django pytest
docker compose run --rm django pytest apps/users/  # Specific app

# Type check
docker compose run --rm django mypy apps

# Linting
docker compose run --rm django ruff check apps
```

### Vue.js Frontend
```bash
# Run tests
docker compose run --rm frontend npm run test:run

# Type check
docker compose run --rm frontend npm run type-check

# Linting
docker compose run --rm frontend npm run lint
```

### React Native Mobile
```bash
# Run tests
docker compose run --rm mobile npm run test:run

# Type check
docker compose run --rm mobile npm run type-check

# Linting
docker compose run --rm mobile npm run lint
```

---

## Success Metrics

### Good Evidence-Based Development:
✅ Every "DONE" claim has test output, type-check output, and manual test description
✅ Changes verified before claiming complete
✅ Files read before making assumptions
✅ All quality gates shown passing

### Poor Evidence-Based Development:
❌ "Should work" without running it
❌ "Tests pass" without showing output
❌ "No errors" without showing type-check
❌ Assumptions instead of verification

---

## Remember

**The difference between amateur and professional:**

- Amateur: "I think this works"
- Professional: "Here's proof this works"

**Show your work. Evidence over assertions.**
