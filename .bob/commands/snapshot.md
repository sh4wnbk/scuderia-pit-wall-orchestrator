---
description: Capture current Bob session into a ⚡ reB0ot Restoration String
argument-hint: --note "your current thought or intent"
---

Run this command in the terminal:

bash reboot_bridge_fixed.sh --export "$(ls -t bob_sessions/bob_task_*.md 2>/dev/null | head -1)" --format structured --note "$1" --output .bob/context/reboot_latest.md
