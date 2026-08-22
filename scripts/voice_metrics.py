"""Measure the register of Claude Code's assistant prose from session transcripts.

Reads ~/.claude/projects/<slug>/*.jsonl, extracts assistant text blocks (skipping
tool calls), and reports the markers that distinguish conversational prose from
build-log fragments.

Baseline captured 2026-08-22 against the pre-rewrite CLAUDE.md is in BASELINE;
the report deltas against it so a re-run answers "did the change take" directly.

Usage:
    python scripts/voice_metrics.py                      # all projects, last 7 days
    python scripts/voice_metrics.py --project rentkee    # substring match on dir
    python scripts/voice_metrics.py --since 2026-08-22   # only sessions after a date
"""

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

PROJECTS = pathlib.Path.home() / ".claude" / "projects"

# Old CLAUDE.md, 232 blocks across the 6 newest rentkee sessions.
BASELINE = {
    "under 200 chars": 0.65,
    "colon-ended fragment": 0.41,
    "contains 'I'": 0.34,
    "ends with a question": 0.06,
}

HEDGES = [
    "I think", "might", "possibly", "it's worth noting", "notably",
    "likely", "appears to", "seems to", "perhaps",
]


def load_texts(files):
    """Return every non-empty assistant text block across the given transcripts."""
    texts = []
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") != "assistant":
                    continue
                content = record.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if block.get("type") == "text" and block.get("text", "").strip():
                        texts.append(block["text"].strip())
    return texts


def measure(texts):
    total = len(texts)
    return {
        "under 200 chars": sum(1 for t in texts if len(t) < 200) / total,
        "colon-ended fragment": sum(1 for t in texts if len(t) < 160 and t.endswith(":")) / total,
        "contains 'I'": sum(1 for t in texts if re.search(r"\bI\b", t)) / total,
        "ends with a question": sum(1 for t in texts if t.rstrip().endswith("?")) / total,
    }


def find_files(project, since):
    cutoff = since.timestamp()
    roots = [d for d in PROJECTS.iterdir() if d.is_dir()]
    if project:
        roots = [d for d in roots if project.lower() in d.name.lower()]
    files = [f for d in roots for f in d.glob("*.jsonl") if f.stat().st_mtime >= cutoff]
    return sorted(files, key=lambda f: -f.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="substring match on the project directory name")
    parser.add_argument("--since", help="YYYY-MM-DD; only sessions modified on or after")
    parser.add_argument("--days", type=int, default=7, help="lookback when --since is omitted")
    args = parser.parse_args()

    if args.since:
        since = dt.datetime.strptime(args.since, "%Y-%m-%d")
    else:
        since = dt.datetime.now() - dt.timedelta(days=args.days)

    files = find_files(args.project, since)
    if not files:
        sys.exit(f"No transcripts under {PROJECTS} since {since:%Y-%m-%d}")

    texts = load_texts(files)
    if not texts:
        sys.exit(f"Found {len(files)} transcripts but no assistant prose in them")

    print(f"{len(files)} sessions since {since:%Y-%m-%d}, {len(texts)} assistant text blocks")
    print(f"median block: {sorted(len(t) for t in texts)[len(texts) // 2]} chars\n")

    print(f"{'':24} {'now':>6} {'was':>6}   delta")
    for label, value in measure(texts).items():
        was = BASELINE[label]
        arrow = "↓" if value < was else "↑" if value > was else "="
        print(f"{label:24} {value:5.0%} {was:6.0%}   {arrow} {abs(value - was):.0%}")

    hedges = sum(len(re.findall(re.escape(h), t, re.I)) for t in texts for h in HEDGES)
    print(f"\nhedge markers: {hedges} across {len(texts)} blocks "
          f"({hedges / len(texts):.2f}/block; baseline 0.03)")


if __name__ == "__main__":
    main()
