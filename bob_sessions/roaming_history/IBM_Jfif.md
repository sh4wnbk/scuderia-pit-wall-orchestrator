---
---
description: Capture and compress the current Bob session into a ⚡ reB0ot Restoration String
argument-hint: --note "your current thought or intent"
---

You are executing the ⚡ reB0ot snapshot workflow. Follow these steps in order:

1. If `.bob/context/` does not exist, create it now.

2. Export the current task session history via Views → More Actions → History → Export. Save the file to `.bob/context/session_latest.md`.

3. Run this command in the terminal:

python reboot.py --export .bob/context/session_latest.md --format structured --note $1

4. Save the resulting Restoration String card to `.bob/context/reboot_latest.md`.

5. Display the card in the terminal for confirmation.