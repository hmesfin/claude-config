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
├── agents/                    # Claude Code specialized agents
│   ├── Backend Architects
│   │   ├── django-tdd-architect.md
│   │   └── fastapi-tdd-architect.md
│   ├── Data Architects
│   │   ├── django-data-architect.md
│   │   └── fastapi-data-architect.md
│   ├── Security Architects
│   │   ├── django-security-architect.md
│   │   └── fastapi-security-architect.md
│   ├── Deployment Agents
│   │   ├── django-vue-staging-agent.md
│   │   └── fastapi-vue-staging-agent.md
│   └── Other Specialized Agents
│       ├── vue-tdd-architect.md
│       ├── async-tdd-architect.md
│       ├── performance-tdd-optimizer.md
│       └── ...
├── hooks/                     # Git-style hooks for Claude Code
├── commands/                  # Custom slash commands
├── CLAUDE.md                  # Global instructions for all projects
├── STAGING_DEPLOYMENT.md      # Traefik staging deployment guide
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

## 🎯 Specialized Agents

### Backend Development
- **django-tdd-architect** - Django REST Framework with TDD
- **fastapi-tdd-architect** - FastAPI async backend with TDD

### Data Architecture
- **django-data-architect** - Django ORM, PostgreSQL, caching
- **fastapi-data-architect** - SQLAlchemy 2.0 async, Alembic migrations

### Security
- **django-security-architect** - DRF permissions, Django auth
- **fastapi-security-architect** - OAuth2/JWT, dependency injection

### Deployment
- **django-vue-staging-agent** - Django+Vue.js Traefik deployment
- **fastapi-vue-staging-agent** - FastAPI+Vue.js Traefik deployment

### Frontend & Full-Stack
- **vue-tdd-architect** - Vue 3 Composition API with Vitest
- **async-tdd-architect** - Celery tasks and background jobs
- **performance-tdd-optimizer** - Performance optimization
- **devops-tdd-engineer** - Docker, CI/CD, infrastructure

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
- **Framework-Specific**: Specialized agents for Django and FastAPI patterns

## 📚 Documentation

- [Staging Deployment Guide](STAGING_DEPLOYMENT.md) - Traefik multi-tenant setup
- [Global Instructions](CLAUDE.md) - Default behavior for all projects

## 🤝 Contributing

This is a personal configuration repo, but if you're collaborating:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a PR

## 📄 License

Personal configuration - use at your own discretion.
