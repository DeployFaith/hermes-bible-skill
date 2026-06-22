# Hermes Bible Skill

Community knowledge base for [Hermes Agent](https://hermes-agent.nousresearch.com) — 169 pages of unofficial docs, 25+ real-world flows, hidden features, SOUL.md patterns, and intent-based routing.

Source: [The Hermes Bible](https://www.hermesbible.com) · Built by [iamlukethedev](https://x.com/iamlukethedev) · Not affiliated with Nous Research.

## What's Inside

| File | What it does |
|------|--------------|
| `SKILL.md` | Main skill file — router with embedded knowledge, flows catalog, intent mappings |
| `references/patterns.md` | SOUL.md templates, delegation patterns, kanban concepts, cron patterns |
| `references/flows-catalog.md` | 26 real-world flows with intent-based routing |
| `references/hidden-features.md` | 8 community-sourced hidden Hermes features |
| `references/index.md` | Full 169-page documentation index with URLs |
| `references/llms-full.md` | Sanitized full-corpus markdown export from `llms-full.txt` for broad audits/offline lookup |

## Installation

Supported install modes:

1. **Full install (recommended):** clone + copy the full skill directory. This preserves `SKILL.md` and linked `references/` files.
2. **Light install:** install the raw `SKILL.md` URL. This is useful for quick access, but linked reference files are not included.
3. **Bundles:** optional slash-command shortcuts for already-installed skills. Bundles do not install the skills they reference.

### Recommended: clone + copy the full skill

This is the recommended install path because it copies both `SKILL.md` and the linked `references/` files.

```bash
# Clone the repo
git clone https://github.com/DeployFaith/hermes-bible-skill.git
cd hermes-bible-skill

# Install into the default Hermes home
mkdir -p ~/.hermes/skills/hermes-bible
cp -r SKILL.md references ~/.hermes/skills/hermes-bible/
```

For a named Hermes profile:

```bash
PROFILE=YOUR_PROFILE
mkdir -p ~/.hermes/profiles/$PROFILE/skills/hermes-bible
cp -r SKILL.md references ~/.hermes/profiles/$PROFILE/skills/hermes-bible/
```

After copying, start a new Hermes session or run `/reload-skills` in a supported interactive surface.

### Light install: main skill only

Hermes can install a direct URL to the raw `SKILL.md` file:

```bash
hermes skills install https://raw.githubusercontent.com/DeployFaith/hermes-bible-skill/main/SKILL.md
```

This installs only `SKILL.md`. Hermes fetches the skill file; it does not clone this repository or install `references/`, `bundles/`, or `scripts/`. The clone + copy method above is recommended for the complete experience. In light mode, agents can still answer from the embedded routing tables and fetch live content from `llms.txt`, `llms-full.txt`, or specific page URLs when tools permit.

### Optional: install a bundle

Bundles add slash commands that load one or more already-installed skills. Install `hermes-bible` first, then copy a bundle file:

```bash
mkdir -p ~/.hermes/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/skill-bundles/
hermes bundles reload
```

Now `/hermes-complete` loads both `hermes-agent` and `hermes-bible` together, assuming both skills are installed.

For a named profile, place the bundle under that profile's Hermes home:

```bash
PROFILE=YOUR_PROFILE
mkdir -p ~/.hermes/profiles/$PROFILE/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/profiles/$PROFILE/skill-bundles/
```

## What It Covers

### Hidden Features (Embedded)
- `/handoff` — move conversations between platforms
- `hermes -c` — continue last session
- Context compression levers
- `/browser connect` — drive your own browser
- REST API endpoints
- Native desktop app
- `/steer` — redirect mid-task
- `/claude-code` — Claude Code in the fleet

### SOUL.md Operating Contract
Full template for making your agent behave like an operator, not a chatbot.

### Real-World Flows
- 4 Agents → PRs for $12 (Jira automation)
- 9-Hour Overnight Workflow
- /goal Playbook (21 workflows)
- The 15 Levels of Hermes Agent Usage
- Polymarket trading agent
- Kanban mastery
- And 20 more...

### Documentation Index
169 pages across 10 sections — Getting Started, Core Features, Messaging, Secrets, Skills, Using Hermes, Integrations, Guides, Developer Guide, Reference.

## Bundles

The `bundles/` directory contains ready-to-use skill bundles:

| Bundle | What it does |
|--------|--------------|
| `hermes-bible.yaml` | Loads just the community knowledge skill |
| `hermes-complete.yaml` | Loads both official docs AND community knowledge together |

Install a bundle:
```bash
mkdir -p ~/.hermes/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/skill-bundles/
hermes bundles reload
```

Then use `/hermes-complete` in chat to load both skills at once. Bundles reference installed skills; install `hermes-bible` first for `/hermes-complete` to load it successfully.

For a named profile, place the bundle under that profile's Hermes home:

```bash
PROFILE=YOUR_PROFILE
mkdir -p ~/.hermes/profiles/$PROFILE/skill-bundles
cp bundles/hermes-complete.yaml ~/.hermes/profiles/$PROFILE/skill-bundles/
```

## How It Works

The skill uses a **progressive disclosure** pattern:

1. **Embedded knowledge** — answers common questions instantly (no fetch needed)
2. **Reference files** — loaded on demand via `skill_view` for deeper topics
3. **Fetch-on-demand** — `web_extract` to hermesbible.com for specific pages

This keeps token usage low (~4K for the main file) while having access to the full 169-page index. The large `references/llms-full.md` corpus is available for broad audits and offline lookup, but should be loaded only when needed.

## Complementary Skills

- `hermes-agent` — Official docs, config commands, tool lists, setup steps
- `hermes-bible` — Community knowledge, patterns, workflows, hidden features

Use both together for complete Hermes expertise.

## License

MIT — The content is sourced from [The Hermes Bible](https://www.hermesbible.com), an unofficial community project. Original documentation is the property of [Nous Research](https://nousresearch.com).

## Self-Updating

The skill includes a self-updater script that fetches the latest content from hermesbible.com's `llms.txt` and `llms-full.txt` files and updates the reference files automatically.

### Manual Update

```bash
# Dry run (default; see what would change)
python3 scripts/hermes-bible-updater.py --dry-run --verbose

# Apply updates without committing or pushing
python3 scripts/hermes-bible-updater.py --write

# Apply updates and create a local commit
python3 scripts/hermes-bible-updater.py --commit

# Apply updates, commit, and push explicitly
python3 scripts/hermes-bible-updater.py --commit --push
```

By default the updater is safe: it reports changes but does not write, commit, or push unless you pass the corresponding flag. Commit mode stages only generated reference files, not the whole worktree; it must not use `git add -A`.

### Automated Updates (Cron)

Set up a cron job to check weekly:

```bash
# Copy the script to your Hermes scripts directory
mkdir -p ~/.hermes/scripts
cp scripts/hermes-bible-updater.py ~/.hermes/scripts/

# Create a cron job (runs every Monday at 3am; dry-run/report only by default)
hermes cron create --name hermes-bible-updater \
  --schedule "0 3 * * 1" \
  --script hermes-bible-updater.py \
  --no-agent
```

The updater will:
1. Fetch the latest `llms.txt` from hermesbible.com
2. Parse all docs and flows
3. Compare generated reference files with current files
4. Report new, removed, and changed content
5. Refresh sanitized `references/llms-full.md` from `llms-full.txt` unless `--skip-full` is passed
6. Redact credential-like assignment values before storing the full-corpus mirror
7. Write only with `--write` or `--commit`
8. Push only with explicit `--commit --push`
9. Print a JSON summary suitable for cron notifications
