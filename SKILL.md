---
name: hermes-bible
description: >
  Community knowledge base for Hermes Agent — 169 pages of unofficial docs,
  25+ real-world flows, hidden features, SOUL.md patterns, and intent-based
  routing to the right resource. Complements the official hermes-agent skill.
triggers:
  - hermes bible
  - hermes community
  - hidden features
  - hermes flows
  - how do other people use hermes
  - hermes patterns
  - hermes best practices
  - what can hermes do
  - hermes use cases
  - hermes workflows
  - SOUL.md template
  - hermes operating contract
  - hermes kanban
  - hermes delegation patterns
  - hermes overnight
  - hermes autonomous
---

# The Hermes Bible — Community Knowledge Base

Unofficial, community-built reference for Hermes Agent. 169 pages of docs + 25+ real-world flows.

**Source:** https://www.hermesbible.com · Built by iamlukethedev · Not affiliated with Nous Research.

---

## When to Use This Skill

| User asks about... | Action |
|---|---|
| Hidden / lesser-known features | Answer from embedded knowledge below |
| SOUL.md patterns / templates | Answer from embedded knowledge below, or fetch flow |
| Real-world Hermes workflows | Search flows catalog, fetch the matching flow |
| Specific Hermes feature deep-dive | Fetch the page from the index |
| Kanban / delegation / cron patterns | Load `references/patterns.md` |
| "What can Hermes do?" | Reference the flows catalog |

**For official config commands, tool lists, setup steps** → use the `hermes-agent` skill instead.

---

## Hidden Features (Community-Sourced)

### 1. `/handoff` — Move a live conversation between platforms
From CLI, run `/handoff telegram` (or discord, slack) to transfer the live conversation — same session ID, full transcript. Resume back with `/resume <title>`. Run `/sethome` once to configure.

### 2. `hermes -c` — Continue your last session
`hermes -c` reopens the most recent CLI session with full history. Add a name: `hermes -c "my project"`.

### 3. Context compression levers
Kicks in ~50% full. Keeps first 3 + last ~20 turns, summarizes middle. Three levers in `config.yaml` (hot-reloading):
- `protect_last_n` — keep more recent turns uncompressed
- `auxiliary.compression.model` — cheap model for summarization
- `model.context_length` — raise ceiling so compression fires later

### 4. `/browser connect` — Drive your own browser
Attach to Chrome/Brave/Edge via CDP. Real-time watch, your cookies, no cloud costs.
```
/browser connect · /browser status · /browser disconnect
```

### 5. REST API
`hermes dashboard` exposes: `GET /api/status`, `/api/sessions`, `/api/sessions/search?q=...`, `/api/config`, `/api/env`. Optional `?profile=<name>`.

### 6. Native desktop app
`hermes desktop` — macOS/Windows/Linux. Same agent as CLI. Streaming chat, drag-drop files, command palette (Cmd/Ctrl+K), voice, settings UI.

### 7. `/steer` — Redirect mid-task without interrupting
Set `/busy steer`. Enter while agent works → injects after next tool call, no interrupt.
```
/steer · /queue · /interrupt
```

### 8. `/claude-code` — Put Claude Code in the fleet
Bundled skill delegates to Anthropic's Claude Code CLI via `-p` (print mode). Free for autonomous coding.

---

## SOUL.md Operating Contract Pattern

A SOUL.md is an **operating contract**, not a personality hack. Key sections:

1. **Identity** — Role, mission, what you coordinate/inspect/decide
2. **Stance** — Direct, practical, opinionated. Push back when vague/distracted.
3. **Accountability** — If output isn't acted on, the feedback loop is broken.
4. **Pushback** — Earn the right to disagree. Every objection needs evidence.
5. **Autonomy** — Broad autonomy with narrow hard line (no publishing/purchasing/messaging/destructive without approval)
6. **Mission** — Active builds, priorities, debt, sunset candidates
7. **Tone** — Private: concise, direct. Public: match user's voice.
8. **Operating Mode** — Default to orchestration, not solo execution
9. **Delegation Rules** — Remain accountable. Synthesize, don't dump.
10. **Standards** — Clear scope, explicit assumptions, grounded evidence
11. **Escalation** — Only when ambiguity changes solution or action is irreversible

Full template: load `references/patterns.md` or fetch `https://www.hermesbible.com/flows/soul-md-operating-contract-template`

---

## Flows Catalog (Intent → Flow)

| Intent | Flow | Category |
|--------|------|----------|
| Hidden features / tips | Hidden Features in Hermes | Guides |
| SOUL.md template | SOUL.md Operating Contract | Configuration |
| SOUL.md deep dive | 170-Line SOUL.md | Configuration |
| Multi-agent / Jira | 4 Agents → PRs for $12 | Engineering |
| /goal workflows | Complete /goal Playbook | Automation |
| Overnight builds | 9-Hour Overnight Workflow | Automation |
| Personal AI OS | Hermes as AI OS | Architecture |
| Kanban mastery | Dominate Projects with Kanban | Orchestration |
| Operator setup | Become a Hermes Operator | Orchestration |
| xurl + X/Twitter | Hermes + xurl System | Automation |
| Trading agent | Polymarket Self-Learning | Trading |
| Grok integration | Grok Three Superpowers | Integrations |
| Security / secrets | Bitwarden Security Stack | Security |
| Self-improvement | Hermes Dreaming | Self-Improvement |
| Desktop app tour | Hermes Desktop Full Tour | Desktop & GUI |
| Context / memory | Context OS for Agent | Memory |
| Research team | 3-Agent Research Dept | Multi-Agent |
| 24/7 automation | 10 Hacks for 24/7 System | Automation |
| Settings that matter | 10 Real Settings | Configuration |
| Architecture overview | Full Guide: Architecture | Guides |
| Agent loops | 8 Loops That Compound | Architecture |

Full catalog with URLs and summaries: load `references/flows-catalog.md`

---

## Documentation Index (Summary)

169 pages across 10 sections. Full index with URLs: load `references/index.md`

| Section | Pages | Covers |
|---------|-------|--------|
| Getting Started | 6 | Install, quickstart, learning path, Termux, Nix |
| Core Features | 45 | Tools, skills, memory, plugins, cron, delegation, kanban, goals, browser, voice, MCP, ACP |
| Messaging | 30 | Telegram, Discord, Slack, WhatsApp, Signal, Email, Matrix, Teams, and 22 more |
| Secrets | 2 | Bitwarden, env-based secrets |
| Skills | 1 | Google Workspace |
| Using Hermes | 15 | CLI, TUI, config, models, sessions, profiles, Docker, security, desktop |
| Integrations | 3 | Providers, Nous Portal |
| Guides | 30 | Tips, tutorials, cron, delegation, plugins, MCP, voice, provider-specific setup |
| Developer Guide | 26 | Architecture, agent loop, tools, providers, plugins, platform adapters |
| Reference | 11 | CLI commands, slash commands, toolsets, MCP config, model catalog, FAQ |

---

## Fetch-on-Demand Instructions

1. **For a specific doc page:** Use `web_extract` with `https://www.hermesbible.com{url}` from `references/index.md`
2. **For a flow:** Use `web_extract` with `https://www.hermesbible.com{url}` from `references/flows-catalog.md`
3. **For patterns (SOUL.md, delegation, kanban, cron):** Load `references/patterns.md` first, fetch if more detail needed
4. **For hidden features:** Embedded above; fetch full flow for edge cases

If `web_extract` fails, use browser to navigate and extract.

---

## Related Skills

- `hermes-agent` — Official docs, config commands, tool lists, setup steps
- This skill — Community knowledge, patterns, workflows, hidden features

Use both together for complete Hermes expertise.
