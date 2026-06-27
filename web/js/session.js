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
  const search = document.getElementById('session-search').value.toLowerCase();

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
      <div class="session-topic">${escapeHtml(topic)}</div>
      <div class="session-meta">
        <span>${formatDate(lastActive)}</span>
        <span>${msgCount} 条</span>
      </div>
      ${kwHtml}
    </div>
  `}).join('');

  container.querySelectorAll('.session-item').forEach(el => {
    el.addEventListener('click', () => {
      const sid = el.dataset.id;
      switchSession(sid);
    });
  });
}

async function switchSession(sessionId) {
  // P1-10: 如果正在流式输出，取消旧 stream
  if (State.isStreaming && State.currentReader) {
    try { State.currentReader.cancel(); } catch (_) {}
    State.isStreaming = false;
    document.getElementById('typing-indicator').style.display = 'none';
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
  renderSessionList();

  document.getElementById('chat-archive-header').style.display = 'flex';
  document.querySelector('.input-area').style.display = 'none';
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('messages').innerHTML = '';

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
  const query = input.value.trim();
  const container = document.getElementById('history-results');

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
