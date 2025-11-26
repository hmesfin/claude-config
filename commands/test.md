---
name: test
description: Run tests with TDD workflow enforcement. Supports Django/Python (pytest), Vue.js (vitest), and React Native (jest) with coverage reporting.
---

# /test Command

Run tests with TDD enforcement, coverage reporting, and quality gates.

## Quick Start

```bash
# Run all tests
python scripts/test_runner.py

# Run backend tests only
python scripts/test_runner.py --backend

# Run frontend tests only
python scripts/test_runner.py --frontend

# Run with coverage
python scripts/test_runner.py --coverage

# Run specific test file
python scripts/test_runner.py --path tests/test_users.py

# Quality gate mode (fail if coverage < threshold)
python scripts/test_runner.py --gate

# Watch mode (re-run on changes)
python scripts/test_runner.py --watch
```

## What This Does

### Backend (Django/FastAPI - pytest)

```bash
# Standard run
docker compose run --rm django pytest

# With coverage
docker compose run --rm django pytest --cov=. --cov-report=term-missing

# Specific file
docker compose run --rm django pytest tests/test_users.py -v

# With markers
docker compose run --rm django pytest -m "not slow"
```

### Frontend (Vue.js - vitest)

```bash
# Standard run
docker compose run --rm frontend npm run test:unit

# With coverage
docker compose run --rm frontend npm run test:unit -- --coverage

# Watch mode
docker compose run --rm frontend npm run test:unit -- --watch
```

### Mobile (React Native - jest)

```bash
# Standard run
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## Coverage Thresholds

Based on TDD standards from `skills/DEVELOPMENT_STANDARDS.md`:

| Code Type | Minimum Coverage |
|-----------|-----------------|
| Standard code | 85% |
| Data/Models | 90% |
| Security code | 95% |
| UI Components | 80% |

## Quality Gate Mode

When run with `--gate`, the command enforces:

1. **All tests pass** - No failures allowed
2. **Coverage thresholds met** - Per code type
3. **No skipped tests** - All tests must run
4. **Lint passes** - No type errors (integrates with `/lint-and-format`)

```bash
# Quality gate for CI
python scripts/test_runner.py --gate

# Exit codes:
# 0 = All gates passed
# 1 = Tests failed
# 2 = Coverage below threshold
# 3 = Skipped tests found
```

## TDD Workflow Integration

### RED Phase
Run tests first to see them fail:
```bash
python scripts/test_runner.py --path tests/test_new_feature.py
# Expected: FAIL (no implementation yet)
```

### GREEN Phase
Run tests to verify implementation:
```bash
python scripts/test_runner.py --path tests/test_new_feature.py
# Expected: PASS
```

### REFACTOR Phase
Run full test suite to ensure no regressions:
```bash
python scripts/test_runner.py --coverage --gate
# Expected: All pass, coverage maintained
```

## Output Format

### Success
```
============================================================
                    TEST RESULTS
============================================================

Backend (pytest):
  ✅ 45 passed, 0 failed, 0 skipped
  📊 Coverage: 87% (threshold: 85%)

Frontend (vitest):
  ✅ 78 passed, 0 failed, 0 skipped
  📊 Coverage: 82% (threshold: 80%)

============================================================
✅ QUALITY GATE: PASSED
============================================================
```

### Failure
```
============================================================
                    TEST RESULTS
============================================================

Backend (pytest):
  ❌ 43 passed, 2 failed, 0 skipped
  📊 Coverage: 72% (threshold: 85%) ⚠️ BELOW THRESHOLD

  Failed Tests:
  - tests/test_users.py::test_user_creation
  - tests/test_auth.py::test_token_refresh

============================================================
❌ QUALITY GATE: FAILED
   - 2 tests failed
   - Coverage 72% < 85% threshold
============================================================
```

## Integration with TDD Agents

This command works with specialized TDD agents:

| Agent | Test Framework |
|-------|---------------|
| `django-tdd-architect` | pytest + Django test client |
| `fastapi-tdd-architect` | pytest + httpx |
| `vue-tdd-architect` | vitest + Vue Test Utils |
| `react-native-tdd-architect` | jest + RNTL |
| `tdd-test-specialist` | All frameworks |
| `e2e-tdd-architect` | Playwright |

## Pre-commit Integration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: run-tests
        name: Run Tests
        entry: python scripts/test_runner.py --gate
        language: system
        pass_filenames: false
        stages: [commit]
```

## CI/CD Integration

GitHub Actions example:

```yaml
- name: Run Tests with Quality Gate
  run: python scripts/test_runner.py --gate --coverage

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Related Commands

- `/lint-and-format` - Run before tests to catch type errors
- `/velocity` - Track test completion metrics
- `/risk-check` - Monitor untested issues

## Notes

- All tests run through Docker for consistency
- Coverage reports saved to `.coverage` and `coverage/`
- Watch mode available for development
- Integrates with VS Code test explorer
