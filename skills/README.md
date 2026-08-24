# Skills Directory

This directory holds two different kinds of thing, and the distinction matters.

## Skills that Claude Code loads

A skill is a directory containing `SKILL.md` with YAML frontmatter (`name`,
`description`). Claude Code discovers those and offers them for invocation.

```
skills/
└── playwright-cli/
    ├── SKILL.md          # loaded
    └── references/       # read on demand by the skill
```

A loose `.md` file sitting directly in `skills/` is **not** a skill. It is
never loaded, never offered, and never read unless something links to it.

## Standards documents

The rest are prose references, kept here for the convenience of linking:

- `DEVELOPMENT_STANDARDS.md` - coding standards, linked from the root README
- `TYPESCRIPT_PATTERNS.md` - TypeScript conventions, linked from `hooks/README.md`

Three other documents lived here and were deleted: `MAESTRO_ORCHESTRATION.md`,
`RESPONSE_QUALITY_STANDARDS.md`, and `BI_DIRECTIONAL_ACCOUNTABILITY.md`. Each
was referenced only by hooks that turned out to be incapable of firing, and by
nothing else in the repo. Recover any of them from git history if needed.

## Where the rules actually live

`CLAUDE.md` is the file Claude Code reads on every session. If a rule needs to
be followed, it belongs there. A standards document in this directory is
reference material a person or a skill can link to, not something the model
sees by default.

## Adding a skill

```bash
mkdir -p skills/my-skill
$EDITOR skills/my-skill/SKILL.md   # needs name + description frontmatter
git add skills/my-skill && git commit && git push
```

It is live in `~/.claude/skills/` on every machine after `git pull`.
