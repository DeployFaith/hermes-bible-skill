# Hermes Bible Skill

Community knowledge base for [Hermes Agent](https://hermes-agent.nousresearch.com) — 169 pages of unofficial docs, 25+ real-world flows, hidden features, SOUL.md patterns, and intent-based routing.

Source: [The Hermes Bible](https://www.hermesbible.com) · Built by [iamlukethedev](https://x.com/iamlukethedev) · Not affiliated with Nous Research.

## What's Inside

| File | What it does |
|------|--------------|
| `SKILL.md` | Main skill file — router with embedded knowledge, flows catalog, intent mappings |
| `references/patterns.md` | SOUL.md templates, delegation patterns, kanban concepts, cron patterns |
| `references/flows-catalog.md` | 21 real-world flows with intent-based routing |
| `references/hidden-features.md` | 8 community-sourced hidden Hermes features |
| `references/index.md` | Full 169-page documentation index with URLs |

## Installation

### Option 1: Copy the skill

```bash
# Clone the repo
git clone https://github.com/DeployFaith/hermes-bible-skill.git

# Copy to your skills directory
cp -r hermes-bible-skill/SKILL.md hermes-bible-skill/references ~/.hermes/profiles/default/skills/hermes-bible/
```

Or for a specific profile:

```bash
cp -r hermes-bible-skill/SKILL.md hermes-bible-skill/references ~/.hermes/profiles/YOUR_PROFILE/skills/hermes-bible/
```

### Option 2: Install with Hermes CLI

```bash
hermes skills install https://github.com/DeployFaith/hermes-bible-skill
```

### Option 3: Use the bundle (loads both official + community docs)

```bash
# Copy the bundle file
cp hermes-bible-skill/bundles/hermes-complete.yaml ~/.hermes/skill-bundles/

# Now /hermes-complete loads both hermes-agent AND hermes-bible together
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
- Polymarket trading agent
- Kanban mastery
- And 16 more...

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
cp bundles/hermes-complete.yaml ~/.hermes/skill-bundles/
```

Then use `/hermes-complete` in chat to load both skills at once.

## How It Works

The skill uses a **progressive disclosure** pattern:

1. **Embedded knowledge** — answers common questions instantly (no fetch needed)
2. **Reference files** — loaded on demand via `skill_view` for deeper topics
3. **Fetch-on-demand** — `web_extract` to hermesbible.com for specific pages

This keeps token usage low (~4K for the main file) while having access to the full 169-page index.

## Complementary Skills

- `hermes-agent` — Official docs, config commands, tool lists, setup steps
- `hermes-bible` — Community knowledge, patterns, workflows, hidden features

Use both together for complete Hermes expertise.

## License

MIT — The content is sourced from [The Hermes Bible](https://www.hermesbible.com), an unofficial community project. Original documentation is the property of [Nous Research](https://nousresearch.com).
