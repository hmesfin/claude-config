# Claude Code Skills Directory

## Purpose

The `skills/` directory contains reference documentation that codifies the mandatory development standards Claude Code MUST follow. Unlike agents (which are specialized execution units) and commands (which are executable operations), skills define the **rules and standards** that govern all development work.

## Directory Structure

```
skills/
├── README.md                    # This file
└── DEVELOPMENT_STANDARDS.md     # Complete development standards reference
```

## What Are Skills?

Skills are **knowledge documents** that:

1. **Codify standards** - Define mandatory rules that Claude Code must follow
2. **Reference documentation** - Extracted from 26+ specialized agents into one source of truth
3. **Quick reference** - Fast lookup for standards without parsing agent prompts
4. **Consistency enforcement** - Single source of truth prevents conflicting guidance

## Skills vs. Agents vs. Commands vs. Hooks

| Component | Purpose | Type | Example |
|-----------|---------|------|---------|
| **Skills** | Define standards | Documentation | `DEVELOPMENT_STANDARDS.md` |
| **Agents** | Execute specialized tasks | Execution units | `django-tdd-architect.md` |
| **Commands** | Perform operations | Executable scripts | `/lint-and-format` |
| **Hooks** | Enforce rules | Prevention scripts | `docker-command-guard.py` |

### Relationship

```
Skills (define standards)
   ↓
Agents (implement standards in specialized tasks)
   ↓
Commands (automate standard operations)
   ↓
Hooks (prevent standard violations)
```

## Available Skills

### DEVELOPMENT_STANDARDS.md

Comprehensive reference covering:

1. **Core TDD Philosophy** - RED-GREEN-REFACTOR cycle, test coverage requirements
2. **File Organization Rules** - 500-line limit, directory structures for Django/Vue/React Native
3. **TypeScript Quality Standards** - 8 battle-tested rules from 584→111 error reduction
4. **Docker Workflow Requirements** - What to run locally vs. in Docker
5. **Code Quality Gates** - Pre-commit quality checks
6. **Testing Standards** - Test categories, organization, patterns
7. **Git Commit Standards** - Commit format, safety protocol

## How to Use Skills

### For Claude Code

When working on any task:

1. **Before starting**: Reference `DEVELOPMENT_STANDARDS.md` for applicable standards
2. **During development**: Follow TDD workflow, file organization rules
3. **Before committing**: Run quality gates, verify TypeScript standards
4. **When stuck**: Reference skills for clarification

### For Specialized Agents

Agents implement standards from this directory:

- `django-tdd-architect` implements Django standards from `DEVELOPMENT_STANDARDS.md`
- `vue-tdd-architect` implements Vue.js standards from `DEVELOPMENT_STANDARDS.md`
- All agents reference the same source of truth

### For Users

Quick reference for:

- Understanding what standards Claude Code follows
- Customizing standards for your projects
- Training new team members on your workflow

## Updating Skills

When updating standards:

1. **Update skill document** in `skills/` directory
2. **Update related agents** to reflect new standards
3. **Update hooks** if enforcement changes
4. **Test changes** in a project to verify consistency
5. **Document changes** in git commit

## Future Skills

Potential additional skills to add:

- `API_DESIGN_STANDARDS.md` - REST/GraphQL API design patterns
- `DATABASE_STANDARDS.md` - Schema design, migration patterns
- `SECURITY_STANDARDS.md` - Security testing, RBAC patterns
- `PERFORMANCE_STANDARDS.md` - Query optimization, caching strategies
- `DEPLOYMENT_STANDARDS.md` - CI/CD, staging/production patterns

## Benefits

1. **Single Source of Truth** - Standards defined once, referenced everywhere
2. **Faster Onboarding** - New agents/users reference one document
3. **Consistency** - All agents follow same standards
4. **Maintainability** - Update standards in one place
5. **Discoverability** - Easy to find what standards apply

## Related Documentation

- `agents/` - Specialized agent prompts (implement skills)
- `commands/` - Slash commands (automate skills)
- `hooks/` - Hooks (enforce skills)
- `CLAUDE.md` - Global user preferences
- `README.md` - Repository overview
