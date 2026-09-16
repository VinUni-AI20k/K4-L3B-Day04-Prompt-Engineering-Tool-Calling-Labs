/**
 * Northstar IT Helpdesk AI Agent — Web UI Client Controller
 * Chatbot Output in Center Column | Tool Calls & JSON Outputs in Right Panel
 */

(function () {
  'use strict';

  // --- STATE ---
  const state = {
    version: 'v0',
    provider: 'simulator',
    model: null,
    artifactVersion: '',
    promptHash: '',
    toolsHash: '',
    history: [], // [{role: 'user'|'assistant', content: '...'}]
    turns: [],    // Full transcript turn records
    currentTranscriptId: `web_session_${Date.now()}`,
    toolsRegistry: [],
    evalCases: { base: [], adversarial: [] },
    activeTurn: null,
  };

  // --- ICONS MAP ---
  const TOOL_ICONS = {
    inspect_device: '🔍',
    create_ticket: '🎫',
    check_service_status: '⚙️',
    clarify: '💬',
    lookup_user: '👤',
    search_kb: '📖',
    policy: '🛡️',
    format_incident_report: '📋',
    search_device_info: '🌐',
  };

  // --- DOM ELEMENTS ---
  const elements = {
    versionTabs: document.getElementById('version-tabs'),
    artifactVersionStr: document.getElementById('artifact-version-string'),
    btnCopyHash: document.getElementById('btn-copy-hash'),
    providerSelect: document.getElementById('provider-select'),
    providerStatusDot: document.getElementById('provider-status-dot'),
    btnToggleSidebar: document.getElementById('btn-toggle-sidebar'),
    sidebarDrawer: document.getElementById('sidebar-drawer'),
    promptHashVal: document.getElementById('prompt-hash-val'),
    toolsHashVal: document.getElementById('tools-hash-val'),
    btnViewPrompt: document.getElementById('btn-view-prompt'),
    btnViewTools: document.getElementById('btn-view-tools'),
    chatMessagesContainer: document.getElementById('chat-messages-container'),
    welcomeMessage: document.getElementById('welcome-message'),
    chatForm: document.getElementById('chat-form'),
    userInputField: document.getElementById('user-input-field'),
    btnSendMessage: document.getElementById('btn-send-message'),
    btnClearChat: document.getElementById('btn-clear-chat'),
    btnExportTranscript: document.getElementById('btn-export-transcript'),
    sessionTurnCounter: document.getElementById('session-turn-counter'),
    executionModeBadge: document.getElementById('execution-mode-badge'),
    clarificationPanel: document.getElementById('clarification-panel'),
    clarifyPromptText: document.getElementById('clarify-prompt-text'),
    clarifyOptionsContainer: document.getElementById('clarify-options-container'),
    evalCasesList: document.getElementById('eval-cases-list'),
    transcriptsList: document.getElementById('transcripts-list'),
    toolsRegistryList: document.getElementById('tools-registry-list'),
    btnRefreshTranscripts: document.getElementById('btn-refresh-transcripts'),
    modalOverlay: document.getElementById('modal-overlay'),
    modalTitle: document.getElementById('modal-title'),
    modalCodeBlock: document.getElementById('modal-code-block'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    toastContainer: document.getElementById('toast-container'),

    // Right Panel Elements
    inspectorToolsContainer: document.getElementById('inspector-tools-container'),
    rawTurnJsonCode: document.getElementById('raw-turn-json-code'),
    btnCopyRawJson: document.getElementById('btn-copy-raw-json'),
    metaArtifactVal: document.getElementById('meta-artifact-val'),
    metaPromptHashVal: document.getElementById('meta-prompt-hash-val'),
    metaToolsHashVal: document.getElementById('meta-tools-hash-val'),
    metaProviderVal: document.getElementById('meta-provider-val'),
  };

  // --- INITIALIZATION ---
  async function init() {
    setupEventListeners();
    await fetchSystemInfo();
    await fetchToolsRegistry();
    await fetchEvalCases();
    await fetchTranscripts();
  }

  // --- API CALLS ---
  async function fetchSystemInfo() {
    try {
      const res = await fetch('/api/info');
      if (!res.ok) throw new Error('Cannot fetch system info');
      const data = await res.json();
      
      state.artifactVersion = data.artifact_version;
      state.promptHash = data.prompt_hash;
      state.toolsHash = data.tools_hash;

      elements.artifactVersionStr.textContent = data.artifact_version || 'v0';
      elements.promptHashVal.textContent = data.prompt_hash ? data.prompt_hash.substring(0, 14) + '...' : 'unknown';
      elements.toolsHashVal.textContent = data.tools_hash ? data.tools_hash.substring(0, 14) + '...' : 'unknown';

      // Update right panel metadata
      updateRightPanelMetadata();

      if (data.recommended_provider && elements.providerSelect) {
        state.provider = data.recommended_provider;
        elements.providerSelect.value = data.recommended_provider;
        updateProviderBadge(data.recommended_provider);
      }
    } catch (err) {
      console.warn('System info load error:', err);
    }
  }

  async function fetchToolsRegistry() {
    try {
      const res = await fetch('/api/tools');
      if (!res.ok) return;
      const data = await res.json();
      state.toolsRegistry = data.tools || [];
      renderToolsRegistry(state.toolsRegistry);
    } catch (err) {
      console.warn('Tools fetch error:', err);
    }
  }

  async function fetchEvalCases() {
    try {
      const res = await fetch('/api/eval_cases');
      if (!res.ok) return;
      const data = await res.json();
      const datasets = data.datasets || {};
      state.evalCases.base = datasets['eval_base.json'] || [];
      state.evalCases.adversarial = datasets['eval_adversarial.json'] || [];
      renderEvalCases('base');
    } catch (err) {
      console.warn('Eval cases error:', err);
    }
  }

  async function fetchTranscripts() {
    try {
      const res = await fetch('/api/transcripts');
      if (!res.ok) return;
      const data = await res.json();
      renderTranscriptsList(data.transcripts || []);
    } catch (err) {
      console.warn('Transcripts error:', err);
    }
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // Version Switching
    elements.versionTabs.addEventListener('click', (e) => {
      const btn = e.target.closest('.v-tab');
      if (!btn) return;
      document.querySelectorAll('.v-tab').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.version = btn.dataset.v;
      updateArtifactVersionDisplay();
      updateRightPanelMetadata();
      showToast(`Đã chuyển phiên bản: ${state.version}`);
    });

    // Copy Artifact Version
    elements.btnCopyHash.addEventListener('click', () => {
      navigator.clipboard.writeText(elements.artifactVersionStr.textContent);
      showToast('Đã sao chép mã Artifact Version!');
    });

    // Provider Selector
    elements.providerSelect.addEventListener('change', (e) => {
      state.provider = e.target.value;
      updateProviderBadge(state.provider);
      updateRightPanelMetadata();
      showToast(`Đã chọn provider: ${state.provider}`);
    });

    // Sidebar Toggle
    elements.btnToggleSidebar.addEventListener('click', () => {
      elements.sidebarDrawer.classList.toggle('collapsed');
    });

    // Sidebar Tabs
    document.querySelectorAll('.side-tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.side-tab').forEach((t) => t.classList.remove('active'));
        document.querySelectorAll('.side-panel').forEach((p) => p.classList.remove('active'));
        tab.classList.add('active');
        const targetPanel = document.getElementById(tab.dataset.target);
        if (targetPanel) targetPanel.classList.add('active');
      });
    });

    // Right Inspector Tabs
    document.querySelectorAll('.insp-tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.insp-tab').forEach((t) => t.classList.remove('active'));
        document.querySelectorAll('.insp-panel').forEach((p) => p.classList.remove('active'));
        tab.classList.add('active');
        const targetPanel = document.getElementById(tab.dataset.target);
        if (targetPanel) targetPanel.classList.add('active');
      });
    });

    // Copy Raw JSON in Right Panel
    elements.btnCopyRawJson.addEventListener('click', () => {
      if (elements.rawTurnJsonCode.textContent) {
        navigator.clipboard.writeText(elements.rawTurnJsonCode.textContent);
        showToast('Đã sao chép Raw Turn JSON!');
      }
    });

    // Eval Case Filters
    document.querySelectorAll('.filter-pill').forEach((pill) => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');
        renderEvalCases(pill.dataset.filter);
      });
    });

    // Quick Prompts Chips
    document.querySelectorAll('.prompt-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        elements.userInputField.value = chip.dataset.prompt;
        submitUserMessage();
      });
    });

    // Chat Form Submit
    elements.chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      submitUserMessage();
    });

    // Enter key submit
    elements.userInputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitUserMessage();
      }
    });

    // Clear Chat
    elements.btnClearChat.addEventListener('click', () => {
      if (confirm('Bạn có chắc chắn muốn xóa màn hình trò chuyện?')) {
        clearChat();
      }
    });

    // Export Transcript
    elements.btnExportTranscript.addEventListener('click', () => {
      exportCurrentTranscript();
    });

    // Refresh Transcripts
    elements.btnRefreshTranscripts.addEventListener('click', () => {
      fetchTranscripts();
      showToast('Đã làm mới danh sách transcript.');
    });

    // View System Prompt
    elements.btnViewPrompt.addEventListener('click', async () => {
      openModal('System Prompt (starter_v0/artifacts/system_prompt.md)', 'Đang tải...');
      try {
        const res = await fetch('/api/info');
        const d = await res.json();
        elements.modalCodeBlock.textContent = d.system_prompt_preview || 'Không tìm thấy tệp system_prompt.md';
      } catch (err) {
        elements.modalCodeBlock.textContent = 'Lỗi nạp prompt: ' + err.message;
      }
    });

    // View Tools Yaml
    elements.btnViewTools.addEventListener('click', () => {
      openModal('Tools Declaration (9 Tools)', JSON.stringify(state.toolsRegistry, null, 2));
    });

    // Close Modal
    elements.btnCloseModal.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', (e) => {
      if (e.target === elements.modalOverlay) closeModal();
    });
  }

  // --- CORE CHAT LOGIC ---
  async function submitUserMessage() {
    const text = elements.userInputField.value.trim();
    if (!text) return;

    elements.userInputField.value = '';
    if (elements.welcomeMessage) {
      elements.welcomeMessage.classList.add('hidden');
    }
    hideClarificationBar();

    // 1. Append User Message to Center Chat
    appendUserMessage(text);

    // 2. Add Typing Indicator
    const typingElem = showTypingIndicator();
    elements.btnSendMessage.disabled = true;

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: state.history,
          version: state.version,
          provider: state.provider,
          model: state.model,
          max_tool_rounds: 4,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server status ${response.status}`);
      }

      const data = await response.json();
      typingElem.remove();

      const turn = data.turn;
      state.turns.push(turn);
      state.activeTurn = turn;

      // Update history
      state.history.push({ role: 'user', content: text });
      if (turn.assistant_text) {
        state.history.push({ role: 'assistant', content: turn.assistant_text });
      }

      if (data.artifact_version && data.artifact_version.artifact_version) {
        state.artifactVersion = data.artifact_version.artifact_version;
        elements.artifactVersionStr.textContent = state.artifactVersion;
      }

      // 3. Render Assistant Text Turn in Center Chat
      appendAssistantTurn(turn);

      // 4. Render Tool Calls & JSON in RIGHT PANEL
      renderRightPanelInspector(turn);

      // 5. Handle clarification if needed
      handleClarificationEvents(turn);

      updateTurnCounter();
      scrollToBottom();
    } catch (err) {
      typingElem.remove();
      appendAssistantError(`Lỗi xử lý: ${err.message}`);
    } finally {
      elements.btnSendMessage.disabled = false;
      elements.userInputField.focus();
    }
  }

  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'chat-turn';
    row.innerHTML = `
      <div class="user-message-row">
        <div class="user-bubble">${escapeHtml(text)}</div>
      </div>
    `;
    elements.chatMessagesContainer.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantTurn(turn) {
    const row = document.createElement('div');
    row.className = 'chat-turn';

    const timeStr = turn.ended_at ? turn.ended_at.split('T')[1]?.substring(0, 8) : new Date().toLocaleTimeString();
    const statusClass = `badge-${turn.status || 'answered'}`;
    const statusText = (turn.status || 'ANSWERED').toUpperCase();

    const toolEvents = turn.tool_events || [];
    let toolPillHtml = '';

    if (toolEvents.length > 0) {
      const toolNames = toolEvents.map((e) => e.tool || 'tool').join(', ');
      toolPillHtml = `
        <button class="tool-summary-pill" id="pill-turn-${state.turns.length}" title="Click để xem chi tiết JSON công cụ ở cột phải">
          <span>⚡ ${toolEvents.length} Tool Call: [${escapeHtml(toolNames)}]</span>
          <span class="arrow-icon">📊 Xem JSON ➔</span>
        </button>
      `;
    }

    const assistantTextHtml = turn.assistant_text
      ? `<div class="assistant-bubble">${escapeHtml(turn.assistant_text)}</div>`
      : '';

    row.innerHTML = `
      <div class="assistant-message-row">
        <div class="assistant-meta-header">
          <div class="assistant-avatar">⚡</div>
          <span class="assistant-name">Northstar Agent</span>
          <span class="turn-timestamp">${timeStr}</span>
          <span class="turn-status-badge ${statusClass}">${statusText}</span>
        </div>
        ${assistantTextHtml}
        ${toolPillHtml}
      </div>
    `;

    // Click handler to inspect this turn in the right panel
    row.addEventListener('click', () => {
      state.activeTurn = turn;
      renderRightPanelInspector(turn);
    });

    elements.chatMessagesContainer.appendChild(row);
  }

  // --- RIGHT PANEL JSON INSPECTOR RENDERER ---
  function renderRightPanelInspector(turn) {
    if (!turn) return;

    const toolEvents = turn.tool_events || [];

    // Render Tool Events Cards
    if (toolEvents.length === 0) {
      elements.inspectorToolsContainer.innerHTML = `
        <div class="json-empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-title">Không Có Tool Call Ở Lượt Này</div>
          <p class="empty-desc">Agent trả lời trực tiếp bằng văn bản mà không cần truy vấn công cụ bên ngoài.</p>
        </div>
      `;
    } else {
      elements.inspectorToolsContainer.innerHTML = toolEvents
        .map((event, idx) => renderToolCallCard(event, idx + 1))
        .join('');
      attachCopyEventsInInspector();
    }

    // Render Raw Turn JSON Code Box
    elements.rawTurnJsonCode.textContent = JSON.stringify(turn, null, 2);

    // Update Metadata Panel
    updateRightPanelMetadata();
  }

  function renderToolCallCard(event, index) {
    const toolName = event.tool || 'unknown_tool';
    const icon = TOOL_ICONS[toolName] || '🛠️';
    const args = event.args || {};
    const result = event.result || {};

    let statusPillClass = 'pill-success';
    let statusPillText = 'SUCCESS';
    let boxStatusClass = 'status-success';
    let errorCalloutHtml = '';

    const hasError = result && (result.error || event.error);
    const needsConfirmation = result && result.status === 'needs_confirmation';
    const awaitingUser = result && result.awaiting_user;

    if (hasError) {
      statusPillClass = 'pill-error';
      statusPillText = 'ERROR / REJECTED';
      boxStatusClass = 'status-error';

      const errCode = result.error || event.error;
      const errMsg = result.message || JSON.stringify(result);

      errorCalloutHtml = `
        <div class="error-callout">
          <span class="error-callout-icon">🚨</span>
          <div class="error-callout-content">
            <div class="error-callout-title">LỖI THỰC THI CÔNG CỤ: [${escapeHtml(errCode)}]</div>
            <div class="error-callout-msg">${escapeHtml(errMsg)}</div>
          </div>
        </div>
      `;
    } else if (needsConfirmation) {
      statusPillClass = 'pill-confirm';
      statusPillText = 'NEEDS CONFIRMATION';
      boxStatusClass = 'status-confirm';

      errorCalloutHtml = `
        <div class="confirm-callout">
          <span class="error-callout-icon">⚠️</span>
          <div class="error-callout-content">
            <div class="confirm-callout-title">YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG</div>
            <div class="confirm-callout-msg">${escapeHtml(result.message || 'Hành động ghi cần xác nhận trước khi thực thi.')}</div>
          </div>
        </div>
      `;
    } else if (awaitingUser) {
      statusPillClass = 'pill-confirm';
      statusPillText = 'WAITING USER';
      boxStatusClass = 'status-confirm';
    }

    const argsJson = JSON.stringify(args, null, 2);
    const resultJson = JSON.stringify(result, null, 2);

    return `
      <div class="tool-call-box ${boxStatusClass}" id="tool-call-${index}">
        <div class="tool-call-header">
          <div class="tool-header-left">
            <div class="tool-icon-circle">${icon}</div>
            <span class="tool-name-title">${escapeHtml(toolName)}</span>
          </div>
          <div class="tool-header-right">
            <span class="status-pill ${statusPillClass}">${statusPillText}</span>
          </div>
        </div>

        <div class="tool-call-body">
          <!-- Input Arguments -->
          <div class="tool-section">
            <div class="json-block-title">📥 THAM SỐ INPUT (JSON):</div>
            <div class="json-code-box">
              <pre><code>${escapeHtml(argsJson)}</code></pre>
            </div>
          </div>

          <!-- Error Callout if any -->
          ${errorCalloutHtml}

          <!-- Execution Result -->
          <div class="tool-section">
            <div class="json-block-title">⚡ KẾT QUẢ THỰC THI (RESULT):</div>
            <div class="json-code-box">
              <pre><code>${escapeHtml(resultJson)}</code></pre>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function attachCopyEventsInInspector() {
    elements.inspectorToolsContainer.querySelectorAll('.btn-copy-sm').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const code = btn.dataset.code;
        if (code) {
          navigator.clipboard.writeText(code);
          showToast('Đã sao chép mã!');
        }
      });
    });
  }

  function updateRightPanelMetadata() {
    if (elements.metaArtifactVal) elements.metaArtifactVal.textContent = state.artifactVersion || state.version;
    if (elements.metaPromptHashVal) elements.metaPromptHashVal.textContent = state.promptHash || '...';
    if (elements.metaToolsHashVal) elements.metaToolsHashVal.textContent = state.toolsHash || '...';
    if (elements.metaProviderVal) elements.metaProviderVal.textContent = state.provider ? state.provider.toUpperCase() : 'SIMULATOR';
  }

  function handleClarificationEvents(turn) {
    const toolEvents = turn.tool_events || [];
    for (const event of toolEvents) {
      const res = event.result || {};
      if (res.awaiting_user) {
        const q = res.question || event.args?.question || 'Bạn vui lòng bổ sung thông tin:';
        showClarificationBar(q, event.args);
        return;
      }
    }
  }

  function showClarificationBar(question, args) {
    elements.clarifyPromptText.textContent = question;
    elements.clarifyOptionsContainer.innerHTML = '';

    if (args && args.response_type === 'yes_no') {
      const btnYes = document.createElement('button');
      btnYes.className = 'clarify-opt-btn';
      btnYes.textContent = '✅ Đồng ý (Yes)';
      btnYes.onclick = () => {
        elements.userInputField.value = 'Đồng ý, hãy tạo ticket.';
        submitUserMessage();
      };

      const btnNo = document.createElement('button');
      btnNo.className = 'clarify-opt-btn';
      btnNo.textContent = '❌ Hủy bỏ (No)';
      btnNo.onclick = () => {
        elements.userInputField.value = 'Hủy bỏ, không tạo ticket nữa.';
        submitUserMessage();
      };

      elements.clarifyOptionsContainer.appendChild(btnYes);
      elements.clarifyOptionsContainer.appendChild(btnNo);
    } else if (args && args.options && Array.isArray(args.options)) {
      args.options.forEach((opt) => {
        const btnOpt = document.createElement('button');
        btnOpt.className = 'clarify-opt-btn';
        btnOpt.textContent = `🔹 ${opt}`;
        btnOpt.onclick = () => {
          elements.userInputField.value = opt;
          submitUserMessage();
        };
        elements.clarifyOptionsContainer.appendChild(btnOpt);
      });
    }

    elements.clarificationPanel.classList.remove('hidden');
  }

  function hideClarificationBar() {
    elements.clarificationPanel.classList.add('hidden');
  }

  function appendAssistantError(errorText) {
    const row = document.createElement('div');
    row.className = 'chat-turn';
    row.innerHTML = `
      <div class="assistant-message-row">
        <div class="assistant-meta-header">
          <div class="assistant-avatar" style="background: var(--danger)">⚠️</div>
          <span class="assistant-name">System / Provider Error</span>
        </div>
        <div class="error-callout" style="margin-top: 6px;">
          <div class="error-callout-msg">${escapeHtml(errorText)}</div>
        </div>
      </div>
    `;
    elements.chatMessagesContainer.appendChild(row);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'chat-turn';
    row.id = 'active-typing-row';
    row.innerHTML = `
      <div class="assistant-message-row">
        <div class="assistant-bubble" style="display: flex; align-items: center; gap: 8px;">
          <span class="spinner" style="width: 16px; height: 16px; border: 2px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></span>
          <span style="font-size: 0.85rem; color: var(--text-muted);">Đang hội thoại & xử lý tool call...</span>
        </div>
      </div>
    `;
    elements.chatMessagesContainer.appendChild(row);
    scrollToBottom();
    return row;
  }

  // --- RENDER EVAL CASES ---
  function renderEvalCases(filterKey) {
    const list = state.evalCases[filterKey] || [];
    elements.evalCasesList.innerHTML = '';

    if (list.length === 0) {
      elements.evalCasesList.innerHTML = '<div class="loading-spinner-box">Không có test case nào.</div>';
      return;
    }

    list.forEach((item) => {
      const card = document.createElement('div');
      card.className = 'case-item-card';
      const expectedTool = item.expect?.tool_calls?.[0]?.name || '';

      card.innerHTML = `
        <div class="case-item-header">
          <span class="case-id-tag">${escapeHtml(item.id || 'CASE')}</span>
          ${expectedTool ? `<span class="case-tool-tag">🎯 ${escapeHtml(expectedTool)}</span>` : ''}
        </div>
        <div class="case-prompt-text">${escapeHtml(item.query || '')}</div>
      `;

      card.addEventListener('click', () => {
        elements.userInputField.value = item.query;
        submitUserMessage();
        showToast(`Đang chạy test case: ${item.id}`);
      });

      elements.evalCasesList.appendChild(card);
    });
  }

  // --- RENDER TRANSCRIPTS ---
  function renderTranscriptsList(transcripts) {
    elements.transcriptsList.innerHTML = '';
    if (transcripts.length === 0) {
      elements.transcriptsList.innerHTML = '<div class="loading-spinner-box">Chưa có transcript nào.</div>';
      return;
    }

    transcripts.forEach((t) => {
      const card = document.createElement('div');
      card.className = 'transcript-card';
      const isSample = t.category === 'sample';

      card.innerHTML = `
        <div class="transcript-filename">${escapeHtml(t.name)}</div>
        <div class="transcript-meta">
          <span>${isSample ? '⭐ Mẫu' : '💾 File đã lưu'}</span> •
          <span>${Math.round(t.size / 1024)} KB</span>
        </div>
      `;

      card.addEventListener('click', () => {
        loadTranscriptFromFile(t.name);
      });

      elements.transcriptsList.appendChild(card);
    });
  }

  async function loadTranscriptFromFile(filename) {
    try {
      showToast(`Đang tải transcript: ${filename}...`);
      const res = await fetch(`/api/transcripts/${encodeURIComponent(filename)}`);
      if (!res.ok) throw new Error('Không thể tải tệp transcript');
      const data = await res.json();

      clearChat();
      if (elements.welcomeMessage) elements.welcomeMessage.classList.add('hidden');

      if (data.version) {
        state.version = data.version;
        document.querySelectorAll('.v-tab').forEach((b) => {
          b.classList.toggle('active', b.dataset.v === data.version);
        });
      }

      if (data.artifact_version) {
        state.artifactVersion = data.artifact_version;
        elements.artifactVersionStr.textContent = data.artifact_version;
      }

      const turns = data.turns || [];
      state.turns = turns;
      turns.forEach((turn, idx) => {
        if (turn.user) appendUserMessage(turn.user);
        appendAssistantTurn(turn);
        if (idx === turns.length - 1) {
          state.activeTurn = turn;
          renderRightPanelInspector(turn);
        }
      });

      updateTurnCounter();
      showToast(`Đã nạp transcript với ${turns.length} lượt!`);
    } catch (err) {
      showToast(`Lỗi nạp transcript: ${err.message}`);
    }
  }

  // --- RENDER TOOLS REGISTRY ---
  function renderToolsRegistry(tools) {
    elements.toolsRegistryList.innerHTML = '';
    tools.forEach((tool) => {
      const card = document.createElement('div');
      card.className = 'tool-registry-card';

      card.innerHTML = `
        <div class="tool-registry-name">${TOOL_ICONS[tool.name] || '🛠️'} ${escapeHtml(tool.name)}</div>
        <p class="tool-registry-desc">${escapeHtml(tool.description || '')}</p>
      `;

      elements.toolsRegistryList.appendChild(card);
    });
  }

  // --- EXPORT TRANSCRIPT ---
  async function exportCurrentTranscript() {
    if (state.turns.length === 0) {
      showToast('Chưa có lượt hội thoại nào để xuất transcript.');
      return;
    }

    const payload = {
      transcript_id: state.currentTranscriptId,
      version: state.version,
      artifact_version: state.artifactVersion || `${state.version}+pUNKNOWN+tUNKNOWN`,
      prompt_hash: state.promptHash,
      tools_hash: state.toolsHash,
      provider: state.provider,
      model: state.model,
      created_at: state.turns[0]?.started_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
      turns: state.turns,
    };

    try {
      const res = await fetch('/api/save_transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const saved = await res.json();
        showToast(`Đã lưu transcript: ${saved.filename}`);
        fetchTranscripts();
      }
    } catch (err) {
      console.warn('Server save transcript error:', err);
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.currentTranscriptId}.transcript.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // --- UTILS ---
  function clearChat() {
    state.history = [];
    state.turns = [];
    state.activeTurn = null;
    state.currentTranscriptId = `web_session_${Date.now()}`;
    elements.chatMessagesContainer.innerHTML = '';
    if (elements.welcomeMessage) {
      elements.chatMessagesContainer.appendChild(elements.welcomeMessage);
      elements.welcomeMessage.classList.remove('hidden');
    }
    elements.inspectorToolsContainer.innerHTML = `
      <div class="json-empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">Chưa có dữ liệu Tool Call</div>
        <p class="empty-desc">Gửi tin nhắn hoặc chọn 1 câu hỏi để xem chi tiết JSON arguments và kết quả thực thi ở đây.</p>
      </div>
    `;
    elements.rawTurnJsonCode.textContent = '// Payload JSON lượt chat sẽ hiển thị tại đây...';
    hideClarificationBar();
    updateTurnCounter();
  }

  function updateTurnCounter() {
    const count = state.turns.length;
    elements.sessionTurnCounter.textContent = `${count} lượt hội thoại`;
  }

  function updateArtifactVersionDisplay() {
    const shortPrompt = state.promptHash ? state.promptHash.substring(0, 12) : 'p8a7b';
    const shortTools = state.toolsHash ? state.toolsHash.substring(0, 12) : 't3f1a';
    state.artifactVersion = `${state.version}+p${shortPrompt}+t${shortTools}`;
    elements.artifactVersionStr.textContent = state.artifactVersion;
  }

  function updateProviderBadge(provider) {
    if (elements.executionModeBadge) {
      elements.executionModeBadge.textContent = `Chế độ: ${provider.toUpperCase()}`;
    }
  }

  function scrollToBottom() {
    elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
  }

  function escapeHtml(str) {
    if (typeof str !== 'string') return String(str);
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function showToast(msg) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    elements.toastContainer.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transition = 'opacity 0.4s ease';
      setTimeout(() => t.remove(), 400);
    }, 2800);
  }

  function openModal(title, content) {
    elements.modalTitle.textContent = title;
    elements.modalCodeBlock.textContent = content;
    elements.modalOverlay.classList.remove('hidden');
  }

  function closeModal() {
    elements.modalOverlay.classList.add('hidden');
  }

  document.addEventListener('DOMContentLoaded', init);
})();
