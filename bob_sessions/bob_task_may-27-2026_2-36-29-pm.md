**User:**

<task>
— Wire DASH, DATA, and SYNC icons in static/index.html
  
  Three changes total: onclick wires on existing buttons, one new slide-up panel (SYNC), one new screen (DATA), and the
  JavaScript to drive them. No changes to any backend files.

  ---
  Part 1 — Add onclick to the three dead nav buttons
  
  Find the bottom nav in screen-ready (the <nav> block with five buttons). Make these three changes:

  DASH button — add onclick="showScreen('ready')":
  <button onclick="showScreen('ready')" class="flex flex-col items-center gap-1 text-on-surface-variant 
  hover:text-primary transition-colors">
    <span class="material-symbols-outlined">dashboard</span>
    <span class="text-label-caps font-label-caps">DASH</span>
  </button>

  DATA button — add onclick="showDataScreen()":
  <button onclick="showDataScreen()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary 
  transition-colors">
    <span class="material-symbols-outlined">analytics</span>
    <span class="text-label-caps font-label-caps">DATA</span>
  </button>

  SYNC button — add onclick="openSync()":
  <button onclick="openSync()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary 
  transition-colors">
    <span class="material-symbols-outlined">sync</span>
    <span class="text-label-caps font-label-caps">SYNC</span>
  </button>

  ---
  Part 2 — Add CSS for the SYNC panel

  In the <style> block, add after the #governancePanel.open rule:

  #syncPanel {
    position: absolute;
    bottom: 0; left: 0; width: 100%;
    transform: translateY(100%);
    transition: transform 0.3s ease;
    z-index: 80;
  }
  #syncPanel.open { transform: translateY(0); }

  ---
  Part 3 — New HTML: SYNC slide-up panel

  Add this block inside #app-shell, just before the closing </div><!-- /app-shell --> tag:

  <!-- ── SYNC PANEL ─────────────────────────────────────────── -->
  <div id="syncPanel" class="bg-surface-container-highest border-t-2 border-primary-container p-margin-md">
    <div class="flex justify-center mb-margin-md cursor-pointer" onclick="closeSync()">
      <div class="w-12 h-1 bg-outline-variant rounded-full"></div>
    </div>
    <div class="flex justify-between items-center mb-margin-md">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-primary-container msym-fill" style="font-size:18px;">sync</span>
        <span class="text-label-caps font-label-caps text-on-surface tracking-widest">RACE CONTEXT</span>
      </div>
      <button onclick="closeSync()" class="text-on-surface-variant hover:text-on-surface">
        <span class="material-symbols-outlined" style="font-size:20px;">close</span>
      </button>
    </div>
    <div class="flex flex-col gap-margin-sm mb-margin-md">
      <div class="flex flex-col gap-1">
        <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">YEAR</span>
        <input id="sync-year" type="number"
          class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 
  outline-none focus:border-primary-container w-full"/>
      </div>
      <div class="flex flex-col gap-1">
        <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">RACE</span>
        <input id="sync-race" type="text" placeholder="e.g. Monaco"
          class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 
  outline-none focus:border-primary-container w-full"/>
      </div>
      <div class="flex flex-col gap-1">
        <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">DRIVER</span>
        <input id="sync-driver" type="text" placeholder="e.g. LEC"
          class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 
  outline-none focus:border-primary-container w-full"/>
      </div>
    </div>
    <div class="flex gap-margin-sm">
      <button onclick="closeSync()"
        class="flex-1 border border-outline-variant text-on-surface-variant text-label-caps font-label-caps py-2 
  hover:border-primary-container transition-colors">
        CANCEL
      </button>
      <button onclick="submitSync()"
        class="flex-1 bg-primary-container text-white text-label-caps font-label-caps py-2 hover:bg-inverse-primary 
  transition-colors">
        CONFIRM
      </button>
    </div>
    <p id="sync-status" class="text-label-caps font-label-caps text-[10px] text-tertiary mt-margin-sm text-center 
  hidden">CONTEXT UPDATED</p>
  </div>

  ---
  Part 4 — New HTML: DATA screen

  Add this as a new screen block after </div><!-- /screen-recording -->:

  <!-- ═══════════════════════════════════════════════════════════
       SCREEN 4 — AUDIT / DATA
  ═══════════════════════════════════════════════════════════ -->
  <div id="screen-data" class="screen">

    <header class="bg-surface flex-shrink-0 flex justify-between items-center w-full px-margin-md h-grid_unit border-b 
  border-outline-variant">
      <div class="flex items-center gap-2">
        <button onclick="showScreen('ready')" class="text-on-surface-variant hover:text-on-surface mr-1">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <span class="text-headline-md font-headline-md font-extrabold text-primary-container uppercase 
  tracking-tighter">GOVERNANCE LOG</span>
      </div>
      <button onclick="loadAudit()" class="text-on-surface-variant hover:text-primary-container transition-colors">
        <span class="material-symbols-outlined">refresh</span>
      </button>
    </header>

    <main class="flex-1 flex flex-col p-margin-md gap-margin-sm pb-4">
      <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">OVERSEER AUDIT TRAIL — MOST RECENT
  FIRST</p>
      <div id="audit-list" class="flex flex-col gap-margin-sm">
        <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">NO AUDIT ENTRIES YET — SUBMIT A
  QUERY FIRST</p>
      </div>
    </main>

    <nav class="flex justify-center items-end pb-4 bg-surface-container-high border-t-2 border-primary-container">
      <button onclick="showScreen('ready')" class="flex flex-col items-center gap-1 bg-primary-container 
  text-on-primary-container rounded-full p-5 -mt-8 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
        <span class="material-symbols-outlined msym-fill" style="font-size:28px;">mic</span>
      </button>
    </nav>

  </div><!-- /screen-data -->

  ---
  Part 5 — JavaScript functions to add

  In the <script> section at the bottom of the file, add these functions:

  // ── SYNC ──────────────────────────────────────────────────────
  function openSync() {
    document.getElementById('sync-year').value  = document.getElementById('ctx-year').textContent.trim();
    document.getElementById('sync-race').value  = document.getElementById('ctx-race').textContent.trim();
    document.getElementById('sync-driver').value = document.getElementById('ctx-driver').textContent.trim();
    document.getElementById('sync-status').classList.add('hidden');
    document.getElementById('syncPanel').classList.add('open');
  }

  function closeSync() {
    document.getElementById('syncPanel').classList.remove('open');
  }

  async function submitSync() {
    const year   = parseInt(document.getElementById('sync-year').value) || 2026;
    const race   = document.getElementById('sync-race').value.trim();
    const driver = document.getElementById('sync-driver').value.trim().toUpperCase();
    if (!race || !driver) return;
    try {
      const res = await fetch('/race-context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year, race, driver })
      });
      if (res.ok) {
        document.getElementById('ctx-year').textContent   = year;
        document.getElementById('ctx-race').textContent   = race.toUpperCase();
        document.getElementById('ctx-driver').textContent = driver;
        const status = document.getElementById('sync-status');
        status.classList.remove('hidden');
        setTimeout(() => { status.classList.add('hidden'); closeSync(); }, 1200);
      }
    } catch(e) { console.error('Sync failed:', e); }
  }

  // ── DATA / AUDIT ──────────────────────────────────────────────
  function showDataScreen() {
    showScreen('data');
    loadAudit();
  }

  async function loadAudit() {
    const list = document.getElementById('audit-list');
    list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">LOADING...</p>';
    try {
      const res     = await fetch('/audit');
      const entries = await res.json();
      if (!entries.length) {
        list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">NO AUDIT ENTRIES
   YET — SUBMIT A QUERY FIRST</p>';
        return;
      }
      list.innerHTML = [...entries].reverse().map(e => `
        <div class="bg-surface-container border border-outline-variant p-margin-sm relative">
          <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
          <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
          <div class="flex justify-between items-center mb-1">
            <span class="text-label-caps font-label-caps text-[10px] ${
              e.hook === 'overseer_decision' ? 'text-primary-container' :
              e.hook === 'anomaly_flag'      ? 'text-error' : 'text-on-surface-variant'
            }">${e.hook.replace(/_/g,' ').toUpperCase()}</span>
            <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">${
              e.timestamp ? e.timestamp.slice(11,19) + ' UTC' : ''
            }</span>
          </div>
          ${e.verdict ? `<p class="text-label-caps font-label-caps text-[10px] font-bold ${
            e.verdict === 'APPROVED' ? 'text-tertiary' :
            e.verdict === 'RETRY'    ? 'text-secondary' : 'text-error'
          }">↳ ${e.verdict}</p>` : ''}
          ${e.failure_reason ? `<p class="text-body-sm font-body-sm text-on-surface-variant text-[10px] mt-1 
  italic">${e.failure_reason}</p>` : ''}
          ${e.data?.signal_type ? `<p class="text-label-caps font-label-caps text-on-surface text-[10px] 
  mt-1">${e.data.signal_type.toUpperCase()}</p>` : ''}
        </div>
      `).join('');
    } catch(e) {
      list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">ERROR REACHING 
  /audit</p>';
    }
  }
</task>
<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:35:01.880Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (//wsl.localhost/Ubuntu/home/shawn/src/ibm_scuderia) Files
.dockerignore
.env.example
.gitignore
app.py
config.py
deploy_cloudrun.sh
Dockerfile
main.py
models.py
pitwall_HAM_it.wav
pitwall_HAM.wav
pitwall_LEC_it.wav
pitwall_LEC.wav
README.md
.bob/
.claude/
.github/
.vscode/
assets/
assets/architecture_diagram.png
assets/architecture_flow.png
assets/governance_loop.png
assets/Pit-Wall_Fan_Orchestrator.png
assets/synthesis_gap.png
assets/trust_output_matrix.png
assets/ui_mockup.png
bob_sessions/
bob_sessions/.gitkeep
bob_sessions/bob_task_may-20-2026_9-20-54-pm.md
bob_sessions/bob_task_may-26-2026_8-44-11-pm.md
bob_sessions/roaming_history/
bob_sessions/roaming_history/IBM_0Uzj.md
bob_sessions/roaming_history/IBM_1pid.md
bob_sessions/roaming_history/IBM_2b0Q.md
bob_sessions/roaming_history/IBM_2bsc.md
bob_sessions/roaming_history/IBM_2vme.md
bob_sessions/roaming_history/IBM_3czL.md
bob_sessions/roaming_history/IBM_3KTF.md
bob_sessions/roaming_history/IBM_3XEm.md
bob_sessions/roaming_history/IBM_4bik.md
bob_sessions/roaming_history/IBM_4bZM.md
bob_sessions/roaming_history/IBM_4Mdu.md
bob_sessions/roaming_history/IBM_4o2N.md
bob_sessions/roaming_history/IBM_4uvA.md
bob_sessions/roaming_history/IBM_4wbN.md
bob_sessions/roaming_history/IBM_4Xhv.md
bob_sessions/roaming_history/IBM_5qRG.md
bob_sessions/roaming_history/IBM_5snO.md
bob_sessions/roaming_history/IBM_5Vgz.md
bob_sessions/roaming_history/IBM_5xBD.md
bob_sessions/roaming_history/IBM_7qTl.md
bob_sessions/roaming_history/IBM_8Bxc.md
bob_sessions/roaming_history/IBM_8cmf.md
bob_sessions/roaming_history/IBM_8wPg.md
bob_sessions/roaming_history/IBM_9kgJ.md
bob_sessions/roaming_history/IBM_9sNK.md
bob_sessions/roaming_history/IBM_23Eh.md
bob_sessions/roaming_history/IBM_56EE.md
bob_sessions/roaming_history/IBM_baZ1.md
bob_sessions/roaming_history/IBM_BBD8.md
bob_sessions/roaming_history/IBM_BH4m.md
bob_sessions/roaming_history/IBM_BiAQ.md
bob_sessions/roaming_history/IBM_bNbJ.md
bob_sessions/roaming_history/IBM_BnKj.md
bob_sessions/roaming_history/IBM_boxh.md
bob_sessions/roaming_history/IBM_BqbC.md
bob_sessions/roaming_history/IBM_bt4B.md
bob_sessions/roaming_history/IBM_bv95.md
bob_sessions/roaming_history/IBM_dd4p.md
bob_sessions/roaming_history/IBM_Dgoo.md
bob_sessions/roaming_history/IBM_DxBB.md
bob_sessions/roaming_history/IBM_dxVq.md
bob_sessions/roaming_history/IBM_eAu7.md
bob_sessions/roaming_history/IBM_EcVX.md
bob_sessions/roaming_history/IBM_eFTO.md
bob_sessions/roaming_history/IBM_eNVt.md
bob_sessions/roaming_history/IBM_EpaU.md
bob_sessions/roaming_history/IBM_EzZQ.md
bob_sessions/roaming_history/IBM_f2kl.md
bob_sessions/roaming_history/IBM_fjtL.md
bob_sessions/roaming_history/IBM_FkDo.md
bob_sessions/roaming_history/IBM_FO6N.md
bob_sessions/roaming_history/IBM_FPlj.md
bob_sessions/roaming_history/IBM_fqRW.md
bob_sessions/roaming_history/IBM_fZKa.md
bob_sessions/roaming_history/IBM_gCUL.md
bob_sessions/roaming_history/IBM_ggjo.md
bob_sessions/roaming_history/IBM_Gnps.md
bob_sessions/roaming_history/IBM_goTj.md
bob_sessions/roaming_history/IBM_h00E.md
bob_sessions/roaming_history/IBM_H5qa.md
bob_sessions/roaming_history/IBM_hElg.md
bob_sessions/roaming_history/IBM_J0Iv.md
bob_sessions/roaming_history/IBM_Jfif.md
bob_sessions/roaming_history/IBM_jqyD.md
bob_sessions/roaming_history/IBM_K4La.md
bob_sessions/roaming_history/IBM_ksgy.md
bob_sessions/roaming_history/IBM_kSJg.md
bob_sessions/roaming_history/IBM_m3AV.md
bob_sessions/roaming_history/IBM_MEpk.md
bob_sessions/roaming_history/IBM_MGyt.md
bob_sessions/roaming_history/IBM_MzSY.md
bob_sessions/roaming_history/IBM_O2uw.md
bob_sessions/roaming_history/IBM_o30A.md
bob_sessions/roaming_history/IBM_O95q.md
bob_sessions/roaming_history/IBM_OlSE.md
bob_sessions/roaming_history/IBM_ot1O.md
bob_sessions/roaming_history/IBM_q97z.md
bob_sessions/roaming_history/IBM_QMOO.md
bob_sessions/roaming_history/IBM_qrAS.md
bob_sessions/roaming_history/IBM_r0Qg.md
bob_sessions/roaming_history/IBM_R3FC.md
bob_sessions/roaming_history/IBM_rhrS.md
bob_sessions/roaming_history/IBM_Rxkw.md
bob_sessions/roaming_history/IBM_s0BQ.md
bob_sessions/roaming_history/IBM_s7ND.md
bob_sessions/roaming_history/IBM_so2B.md
bob_sessions/roaming_history/IBM_ThgV.md
bob_sessions/roaming_history/IBM_tvjQ.md
bob_sessions/roaming_history/IBM_twd1.md
bob_sessions/roaming_history/IBM_U3ti.md
bob_sessions/roaming_history/IBM_Ufdf.md
bob_sessions/roaming_history/IBM_V9iK.md
bob_sessions/roaming_history/IBM_vi6A.md
bob_sessions/roaming_history/IBM_vyfO.md
bob_sessions/roaming_history/IBM_w1hL.md
bob_sessions/roaming_history/IBM_waSq.md
bob_sessions/roaming_history/IBM_wasY.md
bob_sessions/roaming_history/IBM_wBGb.md
bob_sessions/roaming_history/IBM_WD6U.md
bob_sessions/roaming_history/IBM_WOo9.md
bob_sessions/roaming_history/IBM_WRrf.md
bob_sessions/roaming_history/IBM_WZLD.md
bob_sessions/roaming_history/IBM_XKRu.md
bob_sessions/roaming_history/IBM_Y0HO.md
bob_sessions/roaming_history/IBM_YF2y.md
bob_sessions/roaming_history/IBM_YwHG.md
bob_sessions/roaming_history/IBM_YwPe.md
bob_sessions/roaming_history/IBM_Yzn3.md
bob_sessions/roaming_history/IBM_YzUD.md
bob_sessions/roaming_history/IBM_z3X4.md
bob_sessions/roaming_history/IBM_z7h1.md
bob_sessions/roaming_history/IBM_zagt.md
bob_sessions/roaming_history/IBM_ZJ8X.md
bob_sessions/roaming_history/IBM_zJmx.md
chroma_db/
chroma_db/chroma.sqlite3
chroma_db/a8d44d6f-cf9c-4275-862b-3db89948fd7f/
chroma_db/a8d44d6f-cf9c-4275-862b-3db89948fd7f/data_level0.bin
chroma_db/a8d44d6f-cf9c-4275-862b-3db89948fd7f/header.bin
chroma_db/a8d44d6f-cf9c-4275-862b-3db89948fd7f/length.bin
chroma_db/a8d44d6f-cf9c-4275-862b-3db89948fd7f/link_lists.bin
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/data_level0.bin
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/header.bin
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/index_metadata.pickle
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/length.bin
chroma_db/ceeebc53-d98e-4f66-9799-72069802cb99/link_lists.bin
chroma_db/df8bc1b9-ba5d-4843-8077-6cb626b93431/
chroma_db/df8bc1b9-ba5d-4843-8077-6cb626b93431/data_level0.bin
chroma_db/df8bc1b9-ba5d-4843-8077-6cb626b93431/header.bin
chroma_db/df8bc1b9-ba5d-4843-8077-6cb626b93431/length.bin
chroma_db/df8bc1b9-ba5d-4843-8077-6cb626b93431/link_lists.bin
data/
data/fia_2026_section_b_sporting.pdf
data/fia_2026_section_c_technical.pdf
data/pitwall_terminology.py
docs/
docs/01_project_overview.md
docs/02_architecture_diagram_analysis.md
docs/03_sequence_diagram_analysis.md
docs/04_governance_guardrails.md
docs/05_diagram_explanations_plain_english.md
docs/06_final_mermaid_code.md
docs/07_week4_blueprint_design_decisions.md
docs/08_ibm_cloud_migration.md
docs/09_code_engine_cicd_and_secrets.md
docs/10_architectural_overview.md
execution/
execution/__init__.py
execution/execution_module.py
governance/
governance/__init__.py
governance/overseer.py
memory/
memory/__init__.py
memory/docling_loader.py
memory/rag_store.py
orchestrate/
orchestrate/__init__.py
perception/
perception/__init__.py
perception/nlp_synthesizer.py
reasoning/
reasoning/__init__.py
reasoning/agentic_strategist.py
reasoning/planning_engine.py
reasoning/regulation_agent.py
static/
tools/

(File list truncated. Use list_files on specific subdirectories if you need to explore further.)
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you wire up the DASH, DATA, and SYNC icons in static/index.html. Let me start by reading the current file to understand its structure.

<read_file>
<args>
<file>
<path>static/index.html</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'static/index.html'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>static/index.html</path>
<content lines="1-978">
  1 | <!DOCTYPE html>
  2 | <html class="dark" lang="en">
  3 | <head>
  4 | <meta charset="utf-8"/>
  5 | <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  6 | <title>SCUDERIA PIT-WALL</title>
  7 | <link rel="manifest" href="/static/manifest.json">
  8 | <meta name="theme-color" content="#dc0000">
  9 | <meta name="apple-mobile-web-app-capable" content="yes">
 10 | <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
 11 | <meta name="apple-mobile-web-app-title" content="Pit-Wall">
 12 | <link rel="apple-touch-icon" href="/static/icons/icon-192.png">
 13 | <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
 14 | <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;700&family=Barlow+Condensed:wght@700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet"/>
 15 | <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
 16 | <style>
 17 |   .material-symbols-outlined {
 18 |     font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
 19 |   }
 20 |   .msym-fill { font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
 21 | 
 22 |   .scuderia-bracket-tl { border-top: 2px solid #dc0000; border-left: 2px solid #dc0000; width: 8px; height: 8px; position: absolute; top: -1px; left: -1px; }
 23 |   .scuderia-bracket-tr { border-top: 2px solid #dc0000; border-right: 2px solid #dc0000; width: 8px; height: 8px; position: absolute; top: -1px; right: -1px; }
 24 |   .scuderia-bracket-bl { border-bottom: 2px solid #dc0000; border-left: 2px solid #dc0000; width: 8px; height: 8px; position: absolute; bottom: -1px; left: -1px; }
 25 |   .scuderia-bracket-br { border-bottom: 2px solid #dc0000; border-right: 2px solid #dc0000; width: 8px; height: 8px; position: absolute; bottom: -1px; right: -1px; }
 26 | 
 27 |   .bg-grid {
 28 |     background-image: linear-gradient(to right, #1a0907 1px, transparent 1px),
 29 |                       linear-gradient(to bottom, #1a0907 1px, transparent 1px);
 30 |     background-size: 40px 40px;
 31 |   }
 32 | 
 33 |   @keyframes pulse-red {
 34 |     0%   { box-shadow: 0 0 0 0 rgba(220,0,0,0.4); }
 35 |     70%  { box-shadow: 0 0 0 20px rgba(220,0,0,0); }
 36 |     100% { box-shadow: 0 0 0 0 rgba(220,0,0,0); }
 37 |   }
 38 |   .animate-glow { animation: pulse-red 2s infinite; }
 39 | 
 40 |   @keyframes pulse-red-lg {
 41 |     0%   { box-shadow: 0 0 0 0 rgba(220,0,0,0.5); }
 42 |     70%  { box-shadow: 0 0 0 40px rgba(220,0,0,0); }
 43 |     100% { box-shadow: 0 0 0 0 rgba(220,0,0,0); }
 44 |   }
 45 |   .animate-glow-lg { animation: pulse-red-lg 1.5s infinite; }
 46 | 
 47 |   .waveform-bar { width: 3px; background-color: #dc0000; margin: 0 1px; height: 4px; transition: height 0.2s ease; }
 48 | 
 49 |   /* ── Phone frame layout ──────────────────────────────────────────── */
 50 |   html {
 51 |     background-color: #111;
 52 |     background-image: url('/static/tifosi-bg.png');
 53 |     background-size: cover;
 54 |     background-position: center center;
 55 |     background-attachment: fixed;
 56 |   }
 57 |   html::before {
 58 |     content: '';
 59 |     position: fixed;
 60 |     inset: 0;
 61 |     background: transparent;
 62 |     z-index: 0;
 63 |   }
 64 |   
 65 |   #phone-frame {
 66 |     position: relative;
 67 |     z-index: 1;
 68 |     width: 402px;        /* content width + border */
 69 |     height: 872px;
 70 |     margin: 40px auto;
 71 |     border: 14px solid #8c8c8c;
 72 |     border-radius: 48px;
 73 |     overflow: hidden;
 74 |     box-shadow:
 75 |       0 0 0 1px #b4b4b4,
 76 |       inset 0 0 0 1px #5a5a5a,
 77 |       0 32px 80px rgba(0,0,0,0.22);
 78 |   }
 79 | 
 80 |   #app-shell {
 81 |     width: 100%;
 82 |     height: 100%;
 83 |     position: relative;
 84 |     overflow: hidden;
 85 |   }
 86 | 
 87 |   /* Fill viewport on real phones */
 88 |   @media (max-width: 480px) {
 89 |     #phone-frame {
 90 |       width: 100%;
 91 |       height: 100dvh;
 92 |       margin: 0;
 93 |       border: none;
 94 |       border-radius: 0;
 95 |       box-shadow: none;
 96 |     }
 97 |   }
 98 | 
 99 |   /* ── Screen state machine ─────────────────────────────────────────── */
100 |   /* Each screen fills the frame; main scrolls; header+nav stay fixed in flow */
101 |   .screen { display: none; height: 100%; flex-direction: column; overflow: hidden; }
102 |   .screen.active { display: flex; }
103 |   .screen { position: relative; }
104 |   .screen > main { flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch; overscroll-behavior-y: contain; scrollbar-width: none; -ms-overflow-style: none; }
105 |   .screen > main::-webkit-scrollbar { display: none; }
106 |   .scroll-pip { position: absolute; right: 0; width: 1px; height: 24px; background: rgba(220,0,0,0.55); border-radius: 1px; opacity: 0; transition: opacity 0.6s ease; pointer-events: none; z-index: 20; }
107 |   .screen > nav  { flex-shrink: 0; }
108 | 
109 |   /* Governance panel (position:absolute inside screen-response) */
110 |   #governancePanel {
111 |     position: absolute;
112 |     bottom: 0; left: 0; width: 100%;
113 |     max-height: 80%;
114 |     overflow-y: auto;
115 |     transform: translateY(100%);
116 |     transition: transform 0.3s ease;
117 |     z-index: 60;
118 |   }
119 |   #governancePanel.open { transform: translateY(0); }
120 | </style>
121 | <script id="tailwind-config">
122 | tailwind.config = {
123 |   darkMode: "class",
124 |   theme: {
125 |     extend: {
126 |       colors: {
127 |         "surface-bright": "#4a3430",
128 |         "inverse-on-surface": "#412b27",
129 |         "outline-variant": "#5e3f3a",
130 |         "surface-container-lowest": "#1a0907",
131 |         "on-error": "#690005",
132 |         "on-surface-variant": "#e9bcb5",
133 |         "on-primary-container": "#ffece9",
134 |         "error": "#ffb4ab",
135 |         "on-primary": "#690000",
136 |         "surface-container-high": "#3a2521",
137 |         "inverse-surface": "#ffdad5",
138 |         "on-tertiary": "#3d2f00",
139 |         "surface": "#200f0c",
140 |         "primary": "#ffb4a8",
141 |         "surface-dim": "#200f0c",
142 |         "outline": "#af8781",
143 |         "on-background": "#ffdad5",
144 |         "surface-container": "#2e1a17",
145 |         "error-container": "#93000a",
146 |         "primary-fixed": "#ffdad4",
147 |         "surface-variant": "#462f2c",
148 |         "on-secondary-container": "#e1e8ff",
149 |         "surface-container-highest": "#462f2c",
150 |         "inverse-primary": "#c00000",
151 |         "secondary": "#aec6ff",
152 |         "on-surface": "#ffdad5",
153 |         "background": "#200f0c",
154 |         "surface-container-low": "#2a1714",
155 |         "tertiary": "#f1c100",
156 |         "on-secondary": "#002e6b",
157 |         "primary-container": "#dc0000"
158 |       },
159 |       spacing: {
160 |         "gutter": "1px",
161 |         "margin-lg": "24px",
162 |         "margin-xs": "4px",
163 |         "margin-sm": "8px",
164 |         "margin-md": "16px",
165 |         "grid_unit": "40px"
166 |       },
167 |       fontFamily: {
168 |         "headline-lg": ["Barlow Condensed"],
169 |         "headline-md": ["Barlow Condensed"],
170 |         "label-caps":  ["JetBrains Mono"],
171 |         "body-md":     ["Barlow"],
172 |         "data-mono":   ["JetBrains Mono"],
173 |         "body-sm":     ["Barlow"]
174 |       }
175 |     }
176 |   }
177 | }
178 | </script>
179 | </head>
180 | 
181 | <body class="font-body-md selection:bg-primary-container selection:text-white">
182 | 
183 | <!-- Spotlight on white page background -->
184 | <div id="spotlight" style="position:fixed;inset:0;pointer-events:none;z-index:0;"></div>
185 | 
186 | <div id="phone-frame" style="position:relative;z-index:1;">
187 | <div id="app-shell" class="bg-background bg-grid text-on-background">
188 | 
189 | 
190 | <!-- ═══════════════════════════════════════════════════════════
191 |      SCREEN 1 — READY STATE
192 | ═══════════════════════════════════════════════════════════ -->
193 | <div id="screen-ready" class="screen active">
194 | 
195 |   <header class="bg-surface flex justify-between items-center w-full px-margin-md h-grid_unit border-b border-outline-variant flex-shrink-0">
196 |     <span class="text-headline-md font-headline-md font-extrabold text-primary-container uppercase tracking-tighter">SCUDERIA PIT-WALL</span>
197 |     <div class="flex items-center gap-margin-sm">
198 |       <span class="text-label-caps font-label-caps text-on-surface-variant opacity-70">IBM watsonx</span>
199 |       <span class="material-symbols-outlined text-on-surface-variant hover:bg-surface-variant transition-colors duration-150 p-1 cursor-pointer">settings</span>
200 |       <span class="material-symbols-outlined text-on-surface-variant hover:bg-surface-variant transition-colors duration-150 p-1 cursor-pointer">account_circle</span>
201 |     </div>
202 |   </header>
203 | 
204 |   <main class="flex-1 flex flex-col p-margin-md gap-margin-md pb-4">
205 | 
206 |     <!-- Context Row -->
207 |     <div class="grid grid-cols-3 gap-gutter border border-outline-variant bg-outline-variant">
208 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
209 |         <span class="text-label-caps font-label-caps text-on-surface-variant">YEAR</span>
210 |         <span id="ctx-year" class="text-data-mono font-data-mono text-on-surface">2026</span>
211 |       </div>
212 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center border-x border-outline-variant">
213 |         <span class="text-label-caps font-label-caps text-on-surface-variant">RACE</span>
214 |         <span id="ctx-race" class="text-data-mono font-data-mono text-on-surface">MIAMI GP</span>
215 |       </div>
216 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
217 |         <span class="text-label-caps font-label-caps text-on-surface-variant">DRIVER</span>
218 |         <span id="ctx-driver" class="text-data-mono font-data-mono text-primary-container">LECLERC</span>
219 |       </div>
220 |     </div>
221 | 
222 |     <!-- Language + Voice -->
223 |     <div class="flex flex-wrap justify-between items-center gap-2">
224 |       <div class="flex bg-surface-container border border-outline-variant p-1">
225 |         <button onclick="setLang('en')" id="btn-en" class="lang-btn px-3 py-1 text-label-caps font-label-caps bg-primary-container text-white">EN</button>
226 |         <button onclick="setLang('it')" id="btn-it" class="lang-btn px-3 py-1 text-label-caps font-label-caps text-on-surface-variant hover:text-on-surface">IT</button>
227 |       </div>
228 |       <div id="voice-selector" class="flex bg-surface-container border border-outline-variant p-1 gap-1">
229 |         <button onclick="setVoice(this,'allison')" class="voice-btn px-2 py-1 text-label-caps font-label-caps text-[10px] bg-primary-container text-white">ALLISON</button>
230 |         <button onclick="setVoice(this,'michael')" class="voice-btn px-2 py-1 text-label-caps font-label-caps text-[10px] text-on-surface-variant">MICHAEL</button>
231 |         <button onclick="setVoice(this,'george')"  class="voice-btn px-2 py-1 text-label-caps font-label-caps text-[10px] text-on-surface-variant">GEORGE</button>
232 |         <button onclick="setVoice(this,'emma')"    class="voice-btn px-2 py-1 text-label-caps font-label-caps text-[10px] text-on-surface-variant">EMMA</button>
233 |       </div>
234 |     </div>
235 | 
236 |     <!-- Central Mic -->
237 |     <div class="flex-1 flex flex-col items-center justify-center py-margin-lg">
238 |       <div class="relative group cursor-pointer" onclick="toggleMic()">
239 |         <div class="w-32 h-32 rounded-full bg-primary-container flex items-center justify-center animate-glow relative z-10 active:scale-95 transition-transform duration-100">
240 |           <span class="material-symbols-outlined text-white msym-fill" style="font-size:48px;">mic</span>
241 |         </div>
242 |         <div class="absolute -inset-4 border-2 border-dashed border-outline-variant rounded-full opacity-20"></div>
243 |       </div>
244 |       <div class="mt-8 text-center w-full">
245 |         <div class="flex justify-center items-end h-8 mb-2" id="waveform">
246 |           <div class="waveform-bar" style="height:10px;"></div>
247 |           <div class="waveform-bar" style="height:14px;"></div>
248 |           <div class="waveform-bar" style="height:8px;"></div>
249 |           <div class="waveform-bar" style="height:18px;"></div>
250 |           <div class="waveform-bar" style="height:12px;"></div>
251 |           <div class="waveform-bar" style="height:22px;"></div>
252 |           <div class="waveform-bar" style="height:16px;"></div>
253 |           <div class="waveform-bar" style="height:10px;"></div>
254 |         </div>
255 |         <h2 class="text-headline-lg font-headline-lg text-on-surface tracking-widest">AWAITING COMMAND</h2>
256 |         <p class="text-label-caps font-label-caps text-primary-container mt-1">SYSTEM ONLINE / READY TO ANALYZE</p>
257 |       </div>
258 |       <!-- Text input -->
259 |       <div class="w-full max-w-lg mt-6 flex gap-2">
260 |         <input id="text-input" type="text" placeholder="Type your question..."
261 |           class="flex-1 bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 outline-none focus:border-primary-container placeholder:text-on-surface-variant"
262 |           onkeydown="if(event.key==='Enter') submitText()"/>
263 |         <button onclick="submitText()" class="bg-primary-container text-white px-3 py-2 hover:bg-inverse-primary transition-colors">
264 |           <span class="material-symbols-outlined msym-fill" style="font-size:20px;">send</span>
265 |         </button>
266 |       </div>
267 |     </div>
268 | 
269 |     <!-- Bottom modules -->
270 |     <div class="space-y-margin-md">
271 |       <!-- IBM Granite -->
272 |       <section class="bg-surface-container border border-outline-variant p-margin-md relative">
273 |         <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
274 |         <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
275 |         <div class="flex justify-between items-start mb-margin-sm border-b border-outline-variant pb-margin-sm">
276 |           <span class="text-label-caps font-label-caps text-on-surface">ibm/granite-4-h-small</span>
277 |           <span class="text-label-caps font-label-caps text-tertiary">ACTIVE</span>
278 |         </div>
279 |         <div class="grid grid-cols-2 gap-margin-md">
280 |           <div>
281 |             <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">INFERENCE LATENCY</p>
282 |             <p id="latency-ready" class="text-data-mono font-data-mono text-on-surface">--ms</p>
283 |           </div>
284 |           <div>
285 |             <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">RAG INDEX</p>
286 |             <p class="text-data-mono font-data-mono text-on-surface">777 chunks</p>
287 |           </div>
288 |         </div>
289 |         <p class="mt-margin-sm text-body-sm font-body-sm text-on-surface-variant italic">"RAG over FIA 2026 regulations + live race telemetry"</p>
290 |       </section>
291 | 
292 |       <!-- Tyre + Brake -->
293 |       <section class="grid grid-cols-2 gap-gutter bg-outline-variant border border-outline-variant">
294 |         <div class="bg-surface-container p-margin-md flex flex-col gap-2">
295 |           <div class="flex items-center gap-2">
296 |             <span class="material-symbols-outlined text-primary-container" style="font-size:18px;">tire_repair</span>
297 |             <span class="text-label-caps font-label-caps text-on-surface">TYRE DATA</span>
298 |           </div>
299 |           <div class="space-y-1">
300 |             <div class="flex justify-between">
301 |               <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">FL TEMP</span>
302 |               <span class="text-data-mono font-data-mono text-on-surface">94°C</span>
303 |             </div>
304 |             <div class="w-full bg-surface-variant h-1">
305 |               <div class="bg-tertiary h-full w-[85%]"></div>
306 |             </div>
307 |             <div class="flex justify-between">
308 |               <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">WEAR</span>
309 |               <span class="text-data-mono font-data-mono text-on-surface">18%</span>
310 |             </div>
311 |           </div>
312 |         </div>
313 |         <div class="bg-surface-container p-margin-md flex flex-col gap-2">
314 |           <div class="flex items-center gap-2">
315 |             <span class="material-symbols-outlined text-primary-container" style="font-size:18px;">speed</span>
316 |             <span class="text-label-caps font-label-caps text-on-surface">BRAKES</span>
317 |           </div>
318 |           <div class="space-y-1">
319 |             <div class="flex justify-between">
320 |               <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">TEMP</span>
321 |               <span class="text-data-mono font-data-mono text-on-surface">412°C</span>
322 |             </div>
323 |             <div class="w-full bg-surface-variant h-1">
324 |               <div class="bg-primary-container h-full w-[60%]"></div>
325 |             </div>
326 |             <div class="flex justify-between">
327 |               <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">HEALTH</span>
328 |               <span class="text-data-mono font-data-mono text-on-surface">NOMINAL</span>
329 |             </div>
330 |           </div>
331 |         </div>
332 |       </section>
333 |     </div>
334 | 
335 |   </main>
336 | 
337 |   <nav class="flex justify-between items-center px-margin-lg py-margin-sm bg-surface-container-high border-t-2 border-primary-container">
338 |     <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
339 |       <span class="material-symbols-outlined">dashboard</span>
340 |       <span class="text-label-caps font-label-caps">DASH</span>
341 |     </button>
342 |     <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
343 |       <span class="material-symbols-outlined">analytics</span>
344 |       <span class="text-label-caps font-label-caps">DATA</span>
345 |     </button>
346 |     <button onclick="toggleMic()" class="flex flex-col items-center gap-1 bg-primary-container text-on-primary-container rounded-full p-4 -mt-8 scale-110 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
347 |       <span class="material-symbols-outlined msym-fill">sensors</span>
348 |       <span class="text-label-caps font-label-caps">LIVE</span>
349 |     </button>
350 |     <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
351 |       <span class="material-symbols-outlined">sync</span>
352 |       <span class="text-label-caps font-label-caps">SYNC</span>
353 |     </button>
354 |     <button onclick="toggleMic()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
355 |       <span class="material-symbols-outlined">record_voice_over</span>
356 |       <span class="text-label-caps font-label-caps">VOICE</span>
357 |     </button>
358 |   </nav>
359 | 
360 | </div><!-- /screen-ready -->
361 | 
362 | 
363 | <!-- ═══════════════════════════════════════════════════════════
364 |      SCREEN 2 — ACTIVE RECORDING
365 | ═══════════════════════════════════════════════════════════ -->
366 | <div id="screen-recording" class="screen">
367 | 
368 |   <header class="bg-surface flex-shrink-0 flex justify-between items-center w-full px-margin-md h-grid_unit border-b border-primary-container">
369 |     <span class="text-headline-md font-headline-md font-extrabold text-primary-container uppercase tracking-tighter">SCUDERIA PIT-WALL</span>
370 |     <div class="flex items-center gap-2">
371 |       <div class="w-2 h-2 rounded-full bg-primary-container animate-pulse"></div>
372 |       <span class="text-label-caps font-label-caps text-primary-container">RECORDING</span>
373 |     </div>
374 |   </header>
375 | 
376 |   <main class="flex-1 flex flex-col items-center justify-center gap-margin-lg p-margin-md pb-4">
377 | 
378 |     <!-- Context strip -->
379 |     <div class="grid grid-cols-3 gap-gutter border border-outline-variant bg-outline-variant w-full max-w-lg">
380 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
381 |         <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">YEAR</span>
382 |         <span class="text-data-mono font-data-mono text-on-surface text-xs">2026</span>
383 |       </div>
384 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center border-x border-outline-variant">
385 |         <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">RACE</span>
386 |         <span class="text-data-mono font-data-mono text-on-surface text-xs">MIAMI GP</span>
387 |       </div>
388 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
389 |         <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">STT</span>
390 |         <span id="stt-lang" class="text-data-mono font-data-mono text-primary-container text-xs">EN-US</span>
391 |       </div>
392 |     </div>
393 | 
394 |     <!-- Pulsing mic -->
395 |     <div class="relative flex items-center justify-center" style="width:220px;height:220px;">
396 |       <div class="absolute rounded-full bg-primary-container" style="width:200px;height:200px;opacity:0.08;animation:pulse-red-lg 1.2s ease-out infinite;"></div>
397 |       <div class="absolute rounded-full bg-primary-container" style="width:200px;height:200px;opacity:0.08;animation:pulse-red-lg 1.2s ease-out infinite 0.5s;"></div>
398 |       <div class="w-32 h-32 rounded-full bg-primary-container flex items-center justify-center animate-glow-lg relative z-10">
399 |         <span class="material-symbols-outlined text-white msym-fill" style="font-size:52px;">mic</span>
400 |       </div>
401 |     </div>
402 | 
403 |     <!-- Active waveform -->
404 |     <div class="flex justify-center items-end gap-0.5 w-64" style="height:48px;" id="waveform-rec">
405 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
406 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
407 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
408 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
409 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
410 |       <div class="waveform-bar"></div><div class="waveform-bar"></div>
411 |     </div>
412 | 
413 |     <div class="text-center">
414 |       <h2 class="text-headline-lg font-headline-lg text-primary-container tracking-widest">LISTENING...</h2>
415 |       <p class="text-label-caps font-label-caps text-on-surface-variant mt-1">WATSON STT ACTIVE</p>
416 |     </div>
417 | 
418 |     <!-- Live transcript -->
419 |     <div class="w-full max-w-lg bg-surface-container border border-outline-variant p-margin-md relative">
420 |       <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
421 |       <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
422 |       <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-2">TRANSCRIPT</p>
423 |       <p id="live-transcript" class="text-body-sm font-body-sm text-on-surface-variant italic">Awaiting speech input...</p>
424 |     </div>
425 | 
426 |     <!-- Stop -->
427 |     <button onclick="stopRecording()"
428 |       class="border-2 border-primary-container text-primary-container px-8 py-3 text-label-caps font-label-caps tracking-widest hover:bg-primary-container hover:text-white transition-colors">
429 |       STOP &amp; SUBMIT
430 |     </button>
431 | 
432 |   </main>
433 | 
434 | </div><!-- /screen-recording -->
435 | 
436 | 
437 | <!-- ═══════════════════════════════════════════════════════════
438 |      SCREEN 3 — RESPONSE OUTPUT
439 | ═══════════════════════════════════════════════════════════ -->
440 | <div id="screen-response" class="screen" style="position:relative;">
441 | 
442 |   <header class="bg-surface flex-shrink-0 w-full border-b border-outline-variant">
443 |     <div class="flex justify-between items-center w-full px-margin-md h-grid_unit">
444 |       <div class="flex items-center gap-2">
445 |         <button onclick="showScreen('ready')" class="text-on-surface-variant hover:text-on-surface mr-1">
446 |           <span class="material-symbols-outlined">arrow_back</span>
447 |         </button>
448 |         <span class="text-headline-md font-headline-md font-extrabold text-primary-container uppercase tracking-tighter">SCUDERIA PIT-WALL</span>
449 |       </div>
450 |       <div id="response-badge" class="flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-outline text-on-surface-variant">
451 |         <span id="badge-icon" class="material-symbols-outlined msym-fill" style="font-size:14px;">pending</span>
452 |         <span id="badge-text">PROCESSING</span>
453 |       </div>
454 |     </div>
455 |     <div class="px-margin-md py-1 bg-surface-container-low border-t border-outline-variant flex items-center gap-2 overflow-hidden">
456 |       <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px] flex-shrink-0">SESSION: MIAMI GP · LIVE</span>
457 |       <span class="text-on-surface-variant text-[10px] flex-shrink-0">·</span>
458 |       <span id="response-title" class="text-label-caps font-label-caps text-primary-container text-[10px] truncate uppercase">AWAITING RESPONSE</span>
459 |     </div>
460 |   </header>
461 | 
462 |   <main class="flex-1 flex flex-col p-margin-md gap-margin-md pb-4">
463 | 
464 |     <!-- Context row -->
465 |     <div class="grid grid-cols-3 gap-gutter border border-outline-variant bg-outline-variant">
466 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
467 |         <span class="text-label-caps font-label-caps text-on-surface-variant">YEAR</span>
468 |         <span class="text-data-mono font-data-mono text-on-surface">2026</span>
469 |       </div>
470 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center border-x border-outline-variant">
471 |         <span class="text-label-caps font-label-caps text-on-surface-variant">RACE</span>
472 |         <span class="text-data-mono font-data-mono text-on-surface">MIAMI GP</span>
473 |       </div>
474 |       <div class="bg-surface-container p-margin-sm flex flex-col items-center justify-center">
475 |         <span class="text-label-caps font-label-caps text-on-surface-variant">DRIVER</span>
476 |         <span class="text-data-mono font-data-mono text-primary-container">LECLERC</span>
477 |       </div>
478 |     </div>
479 | 
480 |     <!-- AI Narrative -->
481 |     <section class="bg-surface-container border border-outline-variant p-margin-md relative">
482 |       <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
483 |       <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
484 |       <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-margin-sm">IBM GRANITE · ANALYSIS</p>
485 |       <p id="narrative-text" class="text-body-md font-body-md text-on-surface leading-relaxed">
486 |         Routing to IBM watsonx Granite 4-h via /process...
487 |       </p>
488 |     </section>
489 | 
490 |     <!-- Audio player with waveform -->
491 |     <div id="audio-player" style="display:none;"
492 |       class="flex items-center gap-margin-md bg-surface-container border border-outline-variant p-margin-md relative">
493 |       <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
494 |       <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
495 |       <button onclick="togglePlay()"
496 |         class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center flex-shrink-0 hover:bg-inverse-primary transition-colors">
497 |         <span id="play-icon" class="material-symbols-outlined text-white msym-fill" style="font-size:22px;">play_arrow</span>
498 |       </button>
499 |       <div class="flex-1 min-w-0 flex flex-col gap-1">
500 |         <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">WATSON TTS · VOICE OUTPUT</p>
501 |         <p id="tts-label" class="text-data-mono font-data-mono text-on-surface text-sm truncate">TTS: ALLISON EXPRESSIVE</p>
502 |         <div class="flex items-end gap-0.5" style="height:18px;" id="waveform-tts">
503 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
504 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
505 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
506 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
507 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
508 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
509 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
510 |           <div class="waveform-bar"></div><div class="waveform-bar"></div>
511 |         </div>
512 |       </div>
513 |     </div>
514 | 
515 |     <!-- Source citations -->
516 |     <div id="source-citations" style="display:none;" class="flex-col gap-1">
517 |       <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-1">SOURCE CITATIONS</p>
518 |       <div id="source-list" class="flex flex-col gap-1"></div>
519 |     </div>
520 | 
521 |     <!-- New query -->
522 |     <button onclick="showScreen('ready')"
523 |       class="w-full border border-primary-container text-primary-container text-label-caps font-label-caps tracking-widest py-3 hover:bg-primary-container hover:text-white transition-colors">
524 |       NEW QUERY
525 |     </button>
526 | 
527 |   </main>
528 | 
529 |   <!-- Governance handle — sits above the mic nav as a flex child -->
530 |   <div id="governanceHandle" class="flex-shrink-0 flex flex-col items-center cursor-pointer group border-t border-outline-variant" onclick="toggleGovernance()">
531 |     <div class="w-10 h-1 bg-outline-variant rounded-full my-2 group-hover:bg-primary-container transition-colors"></div>
532 |     <div class="w-full py-2 flex justify-center bg-surface-container-highest">
533 |       <span class="text-label-caps font-label-caps text-primary-container tracking-[0.2em]">GOVERNANCE AUDIT</span>
534 |     </div>
535 |   </div>
536 | 
537 |   <!-- Single FAB nav for response screen -->
538 |   <nav class="flex justify-center items-end pb-4 bg-surface-container-high border-t-2 border-primary-container">
539 |     <button onclick="showScreen('ready')" class="flex flex-col items-center gap-1 bg-primary-container text-on-primary-container rounded-full p-5 -mt-8 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
540 |       <span class="material-symbols-outlined msym-fill" style="font-size:28px;">mic</span>
541 |     </button>
542 |   </nav>
543 | 
544 |   <!-- Governance slide panel (position:absolute within screen-response) -->
545 |   <div id="governancePanel" class="bg-surface-container-highest border-t-2 border-primary-container p-margin-md">
546 | 
547 |     <div class="flex justify-center mb-margin-md cursor-pointer" onclick="toggleGovernance()">
548 |       <div class="w-12 h-1 bg-outline-variant rounded-full"></div>
549 |     </div>
550 |     <div class="flex justify-between items-center mb-margin-md">
551 |       <div class="flex items-center gap-2">
552 |         <span class="material-symbols-outlined text-primary-container msym-fill" style="font-size:18px;">security</span>
553 |         <span class="text-label-caps font-label-caps text-on-surface tracking-widest">GOVERNANCE AUDIT</span>
554 |       </div>
555 |       <button onclick="toggleGovernance()" class="text-on-surface-variant hover:text-on-surface">
556 |         <span class="material-symbols-outlined" style="font-size:20px;">close</span>
557 |       </button>
558 |     </div>
559 | 
560 |     <div class="mb-margin-md">
561 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px] mb-2">
562 |         <span class="text-on-surface-variant">CONFIDENCE SCORE</span>
563 |         <span id="conf-value" class="text-on-surface font-bold">--</span>
564 |       </div>
565 |       <div class="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
566 |         <div id="conf-fill" class="bg-primary-container h-full transition-all duration-700 rounded-full" style="width:0%"></div>
567 |       </div>
568 |     </div>
569 | 
570 |     <div class="flex flex-col gap-2 mb-margin-md border border-outline-variant p-margin-sm relative">
571 |       <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
572 |       <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
573 |       <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">OVERSEER PIPELINE — 3 HOOKS</p>
574 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
575 |         <span class="text-on-surface-variant">↳ TRANSCRIPT AUDIT</span>
576 |         <span id="hook1-status" class="text-on-surface-variant">——</span>
577 |       </div>
578 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
579 |         <span class="text-on-surface-variant">↳ RETRIEVAL AUDIT</span>
580 |         <span id="hook2-status" class="text-on-surface-variant">——</span>
581 |       </div>
582 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
583 |         <span class="text-on-surface-variant">↳ PRE-DELIVERY VALIDATION</span>
584 |         <span id="hook3-status" class="text-on-surface-variant">——</span>
585 |       </div>
586 |     </div>
587 | 
588 |     <div class="flex justify-between text-label-caps font-label-caps text-[10px] mb-margin-sm">
589 |       <span class="text-on-surface-variant">INFERENCE LATENCY</span>
590 |       <span id="latency-gov" class="text-on-surface">--ms</span>
591 |     </div>
592 | 
593 |     <div class="flex flex-col gap-1 border-t border-outline-variant pt-margin-sm mb-margin-md">
594 |       <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-1">MODEL LINEAGE</p>
595 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
596 |         <span class="text-on-surface-variant">STT</span><span class="text-on-surface">Watson STT en-US_BroadbandModel</span>
597 |       </div>
598 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
599 |         <span class="text-on-surface-variant">LLM</span><span class="text-on-surface">ibm/granite-4-h-small</span>
600 |       </div>
601 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
602 |         <span class="text-on-surface-variant">TTS</span><span id="gov-tts" class="text-on-surface">Watson TTS AllisonV3</span>
603 |       </div>
604 |       <div class="flex justify-between text-label-caps font-label-caps text-[10px]">
605 |         <span class="text-on-surface-variant">RAG</span><span class="text-on-surface">ChromaDB · 777 chunks · FIA 2026</span>
606 |       </div>
607 |     </div>
608 | 
609 |     <div class="grid grid-cols-2 gap-margin-sm">
610 |       <div class="border border-outline-variant p-margin-sm">
611 |         <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-1">DATA PRIVACY</p>
612 |         <p class="text-label-caps font-label-caps text-[10px]" style="color:#4ade80;">PII CLEAR</p>
613 |       </div>
614 |       <div class="border border-outline-variant p-margin-sm">
615 |         <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px] mb-1">BIAS DETECTION</p>
616 |         <p class="text-label-caps font-label-caps text-[10px]" style="color:#4ade80;">NOMINAL</p>
617 |       </div>
618 |     </div>
619 | 
620 |   </div><!-- /governancePanel -->
621 | 
622 | </div><!-- /screen-response -->
623 | 
624 | 
625 | 
626 | </div><!-- /app-shell -->
627 | </div><!-- /phone-frame -->
628 | 
629 | <script>
630 | // ── State ─────────────────────────────────────────────────────────────────
631 | let currentLang     = 'en';
632 | let currentVoice    = 'allison';
633 | let currentAudio    = null;
634 | let mediaRecorder   = null;
635 | let audioChunks     = [];
636 | let micActive       = false;
637 | let govOpen         = false;
638 | let recWaveInterval = null;
639 | let ttsWaveInterval = null;
640 | let lastQuery       = '';
641 | 
642 | // ── Screens ───────────────────────────────────────────────────────────────
643 | function showScreen(name) {
644 |   document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
645 |   document.getElementById('screen-' + name).classList.add('active');
646 |   if (name !== 'response' && govOpen) toggleGovernance();
647 | }
648 | 
649 | // ── Language ──────────────────────────────────────────────────────────────
650 | function setLang(lang) {
651 |   currentLang = lang;
652 |   document.querySelectorAll('.lang-btn').forEach(b => {
653 |     const active = b.id === 'btn-' + lang;
654 |     b.classList.toggle('bg-primary-container', active);
655 |     b.classList.toggle('text-white', active);
656 |     b.classList.toggle('text-on-surface-variant', !active);
657 |   });
658 |   const vSel = document.getElementById('voice-selector');
659 |   if (vSel) vSel.style.display = lang === 'it' ? 'none' : '';
660 |   const sttEl = document.getElementById('stt-lang');
661 |   if (sttEl) sttEl.textContent = lang === 'it' ? 'IT-IT' : 'EN-US';
662 | }
663 | 
664 | // ── Voice ─────────────────────────────────────────────────────────────────
665 | function setVoice(btn, voice) {
666 |   currentVoice = voice;
667 |   document.querySelectorAll('.voice-btn').forEach(b => {
668 |     b.classList.remove('bg-primary-container', 'text-white');
669 |     b.classList.add('text-on-surface-variant');
670 |   });
671 |   btn.classList.add('bg-primary-container', 'text-white');
672 |   btn.classList.remove('text-on-surface-variant');
673 |   const g = document.getElementById('gov-tts');
674 |   if (g && currentLang === 'en') g.textContent = `Watson TTS ${voice[0].toUpperCase()+voice.slice(1)}V3`;
675 | }
676 | 
677 | // ── Governance bottom sheet ───────────────────────────────────────────────
678 | function toggleGovernance() {
679 |   govOpen = !govOpen;
680 |   document.getElementById('governancePanel').classList.toggle('open', govOpen);
681 | }
682 | 
683 | // ── Recording ─────────────────────────────────────────────────────────────
684 | function toggleMic() {
685 |   if (!micActive) startRecording(); else stopRecording();
686 | }
687 | 
688 | async function startRecording() {
689 |   try {
690 |     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
691 |     audioChunks = [];
692 |     mediaRecorder = new MediaRecorder(stream);
693 |     mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
694 |     mediaRecorder.onstop = async () => {
695 |       stream.getTracks().forEach(t => t.stop());
696 |       const blob = new Blob(audioChunks, { type: 'audio/webm' });
697 |       const b64  = await blobToBase64(blob);
698 |       submitQuery(null, b64);
699 |     };
700 |     mediaRecorder.start(250);
701 |     micActive = true;
702 |     showScreen('recording');
703 |     recWaveInterval = setInterval(() => {
704 |       document.querySelectorAll('#waveform-rec .waveform-bar').forEach(b => {
705 |         b.style.height = (Math.floor(Math.random() * 36) + 4) + 'px';
706 |       });
707 |     }, 120);
708 |   } catch (err) {
709 |     console.warn('[Pit-Wall] Mic denied:', err);
710 |   }
711 | }
712 | 
713 | function stopRecording() {
714 |   micActive = false;
715 |   clearInterval(recWaveInterval);
716 |   if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
717 |   showProcessing('Voice query');
718 |   showScreen('response');
719 | }
720 | 
721 | function blobToBase64(blob) {
722 |   return new Promise(resolve => {
723 |     const reader = new FileReader();
724 |     reader.onload = () => resolve(reader.result.split(',')[1]);
725 |     reader.readAsDataURL(blob);
726 |   });
727 | }
728 | 
729 | // ── Text submit ───────────────────────────────────────────────────────────
730 | function submitText() {
731 |   const q = document.getElementById('text-input').value.trim();
732 |   if (!q) return;
733 |   lastQuery = q;
734 |   document.getElementById('text-input').value = '';
735 |   showProcessing(q);
736 |   showScreen('response');
737 |   submitQuery(q, null);
738 | }
739 | 
740 | // ── Processing state ──────────────────────────────────────────────────────
741 | function showProcessing(label) {
742 |   lastQuery = label || 'Query';
743 |   document.getElementById('response-title').textContent = label ? label.toUpperCase() : 'ANALYZING...';
744 |   document.getElementById('narrative-text').textContent = 'Routing to IBM watsonx Granite 4-h via /process...';
745 | 
746 |   const badge = document.getElementById('response-badge');
747 |   badge.className = 'flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-outline text-on-surface-variant';
748 |   document.getElementById('badge-icon').textContent = 'pending';
749 |   document.getElementById('badge-text').textContent = 'PROCESSING';
750 | 
751 |   document.getElementById('audio-player').style.display   = 'none';
752 |   document.getElementById('source-citations').style.display = 'none';
753 |   stopTtsWave();
754 |   resetHooks();
755 | }
756 | 
757 | // ── API ───────────────────────────────────────────────────────────────────
758 | async function submitQuery(textQuery, audioB64) {
759 |   const body = audioB64
760 |     ? { audio_b64: audioB64, language: currentLang, voice: currentVoice }
761 |     : { text_query: textQuery, language: currentLang, voice: currentVoice };
762 |   const t0 = Date.now();
763 |   try {
764 |     const res = await fetch('/process', {
765 |       method: 'POST',
766 |       headers: { 'Content-Type': 'application/json' },
767 |       body: JSON.stringify(body),
768 |     });
769 |     if (!res.ok) {
770 |       const err = await res.json().catch(() => ({ detail: res.statusText }));
771 |       throw new Error(err.detail || res.statusText);
772 |     }
773 |     const data    = await res.json();
774 |     const elapsed = Date.now() - t0;
775 |     showResponse(data, elapsed);
776 |   } catch (err) {
777 |     showError(err.message);
778 |   }
779 | }
780 | 
781 | function showResponse(data, elapsedMs) {
782 |   document.getElementById('narrative-text').textContent = data.text;
783 |   document.getElementById('latency-gov').textContent    = elapsedMs + 'ms';
784 |   document.getElementById('latency-ready').textContent  = elapsedMs + 'ms';
785 | 
786 |   // Dynamic session title from first words of response
787 |   const words = (data.text || lastQuery).replace(/[^A-Za-z0-9\s]/g, '').trim().toUpperCase();
788 |   document.getElementById('response-title').textContent = words.slice(0, 55) || lastQuery.toUpperCase();
789 | 
790 |   const badge = document.getElementById('response-badge');
791 |   const icon  = document.getElementById('badge-icon');
792 |   const text  = document.getElementById('badge-text');
793 |   if (data.output_type === 'confirmed') {
794 |     badge.className = 'flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-tertiary text-tertiary';
795 |     icon.textContent = 'check_circle'; text.textContent = 'CONFIRMED';
796 |   } else if (data.output_type === 'retry_corrected') {
797 |     badge.className = 'flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-outline text-on-surface';
798 |     icon.textContent = 'refresh'; text.textContent = 'RETRY CORRECTED';
799 |   } else {
800 |     badge.className = 'flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-error text-error';
801 |     icon.textContent = 'warning'; text.textContent = 'UNCERTAINTY';
802 |   }
803 | 
804 |   if (data.traceability_link) {
805 |     const list = document.getElementById('source-list');
806 |     list.innerHTML = '';
807 |     const item = document.createElement('div');
808 |     item.className = 'flex items-center gap-2 bg-surface-container border border-outline-variant p-margin-sm text-label-caps font-label-caps text-[10px]';
809 |     item.innerHTML = `<span class="material-symbols-outlined text-primary-container msym-fill flex-shrink-0" style="font-size:14px;">article</span>`
810 |       + `<span class="text-on-surface-variant break-all">SRC_001 · ${data.traceability_link}</span>`;
811 |     list.appendChild(item);
812 |     const cit = document.getElementById('source-citations');
813 |     cit.style.display = 'flex';
814 |     cit.style.flexDirection = 'column';
815 |   }
816 | 
817 |   if (data.audio_b64) {
818 |     setupAudio(data.audio_b64);
819 |     document.getElementById('tts-label').textContent = currentLang === 'it'
820 |       ? 'TTS: IT-IT FRANCESCAV3'
821 |       : `TTS: ${currentVoice.toUpperCase()} EXPRESSIVE`;
822 |     document.getElementById('audio-player').style.display = 'flex';
823 |   }
824 | 
825 |   updateHooks(data.output_type);
826 | }
827 | 
828 | function showError(msg) {
829 |   document.getElementById('narrative-text').textContent = 'Error: ' + msg;
830 |   const badge = document.getElementById('response-badge');
831 |   badge.className = 'flex items-center gap-1 text-label-caps font-label-caps px-3 py-1 border border-error text-error';
832 |   document.getElementById('badge-icon').textContent = 'error';
833 |   document.getElementById('badge-text').textContent = 'ERROR';
834 | }
835 | 
836 | // ── Governance hooks ──────────────────────────────────────────────────────
837 | function resetHooks() {
838 |   ['hook1-status','hook2-status','hook3-status'].forEach(id => {
839 |     const el = document.getElementById(id);
840 |     el.textContent = '——'; el.style.color = '';
841 |   });
842 |   document.getElementById('conf-value').textContent = '--';
843 |   document.getElementById('conf-fill').style.width  = '0%';
844 | }
845 | 
846 | function updateHooks(outputType) {
847 |   const h1 = document.getElementById('hook1-status');
848 |   const h2 = document.getElementById('hook2-status');
849 |   const h3 = document.getElementById('hook3-status');
850 |   h1.textContent = 'PASS'; h1.style.color = '#4ade80';
851 | 
852 |   if (outputType === 'confirmed') {
853 |     h2.textContent = 'PASS';  h2.style.color = '#4ade80';
854 |     h3.textContent = 'PASS';  h3.style.color = '#4ade80';
855 |     document.getElementById('conf-value').textContent = '0.92';
856 |     document.getElementById('conf-fill').style.width  = '92%';
857 |   } else if (outputType === 'retry_corrected') {
858 |     h2.textContent = 'PASS';  h2.style.color = '#4ade80';
859 |     h3.textContent = 'RETRY'; h3.style.color = '#f1c100';
860 |     document.getElementById('conf-value').textContent = '0.71';
861 |     document.getElementById('conf-fill').style.width  = '71%';
862 |   } else {
863 |     h2.textContent = 'LOW';  h2.style.color = '#f1c100';
864 |     h3.textContent = 'FAIL'; h3.style.color = '#ffb4ab';
865 |     document.getElementById('conf-value').textContent = '0.32';
866 |     document.getElementById('conf-fill').style.width  = '32%';
867 |   }
868 | }
869 | 
870 | // ── Audio ─────────────────────────────────────────────────────────────────
871 | function setupAudio(b64) {
872 |   if (currentAudio) { currentAudio.pause(); currentAudio = null; }
873 |   const bytes = atob(b64);
874 |   const arr   = new Uint8Array(bytes.length);
875 |   for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
876 |   const blob = new Blob([arr], { type: 'audio/wav' });
877 |   currentAudio = new Audio(URL.createObjectURL(blob));
878 |   currentAudio.onended = () => {
879 |     document.getElementById('play-icon').textContent = 'play_arrow';
880 |     stopTtsWave();
881 |   };
882 | }
883 | 
884 | function togglePlay() {
885 |   if (!currentAudio) return;
886 |   if (currentAudio.paused) {
887 |     currentAudio.play();
888 |     document.getElementById('play-icon').textContent = 'pause';
889 |     startTtsWave();
890 |   } else {
891 |     currentAudio.pause();
892 |     document.getElementById('play-icon').textContent = 'play_arrow';
893 |     stopTtsWave();
894 |   }
895 | }
896 | 
897 | function startTtsWave() {
898 |   stopTtsWave();
899 |   ttsWaveInterval = setInterval(() => {
900 |     document.querySelectorAll('#waveform-tts .waveform-bar').forEach(b => {
901 |       b.style.height = (Math.floor(Math.random() * 14) + 2) + 'px';
902 |     });
903 |   }, 100);
904 | }
905 | 
906 | function stopTtsWave() {
907 |   clearInterval(ttsWaveInterval);
908 |   document.querySelectorAll('#waveform-tts .waveform-bar').forEach(b => {
909 |     b.style.height = '4px';
910 |   });
911 | }
912 | 
913 | // ── Custom scroll pip + smooth wheel ─────────────────────────────────────
914 | document.querySelectorAll('.screen > main').forEach(el => {
915 |   const pip = document.createElement('div');
916 |   pip.className = 'scroll-pip';
917 |   el.parentElement.appendChild(pip);
918 | 
919 |   let fadeTimer;
920 |   const PIP_H = 24;
921 | 
922 |   el.addEventListener('scroll', () => {
923 |     if (el.scrollHeight <= el.clientHeight) return;
924 |     const ratio = el.scrollTop / (el.scrollHeight - el.clientHeight);
925 |     pip.style.top = (ratio * (el.clientHeight - PIP_H)) + 'px';
926 |     pip.style.opacity = '1';
927 |     clearTimeout(fadeTimer);
928 |     fadeTimer = setTimeout(() => { pip.style.opacity = '0'; }, 800);
929 |   }, { passive: true });
930 | 
931 |   el.addEventListener('wheel', e => {
932 |     e.preventDefault();
933 |     el.scrollBy({ top: e.deltaY * 0.9, behavior: 'smooth' });
934 |   }, { passive: false });
935 | });
936 | 
937 | // ── Idle waveform (ready screen) ──────────────────────────────────────────
938 | setInterval(() => {
939 |   document.querySelectorAll('#waveform .waveform-bar').forEach(b => {
940 |     b.style.height = (Math.floor(Math.random() * 20) + 4) + 'px';
941 |   });
942 | }, 150);
943 | 
944 | // ── Startup ───────────────────────────────────────────────────────────────
945 | window.addEventListener('load', () => {
946 |   fetch('/race-context', {
947 |     method: 'POST',
948 |     headers: { 'Content-Type': 'application/json' },
949 |     body: JSON.stringify({ year: 2026, race: 'Miami', driver: 'LEC' }),
950 |   })
951 |     .then(r => r.json())
952 |     .then(data => {
953 |       if (data.race && data.year && data.driver) {
954 |         document.getElementById('ctx-year').textContent   = data.year;
955 |         document.getElementById('ctx-race').textContent   = data.race.toUpperCase() + ' GP';
956 |         document.getElementById('ctx-driver').textContent = data.driver === 'LEC' ? 'LECLERC' : data.driver;
957 |       }
958 |     })
959 |     .catch(err => console.error('[Pit-Wall] race context:', err));
960 | });
961 | 
962 | if ('serviceWorker' in navigator) {
963 |   window.addEventListener('load', () => {
964 |     navigator.serviceWorker.register('/service-worker.js')
965 |       .then(reg => console.log('[Pit-Wall] SW registered:', reg.scope))
966 |       .catch(err => console.error('[Pit-Wall] SW failed:', err));
967 |   });
968 | }
969 | 
970 | // ── Mouse spotlight on grid ───────────────────────────────────────────────
971 | const spotlight = document.getElementById('spotlight');
972 | document.addEventListener('mousemove', e => {
973 |   spotlight.style.background = `radial-gradient(400px circle at ${e.clientX}px ${e.clientY}px, rgba(220,0,0,0.05), transparent 70%)`;
974 | });
975 | document.addEventListener('mouseleave', () => { spotlight.style.background = ''; });
976 | </script>
977 | </body>
978 | </html>
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:35:07.974Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.02

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll now implement all the changes to wire up the DASH, DATA, and SYNC icons. Let me create a todo list first to track the work:

<update_todo_list>
<todos>
[ ] Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons
[ ] Part 2: Add CSS for SYNC panel
[ ] Part 3: Add SYNC panel HTML
[ ] Part 4: Add DATA screen HTML
[ ] Part 5: Add JavaScript functions for SYNC and DATA
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:35:15.284Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.10

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons | Pending |
| 2 | Part 2: Add CSS for SYNC panel | Pending |
| 3 | Part 3: Add SYNC panel HTML | Pending |
| 4 | Part 4: Add DATA screen HTML | Pending |
| 5 | Part 5: Add JavaScript functions for SYNC and DATA | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Now I'll implement all the changes in a single apply_diff operation. Let me start with Part 1 - adding onclick handlers to the three navigation buttons:

<apply_diff>
<path>static/index.html</path>
<diff>
<<<<<<< SEARCH
:start_line:337
-------
  <nav class="flex justify-between items-center px-margin-lg py-margin-sm bg-surface-container-high border-t-2 border-primary-container">
    <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">dashboard</span>
      <span class="text-label-caps font-label-caps">DASH</span>
    </button>
    <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">analytics</span>
      <span class="text-label-caps font-label-caps">DATA</span>
    </button>
    <button onclick="toggleMic()" class="flex flex-col items-center gap-1 bg-primary-container text-on-primary-container rounded-full p-4 -mt-8 scale-110 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
      <span class="material-symbols-outlined msym-fill">sensors</span>
      <span class="text-label-caps font-label-caps">LIVE</span>
    </button>
    <button class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">sync</span>
      <span class="text-label-caps font-label-caps">SYNC</span>
    </button>
    <button onclick="toggleMic()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">record_voice_over</span>
      <span class="text-label-caps font-label-caps">VOICE</span>
    </button>
  </nav>
=======
  <nav class="flex justify-between items-center px-margin-lg py-margin-sm bg-surface-container-high border-t-2 border-primary-container">
    <button onclick="showScreen('ready')" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">dashboard</span>
      <span class="text-label-caps font-label-caps">DASH</span>
    </button>
    <button onclick="showDataScreen()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">analytics</span>
      <span class="text-label-caps font-label-caps">DATA</span>
    </button>
    <button onclick="toggleMic()" class="flex flex-col items-center gap-1 bg-primary-container text-on-primary-container rounded-full p-4 -mt-8 scale-110 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
      <span class="material-symbols-outlined msym-fill">sensors</span>
      <span class="text-label-caps font-label-caps">LIVE</span>
    </button>
    <button onclick="openSync()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">sync</span>
      <span class="text-label-caps font-label-caps">SYNC</span>
    </button>
    <button onclick="toggleMic()" class="flex flex-col items-center gap-1 text-on-surface-variant hover:text-primary transition-colors">
      <span class="material-symbols-outlined">record_voice_over</span>
      <span class="text-label-caps font-label-caps">VOICE</span>
    </button>
  </nav>
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'static/index.html'] Result:
<file_write_result>
<path>static/index.html</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:35:31.202Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.17

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons | Pending |
| 2 | Part 2: Add CSS for SYNC panel | Pending |
| 3 | Part 3: Add SYNC panel HTML | Pending |
| 4 | Part 4: Add DATA screen HTML | Pending |
| 5 | Part 5: Add JavaScript functions for SYNC and DATA | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Good! Now let me continue with the remaining changes in a single apply_diff with multiple blocks:

<apply_diff>
<path>static/index.html</path>
<diff>
<<<<<<< SEARCH
:start_line:119
-------
  #governancePanel.open { transform: translateY(0); }
</style>
=======
  #governancePanel.open { transform: translateY(0); }

  #syncPanel {
    position: absolute;
    bottom: 0; left: 0; width: 100%;
    transform: translateY(100%);
    transition: transform 0.3s ease;
    z-index: 80;
  }
  #syncPanel.open { transform: translateY(0); }
</style>
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:622
-------
</div><!-- /screen-response -->



</div><!-- /app-shell -->
=======
</div><!-- /screen-response -->


<!-- ═══════════════════════════════════════════════════════════
     SCREEN 4 — AUDIT / DATA
═══════════════════════════════════════════════════════════ -->
<div id="screen-data" class="screen">

  <header class="bg-surface flex-shrink-0 flex justify-between items-center w-full px-margin-md h-grid_unit border-b border-outline-variant">
    <div class="flex items-center gap-2">
      <button onclick="showScreen('ready')" class="text-on-surface-variant hover:text-on-surface mr-1">
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <span class="text-headline-md font-headline-md font-extrabold text-primary-container uppercase tracking-tighter">GOVERNANCE LOG</span>
    </div>
    <button onclick="loadAudit()" class="text-on-surface-variant hover:text-primary-container transition-colors">
      <span class="material-symbols-outlined">refresh</span>
    </button>
  </header>

  <main class="flex-1 flex flex-col p-margin-md gap-margin-sm pb-4">
    <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">OVERSEER AUDIT TRAIL — MOST RECENT FIRST</p>
    <div id="audit-list" class="flex flex-col gap-margin-sm">
      <p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">NO AUDIT ENTRIES YET — SUBMIT A QUERY FIRST</p>
    </div>
  </main>

  <nav class="flex justify-center items-end pb-4 bg-surface-container-high border-t-2 border-primary-container">
    <button onclick="showScreen('ready')" class="flex flex-col items-center gap-1 bg-primary-container text-on-primary-container rounded-full p-5 -mt-8 shadow-[0_0_15px_rgba(220,0,0,0.5)] border-4 border-background">
      <span class="material-symbols-outlined msym-fill" style="font-size:28px;">mic</span>
    </button>
  </nav>

</div><!-- /screen-data -->


<!-- ── SYNC PANEL ─────────────────────────────────────────── -->
<div id="syncPanel" class="bg-surface-container-highest border-t-2 border-primary-container p-margin-md">
  <div class="flex justify-center mb-margin-md cursor-pointer" onclick="closeSync()">
    <div class="w-12 h-1 bg-outline-variant rounded-full"></div>
  </div>
  <div class="flex justify-between items-center mb-margin-md">
    <div class="flex items-center gap-2">
      <span class="material-symbols-outlined text-primary-container msym-fill" style="font-size:18px;">sync</span>
      <span class="text-label-caps font-label-caps text-on-surface tracking-widest">RACE CONTEXT</span>
    </div>
    <button onclick="closeSync()" class="text-on-surface-variant hover:text-on-surface">
      <span class="material-symbols-outlined" style="font-size:20px;">close</span>
    </button>
  </div>
  <div class="flex flex-col gap-margin-sm mb-margin-md">
    <div class="flex flex-col gap-1">
      <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">YEAR</span>
      <input id="sync-year" type="number"
        class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 outline-none focus:border-primary-container w-full"/>
    </div>
    <div class="flex flex-col gap-1">
      <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">RACE</span>
      <input id="sync-race" type="text" placeholder="e.g. Monaco"
        class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 outline-none focus:border-primary-container w-full"/>
    </div>
    <div class="flex flex-col gap-1">
      <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">DRIVER</span>
      <input id="sync-driver" type="text" placeholder="e.g. LEC"
        class="bg-surface-container border border-outline-variant text-on-surface text-sm font-label-caps px-3 py-2 outline-none focus:border-primary-container w-full"/>
    </div>
  </div>
  <div class="flex gap-margin-sm">
    <button onclick="closeSync()"
      class="flex-1 border border-outline-variant text-on-surface-variant text-label-caps font-label-caps py-2 hover:border-primary-container transition-colors">
      CANCEL
    </button>
    <button onclick="submitSync()"
      class="flex-1 bg-primary-container text-white text-label-caps font-label-caps py-2 hover:bg-inverse-primary transition-colors">
      CONFIRM
    </button>
  </div>
  <p id="sync-status" class="text-label-caps font-label-caps text-[10px] text-tertiary mt-margin-sm text-center hidden">CONTEXT UPDATED</p>
</div>

</div><!-- /app-shell -->
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:975
-------
document.addEventListener('mouseleave', () => { spotlight.style.background = ''; });
</script>
=======
document.addEventListener('mouseleave', () => { spotlight.style.background = ''; });

// ── SYNC ──────────────────────────────────────────────────────
function openSync() {
  document.getElementById('sync-year').value  = document.getElementById('ctx-year').textContent.trim();
  document.getElementById('sync-race').value  = document.getElementById('ctx-race').textContent.trim();
  document.getElementById('sync-driver').value = document.getElementById('ctx-driver').textContent.trim();
  document.getElementById('sync-status').classList.add('hidden');
  document.getElementById('syncPanel').classList.add('open');
}

function closeSync() {
  document.getElementById('syncPanel').classList.remove('open');
}

async function submitSync() {
  const year   = parseInt(document.getElementById('sync-year').value) || 2026;
  const race   = document.getElementById('sync-race').value.trim();
  const driver = document.getElementById('sync-driver').value.trim().toUpperCase();
  if (!race || !driver) return;
  try {
    const res = await fetch('/race-context', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year, race, driver })
    });
    if (res.ok) {
      document.getElementById('ctx-year').textContent   = year;
      document.getElementById('ctx-race').textContent   = race.toUpperCase();
      document.getElementById('ctx-driver').textContent = driver;
      const status = document.getElementById('sync-status');
      status.classList.remove('hidden');
      setTimeout(() => { status.classList.add('hidden'); closeSync(); }, 1200);
    }
  } catch(e) { console.error('Sync failed:', e); }
}

// ── DATA / AUDIT ──────────────────────────────────────────────
function showDataScreen() {
  showScreen('data');
  loadAudit();
}

async function loadAudit() {
  const list = document.getElementById('audit-list');
  list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">LOADING...</p>';
  try {
    const res     = await fetch('/audit');
    const entries = await res.json();
    if (!entries.length) {
      list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">NO AUDIT ENTRIES YET — SUBMIT A QUERY FIRST</p>';
      return;
    }
    list.innerHTML = [...entries].reverse().map(e => `
      <div class="bg-surface-container border border-outline-variant p-margin-sm relative">
        <div class="scuderia-bracket-tl"></div><div class="scuderia-bracket-tr"></div>
        <div class="scuderia-bracket-bl"></div><div class="scuderia-bracket-br"></div>
        <div class="flex justify-between items-center mb-1">
          <span class="text-label-caps font-label-caps text-[10px] ${
            e.hook === 'overseer_decision' ? 'text-primary-container' :
            e.hook === 'anomaly_flag'      ? 'text-error' : 'text-on-surface-variant'
          }">${e.hook.replace(/_/g,' ').toUpperCase()}</span>
          <span class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">${
            e.timestamp ? e.timestamp.slice(11,19) + ' UTC' : ''
          }</span>
        </div>
        ${e.verdict ? `<p class="text-label-caps font-label-caps text-[10px] font-bold ${
          e.verdict === 'APPROVED' ? 'text-tertiary' :
          e.verdict === 'RETRY'    ? 'text-secondary' : 'text-error'
        }">↳ ${e.verdict}</p>` : ''}
        ${e.failure_reason ? `<p class="text-body-sm font-body-sm text-on-surface-variant text-[10px] mt-1 italic">${e.failure_reason}</p>` : ''}
        ${e.data?.signal_type ? `<p class="text-label-caps font-label-caps text-on-surface text-[10px] mt-1">${e.data.signal_type.toUpperCase()}</p>` : ''}
      </div>
    `).join('');
  } catch(e) {
    list.innerHTML = '<p class="text-label-caps font-label-caps text-on-surface-variant text-[10px]">ERROR REACHING /audit</p>';
  }
}
</script>
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'static/index.html'] Result:
<file_write_result>
<path>static/index.html</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:36:13.385Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.25

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons | Pending |
| 2 | Part 2: Add CSS for SYNC panel | Pending |
| 3 | Part 3: Add SYNC panel HTML | Pending |
| 4 | Part 4: Add DATA screen HTML | Pending |
| 5 | Part 5: Add JavaScript functions for SYNC and DATA | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Perfect! All changes have been successfully applied. Let me update the todo list to reflect completion:

<update_todo_list>
<todos>
[x] Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons
[x] Part 2: Add CSS for SYNC panel
[x] Part 3: Add SYNC panel HTML
[x] Part 4: Add DATA screen HTML
[x] Part 5: Add JavaScript functions for SYNC and DATA
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
static\index.html

# VSCode Open Tabs
static/index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-27T18:36:20.237Z
User time zone: America/New_York, UTC-4:00

# Current Cost
$0.34

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Part 1: Add onclick handlers to DASH, DATA, and SYNC buttons | Completed |
| 2 | Part 2: Add CSS for SYNC panel | Completed |
| 3 | Part 3: Add SYNC panel HTML | Completed |
| 4 | Part 4: Add DATA screen HTML | Completed |
| 5 | Part 5: Add JavaScript functions for SYNC and DATA | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Successfully wired DASH, DATA, and SYNC icons in static/index.html with all requested changes:

**Part 1 - Navigation Button Handlers (3 changes):**
- DASH button: Added `onclick="showScreen('ready')"` to navigate back to ready screen
- DATA button: Added `onclick="showDataScreen()"` to open governance log screen
- SYNC button: Added `onclick="openSync()"` to open race context sync panel

**Part 2 - CSS for SYNC Panel:**
- Added `#syncPanel` styles with slide-up animation (translateY transform)
- Added `.open` class for panel visibility

**Part 3 - SYNC Panel HTML:**
- Added slide-up panel with race context form (Year, Race, Driver inputs)
- Includes drag handle, close button, cancel/confirm actions
- Status message for feedback

**Part 4 - DATA Screen HTML:**
- New screen-data with governance log header
- Audit trail list container with loading/empty states
- Single FAB navigation button

**Part 5 - JavaScript Functions:**
- `openSync()` - Populates form with current context and opens panel
- `closeSync()` - Closes sync panel
- `submitSync()` - Posts to /race-context endpoint and updates UI
- `showDataScreen()` - Switches to data screen and loads audit
- `loadAudit()` - Fetches from /audit endpoint and renders entries with color-coded hooks

All changes are frontend-only with no backend modifications required.
</result>
</attempt_completion>

