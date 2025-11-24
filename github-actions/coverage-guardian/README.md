# Test Coverage Guardian

**Purpose**: Enforce test coverage requirements on every pull request

**Location**: Copy these files to your project's `.github/` directory

## Files

1. **coverage-guardian.yml** → Copy to `.github/workflows/coverage-guardian.yml`
2. **check_coverage.py** → Copy to `.github/scripts/check_coverage.py`

## Setup in a Project

```bash
# From your project root
mkdir -p .github/workflows .github/scripts

# Copy workflow
cp ~/claude-config/github-actions/coverage-guardian/coverage-guardian.yml \
   .github/workflows/

# Copy script
cp ~/claude-config/github-actions/coverage-guardian/check_coverage.py \
   .github/scripts/

# Make script executable
chmod +x .github/scripts/check_coverage.py

# Commit and push
git add .github/
git commit -m "feat: Add Test Coverage Guardian workflow"
git push
```

## How It Works

**Triggers**: Runs on every pull request (opened, synchronize, reopened)

**Actions**:
1. Runs pytest with coverage
2. Analyzes coverage results
3. Posts detailed report as PR comment
4. Blocks merge if coverage is below threshold

**Thresholds**:
- **Minimum Coverage**: 85%
- **Security Files**: 95%

**Security File Patterns**: Files containing `auth`, `security`, `permission`, `token`, `password`, `encryption`, `crypto`

## Customization

Edit `check_coverage.py` to adjust:

```python
# Coverage thresholds
MINIMUM_COVERAGE = 85.0  # Change to your preference
SECURITY_COVERAGE = 95.0

# Security-related file patterns
SECURITY_PATTERNS = [
    'auth',
    'security',
    # Add more patterns
]
```

## Example PR Comment

**When Passing**:
```markdown
✅ **Test Coverage Report - PASSED**

📊 **Overall Coverage**: 93.2% (target: 85%)

Summary:
- Total Files: 12
- Files Below Threshold: 0
- Security Files Below Threshold: 0
```

**When Failing**:
```markdown
❌ **Test Coverage Report - FAILED**

📊 **Overall Coverage**: 82.5% (target: 85%)

Summary:
- Total Files: 12
- Files Below Threshold: 3
- Security Files Below Threshold: 1

## ⚠️ Files Below Coverage Threshold
| File | Coverage | Missing Lines | Target |
|------|----------|--------------|--------|
| src/models.py | 78.3% | 15 | 85% |
```

## Local Testing

Test before pushing:

```bash
# Run coverage
pytest --cov=src --cov-report=json --cov-report=term

# Check coverage manually
python .github/scripts/check_coverage.py
```

## Requirements

Your project needs:
- Python 3.7+
- pytest
- pytest-cov

Install:
```bash
pip install pytest pytest-cov
```

---

**Part of P0 GitHub Automation** | See `docs/P0_IMPLEMENTATION.md` for complete guide
