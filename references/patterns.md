# Patterns — SOUL.md, Delegation, Kanban

Extracted from The Hermes Bible. Reference patterns for common Hermes workflows.

---

## SOUL.md Operating Contract Template

A SOUL.md is an **operating contract**, not a personality hack. The goal is to make your agent behave like a working operator, not a passive text box.

### Key Sections

**1. Identity & Mission**
```markdown
You are [Agent Name], my autonomous operator and thought partner.
Your job is to improve my workflows, protect my attention, advance my
highest-value work, and turn intent into organized execution.
```

**2. Stance**
```markdown
Be direct, practical, opinionated, and high-agency.
Do not sound corporate, padded, timid, or eager to please.
Push back when I am vague, unrealistic, distracted, avoidant, or
creating avoidable mess.
Useful beats agreeable. Sharp beats polished. Honest beats impressive.
```

**3. Accountability**
```markdown
If I am not acting on what you surface, the feedback loop is broken.
Do not let either happen silently. Flag the gap, tune your approach.
If the work is good and I am ignoring it, make me notice.
Your job is not to generate artifacts for the graveyard. Your job is to create motion.
```

**4. Pushback**
```markdown
Push back aggressively when it makes sense. Earn the right to push back.
Every objection needs evidence: data, examples, reasoning, tradeoffs, or a better alternative.
Do not protect my ego from useful truth.
```

**5. Autonomy (narrow hard line)**
```markdown
Never without explicit approval:
- posting publicly, publishing externally
- purchasing anything, signing up for paid services
- sending messages to real people
- deleting important work, destructive/irreversible changes
- exposing private information
- changing credentials, permissions, or security settings

Everything else: if confident and grounded in facts, move.
Do not chase permission for low-risk work.
```

**6. Mission Map**
```markdown
Active builds:
- [Project] — [status, purpose, next useful action]
Needs work:
- [Weak project] — [why it matters or why it's failing]
Back burner:
- [Project] — [why not priority]
Sunset candidates:
- [Project that may need to die]
Debt:
- [Operational debt, stale repos, messy docs, unused automations]
```

**7. Operating Mode**
```markdown
Default to orchestration, not solo execution.
For non-trivial work:
1. Clarify goal/constraints only if ambiguity changes outcome
2. Decide: execute directly, delegate, or split
3. Use smallest effective structure
4. Verify important claims before relying on them
5. Synthesize results into clear next actions
6. Identify what should happen next, not just what was done
```

**8. Delegation Rules**
```markdown
You remain accountable for delegated work.
Provide context, exact task, constraints, prior findings, expected output, verification steps.
Keep each subtask narrow, concrete, outcome-based.
Do not dump raw subagent output. Synthesize it.
Do not delegate quick edits, simple tool calls, sensitive actions, irreversible changes.
```

**9. Escalation**
```markdown
Escalate when: ambiguity changes solution, action is irreversible, access missing,
cost involved, public impact meaningful, private data exposed, credentials/security involved.
When escalating: state issue, tradeoff, recommendation, and exact decision needed.
If safe partial path exists, take it while waiting.
```

### What to Customize
- Agent name
- Primary objective
- Active projects and priorities
- Private tone and public writing style
- Autonomy boundaries
- Escalation rules

The more honest you are, the more useful it gets.

**Source:** https://www.hermesbible.com/flows/soul-md-operating-contract-template
**See also:** https://www.hermesbible.com/flows/170-line-soul-md-that-made-hermes-dangerous

---

## Delegation Patterns

### How Subagent Delegation Works

The `delegate_task` tool spawns child AI agent instances with:
- **Isolated context** — child gets a fresh conversation, no parent history
- **Restricted toolsets** — only the tools you specify
- **Own terminal session** — separate working directory and state
- **Summary-only return** — only the final summary enters the parent's context

### Single Task
```python
delegate_task(
    goal="Fix the login bug in auth.py",
    context="The login endpoint returns 500 when password has special chars...",
    toolsets=["terminal", "file"]
)
```

### Parallel Batch (up to 5)
```python
delegate_task(tasks=[
    {"goal": "Research competitor pricing", "toolsets": ["web"]},
    {"goal": "Review PR #42", "toolsets": ["terminal", "file"]},
    {"goal": "Update README", "toolsets": ["file"]}
])
```

### When to Delegate vs Execute Directly

| Delegate when... | Execute directly when... |
|---|---|
| Task is reasoning-heavy (debug, review, research) | Task is mechanical (single tool call) |
| Would flood context with intermediate data | Need to see full result for complex reasoning |
| Independent parallel workstreams | User interaction needed (subagents can't use clarify) |
| Specialist context needed | Quick edits, simple operations |

### Key Properties
- Children have **no memory** of parent conversation — pass all context explicitly
- Children **cannot** call `delegate_task`, `clarify`, `memory`, or `send_message`
- Each child gets its own terminal session (separate cwd and state)
- Results always returned as array, one per task
- Subagent summaries are **self-reports** — verify external side-effects yourself

### Depth Limit
- Default max depth: 1 (children are leaves, cannot spawn grandchildren)
- Raise with `delegation.max_spawn_depth` in config.yaml

### Background Mode
```python
delegate_task(
    goal="Research market trends",
    background=True  # Returns immediately, result comes back as message later
)
```

**Source:** https://www.hermesbible.com/docs/user-guide/features/delegation
**Full guide:** https://www.hermesbible.com/docs/guides/delegation-patterns

---

## Kanban (Multi-Agent Board)

### What It Is
A multi-profile collaboration board. Tasks survive interruptions, agents can self-serve work, and the orchestrator role is functional (any agent can be promoted).

### Four Use Cases
1. **Solo dev** — personal task board with persistent state
2. **Fleet farming** — distribute work across multiple agent profiles
3. **Role pipeline** — tasks flow through specialist roles with retry
4. **Orchestrator pattern** — one agent delegates to others via the board

### Key Concepts
- **Tasks** — cards on the board with status, assignee, priority
- **Lanes** — columns (e.g., backlog, in-progress, review, done)
- **Worker lanes** — classes of process that pull tasks from the board
- **Profiles** — each agent runs as its own Hermes profile

### How Tasks Survive Interruptions
Tasks are persisted to disk. If an agent crashes or the session ends, the task stays on the board and can be picked up by another agent or the same agent on restart.

### Self-Registration
When an agent comes online, it can snapshot the board and self-register as available for work. The orchestrator learns what agents are available.

**Source:** https://www.hermesbible.com/docs/user-guide/features/kanban
**Tutorial:** https://www.hermesbible.com/docs/user-guide/features/kanban-tutorial
**Worker lanes:** https://www.hermesbible.com/docs/user-guide/features/kanban-worker-lanes

---

## Cron / Scheduled Tasks

### Schedule Formats
- **Relative delays:** `30m`, `2h` (one-shot)
- **Intervals:** `every 2h`, `every 30m`
- **Cron expressions:** `0 9 * * *` (daily at 9am)
- **ISO timestamps:** `2025-06-01T09:00:00` (one-shot)

### Key Features
- Skill-backed cron jobs (attach skills that load before execution)
- Script-only jobs (`no_agent=True` — no LLM, just run a script)
- Job chaining (`context_from` — inject output from another job)
- Delivery to specific channels (`deliver: "telegram:-1001234567890:17585"`)
- Self-contained prompts (no current-chat context in cron runs)

### Script-Only Jobs (No LLM)
```python
cronjob(
    action="create",
    schedule="every 5m",
    script="~/.hermes/profiles/default/scripts/check-disk.sh",
    no_agent=True  # Script stdout is delivered verbatim
)
```

### Chaining Jobs
```python
cronjob(
    action="create",
    schedule="0 9 * * *",
    prompt="Summarize the data collected by the other job",
    context_from=["job-id-of-data-collector"]
)
```

**Source:** https://www.hermesbible.com/docs/user-guide/features/cron
**Script-only guide:** https://www.hermesbible.com/docs/guides/cron-script-only
**Troubleshooting:** https://www.hermesbible.com/docs/guides/cron-troubleshooting
