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
- The account holds 161 repos: 130 private, 31 public. An earlier figure of
  ~40 in this document's first draft came from a truncated listing and was
  wrong.

### Private repos DO inherit defaults from a public `.github` repo

Tested 2026-08-03 after publishing a sentinel `PULL_REQUEST_TEMPLATE.md` to
`hmesfin/.github`.

    $ gh api repos/hmesfin/cli-crawler/community/profile \
        --jq '.files | {pull_request_template, issue_template}'
    {"issue_template":null,
     "pull_request_template":{
       "html_url":"https://github.com/hmesfin/.github/blob/main/.github/PULL_REQUEST_TEMPLATE.md",
       ...}}

`cli-crawler` is private and has no `.github` directory of its own. GitHub's
own community-profile endpoint resolves its pull request template to the file
in the public `.github` repo. The same result was returned for the public repo
`yt-dlp-tui`.

`issue_template` returning `null` in the same response is the control: only the
PR template had been pushed at that point, so the endpoint is reporting actual
resolved state rather than echoing the request.

### The community-profile API does not report issue form directories

Tested 2026-08-03. After pushing `ISSUE_TEMPLATE/` with three files,
`community/profile` still returns `issue_template: null` - including for
`hmesfin/.github` itself, where `gh api .../contents/.github/ISSUE_TEMPLATE`
lists all three files.

That field only tracks a legacy single `ISSUE_TEMPLATE.md`. A null there is an
API blind spot and says nothing about whether issue forms work. Do not use this
endpoint to check forms.

### Issue forms validate against GitHub's published schema

Both `01-bug.yml` and `02-feature.yml` validate clean against
`https://www.schemastore.org/github-issue-forms.json` using `jsonschema`
Draft 7.

This matters because a malformed form is not an error - GitHub silently omits
it from the chooser. Schema validation is the check that covers that failure
mode without needing the UI. Worth re-running after any template edit:

    curl -sSL -o /tmp/gh-forms.json https://www.schemastore.org/github-issue-forms.json
    # then validate each ISSUE_TEMPLATE/*.yml against it with jsonschema

Note the `-L`. `json.schemastore.org` 302s to `www.schemastore.org`; without
`-L` you silently get a 174-byte HTML redirect stub instead of the schema.

### Issue forms confirmed working end to end

`hmesfin/yt-dlp-tui#6`, filed 2026-08-03 by the repo owner through the
inherited Bug report form. `yt-dlp-tui` has no `.github/ISSUE_TEMPLATE` of its
own, so the form was inherited from `hmesfin/.github`.

Confirmed by the resulting issue body:

- The chooser rendered and the Bug report form was reachable.
- All five fields rendered with the expected headings.
- `labels: ["bug"]` was applied automatically.
- `Suspected cause` was skippable and emitted `_No response_`, which is what
  GitHub writes for an unfilled optional field. The optional/required split
  works as designed.

## Unverified

1. **Required fields blocking submission.** Issue #6 had every required field
   filled, so the validator was never exercised. Schema validation proves
   `required: true` is correctly declared; nothing yet proves GitHub refuses a
   submission without a repro. Check: open the Bug report form, leave "Steps to
   reproduce" empty, attempt to submit, then cancel out.
2. **PR body prefill.** The community-profile endpoint proves GitHub resolves
   the inherited PR template; it does not prove the compose form populates from
   it. Check: open any `hmesfin/*` compare URL with `?expand=1` and look at the
   description box.

Both need an authenticated browser session - anonymous requests to either page
redirect to `/login`.

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

The `Verified` section of a PR is bound by the No AI Slop rules. Write only
what was actually run or checked. "Not tested" and "untested beyond type
check" are acceptable values; a claim that something passed when it was not
run is the failure this whole arrangement is built to prevent.
```

Rationale for keeping bullets 1-3 global: they are the `No AI Slop` rules
applied to writing. They cost nothing on owned repos and most writing lands
there. Only the fourth bullet created the friction.

The final paragraph is Level 1 of section 7 and is part of this change, not a
later addition.

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

See section 7 for the limits of what this field can guarantee.

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

`--strict` is not enabled. Per the hook's own help text it "Disallows fixup!
and merge commits", so leaving it off exempts merges and autosquash prefixes.
It has nothing to do with reverts.

Accept/block boundaries, established 2026-08-03 by running the hook binary
directly against sample messages:

| Message | Result |
|---|---|
| `fix(api): handle null tenant` | pass |
| `Revert "fix(api): handle null tenant"` (git default) | **block** |
| `revert: fix(api): handle null tenant` | pass |
| `Merge branch main into feature/x` | pass |
| `Merge pull request #12 from hmesfin/feat` | pass |
| `fixup! fix(api): handle null tenant` | pass |
| `fixed the thing` | block |
| `[deploy]` | **block** |

Two consequences worth knowing before rollout:

**`git revert <sha>` will fail the hook.** Git generates `Revert "original
message"`, which is not conventional format. There is no revert exemption in
the source - `is_merge()` and `has_autosquash_prefix()` are the only bypasses.
Reverting means rewriting the message as `revert: <thing>`, or using
`--no-verify`. Rewriting is preferable: `revert:` is a real conventional type
and makes reverts greppable in history.

**The `[deploy]` marker style is blocked.** `gojjotech-website` has commits
titled `[deploy]` and bare `[deploy]` will not pass. Where the marker is a
suffix on an otherwise conventional message
(`chore(case studies): added images [deploy]`) it passes fine, since the check
is on the prefix.

Rollout is one repo at a time. Each repo is verified with a real rejected
commit and a real accepted commit before moving to the next.

### Rollout result, 2026-08-03

15 of 21 repos are fully enforcing: hook in config, `commit-msg` in
`default_install_hook_types`, and `.git/hooks/commit-msg` present. Each was
verified with a real rejected commit and a real accepted commit.

Six were skipped because they had uncommitted work, and committing in them
would have bundled unrelated changes: `data-imports` (left deliberately for the
owner), `djvufl-rentkee`, `etbiz`, `invoicing-service`, `p7`, `team-gojjo-mvp`.

`add-commit-hook.py` in this repo performs the insertion. It works at the text
level so comments and formatting survive, reparses to verify, and refuses to
write if anything looks wrong. Run it, then `pre-commit install`, then test a
rejection before trusting it.

### Most repos had pre-commit configured but never installed

Found during rollout: only 6 of the 21 repos had a `pre-commit` hook in
`.git/hooks/`. The other 15 carried a `.pre-commit-config.yaml` while running
nothing on commit - ruff, formatting, none of it.

Hooks live in `.git/hooks/`, which is local and never cloned, so a fresh clone
starts with no hooks regardless of what the config says. A committed config is
a declaration; the installed hook is the enforcement. They look identical in
review and `pre-commit run --all-files` passes either way.

All 15 rolled-out repos now have both stages installed, which also switches on
the lint hooks that were previously inert. Expect commits to start failing on
lint issues that used to pass.

### 7. The `Verified` field cannot enforce itself

The design leans on the `Verified` field to replace the sign-off gate. That
substitution has a hole, and it is recorded here rather than left implicit.

A PR template is a prompt, not a validator. GitHub's issue forms can require a
repro field because the form is submitted through GitHub's own validator. There
is no equivalent for PR bodies. Nothing stops `Verified: ran the tests` from
being written by an agent that did not run the tests.

This matters more than a normal template gap. If the field reads as diligence
without being diligence, it is worse than the gate it replaced, because the
gate at least put a human in the path.

Three levels of response, in increasing strength and cost:

**Level 1 - tie it to the existing rigor rules.** Add a line to CLAUDE.md
stating that `Verified` in a PR body is bound by the `No AI Slop` rules:
unverified claims must be labelled as such, and `not tested` is an acceptable
value. Zero infrastructure. Enforces nothing mechanically; relies on the same
rules that govern every other claim.

**Level 2 - CI presence check.** A workflow fails the PR when the `Verified`
section is empty or still contains the unedited placeholder comment.
Centralized as a reusable workflow in `hmesfin/.github`, called by a small stub
in each repo:

```yaml
jobs:
  verify:
    uses: hmesfin/.github/.github/workflows/pr-verify.yml@main
```

Public reusable workflows can be called by private repos. Note this is a
different mechanism from default community health files: templates are
inherited with no per-repo file, workflows are not, so every repo needs its own
stub committed.

Honest limit: this catches an unedited or empty field. It does not and cannot
catch a false claim. It raises the cost of laziness, not the cost of lying.

**Level 3 - invert the direction.** Stop asking the author to assert and have
CI report. A workflow runs the test suite and posts results as a PR comment or
check, so anything written under `Verified` can be read against machine output.
This is the only option that actually binds, because it produces evidence
independent of the author.

Cost: real work per stack. The repos span Django, FastAPI, Vue, React Native,
and Flutter, with different test commands and different CI maturity. Several
already have workflows that run tests, so for those it is closer to surfacing
existing output than building new pipelines.

**Decision: Level 1 now, Level 3 later, Level 2 skipped.**

Level 2 is skipped deliberately. It adds a per-repo file and a CI failure mode
while defending only against the case least likely to occur - the placeholder
left untouched is obvious on sight during review. It buys the appearance of
enforcement without the substance, which is the exact failure this section
exists to name.

Level 3 is the correct end state but is a separate project with its own spec,
scoped per stack. It is not blocked by anything here.

Until Level 3 exists, `Verified` is a good-faith field governed by the rigor
rules, and that limitation is understood rather than papered over.

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

- ~~**Private repos may not inherit defaults.**~~ Resolved 2026-08-03. They do.
  See Verified facts. The sync-script fallback is no longer needed.
- **Public `.github` repo leaks template content.** Mitigated by keeping
  templates generic.
- **All-or-nothing `ISSUE_TEMPLATE` override.** A repo adding one custom form
  loses all defaults. Documented in `github-templates/README.md`.
- **Commit hook rejects mid-flow.** Real friction when a message is 90% right.
  Accepted deliberately; history is already ~95% conventional.
- **Dropping the sign-off gate.** Approved. Reversible by editing one paragraph
  of CLAUDE.md if PR quality drops.
- **`Verified` is unenforceable until Level 3.** The field that replaces the
  gate is good-faith only. See section 7. This is the largest known weakness in
  the design and is accepted knowingly, not overlooked. The tripwire: if a
  `Verified` claim is ever found to be false, that is the signal to build Level
  3 rather than to re-add the gate.

## Success criteria

- Opening a PR on a private `hmesfin/*` repo with no local template
  pre-populates the four-field body.
- Filing an issue offers the bug and feature forms plus a blank option, and the
  bug form refuses to submit without a repro.
- `git commit -m "fixed the thing"` fails in a rolled-out repo.
- `git commit -m "fix(api): handle null tenant"` succeeds.
- A fresh `git clone` plus `pre-commit install` wires the commit-msg stage with
  no extra flags.

Explicitly not a success criterion: mechanical enforcement of `Verified`. That
is out of scope by the decision in section 7.

## Follow-on work

`Verified` Level 3 - CI reports test results into the PR so the field can be
read against machine output. Separate spec, scoped per stack (Django, FastAPI,
Vue, React Native, Flutter). Not blocked by anything in this design.
