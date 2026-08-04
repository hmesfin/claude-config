# GitHub Templates and Commit Standards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize PR bodies, issue reports, and commit messages across all
161 `hmesfin/*` repos from a single source of truth, so the CLAUDE.md sign-off
gate can stay narrowed to projects Hamel does not own.

**Architecture:** `claude-config/github-templates/` is canonical. A publish
script pushes the GitHub-facing subset to a public `hmesfin/.github` repo, which
GitHub applies as default community health files to every owned repo lacking its
own. Commit-message enforcement rides the `.pre-commit-config.yaml` already
present in 21 repos, via `conventional-pre-commit` at the `commit-msg` stage.

**Tech Stack:** GitHub default community health files, GitHub issue forms
(YAML), `pre-commit`, `conventional-pre-commit` v4.4.0, `gh` CLI, bash.

**Spec:** `docs/specs/2026-08-03-github-templates-design.md`

**Already done, not in this plan:** spec section 1 (the CLAUDE.md gate
narrowing) and section 7 Level 1 (binding `Verified` to the No AI Slop rules)
are complete and committed as `78b6610` and `8cecbba`. This plan covers spec
sections 2-6.

## Global Constraints

- `conventional-pre-commit` pinned at `rev: v4.4.0` exactly. Do not use `main`.
- Every hook entry sets `stages: [commit-msg]` explicitly, even though the
  hook manifest declares it. 18 of 21 configs set `default_stages: [pre-commit]`
  at top level and the precedence is ambiguous.
- Every touched config sets `default_install_hook_types: [pre-commit, commit-msg]`
  so a plain `pre-commit install` wires both stages.
- `--strict` is NOT enabled. Merge and revert commits must still pass.
- Allowed types, verbatim: `feat, fix, docs, style, refactor, test, chore, ci,
  build, perf, revert`.
- The `hmesfin/.github` repo is PUBLIC and world-readable. No client names, no
  infrastructure detail, no internal process in any published file.
- Creating the public repo requires explicit user confirmation at Task 2 Step 2.
  Do not create it before receiving that confirmation.
- Commit messages in `claude-config` follow Conventional Commits.
- No mechanical enforcement of the PR `Verified` field. Out of scope per spec
  section 7.

## File Structure

| Path | Responsibility |
|---|---|
| `claude-config/github-templates/PULL_REQUEST_TEMPLATE.md` | Four-field PR body |
| `claude-config/github-templates/ISSUE_TEMPLATE/01-bug.yml` | Bug form, repro required |
| `claude-config/github-templates/ISSUE_TEMPLATE/02-feature.yml` | Feature form |
| `claude-config/github-templates/ISSUE_TEMPLATE/config.yml` | Chooser config |
| `claude-config/github-templates/pre-commit-snippet.yaml` | Snippet appended to repo configs. Not published. |
| `claude-config/github-templates/README.md` | Override semantics, publish instructions. Not published. |
| `claude-config/publish-github-templates.sh` | Sync canonical dir to `hmesfin/.github` |

---

### Task 1: Author the canonical templates

**Files:**
- Create: `claude-config/github-templates/PULL_REQUEST_TEMPLATE.md`
- Create: `claude-config/github-templates/ISSUE_TEMPLATE/01-bug.yml`
- Create: `claude-config/github-templates/ISSUE_TEMPLATE/02-feature.yml`
- Create: `claude-config/github-templates/ISSUE_TEMPLATE/config.yml`
- Create: `claude-config/github-templates/pre-commit-snippet.yaml`
- Create: `claude-config/github-templates/README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the directory `claude-config/github-templates/` with the exact file
  names above. Task 2 copies `PULL_REQUEST_TEMPLATE.md` and `ISSUE_TEMPLATE/`.
  Task 4's script excludes `pre-commit-snippet.yaml` and `README.md` by those
  exact names. Task 5 appends the contents of `pre-commit-snippet.yaml`.

- [ ] **Step 1: Create the PR template**

Write `claude-config/github-templates/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What & why

<!-- One or two lines. The diff shows what changed; say why. -->

## Verified

<!--
What was actually run or checked. Paste real output where it's short.
"Not tested" and "untested beyond type check" are valid answers.
Do not claim a suite passed unless it was run.
-->

## Risk

<!-- Blast radius, migrations, rollback path. "None" is valid. -->

## Notes

<!-- Follow-ups, deferred work, anything a reviewer shouldn't have to infer. -->
```

- [ ] **Step 2: Create the bug form**

Write `claude-config/github-templates/ISSUE_TEMPLATE/01-bug.yml`:

```yaml
name: Bug report
description: Something is broken. Include a reproduction.
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        File on a reproduction, not a conviction. If it can't be reproduced,
        say so in Notes rather than filing.
  - type: textarea
    id: repro
    attributes:
      label: Steps to reproduce
      description: Minimal steps someone else could follow start to finish.
      placeholder: |
        1.
        2.
        3.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual
      description: Paste exact output or error text, not a summary of it.
    validations:
      required: true
  - type: input
    id: env
    attributes:
      label: Environment
      placeholder: "branch or commit, OS, service (django / frontend / worker)"
    validations:
      required: true
  - type: textarea
    id: suspected
    attributes:
      label: Suspected cause
      description: >
        Optional. Mark inference as inference. Leave blank unless the cause has
        actually been isolated.
    validations:
      required: false
```

- [ ] **Step 3: Create the feature form**

Write `claude-config/github-templates/ISSUE_TEMPLATE/02-feature.yml`:

```yaml
name: Feature or change
description: Propose new behavior, or a change to behavior that already exists.
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What is missing or wrong today. Describe the problem, not the fix.
    validations:
      required: true
  - type: textarea
    id: proposed
    attributes:
      label: Proposed change
    validations:
      required: true
  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: What is explicitly out of scope. "Not yet clear" is a valid answer.
    validations:
      required: true
  - type: textarea
    id: notes
    attributes:
      label: Notes
    validations:
      required: false
```

- [ ] **Step 4: Create the chooser config**

Write `claude-config/github-templates/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: true
```

- [ ] **Step 5: Create the pre-commit snippet**

Write `claude-config/github-templates/pre-commit-snippet.yaml`:

```yaml
# Appended to each repo's .pre-commit-config.yaml by hand, one repo at a time.
# Not published to hmesfin/.github.
#
# default_install_hook_types goes at TOP level of the config, not under repos:.
# Without it, `pre-commit install` wires only the pre-commit stage and no
# commit message is ever validated - the config looks correct and silently
# does nothing.
#
# stages: [commit-msg] is set explicitly even though the hook manifest already
# declares it, because most configs set default_stages: [pre-commit] at top
# level and the precedence between the two is ambiguous.

default_install_hook_types: [pre-commit, commit-msg]

repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert]
```

- [ ] **Step 6: Create the README**

Write `claude-config/github-templates/README.md`:

```markdown
# GitHub templates

Canonical source. Nothing here is authored directly in `hmesfin/.github`.

## What goes where

- `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/` - published to the public
  `hmesfin/.github` repo by `../publish-github-templates.sh`. GitHub applies
  them as defaults to every `hmesfin/*` repo that has no equivalent file of
  its own.
- `pre-commit-snippet.yaml`, `README.md` - local only, never published.

## The override rule

Per-repo overrides are all-or-nothing per folder:

> If a repository has any files in its own `.github/ISSUE_TEMPLATE` folder,
> such as issue templates or a `config.yml` file, none of the contents of the
> default `.github/ISSUE_TEMPLATE` folder will be used.

So a repo that adds one custom issue form loses ALL inherited forms, including
the bug form. If a repo needs one custom form, copy the defaults in alongside
it.

`PULL_REQUEST_TEMPLATE.md` is a single file and overrides cleanly on its own.

## Publishing

    ./publish-github-templates.sh

The `hmesfin/.github` repo is public. Nothing here may contain client names,
infrastructure detail, or internal process.
```

- [ ] **Step 7: Verify the YAML parses**

Issue forms fail silently in GitHub's UI when malformed, so parse them locally
before they ever reach GitHub.

Run:
```bash
cd /home/hamel/claude-config/github-templates
python3 -c "
import yaml, sys, pathlib
for p in sorted(pathlib.Path('ISSUE_TEMPLATE').glob('*.yml')) + [pathlib.Path('pre-commit-snippet.yaml')]:
    d = yaml.safe_load(p.read_text())
    print(f'{p}: OK ({type(d).__name__})')
"
```
Expected: three lines, each ending `OK (dict)`. Any traceback is a failure —
fix the YAML before continuing.

- [ ] **Step 8: Verify required fields are actually marked required**

Run:
```bash
cd /home/hamel/claude-config/github-templates
python3 -c "
import yaml, pathlib
d = yaml.safe_load(pathlib.Path('ISSUE_TEMPLATE/01-bug.yml').read_text())
req = [f['id'] for f in d['body'] if f.get('validations',{}).get('required')]
print('required:', req)
assert 'repro' in req, 'repro must be required - it is the whole point'
assert 'suspected' not in req, 'suspected must stay optional'
print('OK')
"
```
Expected: `required: ['repro', 'expected', 'actual', 'env']` then `OK`.

- [ ] **Step 9: Commit**

```bash
cd /home/hamel/claude-config
git add github-templates/
git commit -m "feat(templates): add canonical PR and issue templates

PR template carries a Verified field; bug form makes a reproduction a
required field so the repro rule is enforced by GitHub's validator rather
than by memory.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Empirically test whether private repos inherit defaults

This is the load-bearing unknown from the spec. GitHub documents that the
`.github` repo must be public but states no visibility requirement on target
repos. 130 of the 161 repos are private. If they do not inherit, the whole
publish approach is wrong and Task 4 changes shape.

Test with a sentinel value that is unmistakable, so a pass cannot be confused
with a pre-existing file.

**Files:**
- Create (remote): `hmesfin/.github` repository
- Create (remote): `.github/PULL_REQUEST_TEMPLATE.md` in that repo, sentinel content

**Interfaces:**
- Consumes: nothing from Task 1. Runs on sentinel content only.
- Produces: a definitive yes/no that Task 3 and Task 4 branch on.

- [ ] **Step 1: Confirm the repo does not already exist**

Run: `gh repo view hmesfin/.github --json name 2>&1 | head -2`
Expected: `Could not resolve to a Repository`. If it exists, STOP and ask —
the plan assumes creation, not modification.

- [ ] **Step 2: GATE — get explicit user confirmation**

Creating a public repo under the user's name is an outward-facing, externally
visible action. Ask before proceeding:

> "Ready to create the public repo `hmesfin/.github`. It will be world-readable
> and visible on your profile. It'll hold only the generic templates. Go ahead?"

Do not proceed without a clear yes.

- [ ] **Step 3: Create the repo with a sentinel template**

```bash
cd /tmp/claude-1000/-home-hamel--claude/*/scratchpad
rm -rf dotgithub-test && mkdir dotgithub-test && cd dotgithub-test
git init -q
mkdir -p .github
printf '%s\n' 'SENTINEL-INHERIT-TEST-8842 — if you can read this in a PR body of another repo, defaults are inherited.' > .github/PULL_REQUEST_TEMPLATE.md
printf '%s\n' '# .github' '' 'Default community health files for hmesfin repos.' > README.md
git add -A
git commit -q -m "chore: sentinel template for inheritance test"
gh repo create hmesfin/.github --public --source=. --push
```
Expected: repo created, push succeeds.

- [ ] **Step 4: Try the REST endpoint first**

There may be an API that reports resolved templates. Try it before falling back
to the browser. Do not assume it exists.

Run:
```bash
gh api repos/hmesfin/cli-crawler/issues/templates 2>&1 | head -5
```
Expected: either template JSON, or a 404 `Not Found`. A 404 means the endpoint
isn't available — that is not a test failure, move to Step 5.

- [ ] **Step 5: Definitive check — open a real PR body in a private repo**

The reliable check is GitHub's own UI resolving the default. Pick a private
repo with at least two branches, or create a throwaway branch.

```bash
gh repo view hmesfin/cli-crawler --json isPrivate,defaultBranchRef
```

Then open the compare page in the browser and read the PR body field:
`https://github.com/hmesfin/cli-crawler/compare/main...<some-branch>?expand=1`

Use the `playwright-launch` MCP server with the `chrome` channel (the user's
Chrome session is already authenticated to GitHub).

Expected PASS: the PR description box is pre-filled with
`SENTINEL-INHERIT-TEST-8842`.
Expected FAIL: the description box is empty.

- [ ] **Step 6: Record the result in the spec**

Move the finding out of the "Unverified" section of
`docs/specs/2026-08-03-github-templates-design.md` and into "Verified facts",
stating what was observed and on which repo. If it FAILED, also update the
Risks section and note that Task 4 takes the sync-script branch.

- [ ] **Step 7: Commit the finding**

```bash
cd /home/hamel/claude-config
git add docs/specs/2026-08-03-github-templates-design.md
git commit -m "docs(specs): record empirical result of private-repo inheritance test

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Replace the sentinel with the real templates

**Files:**
- Modify (remote): `hmesfin/.github` — replace sentinel, add real templates

**Interfaces:**
- Consumes: `claude-config/github-templates/` from Task 1; the pass/fail from Task 2.
- Produces: a populated `hmesfin/.github`. Task 4 automates what this task does by hand once.

- [ ] **Step 1: Branch on the Task 2 result**

If Task 2 PASSED, continue to Step 2.

If Task 2 FAILED, STOP. Report to the user that defaults do not reach private
repos, that Task 4 becomes a per-repo sync script instead of a publish script,
and get direction before writing to 130 repos. Do not silently switch approach.

- [ ] **Step 2: Copy the real templates in**

```bash
cd /tmp/claude-1000/-home-hamel--claude/*/scratchpad/dotgithub-test
rm -f .github/PULL_REQUEST_TEMPLATE.md
cp /home/hamel/claude-config/github-templates/PULL_REQUEST_TEMPLATE.md .github/
cp -r /home/hamel/claude-config/github-templates/ISSUE_TEMPLATE .github/
ls -R .github/
```
Expected listing: `.github/PULL_REQUEST_TEMPLATE.md`, and
`.github/ISSUE_TEMPLATE/` containing `01-bug.yml`, `02-feature.yml`, `config.yml`.

- [ ] **Step 3: Confirm no unpublishable files leaked**

```bash
test ! -e .github/pre-commit-snippet.yaml && test ! -e .github/README.md && echo "OK: local-only files excluded"
grep -rniE 'gojjo|realgig|rentkee|famapp|hetzner|traefik' .github/ && echo "LEAK FOUND - stop" || echo "OK: no internal identifiers"
```
Expected: `OK: local-only files excluded` and `OK: no internal identifiers`.

- [ ] **Step 4: Push**

```bash
git add -A
git commit -q -m "feat: real PR and issue templates, replacing sentinel"
git push
```

- [ ] **Step 5: Verify the issue chooser renders in a PRIVATE repo**

Open `https://github.com/hmesfin/cli-crawler/issues/new/choose` in the browser.

Expected: "Bug report" and "Feature or change" both listed, plus a blank issue
option. Malformed form YAML causes GitHub to silently omit the form, so a
missing entry means the YAML is broken, not that inheritance failed.

- [ ] **Step 6: Verify the bug form actually blocks submission**

Open the Bug report form, leave "Steps to reproduce" empty, fill everything
else, and attempt to submit.

Expected: GitHub refuses and flags the required field. This is the check that
proves the repro rule is enforced rather than advisory. Do NOT submit a real
issue — cancel out once the validation error appears.

---

### Task 4: Write the publish script

**Files:**
- Create: `claude-config/publish-github-templates.sh`

**Interfaces:**
- Consumes: `claude-config/github-templates/`.
- Produces: a repeatable publish path so Task 3 never has to be done by hand again.

- [ ] **Step 1: Write the script**

Write `claude-config/publish-github-templates.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Publishes github-templates/ to the public hmesfin/.github repo, where GitHub
# applies them as default community health files to every hmesfin/* repo that
# has no equivalent file of its own.
#
# pre-commit-snippet.yaml and README.md are local-only and never published.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/github-templates"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

[ -d "$SRC" ] || { echo -e "${RED}missing $SRC${NC}"; exit 1; }

echo "Cloning hmesfin/.github..."
gh repo clone hmesfin/.github "$WORK/dotgithub" -- -q

cd "$WORK/dotgithub"
rm -rf .github/ISSUE_TEMPLATE .github/PULL_REQUEST_TEMPLATE.md
mkdir -p .github
cp "$SRC/PULL_REQUEST_TEMPLATE.md" .github/
cp -r "$SRC/ISSUE_TEMPLATE" .github/

# Guard: local-only files must never reach the public repo.
for f in pre-commit-snippet.yaml README.md; do
  if [ -e ".github/$f" ]; then
    echo -e "${RED}refusing to publish .github/$f${NC}"; exit 1
  fi
done

# Guard: no internal identifiers in a world-readable repo.
if grep -rqniE 'gojjo|realgig|rentkee|famapp|hetzner|traefik' .github/; then
  echo -e "${RED}internal identifier found in templates - refusing to publish${NC}"
  grep -rniE 'gojjo|realgig|rentkee|famapp|hetzner|traefik' .github/
  exit 1
fi

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi

git add -A
git commit -q -m "chore: sync templates from claude-config"
git push -q
echo -e "${GREEN}Published.${NC}"
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x /home/hamel/claude-config/publish-github-templates.sh
```

- [ ] **Step 3: Verify it is a no-op right now**

Task 3 already pushed identical content, so a correct script must detect no
change. This tests the script without risking a bad publish.

Run: `/home/hamel/claude-config/publish-github-templates.sh`
Expected: `No changes to publish.`

- [ ] **Step 4: Verify the leak guard actually fires**

A guard that has never fired is untested. Prove it rejects.

```bash
cd /home/hamel/claude-config
printf '\n<!-- gojjo internal note -->\n' >> github-templates/PULL_REQUEST_TEMPLATE.md
./publish-github-templates.sh; echo "exit=$?"
git checkout github-templates/PULL_REQUEST_TEMPLATE.md
```
Expected: `internal identifier found in templates - refusing to publish`, then
`exit=1`. The `git checkout` restores the file — confirm with `git status` that
the tree is clean afterward.

- [ ] **Step 5: Commit**

```bash
cd /home/hamel/claude-config
git add publish-github-templates.sh
git commit -m "feat(templates): add publish script with leak guards

Refuses to publish if local-only files or internal identifiers would reach
the public .github repo.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Pilot the commit hook in one repo

Do not touch 21 repos before the mechanism is proven once. `data-imports` is
the pilot: it has no `default_stages`, so it is the simplest case, and it is a
low-traffic repo.

**Files:**
- Modify: `/home/hamel/projects/active/data-imports/.pre-commit-config.yaml`

**Interfaces:**
- Consumes: `claude-config/github-templates/pre-commit-snippet.yaml` from Task 1.
- Produces: a proven procedure that Task 6 repeats 20 times.

- [ ] **Step 1: Check the repo is clean before touching it**

```bash
cd /home/hamel/projects/active/data-imports
git status --short
git branch --show-current
```
Expected: empty status. If dirty, STOP and ask — do not bundle unrelated
changes.

- [ ] **Step 2: Add `default_install_hook_types` at top level**

Insert as the first line of `.pre-commit-config.yaml`:

```yaml
default_install_hook_types: [pre-commit, commit-msg]
```

- [ ] **Step 3: Append the hook under the existing `repos:` list**

Append to the end of the `repos:` list, matching the file's existing
indentation:

```yaml
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert]
```

- [ ] **Step 4: Verify the config still parses**

```bash
cd /home/hamel/projects/active/data-imports
python3 -c "import yaml;d=yaml.safe_load(open('.pre-commit-config.yaml'));print('hooks:',len(d['repos']));print('install_hook_types:',d.get('default_install_hook_types'))"
```
Expected: a repo count one higher than before, and
`install_hook_types: ['pre-commit', 'commit-msg']`.

- [ ] **Step 5: Install both hook stages**

```bash
cd /home/hamel/projects/active/data-imports
pre-commit install
ls -1 .git/hooks/ | grep -E '^(pre-commit|commit-msg)$'
```
Expected: BOTH `commit-msg` and `pre-commit` listed. If `commit-msg` is
missing, `default_install_hook_types` was not picked up — stop and fix before
continuing, because the hook is a silent no-op without it.

- [ ] **Step 6: Stage the config FIRST, then prove it REJECTS**

Order matters. `pre-commit` aborts with "Your pre-commit configuration is
unstaged" if the config is not staged, so the rejection test must come after
`git add`, not before.

```bash
cd <repo>
git add .pre-commit-config.yaml
before=$(git rev-parse HEAD)
git commit -m "fixed the thing"
after=$(git rev-parse HEAD)
[ "$before" = "$after" ] && echo "CONFIRMED: rejected" || echo "PROBLEM: slipped through"
```
Expected: `Conventional Commit ... Failed`, `[Bad commit message] >> fixed the
thing`, and `CONFIRMED: rejected`.

- [ ] **Step 7: Prove it ACCEPTS a good message**

```bash
cd <repo>
git commit -m "ci(pre-commit): enforce conventional commits at commit-msg stage"
git log --oneline -1
```
Expected: `Conventional Commit ... Passed` and the new commit at HEAD.

- [ ] **Step 8: Do NOT test reverts with a real commit**

Reverts are BLOCKED by this hook. Established 2026-08-03:
`--strict` exempts merges and `fixup!` only — there is no revert exemption, and
git's generated `Revert "..."` fails the check.

Do not run a revert commit as a test. A rejected commit creates nothing, so a
follow-up `git reset --hard HEAD~1` will destroy the Step 7 config commit
instead of a throwaway. That mistake was made once during the pilot and had to
be recovered from reflog.

To probe accept/block boundaries, run the hook binary directly against a
message file — no commits, nothing to clean up:

```bash
venv=$(find ~/.cache/pre-commit -name "conventional-pre-commit" -type f | head -1)
t=$(mktemp -d); printf '%s' 'revert: some change' > "$t/m"
"$venv" feat fix docs style refactor test chore ci build perf revert "$t/m" && echo PASS || echo BLOCK
rm -rf "$t"
```

- [ ] **Step 9: Report the pilot result and STOP**

Report to the user: the rejection message text they'll see, the friction it
caused, and confirm they want the same applied to the remaining 20. Do not
proceed to Task 6 without that confirmation. Per the user's working rules, one
change verified before moving on.

---

### Task 6: Roll out to the remaining 20 repos

**Files:**
- Modify: `.pre-commit-config.yaml` in each of the 20 repos below.

The 18 repos that set `default_stages: [pre-commit]` are the ones where the
explicit `stages: [commit-msg]` matters. Verify the reject actually fires in
the first of those (`afrirank`) before trusting the rest.

Remaining repos, in order:
`twilio-callcenter`, `website-togo`, `afrirank`, `crm-service`, `djvufl-famapp`,
`djvufl-rentkee`, `etbiz`, `firstpass-rx`, `gojjo-re-data-services`,
`gojjo-webinar`, `grindszn`, `happenings-service`, `invoicing-service`,
`loom-house`, `p7`, `property-management`, `realgig`, `soccernet`,
`team-gojjo-mvp`, `txtgrub`

**Interfaces:**
- Consumes: the procedure proven in Task 5.
- Produces: 21 repos total enforcing conventional commits.

- [ ] **Step 1: Handle the two remaining no-`default_stages` repos**

For `twilio-callcenter` then `website-togo`, run Task 5 Steps 1–7 exactly.
Expected per repo: Step 6 rejects, Step 7 accepts.

- [ ] **Step 2: Do `afrirank` and confirm the precedence trap is handled**

`afrirank` is the first repo with `default_stages: [pre-commit]`. Run Task 5
Steps 1–7.

Expected: Step 6 still REJECTS. If it does not reject, the top-level
`default_stages` is overriding the hook's `stages` and the entire premise of
the explicit-`stages` workaround is wrong. STOP and report — do not continue
to the remaining 17.

- [ ] **Step 3: Skip `txtgrub`'s duplicate key**

`txtgrub` already has `default_install_hook_types`. Do not add a second one —
duplicate top-level keys make the YAML ambiguous. Instead, verify its existing
value includes `commit-msg`:

```bash
python3 -c "import yaml;d=yaml.safe_load(open('/home/hamel/projects/active/txtgrub/.pre-commit-config.yaml'));print(d.get('default_install_hook_types'))"
```
If `commit-msg` is absent, edit the existing key rather than adding a new one.
Then apply only the `repos:` entry.

- [ ] **Step 4: Work through the remaining 16, one at a time**

For each of `crm-service`, `djvufl-famapp`, `djvufl-rentkee`, `etbiz`,
`firstpass-rx`, `gojjo-re-data-services`, `gojjo-webinar`, `grindszn`,
`happenings-service`, `invoicing-service`, `loom-house`, `p7`,
`property-management`, `realgig`, `soccernet`, `team-gojjo-mvp`:

Run Task 5 Steps 1–7. If any repo's Step 1 shows a dirty tree, SKIP that repo,
note it, and continue. Report skipped repos at the end rather than committing
someone's in-progress work.

- [ ] **Step 5: Final audit**

```bash
cd /home/hamel/projects/active
for f in */.pre-commit-config.yaml; do
  d=$(dirname "$f")
  cp=$(grep -c "conventional-pre-commit" "$f")
  ih=$(grep -c "default_install_hook_types" "$f")
  hk=$([ -f "$d/.git/hooks/commit-msg" ] && echo yes || echo NO)
  printf "%-28s hook=%s install_types=%s commit-msg-installed=%s\n" "$d" "$cp" "$ih" "$hk"
done
```
Expected: all 21 rows show `hook=1`, `install_types=1`, and
`commit-msg-installed=yes`. Any `NO` means that repo is a silent no-op — fix
before declaring done.

- [ ] **Step 6: Report**

State plainly: how many repos got the hook, which were skipped and why, and
whether any needed manual intervention. Do not claim 21 if the audit showed
fewer.

---

## Out of scope

- Mechanical enforcement of the PR `Verified` field. Spec section 7 decided
  Level 1 (already applied to CLAUDE.md) with Level 3 as separate follow-on work.
- The ~140 repos without `.pre-commit-config.yaml`. They get the hook when they
  next adopt pre-commit.
- Any repo outside `~/projects/active/`.
