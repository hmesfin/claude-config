# Claude Configuration Management

Claude Code hooks, commands, skills, and global instructions, shared across
development machines by symlinking `~/.claude/` into this repo.

## 🚀 Quick Setup (New Machine)

```bash
# 1. Clone the repository
cd ~
git clone git@github.com:hmesfin/claude-config.git

# 2. Run the symlink setup script
cd claude-config
./setup-claude-symlinks.sh

# 3. Apply the global settings (not symlinked - see below)
python3 scripts/sync-settings.py --push
ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
```

## 📁 Repository Structure

```
claude-config/
├── CLAUDE.md                  # Global instructions (symlinked to ~/.claude/CLAUDE.md)
├── global-settings.json       # Shared ~/.claude/settings.json, synced explicitly
├── ruff.toml                  # indent-width = 2, matching CLAUDE.md
├── agents/                    # Empty. See "Agents" below
├── agents-archive/            # 26 retired agent definitions, kept for reference
├── commands/                  # Slash commands: deploy-staging, deploy-production, generate-legal
├── hooks/                     # docker-command-guard, post-tool-use/auto-progress-tracker
├── skills/                    # playwright-cli, plus standards docs
├── mcp-servers/               # MCP server configs (currently empty)
├── scripts/                   # sync-settings.py, pre-commit, voice_metrics.py
├── github-actions/            # Reusable workflow definitions
├── github-templates/          # Canonical PR and issue templates
├── docs/                      # Guides, plans, specs, and archived history
├── improvements/              # Proposals not yet acted on
├── .claude/                   # Settings for working *in this repo*
└── setup-claude-symlinks.sh   # Symlink setup script
```

## 🔄 Workflow

### Symlinked directories

`agents/`, `hooks/`, `commands/`, `skills/`, `mcp-servers/`, and `CLAUDE.md`
are symlinked into `~/.claude/`. Edit here, commit, push. On another machine,
`git pull` and the changes are live immediately.

### Global settings (`~/.claude/settings.json`)

This one is **not** symlinked, on purpose. Claude Code writes an
`autoMode.environment` block into it on its own, and that block records
filesystem paths, private repo names, and where secrets live. This repo is
public. A symlink would eventually push all of that to GitHub with nobody
watching.

So it syncs explicitly instead, through `global-settings.json`:

```bash
# after changing settings locally (plugins, permissions, hooks)
python3 scripts/sync-settings.py --pull    # live -> repo, machine keys stripped

# on a new machine, after git pull
python3 scripts/sync-settings.py --push    # repo -> live, local recon preserved

python3 scripts/sync-settings.py --check   # verify the tracked copy is clean
```

`--pull` strips `autoMode`, then re-scans what's left and refuses to write if
anything sensitive survived. The filter is enforced, not trusted. The
pre-commit hook runs the same check before any commit that touches
`global-settings.json`.

## 🪝 Hooks

Wired in `global-settings.json`:

- **docker-command-guard.py** (PreToolUse, Bash) - blocks `python manage.py`
  and dev servers that belong in Docker, and points at the
  `docker compose exec -T <service> /entrypoint` form. `startapp` still runs
  locally, for file ownership.
- **post-tool-use/auto-progress-tracker.py** (PostToolUse, Bash) - on a commit
  containing `fixes #N`, closes the issue, posts a progress comment, and
  unlocks dependent issues.

Hooks receive their payload as JSON on **stdin**. Anything reading
`$CLAUDE_TOOL_INPUT` or `$CLAUDE_FILE_PATHS` silently does nothing, because
those variables are not set. Four hooks were deleted for this reason.

## 🧩 Agents

`agents/` is empty. The 26 definitions that used to live there are in
`agents-archive/`.

Session transcripts over five weeks showed 22 of them had never been
dispatched, and the remaining four accounted for 92 dispatches against 1,502
to `general-purpose`, nearly all from two sessions in a single project. They
also cost roughly 1,600 tokens of system prompt per session and still
mandated test-first with no logic/scaffolding distinction, which contradicts
CLAUDE.md.

Restore any of them with `git mv agents-archive/<name>.md agents/`.

## 📝 Adding New Content

Create the file in the matching directory, commit, push. It is live in
`~/.claude/` on every machine after `git pull`.

- **Hook**: `hooks/my-hook.py`, `chmod +x`, then wire it in `global-settings.json`
  and `--pull`. Read the payload from stdin.
- **Command**: `commands/my-command.md`
- **Skill**: `skills/my-skill/SKILL.md`. A loose `.md` in `skills/` is a
  document, not a skill; only `<name>/SKILL.md` is loaded.

## 🔧 Troubleshooting

### Symlinks not working?

```bash
ls -la ~/.claude/
```

You should see entries like:

```
agents -> /home/<you>/claude-config/agents
hooks -> /home/<you>/claude-config/hooks
```

### Re-run setup

```bash
cd ~/claude-config
./setup-claude-symlinks.sh
```

Your old `~/.claude/` is backed up automatically.

### Restore a backup

```bash
ls ~/.claude.backup.*
rm -rf ~/.claude
mv ~/.claude.backup.YYYYMMDD_HHMMSS ~/.claude
```

`sync-settings.py --push` also backs up `~/.claude/settings.json` before
writing, as `settings.json.bak-<timestamp>`.

## 🎨 Philosophy

- **Single source of truth**: this repository is canonical for everything
  except the machine-specific half of `settings.json`
- **Earn your place**: config that has never run gets deleted, not kept
  because it might be useful someday
- **Match the ceremony to the job**: heavyweight process on request, not by
  default. See the Process Weight section of CLAUDE.md
- **Tests first where there is logic**, not everywhere
- **Public repo**: nothing here should name a private repo, a filesystem
  path, or where secrets live

## 📚 Documentation

- [Global Instructions](CLAUDE.md) - default behavior for all projects
- [Development Standards](skills/DEVELOPMENT_STANDARDS.md) - coding standards
- [Docker Workflow](docs/DOCKER_WORKFLOW.md) - Docker development workflow
- [Multi-Machine Setup](docs/MULTI_MACHINE_SETUP.md) - sync across machines
- [Staging Deployment](docs/STAGING_DEPLOYMENT.md) - Traefik multi-tenant setup

### Historical

`docs/P0_IMPLEMENTATION.md` through `P2_IMPLEMENTATION.md`, `docs/ROADMAP.md`,
and `docs/GH_MCP_IDEAS.md` describe a GitHub project-management command suite
that has since been removed. They are kept as history and do not describe
current behavior.
