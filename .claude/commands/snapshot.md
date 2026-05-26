---
description: Capture current Claude Code session state into reB0ot restoration files
argument-hint: --note "optional note about current intent or state"
---

Take a snapshot of the current session state and persist it so future sessions (Claude Code or Bob) can restore context.

Do the following in order:

1. Read the current git status and recent commits (`git status`, `git log --oneline -10`) to capture what's changed.

2. Update `.bob/context/reboot_latest.md` with a structured snapshot in this format:
```
==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        <one-line description of current state>
LAST ACTION  <what was just done or decided>
NEXT         <the immediate next action>
NOTE         $ARGUMENTS
==================================================
```

3. Update the relevant memory files in `/home/shawn/.claude/projects/-home-shawn-src-ibm-scuderia/memory/` if anything has changed since the last snapshot (deployment state, critical path, decisions made).

4. Confirm what was saved and where.
