# GitHub Templates and Commit Standards

Date: 2026-08-03
Status: approved, not yet implemented

## Problem

Two problems, one fix.

The `Outward-Facing Writing` section of `CLAUDE.md` ends with `Draft -> show me
-> file. Never post outward-facing content without my sign-off.` That rule was
added after users on a project Hamel does not own called a bug report he filed
AI-sounding. The rule solved that case but applies to everything, so every PR
description and every issue on his own repos now needs manual approval.

Separately, no repo under `hmesfin/*` has a PR or issue template. PR and issue
bodies are freeform, which is why the sign-off gate feels necessary: without a
fixed shape, the output can be anything.

The templates are the reason the gate can be narrowed. A PR template with a
required `Verified` field does the job the gate was doing, at the artifact
instead of at the human.

## Current state

- `~/.claude` symlinks into `~/claude-config`, a git repo. Symlinks are created
  by `setup-claude-symlinks.sh`.
- ~40 repos, all under the personal account `hmesfin`. No GitHub organization.
- No PR or issue templates in any owned repo. The templates found on disk
  (oh-my-zsh, cookiecutter-django, sentry, flutter) are vendored third-party.
- No `commit.template` in `~/.gitconfig`.
- Commit history is already ~95% Conventional Commits with scopes:
  `feat(legal):`, `chore(ops):`, `docs(coach):`, `ci:`. One repo appends a
  `[deploy]` marker.
- `pre-commit` is installed at `~/.local/bin/pre-commit`. 21 repos under
  `~/projects/active/` already have `.pre-commit-config.yaml`.
- Only `txtgrub` sets `default_install_hook_types`.

## Verified facts

Confirmed against GitHub docs on 2026-08-03:

- A public repo named `.github` supplies default community health files to
  repos owned by that account. Personal accounts are supported, not just
  organizations.
- `The .github repository must be public for most default community health
  files to be applied organization-wide. Private .github repositories are not
  supported.`
- `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, and `config.yml` are all
  supported as defaults.
- Override is all-or-nothing per folder: `If a repository has any files in its
  own .github/ISSUE_TEMPLATE folder, such as issue templates or a config.yml
  file, none of the contents of the default .github/ISSUE_TEMPLATE folder will
  be used.`
- `conventional-pre-commit` latest release is `v4.4.0`, published 2026-02-18.
  Its manifest declares `stages: [commit-msg]`.

## Unverified

Whether default community health files from a public `.github` repo reach
**private** repos owned by the same account.

GitHub's docs restrict the visibility of the `.github` repo itself but state no
visibility requirement on the target repos, and community reports say private
repos do inherit. That is inference, not confirmation. Most of the ~40 repos
are private, so this is load-bearing and gets an empirical test before anything
is published. See Risks.

## Design

### 1. CLAUDE.md

Replace lines 26-33. The rigor and voice bullets stay global. Only the sign-off
gate is scoped.

```markdown
## Outward-Facing Writing

Applies to anything that leaves our workspace - bug reports, issues, PR
descriptions, comments, emails.

- File on a reproduction, not a conviction. Before reporting a bug, confirm it
  with a concrete, minimal repro I could hand a stranger. Can't reproduce it?
  Say so and don't file.
- Separate confirmed from suspected. State observations as fact; state
  mechanism as inference, and only once it's isolated. Don't assert a root
  cause we haven't nailed down.
- Plain human voice, not model voice. Short sentences. No em-dash pile-ups, no
  rule-of-three cadence, no "Notably / It's worth noting," minimal bolding, no
  grandiose closers. Terse and specific reads as competent; polished-and-hedged
  reads as AI.

**Sign-off gate - projects I don't own.** For upstream issues, third-party PRs,
and comments on repos outside `hmesfin/*`: draft -> show me -> file. Never post
without my sign-off.

On my own repos, file directly. The PR and issue templates carry the rules
above - fill them honestly instead of asking me to approve.
```

Rationale for keeping bullets 1-3 global: they are the `No AI Slop` rules
applied to writing. They cost nothing on owned repos and most writing lands
there. Only the fourth bullet created the friction.

### 2. Source of truth

```
claude-config/
  github-templates/
    PULL_REQUEST_TEMPLATE.md
    ISSUE_TEMPLATE/
      01-bug.yml
      02-feature.yml
      config.yml
    pre-commit-snippet.yaml
    README.md
  publish-github-templates.sh
```

`github-templates/` is canonical. Nothing is authored directly in the published
repo.

### 3. PR template

Four fields. Only what cannot be reconstructed from the diff.

```markdown
## What & why
<!-- one or two lines -->

## Verified
<!-- what I actually ran or checked. Untested? say so here. -->

## Risk
<!-- blast radius, migrations, rollback. "none" is valid. -->

## Notes
<!-- follow-ups, deferred work -->
```

`Verified` is load-bearing. It forces the confirmed-vs-suspected split into
every PR, which is the substitute for the sign-off gate.

Rejected: a checklist variant (tests written, lint clean, migrations reviewed).
On solo repos checkboxes get ticked reflexively and stop carrying information.

### 4. Issue forms

YAML forms, not markdown. Forms support required fields; markdown templates can
be deleted and replaced with freeform text, which is the failure mode being
fixed.

- `01-bug.yml` - required: repro steps, expected, actual, environment. The
  required repro field enforces `file on a reproduction` at GitHub's validator
  instead of relying on the rule being remembered.
- `02-feature.yml` - required: problem, proposed solution, scope.
- `config.yml` - `blank_issues_enabled: true`, so quick personal notes stay
  possible.

### 5. Publishing

`publish-github-templates.sh` clones or updates `hmesfin/.github`, copies
`github-templates/` contents into its `.github/` directory excluding
`pre-commit-snippet.yaml` and `README.md`, commits, pushes.

The `.github` repo is public and world-readable. Templates must contain no
client names, no internal process detail, no infrastructure specifics.

Creating the public repo is an outward-facing action and gets explicit
confirmation before it happens, independent of the sign-off gate change.

### 6. Commit enforcement

Appended to each of the 21 existing `.pre-commit-config.yaml` files:

```yaml
default_install_hook_types: [pre-commit, commit-msg]

repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert]
```

`stages: [commit-msg]` is set explicitly even though the hook manifest declares
it, because the existing configs set `default_stages: [pre-commit]` at the top
level and the precedence between manifest stages and config-level
`default_stages` is ambiguous. Setting it explicitly is correct under either
precedence rule.

`default_install_hook_types` makes a plain `pre-commit install` wire both the
pre-commit and commit-msg stages. Without it, `pre-commit install` installs
only the pre-commit stage, the config looks correct, `pre-commit run
--all-files` passes, and no commit message is ever validated. Silent no-op.

`--strict` is not enabled, so merge and revert commits still pass.

Rollout is one repo at a time. Each repo is verified with a real rejected
commit and a real accepted commit before moving to the next.

## Rejected alternatives

- **`~/.gitmessage` + `git config commit.template`.** Only populates the editor
  buffer. Does nothing for `git commit -m`, which is how Claude and CI commit.
  Would standardize hand-written commits and miss the majority.
- **`commitizen` (the Python `cz` tool).** Heavier, interactive-first, fights
  automation. Its version-bump and changelog features are not needed yet.
- **`commitlint` + `husky`.** JavaScript-only toolchain. Wrong fit for a
  polyglot stack that is mostly Django, FastAPI, Flutter, and React Native.
- **A Claude Code plugin.** Plugins deliver skills and commands to Claude. They
  do not place files in GitHub repos. Wrong mechanism.
- **Per-repo sync script as the primary path.** Requires seeding ~40 repos and
  produces drift on every template change. Retained only as the fallback if the
  private-inheritance test fails.
- **Scope allowlists on commit types.** Would improve changelog grouping but
  requires a curated scope list per repo, and a new scope would have to be
  configured before it could be committed.

## Risks

- **Private repos may not inherit defaults.** Load-bearing and unverified.
  Tested empirically before publishing. If it fails, the same
  `github-templates/` directory feeds a per-repo sync script instead; the
  layout does not change, so the work is not stranded.
- **Public `.github` repo leaks template content.** Mitigated by keeping
  templates generic.
- **All-or-nothing `ISSUE_TEMPLATE` override.** A repo adding one custom form
  loses all defaults. Documented in `github-templates/README.md`.
- **Commit hook rejects mid-flow.** Real friction when a message is 90% right.
  Accepted deliberately; history is already ~95% conventional.
- **Dropping the sign-off gate.** Approved. Reversible by editing one paragraph
  of CLAUDE.md if PR quality drops.

## Success criteria

- Opening a PR on a private `hmesfin/*` repo with no local template
  pre-populates the four-field body.
- Filing an issue offers the bug and feature forms plus a blank option, and the
  bug form refuses to submit without a repro.
- `git commit -m "fixed the thing"` fails in a rolled-out repo.
- `git commit -m "fix(api): handle null tenant"` succeeds.
- A fresh `git clone` plus `pre-commit install` wires the commit-msg stage with
  no extra flags.
