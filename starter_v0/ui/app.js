(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const escapeHtml = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));

  async function api(path, options) {
    const res = await fetch(path, options);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.message || body.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  // ---------------- Tabs ----------------
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
      btn.classList.add("active");
      $(`#panel-${btn.dataset.tab}`).classList.remove("hidden");
      if (btn.dataset.tab === "transcripts") loadTranscripts();
      if (btn.dataset.tab === "evals") loadEvals();
    });
  });

  // ---------------- Meta / sidebar ----------------
  async function loadMeta() {
    const meta = await api("/api/meta");
    $("#meta-version").textContent = meta.version;
    $("#meta-artifact").textContent = meta.artifact_version;
    $("#meta-provider").textContent = meta.provider;
    $("#meta-model").textContent = meta.model || "(default)";
    $("#meta-transcript").textContent = meta.transcript_id;
    const list = $("#tools-list");
    list.innerHTML = "";
    meta.tools.forEach((tool) => {
      const li = document.createElement("li");
      li.className = "tool-item";
      li.innerHTML = `
        <div class="tool-name">${escapeHtml(tool.name)}<span class="badge ${tool.category}">${tool.category}</span></div>
        <div class="tool-desc">${escapeHtml(tool.description)}</div>`;
      list.appendChild(li);
    });
  }

  // ---------------- Shared turn renderer ----------------
  function renderToolEvent(event) {
    const result = event.result || {};
    const isError = Boolean(result.error);
    return `
      <div class="tool-call ${isError ? "error" : "ok"}">
        <div class="tool-call-head">
          <span>${escapeHtml(event.tool || event.name)}</span>
          <span>${isError ? "✕ error" : "✓ ok"}</span>
        </div>
        <pre>args: ${escapeHtml(JSON.stringify(event.args ?? {}, null, 2))}</pre>
        <pre>result: ${escapeHtml(JSON.stringify(result, null, 2))}</pre>
      </div>`;
  }

  function renderTurn(turn) {
    const statusClass = turn.status || "answered";
    const rounds = (turn.rounds || [])
      .map((round, idx) => {
        const calls = (round.tool_results || []).map(renderToolEvent).join("");
        return `
          <div class="round-block">
            <div class="round-label">Round ${round.round ?? idx + 1}${round.assistant_text ? " · " + escapeHtml(round.assistant_text) : ""}</div>
            ${calls || '<div style="font-size:12px;color:var(--muted)">(không gọi tool)</div>'}
          </div>`;
      })
      .join("");

    return `
      <div class="msg user"><div class="bubble">${escapeHtml(turn.user)}</div></div>
      <div class="msg assistant">
        <span class="status-chip ${statusClass}">${escapeHtml(statusClass)}</span>
        <div class="bubble">${escapeHtml(turn.assistant_text || turn.error || "(không có phản hồi)")}</div>
        ${rounds ? `<div class="trace">${rounds}</div>` : ""}
      </div>`;
  }

  // ---------------- Live chat ----------------
  const scrollEl = $("#chat-scroll");
  const emptyEl = $("#chat-empty");
  const form = $("#chat-form");
  const input = $("#chat-input");
  const submitBtn = form.querySelector("button");

  function appendTurn(turn) {
    if (emptyEl) emptyEl.remove();
    const wrap = document.createElement("div");
    wrap.innerHTML = renderTurn(turn);
    while (wrap.firstChild) scrollEl.appendChild(wrap.firstChild);
    scrollEl.scrollTop = scrollEl.scrollHeight;
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    input.value = "";
    submitBtn.disabled = true;
    try {
      const turn = await api("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      appendTurn(turn);
    } catch (err) {
      appendTurn({ user: message, status: "provider_error", assistant_text: null, error: err.message, rounds: [] });
    } finally {
      submitBtn.disabled = false;
      input.focus();
    }
  });

  $("#btn-reset").addEventListener("click", async () => {
    await api("/api/reset", { method: "POST" });
    scrollEl.innerHTML = '<div class="empty-state" id="chat-empty">Hội thoại mới — transcript đã được reset.</div>';
    loadMeta();
  });

  // ---------------- Transcripts tab ----------------
  async function loadTranscripts() {
    const { items } = await api("/api/transcripts");
    const listEl = $("#transcript-list");
    listEl.innerHTML = "";
    if (!items.length) {
      listEl.innerHTML = '<div class="empty-state">Chưa có transcript nào được lưu.</div>';
      return;
    }
    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "list-card";
      card.innerHTML = `
        <div class="lc-title"><span>${escapeHtml(item.transcript_id)}</span><span class="version-pill">${escapeHtml(item.version)}</span></div>
        <div class="lc-sub">${escapeHtml(item.provider)} · ${escapeHtml(item.model || "")} · ${item.turns_count} lượt</div>
        <div class="lc-sub">${escapeHtml(item.created_at)} · ${item.source}</div>`;
      card.addEventListener("click", async () => {
        document.querySelectorAll("#transcript-list .list-card").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        try {
          const detail = await api(`/api/transcripts/${encodeURIComponent(item.id)}`);
          renderTranscriptDetail(detail);
        } catch (err) {
          $("#transcript-detail").innerHTML = `<div class="empty-state">Lỗi tải transcript: ${escapeHtml(err.message)}</div>`;
        }
      });
      listEl.appendChild(card);
    });
  }

  function renderTranscriptDetail(data) {
    const detail = $("#transcript-detail");
    const header = `
      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Version</div><div class="stat-value">${escapeHtml(data.version)}</div></div>
        <div class="stat-box"><div class="stat-label">Provider</div><div class="stat-value">${escapeHtml(data.provider)}</div></div>
        <div class="stat-box"><div class="stat-label">Model</div><div class="stat-value">${escapeHtml(data.model || "-")}</div></div>
        <div class="stat-box"><div class="stat-label">Lượt</div><div class="stat-value">${(data.turns || []).length}</div></div>
      </div>`;
    const turns = (data.turns || []).map(renderTurn).join("<hr style='border:none;border-top:1px solid var(--border);margin:16px 0'>");
    detail.innerHTML = header + `<div class="chat-scroll" style="padding:0">${turns || "(chưa có lượt nào)"}</div>`;
  }

  // ---------------- Evals tab ----------------
  async function loadEvals() {
    const { items } = await api("/api/runs");
    const listEl = $("#eval-list");
    listEl.innerHTML = "";
    if (!items.length) {
      listEl.innerHTML = '<div class="empty-state">Chưa có run eval nào trong runs/.</div>';
      return;
    }
    items.forEach((item) => {
      const summary = item.summary || {};
      const card = document.createElement("div");
      card.className = "list-card";
      card.innerHTML = `
        <div class="lc-title"><span>${escapeHtml(item.run_id)}</span><span class="version-pill">${escapeHtml(item.version)}</span></div>
        <div class="lc-sub">${escapeHtml(item.provider)} · ${escapeHtml(item.model || "")}</div>
        <div class="lc-sub">accuracy ${(summary.case_accuracy ?? 0) * 100 | 0}% · errors ${summary.provider_error_cases ?? "-"}</div>`;
      card.addEventListener("click", async () => {
        document.querySelectorAll("#eval-list .list-card").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        const detail = await api(`/api/runs/${encodeURIComponent(item.run_id)}`);
        renderEvalDetail(detail);
      });
      listEl.appendChild(card);
    });
  }

  function statBox(label, value, kind) {
    return `<div class="stat-box ${kind || ""}"><div class="stat-label">${escapeHtml(label)}</div><div class="stat-value">${escapeHtml(value)}</div></div>`;
  }

  function renderEvalDetail(data) {
    const s = data.summary || {};
    const valid = s.provider_error_cases === 0 && s.measured_cases === s.total_cases;
    const header = `
      <div class="stat-grid">
        ${statBox("Total cases", s.total_cases)}
        ${statBox("Measured", s.measured_cases)}
        ${statBox("Provider errors", s.provider_error_cases, s.provider_error_cases ? "err" : "ok")}
        ${statBox("Case accuracy", `${Math.round((s.case_accuracy ?? 0) * 100)}%`)}
        ${statBox("Tool routing", `${Math.round((s.tool_routing_accuracy ?? 0) * 100)}%`)}
        ${statBox("Args accuracy", `${Math.round((s.argument_accuracy ?? 0) * 100)}%`)}
      </div>
      <p style="font-size:12.5px;color:${valid ? "var(--ok)" : "var(--err)"}">
        ${valid ? "✓ Run hợp lệ để làm evidence (provider_error_cases=0, measured=total)." : "✕ Run CHƯA hợp lệ — cần chạy lại (provider_error_cases != 0 hoặc thiếu measured case)."}
      </p>`;

    const rows = (data.results || [])
      .map((item) => {
        const passed = item.result?.passed;
        const calls = JSON.stringify(item.result?.actual_tool_calls ?? [], null, 0);
        return `
          <tr>
            <td>${escapeHtml(item.id)}</td>
            <td class="${passed ? "pass-pill" : "fail-pill"}">${passed ? "PASS" : "FAIL"}</td>
            <td>${escapeHtml(item.result?.failure_type || "-")}</td>
            <td><code style="font-size:11px">${escapeHtml(calls)}</code></td>
          </tr>`;
      })
      .join("");

    const table = `
      <table class="case-table">
        <thead><tr><th>Case</th><th>Kết quả</th><th>Failure type</th><th>Tool calls thực tế</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;

    $("#eval-detail").innerHTML = header + table;
  }

  // ---------------- Init ----------------
  loadMeta().catch((err) => {
    $("#meta-card").innerHTML = `<div style="color:#fca5a5;font-size:12px">Không kết nối được server: ${escapeHtml(err.message)}</div>`;
  });
})();
