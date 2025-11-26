#!/usr/bin/env python3
"""
TDD Test Runner

Unified test runner for Django/FastAPI (pytest), Vue.js (vitest), and React Native (jest).
Supports coverage reporting, quality gates, and TDD workflow enforcement.

Usage:
    python test_runner.py              # Run all tests
    python test_runner.py --backend    # Run backend tests only
    python test_runner.py --frontend   # Run frontend tests only
    python test_runner.py --coverage   # Run with coverage
    python test_runner.py --gate       # Quality gate mode
    python test_runner.py --watch      # Watch mode
    python test_runner.py --path tests/test_users.py  # Specific file
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Coverage thresholds based on TDD standards
COVERAGE_THRESHOLDS = {
    "standard": 85,
    "data": 90,
    "security": 95,
    "ui": 80,
}

# Exit codes
EXIT_SUCCESS = 0
EXIT_TESTS_FAILED = 1
EXIT_COVERAGE_FAILED = 2
EXIT_SKIPPED_TESTS = 3


@dataclass
class TestResult:
    """Result from a test run."""
    framework: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float | None = None
    duration: float | None = None
    output: str = ""
    error: str = ""
    success: bool = True


def detect_project_type() -> dict:
    """Detect what type of project this is based on config files."""
    project = {
        "has_backend": False,
        "has_frontend": False,
        "has_mobile": False,
        "backend_type": None,  # "django" or "fastapi"
        "frontend_type": None,  # "vue" or "react"
        "uses_docker": False,
    }

    cwd = Path.cwd()

    # Check for Docker
    if (cwd / "docker-compose.yml").exists() or (cwd / "docker-compose.yaml").exists():
        project["uses_docker"] = True

    # Check for Django
    if (cwd / "manage.py").exists():
        project["has_backend"] = True
        project["backend_type"] = "django"

    # Check for FastAPI
    if (cwd / "app" / "main.py").exists() or any(
        "fastapi" in str(f) for f in cwd.glob("**/requirements*.txt")
    ):
        project["has_backend"] = True
        project["backend_type"] = "fastapi"

    # Check for pyproject.toml
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "django" in content.lower():
            project["has_backend"] = True
            project["backend_type"] = "django"
        elif "fastapi" in content.lower():
            project["has_backend"] = True
            project["backend_type"] = "fastapi"

    # Check for Vue.js
    package_json = cwd / "package.json"
    frontend_package = cwd / "frontend" / "package.json"

    for pkg_file in [package_json, frontend_package]:
        if pkg_file.exists():
            try:
                pkg = json.loads(pkg_file.read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "vue" in deps:
                    project["has_frontend"] = True
                    project["frontend_type"] = "vue"
                elif "react-native" in deps:
                    project["has_mobile"] = True
                    project["frontend_type"] = "react-native"
                elif "react" in deps:
                    project["has_frontend"] = True
                    project["frontend_type"] = "react"
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    return project


def run_backend_tests(
    project: dict,
    coverage: bool = False,
    path: str | None = None,
    verbose: bool = False,
) -> TestResult:
    """Run backend tests with pytest."""
    result = TestResult(framework="pytest")

    # Build command
    if project["uses_docker"]:
        cmd = ["docker", "compose", "run", "--rm", "django", "pytest"]
    else:
        cmd = ["pytest"]

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=json"])

    if path:
        cmd.append(path)

    if verbose:
        cmd.append("-v")

    # Run tests
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )
        result.output = proc.stdout
        result.error = proc.stderr
        result.success = proc.returncode == 0

        # Parse pytest output
        result = parse_pytest_output(result)

        # Parse coverage if enabled
        if coverage:
            result = parse_coverage_json(result)

    except subprocess.TimeoutExpired:
        result.error = "Test run timed out after 10 minutes"
        result.success = False
    except FileNotFoundError:
        result.error = "pytest not found. Install with: pip install pytest"
        result.success = False

    return result


def run_frontend_tests(
    project: dict,
    coverage: bool = False,
    path: str | None = None,
    watch: bool = False,
) -> TestResult:
    """Run frontend tests with vitest or jest."""
    result = TestResult(framework="vitest")

    # Determine command based on frontend type
    if project["frontend_type"] == "vue":
        if project["uses_docker"]:
            cmd = ["docker", "compose", "run", "--rm", "frontend", "npm", "run", "test:unit"]
        else:
            cmd = ["npm", "run", "test:unit"]

        if coverage:
            cmd.extend(["--", "--coverage"])
        if watch:
            cmd.extend(["--", "--watch"])
        if path:
            cmd.extend(["--", path])

    elif project["frontend_type"] == "react-native":
        result.framework = "jest"
        cmd = ["npm", "test"]
        if coverage:
            cmd.extend(["--", "--coverage"])
        if watch:
            cmd.extend(["--", "--watch"])
        if path:
            cmd.extend(["--", path])

    else:
        result.error = "Unknown frontend type"
        result.success = False
        return result

    # Run tests
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        result.output = proc.stdout
        result.error = proc.stderr
        result.success = proc.returncode == 0

        # Parse output based on framework
        if result.framework == "vitest":
            result = parse_vitest_output(result)
        else:
            result = parse_jest_output(result)

    except subprocess.TimeoutExpired:
        result.error = "Test run timed out after 10 minutes"
        result.success = False
    except FileNotFoundError:
        result.error = "npm not found"
        result.success = False

    return result


def parse_pytest_output(result: TestResult) -> TestResult:
    """Parse pytest output for test counts."""
    output = result.output + result.error

    # Match patterns like "5 passed, 2 failed, 1 skipped"
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    skipped_match = re.search(r"(\d+) skipped", output)

    if passed_match:
        result.passed = int(passed_match.group(1))
    if failed_match:
        result.failed = int(failed_match.group(1))
    if skipped_match:
        result.skipped = int(skipped_match.group(1))

    # Match duration
    duration_match = re.search(r"in ([\d.]+)s", output)
    if duration_match:
        result.duration = float(duration_match.group(1))

    return result


def parse_vitest_output(result: TestResult) -> TestResult:
    """Parse vitest output for test counts."""
    output = result.output + result.error

    # Match patterns like "Tests  5 passed | 2 failed | 1 skipped"
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    skipped_match = re.search(r"(\d+) skipped", output)

    if passed_match:
        result.passed = int(passed_match.group(1))
    if failed_match:
        result.failed = int(failed_match.group(1))
    if skipped_match:
        result.skipped = int(skipped_match.group(1))

    # Match coverage
    coverage_match = re.search(r"All files\s*\|\s*([\d.]+)", output)
    if coverage_match:
        result.coverage = float(coverage_match.group(1))

    return result


def parse_jest_output(result: TestResult) -> TestResult:
    """Parse jest output for test counts."""
    output = result.output + result.error

    # Match patterns like "Tests: 2 failed, 5 passed, 7 total"
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    skipped_match = re.search(r"(\d+) skipped", output)

    if passed_match:
        result.passed = int(passed_match.group(1))
    if failed_match:
        result.failed = int(failed_match.group(1))
    if skipped_match:
        result.skipped = int(skipped_match.group(1))

    # Match coverage
    coverage_match = re.search(r"All files\s*\|\s*([\d.]+)", output)
    if coverage_match:
        result.coverage = float(coverage_match.group(1))

    return result


def parse_coverage_json(result: TestResult) -> TestResult:
    """Parse coverage.json for coverage percentage."""
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        try:
            data = json.loads(coverage_file.read_text())
            totals = data.get("totals", {})
            covered = totals.get("covered_lines", 0)
            total = totals.get("num_statements", 1)
            result.coverage = round((covered / total) * 100, 1) if total > 0 else 0
        except (json.JSONDecodeError, KeyError):
            pass
    return result


def check_quality_gate(
    results: list[TestResult],
    threshold: int = COVERAGE_THRESHOLDS["standard"],
) -> tuple[bool, list[str]]:
    """Check if all quality gates pass."""
    passed = True
    failures = []

    for result in results:
        # Check for test failures
        if result.failed > 0:
            passed = False
            failures.append(f"{result.framework}: {result.failed} tests failed")

        # Check for skipped tests
        if result.skipped > 0:
            passed = False
            failures.append(f"{result.framework}: {result.skipped} tests skipped")

        # Check coverage threshold
        if result.coverage is not None and result.coverage < threshold:
            passed = False
            failures.append(
                f"{result.framework}: Coverage {result.coverage}% < {threshold}% threshold"
            )

    return passed, failures


def print_results(results: list[TestResult], gate_mode: bool = False) -> int:
    """Print formatted test results."""
    print("\n" + "=" * 60)
    print("                    TEST RESULTS")
    print("=" * 60 + "\n")

    all_passed = True
    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for result in results:
        framework_name = result.framework.capitalize()

        if result.success and result.failed == 0:
            status = "✅"
        else:
            status = "❌"
            all_passed = False

        print(f"{framework_name} ({result.framework}):")
        print(f"  {status} {result.passed} passed, {result.failed} failed, {result.skipped} skipped")

        if result.coverage is not None:
            threshold = COVERAGE_THRESHOLDS["standard"]
            coverage_status = "" if result.coverage >= threshold else f" ⚠️ BELOW THRESHOLD"
            print(f"  📊 Coverage: {result.coverage}% (threshold: {threshold}%){coverage_status}")

        if result.duration:
            print(f"  ⏱️  Duration: {result.duration:.1f}s")

        # Show failed tests if any
        if result.failed > 0 and result.output:
            print("\n  Failed Tests:")
            # Extract failed test names from output
            for line in result.output.split("\n"):
                if "FAILED" in line or "✗" in line:
                    print(f"    - {line.strip()[:60]}")

        print()

        total_passed += result.passed
        total_failed += result.failed
        total_skipped += result.skipped

    # Quality gate summary
    if gate_mode:
        gate_passed, failures = check_quality_gate(results)
        print("=" * 60)
        if gate_passed:
            print("✅ QUALITY GATE: PASSED")
        else:
            print("❌ QUALITY GATE: FAILED")
            for failure in failures:
                print(f"   - {failure}")
        print("=" * 60)

        if not gate_passed:
            if total_failed > 0:
                return EXIT_TESTS_FAILED
            elif total_skipped > 0:
                return EXIT_SKIPPED_TESTS
            else:
                return EXIT_COVERAGE_FAILED
    else:
        print("=" * 60)
        print(f"Total: {total_passed} passed, {total_failed} failed, {total_skipped} skipped")
        print("=" * 60)

    return EXIT_SUCCESS if all_passed else EXIT_TESTS_FAILED


def main():
    parser = argparse.ArgumentParser(
        description="Run tests with TDD workflow enforcement",
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend tests only",
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run frontend tests only",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Quality gate mode (fail if thresholds not met)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch mode (re-run on changes)",
    )
    parser.add_argument(
        "--path",
        help="Specific test file or directory",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Detect project type
    project = detect_project_type()

    if args.verbose:
        print(f"Detected project: {project}")

    results = []

    # Determine what to run
    run_backend = args.backend or (not args.backend and not args.frontend)
    run_frontend = args.frontend or (not args.backend and not args.frontend)

    # Run backend tests
    if run_backend and project["has_backend"]:
        print("Running backend tests...")
        result = run_backend_tests(
            project,
            coverage=args.coverage,
            path=args.path if not args.frontend else None,
            verbose=args.verbose,
        )
        results.append(result)

    # Run frontend tests
    if run_frontend and (project["has_frontend"] or project["has_mobile"]):
        print("Running frontend tests...")
        result = run_frontend_tests(
            project,
            coverage=args.coverage,
            path=args.path if not args.backend else None,
            watch=args.watch,
        )
        results.append(result)

    # No tests found
    if not results:
        print("No test frameworks detected. Check your project configuration.")
        sys.exit(EXIT_TESTS_FAILED)

    # Output results
    if args.json:
        output = {
            "results": [
                {
                    "framework": r.framework,
                    "passed": r.passed,
                    "failed": r.failed,
                    "skipped": r.skipped,
                    "coverage": r.coverage,
                    "duration": r.duration,
                    "success": r.success,
                }
                for r in results
            ],
            "gate_passed": check_quality_gate(results)[0] if args.gate else None,
        }
        print(json.dumps(output, indent=2))
    else:
        exit_code = print_results(results, gate_mode=args.gate)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
