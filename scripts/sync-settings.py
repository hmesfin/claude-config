#!/usr/bin/env python3
"""Sync ~/.claude/settings.json with the copy tracked in this repo.

This repo is public. The live settings file carries an autoMode.environment
block that Claude Code regenerates on its own, and that block records
filesystem paths, private repo names, and where secrets live. A plain symlink
would eventually push all of that to GitHub with nobody watching.

So the tracked copy is a filtered subset, and the filter is enforced rather
than trusted: pull strips the machine-specific keys, then re-scans the result
and refuses to write if anything sensitive survived.

  sync-settings.py --pull    live  -> repo   (strip machine keys, then verify)
  sync-settings.py --push    repo  -> live   (merge, keep live machine keys)
  sync-settings.py --check   verify the tracked copy is clean, exit 1 if not
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

LIVE_PATH = Path.home() / ".claude" / "settings.json"
REPO_PATH = Path(__file__).resolve().parent.parent / "global-settings.json"

# Regenerated per machine and per project by Claude Code. Never tracked.
MACHINE_KEYS: set[str] = {"autoMode"}

# If any of these survive the strip, something changed upstream and the
# filter no longer covers it. Fail loudly rather than publish.
FORBIDDEN: list[tuple[str, str]] = [
  (r"/home/[a-z]", "absolute home-directory path"),
  (r"/Users/[a-z]", "absolute macOS home path"),
  (r"hmesfin/", "private repo reference"),
  (r"\.envs?/", "secrets location"),
  (r"key\.properties", "signing key reference"),
]


def load(path: Path) -> dict[str, Any]:
  if not path.exists():
    sys.exit(f"missing: {path}")
  return json.loads(path.read_text(encoding="utf-8"))


def scan(data: dict[str, Any]) -> list[str]:
  """Return a description of every forbidden pattern present in data."""
  blob = json.dumps(data)
  return [why for pattern, why in FORBIDDEN if re.search(pattern, blob)]


def pull() -> None:
  live = load(LIVE_PATH)
  tracked = {k: v for k, v in live.items() if k not in MACHINE_KEYS}
  dropped = sorted(set(live) & MACHINE_KEYS)

  problems = scan(tracked)
  if problems:
    sys.exit(
      "refusing to write - sensitive content survived the filter:\n  "
      + "\n  ".join(problems)
      + "\n\nAdd the offending key to MACHINE_KEYS in scripts/sync-settings.py."
    )

  REPO_PATH.write_text(json.dumps(tracked, indent=2) + "\n", encoding="utf-8")
  print(f"pulled -> {REPO_PATH}")
  if dropped:
    print(f"  dropped machine-specific keys: {', '.join(dropped)}")


def push() -> None:
  tracked = load(REPO_PATH)
  live = load(LIVE_PATH) if LIVE_PATH.exists() else {}

  merged = dict(tracked)
  for key in MACHINE_KEYS:
    if key in live:
      merged[key] = live[key]

  if LIVE_PATH.exists():
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = LIVE_PATH.with_name(f"settings.json.bak-{stamp}")
    backup.write_text(LIVE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"  backup: {backup}")

  LIVE_PATH.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
  print(f"pushed -> {LIVE_PATH}")
  kept = sorted(k for k in MACHINE_KEYS if k in live)
  if kept:
    print(f"  kept local keys: {', '.join(kept)}")


def check() -> None:
  problems = scan(load(REPO_PATH))
  if problems:
    print("tracked settings contain sensitive content:", file=sys.stderr)
    for why in problems:
      print(f"  {why}", file=sys.stderr)
    sys.exit(1)
  print("tracked settings are clean")


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--pull", action="store_true", help="live -> repo")
  group.add_argument("--push", action="store_true", help="repo -> live")
  group.add_argument("--check", action="store_true", help="verify tracked copy")
  args = parser.parse_args()

  if args.pull:
    pull()
  elif args.push:
    push()
  else:
    check()


if __name__ == "__main__":
  main()
