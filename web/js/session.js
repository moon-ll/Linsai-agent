/**
 * session.js — 会话管理、历史会话查看、历史搜索
 */

// ============================================
// 会话管理
// ============================================
async function loadSessions() {
  try {
    const data = await apiGet('/api/sessions');
    State.sessions = Array.isArray(data) ? data : [];
    renderSessionList();
  } catch (e) {
    console.error('加载会话失败:', e);
    State.sessions = [];
    renderSessionList();
    showToast('加载会话失败', 'error');
  }
}

function renderSessionList() {
  const container = document.getElementById('session-list');
  const search = (document.getElementById('session-search')?.value || '').toLowerCase();

  let sessions = Array.isArray(State.sessions) ? State.sessions : [];
  if (search) {
    sessions = sessions.filter(s => {
      const topic = (s && typeof s.topic === 'string') ? s.topic : '';
      return topic.toLowerCase().includes(search);
    });
  }

  container.innerHTML = sessions.map(s => {
    const sid = (s && typeof s.session_id === 'string') ? s.session_id : '';
    const topic = (s && typeof s.topic === 'string') ? s.topic : '未命名会话';
    const lastActive = s && s.last_active;
    const msgCount = (s && typeof s.message_count === 'number') ? s.message_count : 0;
    const kws = State.sessionKeywords[sid] || [];
    const kwHtml = kws.length > 0
      ? `<div class="keyword-tags">${kws.slice(0, 4).map(k => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('')}</div>`
      : '';
    return `
    <div class="session-item ${sid === State.currentSessionId && !State.viewingArchive ? 'active' : ''}"
         data-id="${escapeHtml(sid)}">
      <div class="session-item-main">
        <div class="session-topic">${escapeHtml(topic)}</div>
        <div class="session-meta">
          <span>${formatDate(lastActive)}</span>
          <span>${msgCount} 条</span>
        </div>
        ${kwHtml}
      </div>
      <button class="session-delete-btn" title="删除会话" data-id="${escapeHtml(sid)}">✕</button>
    </div>
  `}).join('');

  container.querySelectorAll('.session-item').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.closest('.session-delete-btn')) return;
      const sid = el.dataset.id;
      switchSession(sid);
    });
  });

  container.querySelectorAll('.session-delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const sid = btn.dataset.id;
      const topic = btn.closest('.session-item')?.querySelector('.session-topic')?.textContent || sid;
      if (!confirm(`确定删除会话「${topic}」？\n删除后会备份到 archived/_deleted/。`)) return;
      try {
        const resp = await fetch(`/api/sessions/${encodeURIComponent(sid)}`, { method: 'DELETE' });
        const data = await resp.json();
        if (data.success) {
          showToast('会话已删除', 'success');
          await loadSessions();
          if (State.currentSessionId === sid) {
            State.currentSessionId = null;
            document.getElementById('messages').innerHTML = '';
            document.getElementById('welcome-screen').style.display = 'flex';
          }
        } else {
          showToast(data.error || '删除失败', 'error');
        }
      } catch (e) {
        showToast('删除失败: ' + e.message, 'error');
      }
    });
  });
}

async function switchSession(sessionId) {
  // P1-10: 如果正在流式输出，取消旧 stream
  if (State.isStreaming && State.currentReader) {
    try { State.currentReader.cancel(); } catch (_) {}
    State.isStreaming = false;
    const _typingEl = document.getElementById('typing-indicator');
    if (_typingEl) _typingEl.style.display = 'none';
  }

  State.currentSessionId = sessionId;
  State.viewingArchive = false;
  renderSessionList();

  // Bug fix: 空指针防护
  const archiveHeader = document.getElementById('chat-archive-header');
  if (archiveHeader) archiveHeader.style.display = 'none';
  const inputArea = document.querySelector('.input-area');
  if (inputArea) inputArea.style.display = 'block';
  const welcomeScreen = document.getElementById('welcome-screen');
  if (welcomeScreen) welcomeScreen.style.display = 'none';
  const messagesEl = document.getElementById('messages');
  if (messagesEl) messagesEl.innerHTML = '';

  try {
    const data = await apiGet(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
    State.currentMode = data.mode || 'co-working';
    updateModeBadge(State.currentMode);

    // v6.7.11: review 模式绑定快捷审核按钮
    State.currentReviewProposalId = data.project_id || null;
    renderReviewActionBar();

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.timestamp, false, msg.msg_id);
      });
      scrollToBottom();
      if (data.messages.length > 3) {
        showHistoryHint(data.messages.length);
      }
    } else {
      appendMessage('assistant', `你好，我是林赛。\n\n我们今天聊「${data.topic}」？先画个框图，说说你的整体思路。`, null, false);
    }

    updateStatus(`已加载: ${data.topic || sessionId}`);
  } catch (e) {
    console.error('加载消息失败:', e);
    showToast('加载消息失败', 'error');
  }

  // v3.4: 会话加载后注入林赛主动提醒
  if (typeof injectProactiveOpening === 'function') {
    injectProactiveOpening();
  }

  loadTasks();
}

// ============================================
// 历史会话查看（只读模式）
// ============================================
async function viewArchiveSession(sessionId) {
  State.viewingArchive = true;
  State.currentReviewProposalId = null;
  renderSessionList();
  const bar = document.getElementById('review-action-bar');
  if (bar) bar.style.display = 'none';

  const _archiveHeader = document.getElementById('chat-archive-header');
  if (_archiveHeader) _archiveHeader.style.display = 'flex';
  const _inputArea = document.querySelector('.input-area');
  if (_inputArea) _inputArea.style.display = 'none';
  const _welcomeScreen = document.getElementById('welcome-screen');
  if (_welcomeScreen) _welcomeScreen.style.display = 'none';
  const _messagesEl = document.getElementById('messages');
  if (_messagesEl) _messagesEl.innerHTML = '';

  try {
    const data = await apiGet(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
    document.getElementById('archive-topic').textContent = data.topic || sessionId;
    document.getElementById('archive-meta').textContent = `${data.messages?.length || 0} 条消息 · ${data.mode || 'co-working'}`;

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.timestamp, false, msg.msg_id);
      });
      scrollToBottom();
    } else {
      appendMessage('assistant', '（此会话暂无消息）', null, false);
    }

    updateStatus(`查看历史: ${data.topic || sessionId}`);
  } catch (e) {
    console.error('加载历史失败:', e);
    showToast('加载历史失败', 'error');
  }
}

// ============================================
// 历史搜索
// ============================================
async function searchHistory() {
  const input = document.getElementById('history-search-input');
  if (!input) return;
  const query = input.value.trim();
  const container = document.getElementById('history-results');
  if (!container) return;

  if (!query) {
    container.innerHTML = '<p class="empty">输入关键词搜索历史记录</p>';
    return;
  }

  container.innerHTML = '<p class="empty">◐ 搜索中…</p>';

  try {
    const data = await apiGet(`/api/history?q=${encodeURIComponent(query)}`);
    const results = data.results || [];

    if (results.length === 0) {
      container.innerHTML = '<p class="empty">未找到匹配记录</p>';
      return;
    }

    container.innerHTML = results.map(r => `
      <div class="history-result-item" data-session="${escapeHtml(r.session_id)}">
        <div class="result-topic">${escapeHtml(r.topic)}</div>
        <div class="result-preview">${escapeHtml(r.content_preview)}</div>
        <div class="result-meta">${r.role === 'user' ? '你' : '林赛'} · ${formatDate(r.timestamp)}</div>
      </div>
    `).join('');

    container.querySelectorAll('.history-result-item').forEach(el => {
      el.addEventListener('click', () => {
        const sid = el.dataset.session;
        viewArchiveSession(sid);
      });
    });
  } catch (e) {
    console.error('搜索失败:', e);
    container.innerHTML = '<p class="empty">搜索失败</p>';
  }
}

// ============================================
// 加载会话关键词
// ============================================
async function loadSessionKeywords() {
  for (const s of State.sessions) {
    try {
      const data = await apiGet(`/api/sessions/${encodeURIComponent(s.session_id)}/keywords`);
      State.sessionKeywords[s.session_id] = data.keywords || [];
    } catch (e) {
      State.sessionKeywords[s.session_id] = [];
    }
  }
  renderSessionList();
}

async function createNewSession(topic, mode) {
  try {
    const data = await apiPost('/api/sessions', { topic, mode });
    State.sessions.unshift(data);
    renderSessionList();
    switchSession(data.session_id);
    showToast('会话已创建');
  } catch (e) {
    console.error('创建会话失败:', e);
    showToast('创建会话失败', 'error');
  }
}

// v6.7.11: 根据当前会话模式渲染/隐藏审核快捷按钮
function renderReviewActionBar() {
  const bar = document.getElementById('review-action-bar');
  if (!bar) return;

  // 非 review 模式或只读归档浏览时隐藏
  if (State.viewingArchive || State.currentMode !== 'review' || !State.currentReviewProposalId) {
    bar.style.display = 'none';
    return;
  }

  bar.style.display = 'flex';
  const proposalId = State.currentReviewProposalId;

  const approveBtn = document.getElementById('review-approve-btn');
  const rejectBtn = document.getElementById('review-reject-btn');
  const pauseBtn = document.getElementById('review-pause-btn');

  // 解绑旧事件：克隆替换
  const cloneApprove = approveBtn.cloneNode(true);
  const cloneReject = rejectBtn.cloneNode(true);
  const clonePause = pauseBtn.cloneNode(true);
  approveBtn.parentNode.replaceChild(cloneApprove, approveBtn);
  rejectBtn.parentNode.replaceChild(cloneReject, rejectBtn);
  pauseBtn.parentNode.replaceChild(clonePause, pauseBtn);

  cloneApprove.addEventListener('click', () => handleReviewVerdict(proposalId, 'approve'));
  cloneReject.addEventListener('click', () => handleReviewVerdict(proposalId, 'reject'));
  clonePause.addEventListener('click', () => handleReviewVerdict(proposalId, 'pause'));
}

async function handleReviewVerdict(proposalId, verdict) {
  const labels = {
    approve: { action: '通过并归档', prompt: '请输入批准意见（可选）：', defaultReason: '审核通过，同意归档。' },
    reject: { action: '退回修改', prompt: '请输入修改意见（可选）：', defaultReason: '请根据审核意见继续优化。' },
    pause: { action: '暂停审核', prompt: '请输入暂停原因（可选）：', defaultReason: '稍后处理。' },
  };
  const cfg = labels[verdict];
  const confirmed = await confirmModal(
    `<div class="ta-left">确认<strong>${cfg.action}</strong>？</div>`,
    '确认', '取消'
  );
  if (!confirmed) return;

  const reason = await promptModal(cfg.prompt, cfg.defaultReason);
  if (reason === null) return;

  try {
    showToast('提交审核结论...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/review-verdict`, {
      verdict,
      reason,
    });
    if (result.status !== 'ok') {
      throw new Error(result.error || '审核结论提交失败');
    }
    const toastLabels = { approve: '✓ 已通过并归档', reject: '↩ 已退回优化', pause: '⏸ 已暂停' };
    showToast(toastLabels[verdict], 'success');
    // 归档或暂停后隐藏审核栏
    if (verdict !== 'pause') {
      const bar = document.getElementById('review-action-bar');
      if (bar) bar.style.display = 'none';
    }
    // 刷新生命周期仪表盘
    if (typeof renderLifecycleDashboard === 'function') {
      renderLifecycleDashboard();
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// v3.5.1: 注册模块初始化
// session.js 无独立 bind 函数，事件绑定在 app.js bindEvents() 中完成
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('session', () => {
    // 会话模块事件绑定由 app.js 统一处理，此处保留接口供未来迁移
  });
}
