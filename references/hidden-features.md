# Hidden Features — Community Collection

Source: https://www.hermesbible.com/flows/hidden-hermes-features-you-should-know
A living collection compiled from the community. Lesser-known commands, behaviors, and tricks.

---

## 1. `/handoff` — Move a live conversation between platforms

From a CLI session, run `/handoff telegram` (or discord, slack, …) to transfer the live conversation to that platform's home channel — same session id, full transcript, tool calls, and all.

Start something at your desk in the terminal, then walk away and keep going on your phone. The session doesn't fork or restart; it's literally the same thread continuing on a new surface. Resume back to the CLI later with `/resume <title>`.

Run `/sethome` once from the destination chat to configure it. Telegram opens a fresh forum topic; Discord opens an auto-archive thread.

---

## 2. `hermes -c` — Continue your last session

`hermes -c` (or `--continue`) reopens the most recent CLI session with its full history. Add a name to resume the most recent session in a lineage: `hermes -c "my project"`.

After a crash, a closed terminal, or stepping away from a long brainstorm, you pick up exactly where you left off — context intact. A compact recap panel shows the last exchanges before the prompt returns.

---

## 3. Context compression — what it keeps, what it drops

The clamp in the status bar = compression count. Kicks in around 50% full by default.

When compression fires:
- **Keeps:** first 3 turns + last ~20 turns
- **Summarizes:** everything in between
- A detail from the middle of a long session can drop out — agent may repeat work

**Three levers** (all in `config.yaml`, hot-reloading on a running gateway):
- `protect_last_n` — keep more recent turns uncompressed
- `auxiliary.compression.model` — point summarizer at a cheap, fast model
- `model.context_length` — raise the ceiling so compression fires later

---

## 4. `/browser connect` — Drive your own browser

Instead of a cloud browser, attach Hermes to your own running Chrome, Brave, Chromium, or Edge via Chrome DevTools Protocol (CDP).

- Watch what the agent does in real time
- Use pages that need your logged-in cookies and sessions
- Skip cloud-browser costs

```
/browser connect      — auto-launch/attach at 127.0.0.1:9222
/browser status       — check the connection
/browser disconnect   — detach
```

**Note:** CLI-only slash command — run from terminal, not from WebUI/Telegram/Discord.

---

## 5. REST API (Web Dashboard)

`hermes dashboard` exposes a REST API that the frontend consumes — and you can call directly for automation.

```
GET /api/status                   — version, gateway, active sessions
GET /api/sessions                 — 20 most recent + metadata
GET /api/sessions/search?q=...   — full-text message search
GET /api/config · PUT /api/config — read / write config
GET/PUT/DELETE /api/env           — manage env vars
```

Management endpoints accept optional `?profile=<name>` to scope to a specific profile.

---

## 6. Native cross-platform desktop app

`hermes desktop` launches a native app for macOS, Windows, and Linux. Built around the same agent as CLI and gateway — sharing config, keys, sessions, skills, and memory.

Anything you set up in the terminal is already there, and anything you do in the app shows up in the terminal. Features:
- Streaming chat with live tool activity
- Drag-and-drop file attach
- Right-hand preview rail
- Command palette (Cmd/Ctrl+K)
- Voice mode
- Full settings UI (no YAML editing)

---

## 7. `/steer` — Redirect mid-task without interrupting

Set `display.busy_input_mode: "steer"` (or just `/busy steer` in CLI). Now when you press Enter while the agent is working, your message is injected into the current run after the next tool call — no interrupt, no new turn.

```
/steer      — inject after the next tool call
/queue      — send as the next turn
/interrupt  — default: stop and handle now
```

Use it to drop a course-correction like "actually, also check the tests" while it's still editing code, without canceling in-flight work.

---

## 8. `/claude-code` — Put Claude Code in the fleet

The bundled `claude-code` skill lets Hermes delegate coding tasks to Anthropic's Claude Code CLI through the terminal — including running whole skill workflows.

Because Anthropic left print mode (`-p`) available, Hermes can hand Claude a one-shot task and get the result back. If you already have Claude set up, adding it to the fleet is basically free — and a real boon for autonomous coding.

---

## Keep Them Coming

This is a living wiki, not a finished list. More features will be added as the community surfaces them.

**Source thread:** https://x.com/hermes_updates
**Living wiki:** https://get-hermes.ai/hidden-features
