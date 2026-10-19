(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const input = $("input"), output = $("output");
  const runBtn = $("runBtn"), runLabel = $("runLabel");
  const outPane = $("outPane"), emptyState = $("emptyState");
  const inCount = $("inCount"), outCount = $("outCount");
  const copyBtn = $("copyBtn"), downloadBtn = $("downloadBtn");
  const results = $("results"), metricGrid = $("metricGrid"), warnings = $("warnings");
  const runProvider = $("runProvider"), runTone = $("runTone");
  const statusEl = $("status"), statusText = $("statusText");

  let tone = "academic";
  let busy = false;
  let lastOutput = "";

  const SAMPLE = `Urban green space has emerged as a pivotal element within the contemporary public health landscape, and it is worth noting that a growing body of research has sought to elucidate the mechanisms through which such environments foster wellbeing (Smith, 2020). The utilization of parks and recreational areas has been demonstrated to facilitate robust improvements in both physiological and psychological health outcomes across a myriad of demographic groups. Furthermore, the seamless integration of natural elements into dense urban fabrics has been shown to leverage existing social infrastructure in ways that amplify community cohesion and collective resilience (Jones et al., 2021a).

The relationship between green space exposure and stress reduction has been particularly well documented within the extant literature, with numerous studies reporting significant attenuation of cortisol levels following even brief periods of exposure to vegetated environments. Moreover, the restorative capacity of natural settings has been theorized to operate through attentional mechanisms, whereby the soft fascination elicited by foliage and moving water permits the deliberate cognitive faculties to recover from sustained overuse (Chen and Rao, 2019, p. 45). It is worth noting that this theoretical framework has proven remarkably robust across diverse cultural contexts, although the precise parameters of exposure duration and dosage remain subjects of ongoing empirical negotiation.`;

  /* ---------- helpers ---------- */
  const words = (s) => (s.trim() ? s.trim().split(/\s+/).length : 0);
  const fmtWords = (n) => (n === 1 ? "1 word" : n.toLocaleString() + " words");

  function toast(msg) {
    const t = $("toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove("show"), 2200);
  }

  function updateCounts() {
    inCount.textContent = fmtWords(words(input.value));
    outCount.textContent = fmtWords(words(output.value));
  }

  function setBusy(state) {
    busy = state;
    runBtn.disabled = state;
    runLabel.textContent = state ? "Rewriting…" : "Humanize";
    runBtn.querySelector(".arrow, .spin").outerHTML = state
      ? '<span class="spin" aria-hidden="true"></span>'
      : '<svg class="arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    outPane.classList.toggle("loading", state);
    if (state) emptyState.style.display = "none";
  }

  /* ---------- metrics ---------- */
  function deltaChip(text, kind) {
    return `<span class="delta ${kind}">${text}</span>`;
  }

  function barPct(value, max) {
    return Math.max(2, Math.min(100, (value / max) * 100));
  }

  function metricCard({ label, before, after, display, chip, chipKind, max, sub }) {
    const beforePct = max ? Math.max(1, Math.min(100, (before / max) * 100)) : 0;
    const afterPct = max ? barPct(after, max) : 0;
    return `
      <article class="metric">
        <div class="metric-top">
          <span class="metric-label">${label}</span>
          ${chip ? deltaChip(chip, chipKind) : ""}
        </div>
        <div class="metric-value">
          <span class="before">${display.before}</span>
          <span class="arrow">→</span>
          <span class="after">${display.after}</span>
          ${display.unit ? `<span class="unit">${display.unit}</span>` : ""}
        </div>
        ${max ? `<div class="bar"><span class="bar-fill" style="width:${afterPct}%"></span><span class="bar-tick" style="left:${beforePct}%"></span></div>` : ""}
        <div class="metric-sub">${sub}</div>
      </article>`;
  }

  function renderMetrics(data) {
    const o = data.metrics.original, h = data.metrics.humanized;

    const dBurst = +(h.burstiness - o.burstiness).toFixed(2);
    const dDens = +(h.ai_ism_density - o.ai_ism_density).toFixed(2);
    const wordPct = o.word_count
      ? Math.round(((h.word_count - o.word_count) / o.word_count) * 100)
      : 0;

    const burstKind = dBurst > 0.03 ? "good" : dBurst < -0.03 ? "bad" : "";
    const densKind = dDens < -0.05 ? "good" : dDens > 0.05 ? "bad" : "";
    const wordKind = Math.abs(wordPct) <= 15 ? "good" : "bad";

    metricGrid.innerHTML = [
      metricCard({
        label: "Burstiness",
        before: o.burstiness, after: h.burstiness, max: 1.2,
        display: { before: o.burstiness.toFixed(2), after: h.burstiness.toFixed(2) },
        chip: (dBurst > 0 ? "+" : "") + dBurst.toFixed(2),
        chipKind: burstKind,
        sub: burstKind === "good" ? "sentence rhythm opened up"
           : burstKind === "bad" ? "flatter than before"
           : "rhythm held steady",
      }),
      metricCard({
        label: "AI-isms / 100w",
        before: o.ai_ism_density, after: h.ai_ism_density, max: 8,
        display: { before: o.ai_ism_density.toFixed(2), after: h.ai_ism_density.toFixed(2) },
        chip: (dDens > 0 ? "+" : "") + dDens.toFixed(2),
        chipKind: densKind,
        sub: densKind === "good" ? "buzzwords cleared out"
           : densKind === "bad" ? "new clichés crept in"
           : "no change in density",
      }),
      metricCard({
        label: "Length",
        before: o.word_count, after: h.word_count,
        display: { before: o.word_count.toLocaleString(), after: h.word_count.toLocaleString(), unit: "words" },
        chip: (wordPct > 0 ? "+" : "") + wordPct + "%",
        chipKind: wordKind,
        sub: wordKind === "good" ? "within the ±15% guardrail" : "drifted outside ±15%",
      }),
      metricCard({
        label: "Provider",
        before: 0, after: 0,
        display: { before: "—", after: data.provider },
        chip: "free tier", chipKind: "",
        sub: "same model handled rewrite + check",
      }),
    ].join("");

    runProvider.textContent = data.provider;
    runTone.textContent = tone;

    warnings.innerHTML = "";
    warnings.hidden = false;

    if (data.warnings && data.warnings.length) {
      warnings.classList.remove("ok");
      warnings.innerHTML = `
        <h3><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>
        ${data.warnings.length} thing${data.warnings.length === 1 ? "" : "s"} to check</h3>
        <ul>${data.warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")}</ul>`;
    } else {
      warnings.classList.add("ok");
      warnings.innerHTML = `
        <h3><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="m4 12.5 5 5L20 6.5"/></svg>
        Clean run</h3>
        <ul><li>Every citation, quotation and URL survived the rewrite.</li></ul>`;
    }

    results.hidden = false;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  /* ---------- actions ---------- */
  async function run() {
    if (busy) return;
    const text = input.value.trim();
    if (!text) {
      toast("Paste something first");
      input.focus();
      return;
    }

    setBusy(true);
    try {
      const res = await fetch("/humanize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          tone,
          provider: $("provider").value || null,
          verify: $("verify").checked,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);

      lastOutput = data.humanized || "";
      output.value = lastOutput;
      outPane.classList.add("has-output");
      emptyState.style.display = "none";
      copyBtn.disabled = downloadBtn.disabled = !lastOutput;
      updateCounts();
      renderMetrics(data);
      toast("Done — check the run report");

      if (window.matchMedia("(max-width: 920px)").matches) {
        results.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (err) {
      toast(err.message || "Something went wrong");
      output.value = "";
      lastOutput = "";
      outPane.classList.remove("has-output");
      emptyState.style.display = "";
      copyBtn.disabled = downloadBtn.disabled = true;
      warnings.hidden = false;
      warnings.classList.remove("ok");
      warnings.innerHTML = `<h3>Request failed</h3><ul><li>${escapeHtml(err.message || String(err))}</li></ul>`;
    } finally {
      setBusy(false);
    }
  }

  /* ---------- wiring ---------- */
  document.querySelectorAll(".seg").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".seg").forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-pressed", "true");
      tone = btn.dataset.tone;
    });
  });

  runBtn.addEventListener("click", run);

  input.addEventListener("input", updateCounts);
  input.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      run();
    }
  });

  $("clearBtn").addEventListener("click", () => {
    input.value = "";
    output.value = "";
    lastOutput = "";
    outPane.classList.remove("has-output");
    emptyState.style.display = "";
    copyBtn.disabled = downloadBtn.disabled = true;
    results.hidden = true;
    updateCounts();
    input.focus();
  });

  $("sampleBtn").addEventListener("click", () => {
    input.value = SAMPLE;
    updateCounts();
    input.focus();
    toast("Sample loaded — hit Humanize");
  });

  copyBtn.addEventListener("click", async () => {
    if (!lastOutput) return;
    try {
      await navigator.clipboard.writeText(lastOutput);
      toast("Copied to clipboard");
    } catch {
      output.select();
      document.execCommand("copy");
      toast("Copied");
    }
  });

  downloadBtn.addEventListener("click", () => {
    if (!lastOutput) return;
    const blob = new Blob([lastOutput], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "humanized.txt";
    a.click();
    URL.revokeObjectURL(a.href);
    toast("Saved as humanized.txt");
  });

  /* health check on load */
  (async () => {
    try {
      const r = await fetch("/health");
      if (!r.ok) throw new Error();
      const j = await r.json();
      statusEl.classList.add("ok");
      statusText.textContent = `online · ${j.provider}`;
    } catch {
      statusEl.classList.add("err");
      statusText.textContent = "offline";
    }
  })();

  updateCounts();
})();