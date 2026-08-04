"""Insert conventional-pre-commit into a .pre-commit-config.yaml.

Text-level insertion so comments and formatting survive. Verifies by reparsing.
Idempotent: exits 2 if the hook is already present.
"""

import re
import sys
import pathlib
import yaml

HOOK = """
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert]
"""

INSTALL_TYPES = "default_install_hook_types: [pre-commit, commit-msg]"
TOP_LEVEL_KEY = re.compile(r"^[A-Za-z_][\w-]*:")


def main(path_str: str) -> int:
    path = pathlib.Path(path_str)
    text = path.read_text()
    if "conventional-pre-commit" in text:
        print(f"SKIP  {path_str} (already present)")
        return 2

    before = yaml.safe_load(text)
    n_before = len(before["repos"])
    lines = text.splitlines()

    # Find where the repos: block ends. Scan forward from `repos:` until the
    # next top-level key; remember the last non-blank, non-comment line, so a
    # trailing `# comment` + `ci:` block does not get split.
    start = next(i for i, ln in enumerate(lines) if ln.startswith("repos:"))
    last = start
    for i in range(start + 1, len(lines)):
        if TOP_LEVEL_KEY.match(lines[i]):
            break
        if lines[i].strip() and not lines[i].strip().startswith("#"):
            last = i

    lines[last + 1 : last + 1] = HOOK.strip("\n").split("\n")

    # Add default_install_hook_types unless already set: after default_stages
    # if present, else immediately above repos:.
    if "default_install_hook_types" not in text:
        anchor = next(
            (i for i, ln in enumerate(lines) if ln.startswith("default_stages:")), None
        )
        if anchor is not None:
            lines.insert(anchor + 1, INSTALL_TYPES)
        else:
            repos_i = next(i for i, ln in enumerate(lines) if ln.startswith("repos:"))
            lines.insert(repos_i, INSTALL_TYPES)
            lines.insert(repos_i + 1, "")

    out = "\n".join(lines) + "\n"
    after = yaml.safe_load(out)

    assert len(after["repos"]) == n_before + 1, "repo count did not increase by one"
    # Membership, not equality: a repo may legitimately also install pre-push.
    types = after.get("default_install_hook_types") or []
    assert "commit-msg" in types, f"commit-msg missing from install types: {types}"
    assert "pre-commit" in types, f"pre-commit missing from install types: {types}"
    hook = after["repos"][-1]
    assert "conventional-pre-commit" in hook["repo"], "hook not last in repos list"
    assert hook["hooks"][0]["stages"] == ["commit-msg"], "stages not explicit"
    # Everything that was there before must still be there.
    for key, val in before.items():
        if key != "repos":
            assert after.get(key) == val, f"top-level key {key} changed"

    path.write_text(out)
    print(f"OK    {path_str} (repos {n_before} -> {len(after['repos'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
