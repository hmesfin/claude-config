# Claude Configuration Management

This repository manages Claude Code agents, hooks, commands, and global instructions across multiple development machines.

## 🚀 Quick Setup (New Machine)

```bash
# 1. Clone the repository
cd ~
git clone git@github.com:hmesfin/claude-config.git

# 2. Run the symlink setup script
cd claude-config
./setup-claude-symlinks.sh
```

That's it! Your `~/.claude/` directory now points to this repository.

## 📁 Repository Structure

```
claude-config/
├── agents/                    # Claude Code specialized agents (20+ agents)
│   ├── Backend Architects
│   │   ├── django-tdd-architect.md
│   │   ├── fastapi-tdd-architect.md
│   │   ├── django-data-architect.md
│   │   └── fastapi-data-architect.md
│   ├── Frontend Architects
│   │   ├── vue-tdd-architect.md
│   │   └── react-native-tdd-architect.md
│   ├── Mobile Development (React Native)
│   │   ├── mobile-data-architect.md
│   │   ├── mobile-security-architect.md
│   │   ├── mobile-performance-optimizer.md
│   │   ├── mobile-realtime-architect.md
│   │   ├── native-module-tdd-engineer.md
│   │   └── expo-deployment-agent.md
│   ├── Security Architects
│   │   ├── django-security-architect.md
│   │   ├── fastapi-security-architect.md
│   │   └── security-tdd-architect.md
│   ├── Deployment Agents
│   │   ├── django-vue-staging-agent.md
│   │   ├── fastapi-vue-staging-agent.md
│   │   └── expo-deployment-agent.md
│   └── Infrastructure & Performance
│       ├── async-tdd-architect.md
│       ├── realtime-tdd-architect.md
│       ├── performance-tdd-optimizer.md
│       ├── devops-tdd-engineer.md
│       ├── observability-tdd-engineer.md
│       ├── data-tdd-architect.md
│       ├── tdd-test-specialist.md
│       └── project-orchestrator.md
├── agents/                    # Claude Code specialized agents (20+ agents)
├── hooks/                     # Git-style hooks for Claude Code
├── commands/                  # Custom slash commands
├── skills/                    # Development standards and patterns
├── mcp-servers/               # MCP server configurations
├── docs/                      # Project documentation
│   ├── GH_MCP_IDEAS.md       # GitHub MCP automation ideas
│   ├── P0_IMPLEMENTATION.md  # P0 features documentation
│   ├── P1_IMPLEMENTATION.md  # P1 features documentation
│   ├── P2_IMPLEMENTATION.md  # P2 features documentation
│   ├── DOCKER_WORKFLOW.md    # Docker workflow guide
│   ├── MULTI_MACHINE_SETUP.md # Multi-machine sync guide
│   ├── ROADMAP.md            # Project roadmap
│   ├── STAGING_DEPLOYMENT.md # Traefik staging deployment guide
│   └── archive/              # Historical documentation
├── .claude/                   # Project-specific Claude Code settings
├── CLAUDE.md                  # Global instructions (symlinked to ~/.claude/CLAUDE.md)
├── setup-claude-symlinks.sh   # Symlink setup script
└── README.md                  # This file
```

## 🔄 Workflow

### On Your Main Development Machine

1. **Make changes** to agents, hooks, or commands in this repo
2. **Test** your changes
3. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update agent configurations"
   git push
   ```

### On Other Machines (WSL, servers, etc.)

Simply pull the latest changes:

```bash
cd ~/claude-config
git pull
```

Changes are **instantly available** in `~/.claude/` thanks to symlinks!

### Global settings (`~/.claude/settings.json`)

This one is **not** symlinked, on purpose. Claude Code writes an
`autoMode.environment` block into it on its own, and that block records
filesystem paths, private repo names, and where secrets live. **This repo is
public.** A symlink would eventually push all of that to GitHub with nobody
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
anything sensitive survived. The filter is enforced, not trusted.

Install the pre-commit guard so a bad `global-settings.json` can't be
committed at all:

```bash
ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
```

## 🎯 Specialized Agents

### Backend Development
- **django-tdd-architect** - Django REST Framework with TDD
- **fastapi-tdd-architect** - FastAPI async backend with TDD
- **django-data-architect** - Django ORM, PostgreSQL, caching
- **fastapi-data-architect** - SQLAlchemy 2.0 async, Alembic migrations

### Security
- **django-security-architect** - DRF permissions, Django RBAC
- **fastapi-security-architect** - OAuth2/JWT, dependency-based auth
- **mobile-security-architect** - Biometric auth, secure storage, mobile RBAC

### Frontend Development
- **vue-tdd-architect** - Vue 3 Composition API with Vitest
- **react-native-tdd-architect** - React Native with Jest & Testing Library

### Mobile Development (React Native)
- **mobile-data-architect** - Offline-first data, sync strategies, WatermelonDB
- **mobile-security-architect** - Biometric, Keychain/Keystore, JWT
- **mobile-performance-optimizer** - Startup time, FPS, memory, bundle size
- **mobile-realtime-architect** - WebSocket, chat, live tracking
- **native-module-tdd-engineer** - Native bridges (iOS Swift, Android Kotlin)
- **expo-deployment-agent** - EAS Build/Update, App Store/Play Store

### Infrastructure & Performance
- **async-tdd-architect** - Celery tasks and background jobs
- **realtime-tdd-architect** - WebSockets, Django Channels
- **performance-tdd-optimizer** - Performance optimization (web)
- **devops-tdd-engineer** - Docker, CI/CD, infrastructure
- **observability-tdd-engineer** - Monitoring, logging, alerting

### Deployment
- **django-vue-staging-agent** - Django+Vue.js Traefik deployment
- **fastapi-vue-staging-agent** - FastAPI+Vue.js Traefik deployment
- **expo-deployment-agent** - React Native EAS Build & submission

## 📝 Adding New Content

### Adding a New Agent

1. Create the agent file in `agents/`:
   ```bash
   cd ~/claude-config/agents
   nano my-new-agent.md
   ```

2. Commit and push:
   ```bash
   git add agents/my-new-agent.md
   git commit -m "Add my-new-agent for XYZ tasks"
   git push
   ```

3. The agent is immediately available in `~/.claude/agents/` on all machines after `git pull`

### Adding a New Hook

1. Create hook in `hooks/`:
   ```bash
   cd ~/claude-config/hooks
   nano my-hook.sh
   chmod +x my-hook.sh
   ```

2. Commit and push (same as above)

### Adding a New Slash Command

1. Create command in `commands/`:
   ```bash
   cd ~/claude-config/commands
   nano my-command.md
   ```

2. Commit and push (same as above)

## 🔧 Troubleshooting

### Symlinks Not Working?

Check if symlinks exist:
```bash
ls -la ~/.claude/
```

You should see entries like:
```
agents -> /home/hmesfin/claude-config/agents
hooks -> /home/hmesfin/claude-config/hooks
...
```

### Re-run Setup

If something goes wrong, you can re-run the setup:
```bash
cd ~/claude-config
./setup-claude-symlinks.sh
```

Your old `~/.claude/` will be backed up automatically.

### Restore Backup

If you need to restore a backup:
```bash
ls ~/.claude.backup.*  # List available backups
rm -rf ~/.claude
mv ~/.claude.backup.YYYYMMDD_HHMMSS ~/.claude
```

## 🎨 Philosophy

- **Single Source of Truth**: This Git repository is the canonical source
- **No Manual Copying**: Symlinks ensure instant sync across machines
- **Version Control**: All changes tracked in Git
- **Easy Rollback**: `git checkout` to revert any change
- **TDD Everything**: All agents enforce test-first development
- **Framework-Specific**: Specialized agents for Django, FastAPI, Vue.js, and React Native
- **Full-Stack Coverage**: Backend (Django/FastAPI) + Web (Vue.js) + Mobile (React Native)
- **<500 Line Limit**: All agents enforce file size constraints for maintainability

## 📚 Documentation

### Core Documentation
- [Global Instructions](CLAUDE.md) - Default behavior for all projects (symlinked to ~/.claude/)
- [Development Standards](skills/DEVELOPMENT_STANDARDS.md) - Mandatory coding standards
- [Docker Workflow](docs/DOCKER_WORKFLOW.md) - Docker development workflow
- [Multi-Machine Setup](docs/MULTI_MACHINE_SETUP.md) - Sync across machines

### Deployment Guides
- [Staging Deployment](docs/STAGING_DEPLOYMENT.md) - Traefik multi-tenant setup

### GitHub MCP Automation
- [GitHub MCP Ideas](docs/GH_MCP_IDEAS.md) - Automation enhancement roadmap
- [P0 Implementation](docs/P0_IMPLEMENTATION.md) - Critical features (Auto-Progress, Test Coverage)
- [P1 Implementation](docs/P1_IMPLEMENTATION.md) - High-value features (Code Review, Velocity, Dependencies)
- [P2 Implementation](docs/P2_IMPLEMENTATION.md) - Nice-to-have features (Release Notes, Risk Alerts, Batching)
- [Roadmap](docs/ROADMAP.md) - Overall project roadmap

## 🤝 Contributing

This is a personal configuration repo, but if you're collaborating:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a PR

## 📄 License

Personal configuration - use at your own discretion.
