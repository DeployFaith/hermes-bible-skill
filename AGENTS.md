# AGENTS.md — Hermes Bible Skill

This repository contains the `hermes-bible` skill for Hermes Agent.

## Goal

If the user asks you to install this skill, prefer the full local install so the
agent receives both `SKILL.md` and the linked `references/` files.

## Install Rules

### Full install, default Hermes home

From the repository root:

```bash
mkdir -p ~/.hermes/skills/hermes-bible
cp -r SKILL.md references ~/.hermes/skills/hermes-bible/
```

Then tell the user to start a new Hermes session or run `/reload-skills` where supported.

### Full install, named profile

Ask for the profile name if it is not clear. Then run:

```bash
PROFILE=PROFILE_NAME
mkdir -p ~/.hermes/profiles/$PROFILE/skills/hermes-bible
cp -r SKILL.md references ~/.hermes/profiles/$PROFILE/skills/hermes-bible/
```

### Light install

Only use this when the user explicitly wants a quick/light install:

```bash
hermes skills install https://raw.githubusercontent.com/DeployFaith/hermes-bible-skill/main/SKILL.md
```

This installs only `SKILL.md`. It does not install `references/`, `bundles/`, or
`scripts/`.

## Bundle Install

Bundles are optional shortcuts. They do not install skills.

Default Hermes home:

```bash
mkdir -p ~/.hermes/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/skill-bundles/
hermes bundles reload
```

Named profile:

```bash
PROFILE=PROFILE_NAME
mkdir -p ~/.hermes/profiles/$PROFILE/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/profiles/$PROFILE/skill-bundles/
```

## Updater Safety

The updater is safe by default:

```bash
python3 scripts/hermes-bible-updater.py --dry-run
```

Use `--write` to update generated reference files locally.

Only commit or push when the user explicitly asks:

```bash
python3 scripts/hermes-bible-updater.py --commit
python3 scripts/hermes-bible-updater.py --commit --push
```

Do not use `git add -A` for updater commits. Stage only intended generated files.

## Source Authority

Hermes Bible is community knowledge. For current Hermes commands, config keys,
security behavior, and setup semantics, prefer:

1. official Hermes docs
2. the `hermes-agent` skill if available
3. live `hermes --help` / CLI output

If those conflict with this repo, official docs and live CLI output win.

## Validation Before Reporting Success

After install, confirm the files exist:

```bash
test -f ~/.hermes/skills/hermes-bible/SKILL.md
test -f ~/.hermes/skills/hermes-bible/references/index.md
test -f ~/.hermes/skills/hermes-bible/references/flows-catalog.md
test -f ~/.hermes/skills/hermes-bible/references/hidden-features.md
test -f ~/.hermes/skills/hermes-bible/references/patterns.md
```

Adjust the path for named profiles.
