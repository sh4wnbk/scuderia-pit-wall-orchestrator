---
description: Restore Claude Code session context from reB0ot snapshot and memory files
---

Bootstrap this session with full project context. Do the following in order:

1. Read `.bob/context/reboot_latest.md` — get the last known STATE, LAST ACTION, and NEXT.

2. Read `/home/shawn/.claude/projects/-home-shawn-src-ibm-scuderia/memory/MEMORY.md` — get the memory index, then read any files relevant to the current work (project_hackathon.md, project_deployment.md, project_build_state.md).

3. Read `CLAUDE.md` in the project root — architectural overview and deployment status.

4. Run `git log --oneline -5` and `git status` — capture what's changed since the last snapshot.

5. Summarize restored context in this format:
   - **Project**: what this is
   - **Last state**: what the snapshot says was happening
   - **Current git state**: any changes since snapshot
   - **Next action**: what to do now
   - **Open blockers**: anything unresolved

Do not ask the user to repeat context. Pick up where the snapshot left off.
