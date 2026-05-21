# ⚡ reB0ot - Video Demo Script

## [SLIDE 1: Title Slide - Static]
**On screen:** Your name + "⚡ reB0ot" branding

---

## [VIDEO 1: Reboot Application Demo - ~10 seconds]
**Command:** `.\run.ps1 --export reboot.py --format structured`

**Narration:**
"Let me show you reB0ot in action. I'm running it on the reboot.py file itself - the core application code. Watch as it authenticates with IBM Cloud and generates a structured restoration string. In just seconds, it analyzes the project state, shows what's been implemented, and identifies the next steps needed to complete the restoration string generation."

---

## [VIDEO 2: Debug Task - 23 seconds]
**Command:** `.\run.ps1 --export bob_sessions/bob_task_debug.md --format paragraph`

**Narration:**
"This is reB0ot in action. I'm running it on a debugging session I had with Bob IDE. I just hit run from the chat window, and reB0ot reads my exported session file and generates a restoration string in paragraph format. In 23 seconds, I get a concise summary of what I was debugging, what I found, and where I left off."

---

## [VIDEO 3: Max New Tokens Task - 24-29 seconds]
**Command:** `.\run.ps1 --export bob_sessions/bob_task_max_new_tokens.md --format structured`

**Narration:**
"Here's another session where I was working on adjusting token limits. This time I'm using structured format, which gives me a breakdown with clear sections: my task, what I accomplished, next steps, and the files I touched. Takes about 25 seconds, and now I have everything I need to pick up exactly where I left off."

---

## [VIDEO 4: Explain Codebase Task - 53 seconds to 1:21]
**Command:** `.\run.ps1 --export bob_sessions/bob_task_create_explain_codebase.md --format paragraph`

**Narration:**
"This was a longer session where I asked Bob to explain the entire codebase. The exported file was much larger, but reB0ot handles it efficiently. It takes about a minute, but look at the output - it distills a complex conversation into a clear summary. I can see what parts of the codebase I explored, what I learned, and what questions I still need to answer."

---

## [VIDEO 5: Create Reboot File Task - 2:01 to 2:04, then error]
**Command:** `.\run.ps1 --export bob_sessions/bob_task_create_reboot_file.md --format structured`

**Narration:**
"Here's an interesting case - this was the session where I actually created the reB0ot tool itself. It's a longer, more complex session, so it takes about two minutes to process. You'll see it authenticate with IBM Cloud, start generating the restoration string, and then... it hits a server error. This is actually a 500 error from the watsonx API - not a problem with reB0ot, but a temporary issue on IBM's side. In real use, you'd just retry the command. But this shows you the tool in action on a real, complex development session."

---

## [SLIDE 2: Thank You - Static]
**On screen:** Thank you message, GitHub repo link, #watsonxHackathon

---

**Total time:** ~4-5 minutes with narration