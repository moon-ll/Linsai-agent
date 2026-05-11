/**
 * LinSai-CoPilot Web 前端逻辑
 * 零框架依赖，原生 JavaScript
 */

// ============================================
// 全局状态
// ============================================
const State = {
  currentSessionId: null,
  currentMode: 'co-working',
  sessions: [],
  tasks: [],
  isStreaming: false,
  theme: localStorage.getItem('linsai-theme') || 'auto',
  autonomy: localStorage.getItem('linsai-autonomy') || 'suggest',
  viewingArchive: false,  // 是否正在查看历史会话
  sessionKeywords: {},    // 缓存会话关键词
};

const API_BASE = '';

// ============================================
// 主题管理
// ============================================
function applyTheme(theme) {
  const html = document.documentElement;
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  } else {
    html.setAttribute('data-theme', theme);
  }
  State.theme = theme;
  localStorage.setItem('linsai-theme', theme);

  // 更新按钮图标
  const btn = document.getElementById('theme-toggle');
  btn.textContent = html.getAttribute('data-theme') === 'dark' ? '🌙' : '🔆';
}

function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

// ============================================
// 工具函数
// ============================================
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

/**
 * 轻量级 Markdown 渲染器
 * 支持：段落、粗体、斜体、代码块、行内代码、列表、引用、链接
 */
function renderMarkdown(text) {
  if (!text) return '';

  let html = escapeHtml(text);

  // 代码块
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
  });

  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // 斜体
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // 引用
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

  // 无序列表
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>');

  // 有序列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // 段落（按空行分段）
  const paragraphs = html.split(/\n\n+/);
  html = paragraphs.map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<') && !p.startsWith('<li>')) return p;
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('');

  return html;
}

// ============================================
// Toast 提醒
// ============================================
function showToast(message, type = 'success', duration = 3000) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(30px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ============================================
// API 请求
// ============================================
async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ============================================
// 模态框
// ============================================
function showModal(htmlContent) {
  let overlay = document.getElementById('modal-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'modal-overlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML = '<div class="modal" id="modal-content"></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();
    });
  }
  document.getElementById('modal-content').innerHTML = htmlContent;
  overlay.style.display = 'flex';
}

function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.style.display = 'none';
}

// ============================================
// 会话管理
// ============================================
async function loadSessions() {
  try {
    State.sessions = await apiGet('/api/sessions');
    renderSessionList();
  } catch (e) {
    console.error('加载会话失败:', e);
    showToast('加载会话失败', 'error');
  }
}

function renderSessionList() {
  const container = document.getElementById('session-list');
  const search = document.getElementById('session-search').value.toLowerCase();

  let sessions = State.sessions;
  if (search) {
    sessions = sessions.filter(s =>
      (s.topic || '').toLowerCase().includes(search)
    );
  }

  container.innerHTML = sessions.map(s => {
    const kws = State.sessionKeywords[s.session_id] || [];
    const kwHtml = kws.length > 0
      ? `<div class="keyword-tags">${kws.slice(0, 4).map(k => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('')}</div>`
      : '';
    return `
    <div class="session-item ${s.session_id === State.currentSessionId && !State.viewingArchive ? 'active' : ''}"
         data-id="${escapeHtml(s.session_id)}">
      <div class="session-topic">${escapeHtml(s.topic || '未命名会话')}</div>
      <div class="session-meta">
        <span>${formatDate(s.last_active)}</span>
        <span>${s.message_count || 0} 条</span>
      </div>
      ${kwHtml}
    </div>
  `}).join('');

  // 绑定点击事件 — 点击会话列表 = 续接对话（不是只读浏览）
  container.querySelectorAll('.session-item').forEach(el => {
    el.addEventListener('click', () => {
      const sid = el.dataset.id;
      switchSession(sid);
    });
  });
}

async function switchSession(sessionId) {
  State.currentSessionId = sessionId;
  State.viewingArchive = false;
  renderSessionList();

  // 隐藏归档头部，显示输入区
  document.getElementById('chat-archive-header').style.display = 'none';
  document.querySelector('.input-area').style.display = 'block';

  // 隐藏欢迎页
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('messages').innerHTML = '';

  // 加载消息
  try {
    const data = await apiGet(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
    State.currentMode = data.mode || 'co-working';
    updateModeBadge(State.currentMode);

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.timestamp, false, msg.msg_id);
      });
      scrollToBottom();
      // 消息较多时显示历史提示
      if (data.messages.length > 3) {
        showHistoryHint(data.messages.length);
      }
    } else {
      // 空会话显示欢迎语
      appendMessage('assistant', `你好，我是林赛。\n\n我们今天聊「${data.topic}」？先画个框图，说说你的整体思路。`, null, false);
    }

    updateStatus(`已加载: ${data.topic || sessionId}`);
  } catch (e) {
    console.error('加载消息失败:', e);
    showToast('加载消息失败', 'error');
  }

  // 加载任务
  loadTasks();
}

// ============================================
// 历史会话查看（只读模式）
// ============================================
async function viewArchiveSession(sessionId) {
  State.viewingArchive = true;
  renderSessionList();

  // 显示归档头部，隐藏输入区
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

function backToCurrentSession() {
  if (State.currentSessionId) {
    State.viewingArchive = false;
    switchSession(State.currentSessionId);
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

// ============================================
// 消息渲染
// ============================================
function appendMessage(role, content, timestamp, animate = true, msgId = null) {
  const container = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  if (msgId) div.dataset.msgId = msgId;

  const avatar = role === 'user' ? '你' : '林';
  const time = timestamp ? formatTime(timestamp) : formatTime(new Date().toISOString());

  // 只有用户消息显示编辑/删除按钮
  const actions = role === 'user' && msgId ? `
    <div class="message-actions">
      <button class="msg-action-btn" data-action="edit">编辑</button>
      <button class="msg-action-btn" data-action="delete">删除</button>
    </div>
  ` : '';

  div.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div>
      <div class="message-bubble">${renderMarkdown(content)}</div>
      ${actions}
      <div class="message-time">${time}</div>
    </div>
  `;

  if (!animate) {
    div.style.animation = 'none';
  }

  // 绑定操作按钮事件
  if (msgId) {
    div.querySelectorAll('.msg-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'edit') openEditMessage(msgId, content);
        if (action === 'delete') deleteMessage(msgId);
      });
    });
  }

  container.appendChild(div);
  scrollToBottom();
  return div;
}

function scrollToBottom() {
  const container = document.getElementById('messages');
  container.scrollTop = container.scrollHeight;
}

// ============================================
// SSE 流式发送消息
// ============================================
async function sendMessage(content) {
  if (!State.currentSessionId) {
    showToast('请先创建或选择一个会话', 'warning');
    return;
  }
  if (State.isStreaming) {
    showToast('林赛正在回复，请稍候', 'warning');
    return;
  }
  if (!content.trim()) return;

  // 显示用户消息
  appendMessage('user', content);
  document.getElementById('message-input').value = '';

  // 显示打字指示器
  State.isStreaming = true;
  document.getElementById('typing-indicator').style.display = 'flex';
  updateStatus('林赛正在思考…');

  // 创建林赛消息占位
  const assistantDiv = appendMessage('assistant', '', null, true);
  const bubble = assistantDiv.querySelector('.message-bubble');
  bubble.innerHTML = ''; // 清空，准备流式填充

  // 超时保护：120 秒后强制重置
  const STREAM_TIMEOUT_MS = 120000;
  let streamTimeoutId = null;

  try {
    const res = await fetch(API_BASE + `/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, mode: State.currentMode }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';
    let streamDone = false;

    // 设置超时
    streamTimeoutId = setTimeout(() => {
      if (!streamDone) {
        console.warn('[SSE] 流超时，强制结束');
        try { reader.cancel(); } catch (_) {}
        State.isStreaming = false;
        document.getElementById('typing-indicator').style.display = 'none';
        updateStatus('响应超时');
        showToast('林赛响应超时，请重试', 'error');
      }
    }, STREAM_TIMEOUT_MS);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const dataStr = line.slice(6);
        if (dataStr === '[DONE]') continue;

        try {
          const data = JSON.parse(dataStr);
          if (data.type === 'token') {
            fullText += data.content;
            bubble.innerHTML = renderMarkdown(fullText);
            scrollToBottom();
          } else if (data.type === 'tools') {
            // 显示工具调用提示
            const calls = data.calls || [];
            const toolNames = calls.map(c => c.name).join(', ');
            const hint = document.createElement('div');
            hint.className = 'tool-call-hint';
            hint.innerHTML = `🔧 调用工具: ${escapeHtml(toolNames)}`;
            hint.style.cssText = 'font-size:0.75rem;color:var(--text-tertiary);padding:4px 12px;background:var(--bg-secondary);border-radius:12px;margin-bottom:8px;display:inline-block;';
            const bubbleContainer = bubble.parentElement;
            if (bubbleContainer && !bubbleContainer.querySelector('.tool-call-hint')) {
              bubbleContainer.insertBefore(hint, bubble);
            }
          } else if (data.type === 'done') {
            streamDone = true;
            break; // 收到 done 立即退出，不等待连接关闭
          } else if (data.type === 'error') {
            throw new Error(data.message);
          }
        } catch (e) {
          if (e.message && e.message !== 'Unexpected end of JSON input') {
            console.warn('[SSE] 解析异常:', e.message);
          }
        }
      }

      if (streamDone) break;
    }

    // 最终渲染确保 Markdown 完整解析
    bubble.innerHTML = renderMarkdown(fullText);
    updateStatus('就绪');

    // 刷新会话列表（更新消息数）
    loadSessions();

  } catch (e) {
    console.error('发送消息失败:', e);
    bubble.innerHTML = `<p style="color:var(--error-color)">✗ 发送失败: ${escapeHtml(e.message)}</p>`;
    updateStatus('发送失败');
  } finally {
    if (streamTimeoutId) clearTimeout(streamTimeoutId);
    State.isStreaming = false;
    document.getElementById('typing-indicator').style.display = 'none';
    console.log('[SSE] 流已结束，状态已重置');
  }
}

// ============================================
// 文件上传
// ============================================
async function uploadFiles(files) {
  if (!files || files.length === 0) return;

  const progressBar = document.getElementById('upload-progress');
  const progressFill = document.getElementById('progress-fill');
  const progressText = document.getElementById('progress-text');
  progressBar.style.display = 'flex';

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const pct = Math.round(((i) / files.length) * 100);
    progressFill.style.width = pct + '%';
    progressText.textContent = pct + '%';

    try {
      const isText = file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.txt');
      let content, isBase64;

      if (isText) {
        content = await file.text();
        isBase64 = false;
      } else {
        const arrayBuffer = await file.arrayBuffer();
        const bytes = new Uint8Array(arrayBuffer);
        let binary = '';
        for (let b of bytes) binary += String.fromCharCode(b);
        content = btoa(binary);
        isBase64 = true;
      }

      const category = file.name.match(/\.(pdf|doc|docx)$/i) ? 'papers' : 'notes';
      const result = await apiPost('/api/upload', {
        filename: file.name,
        content,
        category,
        is_base64: isBase64,
      });

      if (result.success) {
        showToast(`已上传: ${result.filename}`);
        // 在对话中插入文件引用
        if (State.currentSessionId) {
          const card = `
📎 **文件已上传**\n\n` +
            `- 名称: ${result.filename}\n` +
            `- 位置: ${result.path}\n` +
            (result.preview ? `- 预览: ${result.preview.substring(0, 80)}…\n` : '') +
            `\n使用 \`/read ${result.path}\` 读取全文。`;
          appendMessage('assistant', card, null, true);
        }
        loadReferences();
      } else {
        showToast(`上传失败: ${result.error}`, 'error');
      }
    } catch (e) {
      console.error('上传失败:', e);
      showToast(`上传失败: ${e.message}`, 'error');
    }
  }

  progressFill.style.width = '100%';
  progressText.textContent = '100%';
  setTimeout(() => {
    progressBar.style.display = 'none';
    progressFill.style.width = '0%';
  }, 800);
}

// ============================================
// 文献列表
// ============================================
async function loadReferences() {
  try {
    const refs = await apiGet('/api/references');
    renderReferenceList(refs);
  } catch (e) {
    console.error('加载文献失败:', e);
  }
}

function renderReferenceList(refs) {
  const container = document.getElementById('reference-list');
  if (!refs || refs.length === 0) {
    container.innerHTML = '<p class="empty">暂无引用</p>';
    return;
  }
  container.innerHTML = refs.slice(0, 10).map(r => `
    <div class="reference-item" data-path="${escapeHtml(r.path || '')}">
      📄 ${escapeHtml(r.title || r.filename || '未命名')}
    </div>
  `).join('');

  container.querySelectorAll('.reference-item').forEach(el => {
    el.addEventListener('click', () => {
      const path = el.dataset.path;
      if (path) {
        const input = document.getElementById('message-input');
        input.value = `/read ${path}`;
        input.focus();
      }
    });
  });
}

// ============================================
// Agora 导出
// ============================================
const AGORA_PERSONAS = [
  '费曼', '狄拉克', '爱因斯坦', '玻尔', '海森堡',
  '薛定谔', '泡利', '冯·诺依曼', '居里夫人', '普朗克',
  '玻尔兹曼', '麦克斯韦', '高斯', '欧拉', '希尔伯特',
  '诺特', '杨振宁', '李政道', '盖尔曼', '费米',
];

let selectedPersonas = [];

function renderPersonaGrid() {
  const grid = document.getElementById('persona-grid');
  grid.innerHTML = AGORA_PERSONAS.map(p => `
    <div class="persona-item" data-name="${escapeHtml(p)}">${escapeHtml(p)}</div>
  `).join('');

  grid.querySelectorAll('.persona-item').forEach(el => {
    el.addEventListener('click', () => {
      const name = el.dataset.name;
      if (el.classList.contains('selected')) {
        el.classList.remove('selected');
        selectedPersonas = selectedPersonas.filter(x => x !== name);
      } else {
        el.classList.add('selected');
        selectedPersonas.push(name);
      }
    });
  });
}

async function handleAgoraExport() {
  if (!State.currentSessionId) {
    showToast('请先选择一个会话', 'warning');
    return;
  }
  if (selectedPersonas.length === 0) {
    showToast('请至少选择一位历史人物', 'warning');
    return;
  }

  try {
    document.getElementById('confirm-agora').textContent = '导出中…';
    const data = await apiPost('/api/agora', {
      session_id: State.currentSessionId,
      topic: '',
      personas: selectedPersonas,
    });
    showToast(`Agora 导出成功: ${data.path}`);
    document.getElementById('agora-modal').style.display = 'none';
  } catch (e) {
    console.error('Agora 导出失败:', e);
    showToast(`导出失败: ${e.message}`, 'error');
  } finally {
    document.getElementById('confirm-agora').textContent = '导出';
  }
}

// ============================================
// 消息编辑/删除
// ============================================
let editingMsgId = null;

function openEditMessage(msgId, content) {
  editingMsgId = msgId;
  document.getElementById('edit-message-content').value = content;
  document.getElementById('edit-message-modal').style.display = 'flex';
}

async function saveEditMessage() {
  if (!editingMsgId || !State.currentSessionId) return;
  const newContent = document.getElementById('edit-message-content').value.trim();
  if (!newContent) {
    showToast('内容不能为空', 'warning');
    return;
  }

  try {
    await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages/${editingMsgId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newContent }),
    });

    // 更新 DOM
    const msgDiv = document.querySelector(`.message[data-msg-id="${editingMsgId}"]`);
    if (msgDiv) {
      msgDiv.querySelector('.message-bubble').innerHTML = renderMarkdown(newContent);
      // 更新编辑按钮的 content 引用
      const editBtn = msgDiv.querySelector('[data-action="edit"]');
      if (editBtn) {
        editBtn.replaceWith(editBtn.cloneNode(true));
        msgDiv.querySelector('[data-action="edit"]').addEventListener('click', (e) => {
          e.stopPropagation();
          openEditMessage(editingMsgId, newContent);
        });
      }
    }

    showToast('消息已更新');
    document.getElementById('edit-message-modal').style.display = 'none';
    editingMsgId = null;
  } catch (e) {
    console.error('编辑失败:', e);
    showToast('编辑失败', 'error');
  }
}

async function deleteMessage(msgId) {
  if (!confirm('确定删除这条消息？')) return;
  if (!State.currentSessionId) return;

  try {
    await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages/${msgId}`, {
      method: 'DELETE',
    });

    const msgDiv = document.querySelector(`.message[data-msg-id="${msgId}"]`);
    if (msgDiv) msgDiv.remove();
    showToast('消息已删除');
  } catch (e) {
    console.error('删除失败:', e);
    showToast('删除失败', 'error');
  }
}

// ============================================
// 任务面板
// ============================================
async function loadTasks() {
  try {
    State.tasks = await apiGet('/api/tasks');
    renderTaskBoard();
  } catch (e) {
    console.error('加载任务失败:', e);
  }
}

function renderTaskBoard() {
  const columns = {
    backlog: document.getElementById('task-backlog'),
    active: document.getElementById('task-active'),
    completed: document.getElementById('task-completed'),
  };

  // 清空
  Object.values(columns).forEach(c => c.innerHTML = '');

  if (!State.tasks || State.tasks.length === 0) {
    columns.backlog.innerHTML = '<p class="empty">暂无任务</p>';
    return;
  }

  State.tasks.forEach(t => {
    const status = t.status === 'paused' ? 'backlog' : t.status;
    const col = columns[status];
    if (!col) return;

    const progress = t.progress || 0;
    const subtasks = t.subtasks || [];
    const doneCount = subtasks.filter(st => st.done).length;
    const subtaskLabel = subtasks.length > 0 ? `${doneCount}/${subtasks.length}` : '';
    const overdue = t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed';

    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <div class="task-card-title">${escapeHtml(t.title || '未命名')}</div>
      <div class="task-card-meta">
        ${overdue ? '<span class="task-overdue">逾期</span>' : ''}
        ${t.priority ? `<span class="task-priority task-priority-${t.priority}">${t.priority}</span>` : ''}
        ${t.due_date ? formatDate(t.due_date) : ''}
      </div>
      <div class="task-card-progress">
        <div class="progress-track">
          <div class="progress-fill-bar" style="width:${progress}%"></div>
        </div>
        <span class="progress-label">${progress}% ${subtaskLabel}</span>
      </div>
    `;
    card.addEventListener('click', () => openTaskDetail(t.task_id));
    col.appendChild(card);
  });
}

async function openTaskDetail(taskId) {
  try {
    const task = await apiGet(`/api/tasks/${encodeURIComponent(taskId)}`);
    const subtasks = task.subtasks || [];
    const milestones = task.milestones || [];

    const subtasksHtml = subtasks.length > 0 ? `
      <div style="margin-top:12px;">
        <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">子任务</div>
        ${subtasks.map(st => `
          <label style="display:flex;align-items:center;gap:6px;padding:3px 0;cursor:pointer;font-size:0.85rem;">
            <input type="checkbox" data-stid="${st.id}" ${st.done ? 'checked' : ''}>
            <span style="${st.done ? 'text-decoration:line-through;color:var(--text-tertiary);' : ''}">${escapeHtml(st.title)}</span>
          </label>
        `).join('')}
      </div>
    ` : '<div style="margin-top:12px;font-size:0.8rem;color:var(--text-tertiary);">暂无子任务</div>';

    const milestonesHtml = milestones.length > 0 ? `
      <div style="margin-top:12px;">
        <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">里程碑</div>
        ${milestones.map(m => `
          <div style="font-size:0.8rem;padding:2px 0;">
            ${m.reached ? '✓' : '○'} ${escapeHtml(m.label)} (${m.date})
          </div>
        `).join('')}
      </div>
    ` : '';

    const html = `
      <div style="max-width:400px;">
        <h3 style="margin:0 0 8px;">${escapeHtml(task.title)}</h3>
        <div style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:12px;">
          ${task.status} · ${task.priority || '普通'} · 进度 ${task.progress || 0}%
        </div>
        ${task.description ? `<div style="font-size:0.85rem;margin-bottom:12px;">${escapeHtml(task.description)}</div>` : ''}
        <div style="margin-bottom:12px;">
          <input type="range" min="0" max="100" value="${task.progress || 0}" id="task-progress-slider" style="width:100%;">
          <div style="text-align:center;font-size:0.8rem;margin-top:4px;"><span id="task-progress-value">${task.progress || 0}</span>%</div>
        </div>
        ${subtasksHtml}
        ${milestonesHtml}
        <div style="margin-top:16px;display:flex;gap:8px;justify-content:flex-end;">
          <button class="btn-text" id="close-task-detail">关闭</button>
          <button class="btn-primary" id="save-task-progress">保存</button>
        </div>
      </div>
    `;

    showModal(html);

    // 进度滑块实时更新
    const slider = document.getElementById('task-progress-slider');
    const valueLabel = document.getElementById('task-progress-value');
    if (slider && valueLabel) {
      slider.addEventListener('input', (e) => {
        valueLabel.textContent = e.target.value;
      });
    }

    // 子任务勾选
    document.querySelectorAll('#modal-content input[type="checkbox"][data-stid]').forEach(cb => {
      cb.addEventListener('change', async (e) => {
        const stid = e.target.dataset.stid;
        await apiPut(`/api/tasks/${encodeURIComponent(taskId)}/subtasks`, { action: 'toggle', subtask_id: stid });
        await loadTasks();
      });
    });

    // 保存进度
    document.getElementById('save-task-progress').addEventListener('click', async () => {
      const val = parseInt(document.getElementById('task-progress-slider').value, 10);
      await apiPut(`/api/tasks/${encodeURIComponent(taskId)}/progress`, { progress: val });
      await loadTasks();
      closeModal();
    });

    document.getElementById('close-task-detail').addEventListener('click', closeModal);

  } catch (e) {
    console.error('加载任务详情失败:', e);
    showToast('加载任务详情失败', 'error');
  }
}

// ============================================
// 主动提醒
// ============================================
async function checkHeartbeat() {
  try {
    const data = await apiGet('/api/heartbeat');
    if (data.reminders && data.reminders.length > 0) {
      data.reminders.forEach(r => showToast(r, 'warning', 6000));
    }
  } catch (e) {
    // 静默失败
  }
}

// ============================================
// UI 更新
// ============================================
function updateModeBadge(mode) {
  const map = {
    'co-working': '并肩工作',
    'deep-talk': '深度对话',
    'quick-check': '快速验证',
  };
  document.getElementById('mode-badge').textContent = map[mode] || mode;
}

function updateStatus(text) {
  document.getElementById('status-text').textContent = text;
}

// ============================================
// 事件绑定
// ============================================
function bindEvents() {
  // 主题切换
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  // 设置面板
  document.getElementById('settings-toggle').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'flex';
    document.getElementById('theme-select').value = State.theme;
    document.getElementById('autonomy-select').value = State.autonomy;
    // 刷新各状态（轻量：只加载设置面板需要的）
    loadLLMStatus();
    loadUsage();
  });

  // 顶部 provider-badge 点击打开设置面板
  document.getElementById('provider-badge').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'flex';
    document.getElementById('theme-select').value = State.theme;
    document.getElementById('autonomy-select').value = State.autonomy;
    loadLLMStatus();
    loadUsage();
  });
  document.getElementById('close-settings').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'none';
  });
  document.getElementById('settings-drawer').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 关闭归档浏览视图
  document.getElementById('close-archive-view').addEventListener('click', () => {
    document.getElementById('chat-archive-header').style.display = 'none';
    document.querySelector('.input-area').style.display = 'block';
    State.viewingArchive = false;
    renderSessionList();
    // 如果当前有会话，回到续接模式
    if (State.currentSessionId) {
      switchSession(State.currentSessionId);
    }
  });

  // 关闭历史提示条
  document.getElementById('history-hint-close').addEventListener('click', () => {
    document.getElementById('history-hint').style.display = 'none';
  });

  // 主题选择
  document.getElementById('theme-select').addEventListener('change', (e) => {
    applyTheme(e.target.value);
  });

  // 自主级别选择
  document.getElementById('autonomy-select').addEventListener('change', (e) => {
    State.autonomy = e.target.value;
    localStorage.setItem('linsai-autonomy', e.target.value);
    showToast(`自主级别已设为: ${e.target.value}`);
  });

  // 设置面板内备份按钮
  document.getElementById('drawer-backup-btn').addEventListener('click', () => {
    showToast('请在终端运行: python3 scripts/backup_manager.py', 'warning', 5000);
  });

  // 加载 LLM 状态
  loadLLMStatus();

  // 新建会话
  document.getElementById('new-session-btn').addEventListener('click', () => {
    document.getElementById('new-session-modal').style.display = 'flex';
    document.getElementById('new-session-topic').focus();
  });
  document.getElementById('cancel-new-session').addEventListener('click', () => {
    document.getElementById('new-session-modal').style.display = 'none';
  });
  document.getElementById('confirm-new-session').addEventListener('click', () => {
    const topic = document.getElementById('new-session-topic').value.trim();
    const mode = document.getElementById('new-session-mode').value;
    if (!topic) {
      showToast('请输入会话主题', 'warning');
      return;
    }
    createNewSession(topic, mode);
    document.getElementById('new-session-modal').style.display = 'none';
    document.getElementById('new-session-topic').value = '';
  });
  document.getElementById('new-session-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });
  document.getElementById('new-session-topic').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      document.getElementById('confirm-new-session').click();
    }
  });

  // 会话搜索
  document.getElementById('session-search').addEventListener('input', renderSessionList);

  // 发送消息
  document.getElementById('send-btn').addEventListener('click', () => {
    const input = document.getElementById('message-input');
    sendMessage(input.value);
  });
  document.getElementById('message-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e.target.value);
    }
  });

  // 输入时实时检测激活的技能
  let _skillDebounce = null;
  document.getElementById('message-input').addEventListener('input', (e) => {
    clearTimeout(_skillDebounce);
    _skillDebounce = setTimeout(() => {
      updateSkillBadge(e.target.value);
    }, 300);
  });

  // 快捷命令按钮
  document.querySelectorAll('.cmd-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.cmd;
      const input = document.getElementById('message-input');
      if (cmd === '/mode') {
        showToast('模式切换请在新建会话时选择', 'warning');
      } else if (cmd === '/read') {
        input.value = '/read ';
        input.focus();
      } else if (cmd === '/agora') {
        selectedPersonas = [];
        renderPersonaGrid();
        document.getElementById('agora-modal').style.display = 'flex';
      } else if (cmd === '/summary') {
        sendMessage('/summary');
      }
    });
  });

  // Agora 弹窗
  document.getElementById('cancel-agora').addEventListener('click', () => {
    document.getElementById('agora-modal').style.display = 'none';
  });
  document.getElementById('confirm-agora').addEventListener('click', handleAgoraExport);
  document.getElementById('agora-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 编辑消息弹窗
  document.getElementById('cancel-edit-message').addEventListener('click', () => {
    document.getElementById('edit-message-modal').style.display = 'none';
    editingMsgId = null;
  });
  document.getElementById('confirm-edit-message').addEventListener('click', saveEditMessage);
  document.getElementById('edit-message-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
      editingMsgId = null;
    }
  });

  // 文件上传
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');

  document.getElementById('upload-btn').addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    uploadFiles(e.target.files);
    fileInput.value = ''; // 重置，允许重复选择同一文件
  });

  uploadZone.addEventListener('click', () => fileInput.click());

  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });
  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
  });
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  });

  // 快速开始按钮
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const topic = btn.dataset.topic;
      createNewSession(topic, 'co-working');
    });
  });

  // 移动端侧边栏切换
  document.getElementById('sidebar-toggle').addEventListener('click', () => {
    document.getElementById('left-sidebar').classList.toggle('open');
  });

  // 归档按钮 → 打开历史搜索侧边栏
  document.getElementById('archived-btn').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'flex';
  });

  // 顶部栏"查看历史记录"按钮 → 只读浏览当前会话
  document.getElementById('view-history-btn').addEventListener('click', () => {
    if (!State.currentSessionId) {
      showToast('请先选择一个会话', 'warning');
      return;
    }
    viewArchiveSession(State.currentSessionId);
  });

  // 关闭历史搜索
  document.getElementById('close-history').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'none';
  });

  // 历史搜索
  document.getElementById('history-search-btn').addEventListener('click', searchHistory);
  document.getElementById('history-search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchHistory();
  });

  // 返回当前会话（如果按钮存在）
  document.getElementById('back-to-current')?.addEventListener('click', backToCurrentSession);

  // 底部按钮
  document.getElementById('backup-btn').addEventListener('click', () => {
    showToast('请在终端运行: python3 scripts/backup_manager.py', 'warning', 5000);
  });
  document.getElementById('export-btn').addEventListener('click', () => {
    showToast('导出功能开发中', 'warning');
  });

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (State.theme === 'auto') {
      applyTheme('auto');
    }
  });

  // 全局拖拽上传（拖拽到页面任意位置）
  document.addEventListener('dragover', (e) => {
    if (e.dataTransfer.types.includes('Files')) {
      uploadZone.classList.add('drag-over');
    }
  });
  document.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
      uploadZone.classList.remove('drag-over');
    }
  });
  document.addEventListener('drop', (e) => {
    uploadZone.classList.remove('drag-over');
  });

  // 知识库管理器事件
  bindKbManagerEvents();
}

// ============================================
// LLM Provider 状态与切换
// ============================================
async function loadLLMStatus() {
  try {
    const [providersData, currentData] = await Promise.all([
      apiGet('/api/providers'),
      apiGet('/api/providers/current')
    ]);

    const providers = providersData.providers || [];
    const current = currentData.current || 'auto';

    // 更新顶部 provider-badge
    const badge = document.getElementById('provider-badge');
    if (badge) {
      if (current === 'auto') {
        badge.textContent = 'auto';
        badge.title = '自动选择 Provider';
      } else if (current === 'cli_auto') {
        const cli = providers.find(p => p.type === 'cli' && p.available);
        badge.textContent = `💻 ${cli ? cli.name : 'CLI'}`;
        badge.title = `强制 CLI 模式 (${cli ? cli.name : '无可用 CLI'})`;
      } else {
        const currentProvider = providers.find(p => p.name === current);
        if (currentProvider) {
          const typeIcon = currentProvider.type === 'api' ? '🌐' : '💻';
          badge.textContent = `${typeIcon} ${currentProvider.name}`;
          badge.title = `当前: ${currentProvider.name} (${currentProvider.type === 'api' ? currentProvider.model || 'API' : 'CLI'})`;
        } else {
          badge.textContent = current;
          badge.title = '当前 Provider';
        }
      }
    }

    // 更新设置面板中的 provider 列表
    const container = document.getElementById('llm-status');
    if (!container) return;

    if (providers.length === 0) {
      container.innerHTML = '✗ 无可用 Provider';
      return;
    }

    // 生成 radio 按钮列表
    const html = [];

    // 自动选择
    html.push(`
      <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:4px 0;" data-provider="auto">
        <input type="radio" name="provider-select" value="auto" ${current === 'auto' ? 'checked' : ''}>
        <span>🔄 自动选择（推荐）</span>
      </label>
    `);

    // CLI 自动模式
    const hasCli = providers.some(p => p.type === 'cli');
    const cliAvail = providers.some(p => p.type === 'cli' && p.available);
    html.push(`
      <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:4px 0;${cliAvail ? '' : 'opacity:0.5;'}">
        <input type="radio" name="provider-select" value="cli_auto" ${current === 'cli_auto' ? 'checked' : ''} ${cliAvail ? '' : 'disabled'}>
        <span>💻 CLI 自动（${cliAvail ? '第一个可用 CLI' : '无可用的 CLI'}）</span>
      </label>
    `);

    // 分割线
    if (providers.length > 0) {
      html.push(`<div style="border-top:1px solid var(--border-color);margin:4px 0;"></div>`);
    }

    providers.forEach(p => {
      const icon = p.available ? '✓' : '✗';
      const typeLabel = p.type === 'api' ? `API (${p.model || '未知模型'})` : 'CLI';
      const disabled = !p.available ? 'disabled' : '';
      const opacity = !p.available ? 'opacity:0.5;' : '';
      html.push(`
        <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:4px 0;${opacity}" data-provider="${escapeHtml(p.name)}">
          <input type="radio" name="provider-select" value="${escapeHtml(p.name)}" ${current === p.name ? 'checked' : ''} ${disabled}>
          <span>${icon} ${escapeHtml(p.name)} <span style="color:var(--text-tertiary)">${typeLabel}</span></span>
        </label>
      `);
    });

    container.innerHTML = html.join('');

    // 绑定 radio 按钮切换事件
    container.querySelectorAll('input[name="provider-select"]').forEach(radio => {
      radio.addEventListener('change', async (e) => {
        const providerName = e.target.value;
        await switchProvider(providerName);
      });
    });
  } catch (e) {
    console.error('加载 LLM 状态失败:', e);
    const container = document.getElementById('llm-status');
    if (container) container.innerHTML = '✗ 加载失败';
  }
}

async function switchProvider(providerName) {
  try {
    const data = await apiPost('/api/switch-provider', { provider: providerName });
    if (data.success) {
      const label = providerName === 'auto' ? '自动选择' : providerName === 'cli_auto' ? 'CLI 自动' : providerName;
      showToast(`✓ 已切换到 ${label}`, 'success');
      // 刷新状态显示
      await loadLLMStatus();
    } else {
      showToast(`✗ 切换失败: ${data.error || '未知错误'}`, 'error');
    }
  } catch (e) {
    console.error('切换 Provider 失败:', e);
    showToast('✗ 切换 Provider 失败', 'error');
  }
}

// ============================================
// 历史消息提示
// ============================================
function showHistoryHint(count) {
  const hint = document.getElementById('history-hint');
  if (!hint) return;
  hint.querySelector('span').textContent = `↑ 已加载 ${count} 条消息，向上滚动查看历史`;
  hint.style.display = 'flex';
  // 5 秒后自动隐藏
  setTimeout(() => {
    if (hint) hint.style.display = 'none';
  }, 8000);
}

// ============================================
// Token 用量
// ============================================
async function loadUsage() {
  try {
    const data = await apiGet('/api/usage');
    const container = document.getElementById('usage-status');
    if (!container) return;

    const daily = data.daily || {};
    const total = data.total || {};
    const byProvider = data.by_provider || {};

    const prompt = daily.prompt || 0;
    const completion = daily.completion || 0;
    const calls = daily.calls || 0;

    let html = `<div>今日: <strong>${prompt + completion}</strong> tokens（${calls} 次调用）</div>`;
    html += `<div style="color:var(--text-tertiary);font-size:0.75rem;margin-top:2px;">`;
    html += `prompt: ${prompt} · completion: ${completion}`;
    html += `</div>`;

    if (Object.keys(byProvider).length > 0) {
      html += `<div style="margin-top:4px;">`;
      Object.entries(byProvider).forEach(([name, stats]) => {
        const isEst = name === 'kimi' || name === 'claude';
        const label = isEst ? '（估算）' : '';
        html += `<span style="font-size:0.75rem;color:var(--text-tertiary);margin-right:8px;">${name}: ${stats.prompt + stats.completion}${label}</span>`;
      });
      html += `</div>`;
    }

    container.innerHTML = html;
  } catch (e) {
    console.error('加载用量失败:', e);
    const container = document.getElementById('usage-status');
    if (container) container.innerHTML = '✗ 加载失败';
  }
}

// ============================================
// 技能系统（实时检测输入框中的技能）
// ============================================
async function updateSkillBadge(text) {
  const badge = document.getElementById('skill-badge');
  if (!badge) return;
  if (!text || text.length < 2) {
    badge.style.display = 'none';
    return;
  }
  try {
    const data = await apiGet(`/api/skills/active?q=${encodeURIComponent(text)}`);
    const active = data.active || [];
    if (active.length > 0) {
      badge.textContent = `🎯 ${active.join(', ')}`;
      badge.style.display = 'inline-flex';
    } else {
      badge.style.display = 'none';
    }
  } catch (e) {
    badge.style.display = 'none';
  }
}

// ============================================
// 技能管理器
// ============================================
let _skillConfigCache = null;
let _allSkillsCache = [];

function openSkillManager() {
  document.getElementById('skill-manager-overlay').style.display = 'flex';
  loadSkillList();
}

function closeSkillManager() {
  document.getElementById('skill-manager-overlay').style.display = 'none';
}

async function loadSkillList() {
  const container = document.getElementById('skill-list-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const [config, allData] = await Promise.all([
      apiGet('/api/skills/config'),
      apiGet('/api/skills'),
    ]);
    _skillConfigCache = config;
    _allSkillsCache = allData.skills || [];

    // 设置模式
    const mode = config.mode || 'auto';
    document.getElementById(`skill-mode-${mode}`).checked = true;

    renderSkillList(_allSkillsCache, config.active_skills || []);
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

function renderSkillList(skills, activeSkills) {
  const container = document.getElementById('skill-list-content');
  if (!skills.length) {
    container.innerHTML = '<div class="kb-empty">暂无技能</div>';
    return;
  }

  const activeSet = new Set(activeSkills);
  const mode = _skillConfigCache?.mode || 'auto';

  let html = '';
  skills.forEach(skill => {
    const isActive = activeSet.has(skill.name);
    const checked = isActive ? 'checked' : '';
    const dimmed = (mode === 'manual' && !isActive) ? 'opacity:0.5;' : '';
    html += `
      <label class="skill-row" style="${dimmed}">
        <input type="checkbox" class="skill-checkbox" data-name="${skill.name}" ${checked}>
        <div class="skill-info">
          <div class="skill-name">${skill.name}</div>
          <div class="skill-desc">${skill.description || '暂无描述'}</div>
          <div class="skill-triggers">触发: ${skill.triggers || '无'}</div>
        </div>
      </label>
    `;
  });
  container.innerHTML = html;

  // 更新计数
  const count = activeSet.size;
  document.getElementById('skill-active-count').textContent = `已激活 ${count}/${skills.length}`;

  // 绑定复选框事件
  container.querySelectorAll('.skill-checkbox').forEach(cb => {
    cb.addEventListener('change', updateSkillCount);
  });
}

function updateSkillCount() {
  const checked = document.querySelectorAll('.skill-checkbox:checked');
  const total = document.querySelectorAll('.skill-checkbox').length;
  document.getElementById('skill-active-count').textContent = `已激活 ${checked.length}/${total}`;
}

function filterSkillList() {
  const query = document.getElementById('skill-search-input').value.trim().toLowerCase();
  if (!query) {
    renderSkillList(_allSkillsCache, getSelectedSkillNames());
    return;
  }
  const filtered = _allSkillsCache.filter(s =>
    s.name.toLowerCase().includes(query) ||
    (s.description && s.description.toLowerCase().includes(query)) ||
    (s.triggers && s.triggers.toLowerCase().includes(query))
  );
  renderSkillList(filtered, getSelectedSkillNames());
}

function getSelectedSkillNames() {
  return Array.from(document.querySelectorAll('.skill-checkbox:checked')).map(cb => cb.dataset.name);
}

function onSkillModeChange() {
  const mode = document.querySelector('input[name="skill-mode"]:checked')?.value || 'auto';
  // 手动模式下，未选中的技能变暗
  document.querySelectorAll('.skill-row').forEach(row => {
    const cb = row.querySelector('.skill-checkbox');
    if (mode === 'manual' && !cb.checked) {
      row.style.opacity = '0.5';
    } else {
      row.style.opacity = '1';
    }
  });
}

async function saveSkillConfig() {
  const mode = document.querySelector('input[name="skill-mode"]:checked')?.value || 'auto';
  const active = getSelectedSkillNames();
  try {
    await apiPost('/api/skills/config', { mode, active_skills: active });
    _skillConfigCache = { mode, active_skills: active };
    showToast(`✓ 技能配置已保存: ${mode === 'auto' ? '自动模式' : '手动模式'}，${active.length} 个技能激活`);
    closeSkillManager();
  } catch (e) {
    showToast('✗ 保存失败: ' + e.message, 'error');
  }
}

async function resetSkillConfig() {
  try {
    const allNames = _allSkillsCache.map(s => s.name);
    await apiPost('/api/skills/config', { mode: 'auto', active_skills: allNames });
    _skillConfigCache = { mode: 'auto', active_skills: allNames };
    document.getElementById('skill-mode-auto').checked = true;
    document.getElementById('skill-search-input').value = '';
    renderSkillList(_allSkillsCache, allNames);
    showToast('✓ 已重置为默认（自动模式，全部激活）');
  } catch (e) {
    showToast('✗ 重置失败: ' + e.message, 'error');
  }
}

// ============================================
// 初始化
// ============================================
async function init() {
  // 应用主题
  applyTheme(State.theme);

  // 加载版本
  try {
    const data = await apiGet('/api/version');
    document.getElementById('version-label').textContent = data.version;
  } catch (e) {
    console.error('获取版本失败:', e);
  }

  // 加载会话
  await loadSessions();

  // 加载会话关键词（异步，不阻塞）
  loadSessionKeywords();

  // 检查主动提醒
  await checkHeartbeat();

  // 加载文献
  loadReferences();

  // 加载用量（异步，不阻塞）
  loadUsage();

  // 绑定事件
  bindEvents();

  // 检查是否有活跃会话，有则自动选中最新
  if (State.sessions.length > 0) {
    const active = State.sessions.find(s => s.status === 'active') || State.sessions[0];
    // 不自动切换，让用户选择
  }

  console.log('✓ LinSai Web 界面已就绪');
}

// 启动
document.addEventListener('DOMContentLoaded', init);

// ============================================
// 知识库管理器
// ============================================

const KBManager = {
  activeTab: 'overview',
  wikiPages: [],
  rawFiles: [],
  graph: {},
  growthLog: [],
  candidates: [],
};

function openKbManager() {
  document.getElementById('kb-manager-overlay').style.display = 'flex';
  loadKbOverview();
}

function closeKbManager() {
  document.getElementById('kb-manager-overlay').style.display = 'none';
}

function switchKbTab(tab) {
  KBManager.activeTab = tab;
  document.querySelectorAll('.kb-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.kb-panel').forEach(p => p.classList.toggle('active', p.id === `kb-panel-${tab}`));

  if (tab === 'overview') loadKbOverview();
  else if (tab === 'raw') loadKbRaw();
  else if (tab === 'wiki') loadKbWiki();
  else if (tab === 'graph') loadKbGraph();
  else if (tab === 'growth') loadKbGrowth();
  else if (tab === 'health') loadKbHealth();
  else if (tab === 'aliases') loadKbAliases();
}

async function loadKbOverview() {
  const container = document.getElementById('kb-overview-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const [status, graph, candidates] = await Promise.all([
      apiGet('/api/knowledge'),
      apiGet('/api/knowledge/graph'),
      apiGet('/api/knowledge/growth-candidates'),
    ]);

    const stages = graph.growth_stages || {};
    const stageHtml = Object.entries(stages).map(([s, c]) => {
      const labels = { seedling: '🌱 幼苗', growing: '🌿 成长中', mature: '🌳 成熟', archived: '📦 归档' };
      return `<span class="kb-badge kb-badge-${s}">${labels[s] || s}: ${c}</span>`;
    }).join(' ');

    container.innerHTML = `
      <div class="kb-stat-grid">
        <div class="kb-stat-card">
          <div class="kb-stat-value">${status.raw_count || 0}</div>
          <div class="kb-stat-label">Raw 文件</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${status.wiki_count || 0}</div>
          <div class="kb-stat-label">Wiki 页面</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${status.chunks || 0}</div>
          <div class="kb-stat-label">索引段落</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${graph.node_count || 0}</div>
          <div class="kb-stat-label">知识节点</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${graph.edge_count || 0}</div>
          <div class="kb-stat-label">关联关系</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${candidates.candidates?.length || 0}</div>
          <div class="kb-stat-label">待生长</div>
        </div>
      </div>
      <div style="margin-top:12px;">${stageHtml}</div>
      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-text" onclick="openLocalFile('knowledge')">📂 打开知识库文件夹</button>
        <button class="btn-text" onclick="openLocalFile('knowledge/raw')">📂 打开 Raw 文件夹</button>
        <button class="btn-text" onclick="openLocalFile('knowledge/wiki')">📂 打开 Wiki 文件夹</button>
      </div>
      <div style="color:var(--text-tertiary);font-size:0.75rem;margin-top:8px;">
        索引时间: ${status.built_at || '未知'}
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

async function loadKbRaw() {
  const container = document.getElementById('kb-raw-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const data = await apiGet('/api/knowledge/raw');
    const files = data.files || [];
    if (files.length === 0) {
      container.innerHTML = '<div class="kb-empty">📂 暂无 raw 文件<br>将 .md/.txt 文件放入 knowledge/raw/ 目录即可</div>';
      return;
    }
    const cats = {};
    files.forEach(f => {
      const cat = f.category || '其他';
      if (!cats[cat]) cats[cat] = [];
      cats[cat].push(f);
    });

    let html = '';
    for (const [cat, list] of Object.entries(cats)) {
      const catLabels = { papers: '📄 论文', notes: '📝 笔记', webclips: '🌐 剪藏' };
      html += `<div class="kb-section-title">${catLabels[cat] || cat}</div>`;
      list.forEach(f => {
        html += `
          <div class="kb-list-item">
            <div class="kb-list-main">
              <div class="kb-list-title">${f.name}</div>
              <div class="kb-list-meta">${(f.size / 1024).toFixed(1)} KB · ${new Date(f.mtime * 1000).toLocaleDateString()}</div>
            </div>
            <div class="kb-list-actions">
              <button class="kb-action-btn" onclick="openLocalFile('${f.path}')" title="打开文件">📂</button>
            </div>
          </div>
        `;
      });
    }
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败</div>`;
  }
}

async function loadKbWiki() {
  const container = document.getElementById('kb-wiki-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const filter = document.getElementById('kb-wiki-filter')?.value || '';
    const data = await apiGet(`/api/knowledge/wiki${filter ? '?type=' + filter : ''}`);
    const pages = data.pages || [];
    KBManager.wikiPages = pages;

    if (pages.length === 0) {
      container.innerHTML = '<div class="kb-empty">📝 暂无 Wiki 页面<br>通过"新建概念 Stub"或 raw→wiki 提炼来创建</div>';
      return;
    }

    const stageLabels = { seedling: '🌱', growing: '🌿', mature: '🌳', archived: '📦' };
    let html = '';
    pages.forEach(p => {
      const stageIcon = stageLabels[p.growth_stage] || '○';
      html += `
        <div class="kb-list-item">
          <div class="kb-list-main" onclick="openWikiDetail('${p.path}')">
            <div class="kb-list-title">${stageIcon} ${p.title}</div>
            <div class="kb-list-meta">
              ${p.type} · 确信度 ${(p.confidence * 100).toFixed(0)}%
              ${p.tags?.length ? '· ' + p.tags.join(', ') : ''}
            </div>
          </div>
          <div class="kb-list-actions">
            <button class="kb-action-btn" onclick="event.stopPropagation(); openLocalFile('${p.path}')" title="在编辑器中打开">📂</button>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败</div>`;
  }
}

async function loadKbGraph() {
  const container = document.getElementById('kb-graph-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const data = await apiGet('/api/knowledge/graph');
    const nodes = data.node_count || 0;
    const edges = data.edge_count || 0;

    if (nodes === 0) {
      container.innerHTML = '<div class="kb-empty">🔗 知识图谱为空<br>创建 Wiki 页面并添加 related 字段即可建立关联</div>';
      return;
    }

    container.innerHTML = `
      <div class="kb-stat-grid" style="grid-template-columns: repeat(2, 1fr);">
        <div class="kb-stat-card">
          <div class="kb-stat-value">${nodes}</div>
          <div class="kb-stat-label">节点</div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-value">${edges}</div>
          <div class="kb-stat-label">边</div>
        </div>
      </div>
      <div class="kb-section-title">生长阶段分布</div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        ${Object.entries(data.growth_stages || {}).map(([s, c]) => {
          const labels = { seedling: '🌱 幼苗', growing: '🌿 成长中', mature: '🌳 成熟', archived: '📦 归档' };
          return `<span class="kb-badge kb-badge-${s}">${labels[s] || s}: ${c}</span>`;
        }).join('')}
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败</div>`;
  }
}

async function loadKbGrowth() {
  const container = document.getElementById('kb-growth-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const [logData, candData] = await Promise.all([
      apiGet('/api/knowledge/growth-log?limit=20'),
      apiGet('/api/knowledge/growth-candidates'),
    ]);

    const logs = logData.log || [];
    const candidates = candData.candidates || [];

    let html = '';

    // 待生长概念
    if (candidates.length > 0) {
      html += `<div class="kb-section-title">🌱 待生长概念 (${candidates.length})</div>`;
      candidates.forEach(c => {
        html += `
          <div class="kb-list-item" onclick="openWikiDetail('${c.path}')">
            <div class="kb-list-title">🌱 ${c.title}</div>
            <div class="kb-list-meta">${c.reason}</div>
          </div>
        `;
      });
    }

    // 生长日志
    html += `<div class="kb-section-title">📜 最近生长记录</div>`;
    if (logs.length === 0) {
      html += '<div class="kb-empty">暂无生长记录</div>';
    } else {
      logs.forEach(l => {
        const actionLabels = { create: '✨ 创建', update: '✏️ 更新', link: '🔗 关联', distill: '🧪 提炼', ingest: '📥 纳入' };
        html += `
          <div style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:0.8rem;">
            <div style="display:flex;justify-content:space-between;">
              <span>${actionLabels[l.action] || l.action} <strong>${l.target?.split('/').pop()}</strong></span>
              <span style="color:var(--text-tertiary);">${new Date(l.timestamp).toLocaleDateString()}</span>
            </div>
            <div style="color:var(--text-tertiary);margin-top:2px;">${l.reason || ''}</div>
          </div>
        `;
      });
    }

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败</div>`;
  }
}

async function loadKbHealth() {
  const container = document.getElementById('kb-health-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const health = await apiGet('/api/knowledge/health');
    const stages = health.growth_stages || {};
    const stageLabels = { seedling: '🌱 幼苗', growing: '🌿 成长中', mature: '🌳 成熟' };
    const stageHtml = Object.entries(stages).map(([s, c]) => `<span class="kb-badge kb-badge-${s}">${stageLabels[s] || s}: ${c}</span>`).join(' ');

    container.innerHTML = `
      <div class="kb-health-grid">
        <div class="kb-health-card">
          <div class="kb-health-value">${health.raw_count || 0}</div>
          <div class="kb-health-label">Raw 文件</div>
        </div>
        <div class="kb-health-card">
          <div class="kb-health-value">${health.wiki_count || 0}</div>
          <div class="kb-health-label">Wiki 页面</div>
        </div>
        <div class="kb-health-card">
          <div class="kb-health-value">${health.capture_count || 0}</div>
          <div class="kb-health-label">对话捕获</div>
        </div>
        <div class="kb-health-card">
          <div class="kb-health-value">${health.graph_nodes || 0}</div>
          <div class="kb-health-label">图谱节点</div>
        </div>
        <div class="kb-health-card">
          <div class="kb-health-value">${health.graph_edges || 0}</div>
          <div class="kb-health-label">关联边</div>
        </div>
        <div class="kb-health-card">
          <div class="kb-health-value">${health.growth_candidates || 0}</div>
          <div class="kb-health-label">生长候选</div>
        </div>
      </div>
      <div style="margin-top:12px;">${stageHtml}</div>
      <div class="kb-health-section">
        <div class="kb-health-row"><span>本周新增</span><span>${health.week_new || 0} 条</span></div>
        <div class="kb-health-row"><span>待蒸馏 raw</span><span>${health.pending_distill || 0} 个</span></div>
        <div class="kb-health-row"><span>孤儿节点</span><span>${health.graph_orphans || 0} 个</span></div>
        <div class="kb-health-row"><span>索引时间</span><span>${health.built_at ? new Date(health.built_at).toLocaleString() : '未知'}</span></div>
      </div>
      <div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;">
        <button class="btn-text" onclick="runMaintenance('reindex')">🔄 重建索引</button>
        <button class="btn-text" onclick="runMaintenance('orphans')">🧹 清理孤儿</button>
        <button class="btn-text" onclick="runMaintenance('candidates')">📋 候选报告</button>
        <button class="btn-text" onclick="runMaintenance('weekly')">🔧 周维护</button>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

async function loadKbAliases() {
  const container = document.getElementById('kb-aliases-content');
  container.innerHTML = '◐ 加载中…';
  try {
    const data = await apiGet('/api/knowledge/aliases');
    const aliases = data.aliases || {};
    let html = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span style="font-size:0.85rem;color:var(--text-secondary);">别名映射：查询时自动展开同义词</span>
        <button class="btn-text" onclick="saveAliases()">💾 保存</button>
      </div>
      <div id="aliases-editor" style="display:flex;flex-direction:column;gap:8px;">
    `;

    const entries = Object.entries(aliases);
    if (entries.length === 0) {
      html += `<div class="kb-empty">暂无别名映射。点击"添加"创建。</div>`;
    } else {
      entries.forEach(([canonical, alts], idx) => {
        html += `
          <div class="alias-row" data-idx="${idx}">
            <input type="text" class="alias-canonical" value="${canonical}" placeholder="标准词" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid var(--border-color);background:var(--surface);color:var(--text-primary);">
            <span style="color:var(--text-tertiary);">→</span>
            <input type="text" class="alias-alts" value="${Array.isArray(alts) ? alts.join(', ') : alts}" placeholder="别名1, 别名2" style="flex:2;padding:6px 8px;border-radius:6px;border:1px solid var(--border-color);background:var(--surface);color:var(--text-primary);">
            <button class="btn-icon" onclick="this.parentElement.remove()" title="删除">🗑️</button>
          </div>
        `;
      });
    }
    html += `</div>`;
    html += `
      <div style="margin-top:12px;">
        <button class="btn-text" onclick="addAliasRow()">➕ 添加别名</button>
      </div>
    `;
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

function addAliasRow() {
  const editor = document.getElementById('aliases-editor');
  const idx = editor.children.length;
  const row = document.createElement('div');
  row.className = 'alias-row';
  row.dataset.idx = idx;
  row.innerHTML = `
    <input type="text" class="alias-canonical" placeholder="标准词" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid var(--border-color);background:var(--surface);color:var(--text-primary);">
    <span style="color:var(--text-tertiary);">→</span>
    <input type="text" class="alias-alts" placeholder="别名1, 别名2" style="flex:2;padding:6px 8px;border-radius:6px;border:1px solid var(--border-color);background:var(--surface);color:var(--text-primary);">
    <button class="btn-icon" onclick="this.parentElement.remove()" title="删除">🗑️</button>
  `;
  editor.appendChild(row);
}

async function saveAliases() {
  const rows = document.querySelectorAll('.alias-row');
  const aliases = {};
  rows.forEach(row => {
    const canonical = row.querySelector('.alias-canonical').value.trim();
    const altsStr = row.querySelector('.alias-alts').value.trim();
    if (canonical && altsStr) {
      aliases[canonical] = altsStr.split(',').map(s => s.trim()).filter(Boolean);
    }
  });
  try {
    await apiPost('/api/knowledge/aliases', { aliases });
    showToast('✓ 别名已保存', 'success');
  } catch (e) {
    showToast('✗ 保存失败: ' + e.message, 'error');
  }
}

async function runMaintenance(task) {
  try {
    showToast(`◐ 运行 ${task}...`, 'info');
    const result = await apiPost('/api/knowledge/maintenance', { task });
    if (result.success) {
      showToast(`✓ ${task} 完成`, 'success');
      if (KBManager.activeTab === 'health') loadKbHealth();
      else if (KBManager.activeTab === 'overview') loadKbOverview();
    } else {
      showToast('✗ 失败: ' + (result.error || '未知错误'), 'error');
    }
  } catch (e) {
    showToast('✗ 请求失败: ' + e.message, 'error');
  }
}

async function openWikiDetail(wikiPath) {
  const overlay = document.getElementById('kb-wiki-detail-overlay');
  const titleEl = document.getElementById('kb-wiki-detail-title');
  const bodyEl = document.getElementById('kb-wiki-detail-body');

  overlay.style.display = 'flex';
  bodyEl.innerHTML = '◐ 加载中…';

  try {
    const relPath = wikiPath.replace(/^wiki\//, '');
    const data = await apiGet(`/api/knowledge/wiki/${encodeURIComponent(relPath)}`);
    const fm = data.frontmatter || {};
    const body = data.body || '';

    titleEl.textContent = fm.title || relPath;

    const stageLabels = { seedling: '🌱 幼苗', growing: '🌿 成长中', mature: '🌳 成熟', archived: '📦 归档' };
    const stage = stageLabels[fm.growth_stage] || fm.growth_stage || '未知';

    // 简单 Markdown 渲染
    let renderedBody = body
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>');

    // 包裹列表项
    renderedBody = renderedBody.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

    bodyEl.innerHTML = `
      <div class="kb-detail-actions">
        <button class="btn-text" onclick="openLocalFile('${wikiPath}')">📂 在编辑器中打开</button>
        <button class="btn-text" onclick="copyToClipboard('${wikiPath}')">📋 复制路径</button>
      </div>
      <div class="kb-frontmatter">
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">类型</span><span class="kb-frontmatter-value">${fm.type || '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">生长阶段</span><span class="kb-frontmatter-value">${stage}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">确信度</span><span class="kb-frontmatter-value">${(fm.confidence * 100).toFixed(0)}%</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">标签</span><span class="kb-frontmatter-value">${(fm.tags || []).join(', ') || '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">关联</span><span class="kb-frontmatter-value">${(fm.related || []).join(', ') || '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">更新</span><span class="kb-frontmatter-value">${fm.updated ? new Date(fm.updated).toLocaleString() : '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">路径</span><span class="kb-frontmatter-value">${wikiPath}</span></div>
      </div>
      <div class="kb-wiki-body">${renderedBody}</div>
    `;
  } catch (e) {
    bodyEl.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

async function openLocalFile(relPath) {
  try {
    const data = await apiPost('/api/open-local', { path: relPath });
    if (data.success) {
      showToast('✓ 已打开本地文件', 'success');
    } else {
      showToast('✗ 打开失败: ' + (data.error || '未知错误'), 'error');
    }
  } catch (e) {
    showToast('✗ 打开失败: ' + e.message, 'error');
  }
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('✓ 已复制到剪贴板', 'success');
  } catch (e) {
    // 回退方案
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('✓ 已复制到剪贴板', 'success');
  }
}

function closeWikiDetail() {
  document.getElementById('kb-wiki-detail-overlay').style.display = 'none';
}

async function createWikiStub(force = false) {
  const concept = prompt('请输入新概念名称：');
  if (!concept) return;
  try {
    const data = await apiPost('/api/knowledge/stub', { concept, context: '手动创建', force });
    if (data.success) {
      showToast(`✨ 已创建 stub: ${concept}`, 'success');
      if (KBManager.activeTab === 'wiki') loadKbWiki();
      else if (KBManager.activeTab === 'growth') loadKbGrowth();
      else if (KBManager.activeTab === 'overview') loadKbOverview();
      else if (KBManager.activeTab === 'health') loadKbHealth();
    } else if (data.action === 'suggest_merge') {
      const similarList = data.similar.map(s => `• ${s.title} [${s.source}:${s.growth_stage}]`).join('\n');
      const confirmCreate = confirm(`检测到相似概念:\n${similarList}\n\n${data.message}\n\n点击"确定"强制创建，点击"取消"取消。`);
      if (confirmCreate) {
        createWikiStub(true);
      }
    } else {
      showToast('✗ 创建失败', 'error');
    }
  } catch (e) {
    showToast('✗ 创建失败: ' + e.message, 'error');
  }
}

// 知识库管理器事件绑定（在 bindEvents 中调用）
function bindKbManagerEvents() {
  // 工具栏按钮
  document.getElementById('toolbar-kb')?.addEventListener('click', openKbManager);
  document.getElementById('toolbar-skills')?.addEventListener('click', openSkillManager);
  document.getElementById('toolbar-tasks')?.addEventListener('click', () => {
    // 滚动到任务面板（右侧）
    const panel = document.querySelector('.task-panel') || document.querySelector('.right-panel');
    if (panel) panel.scrollIntoView({ behavior: 'smooth' });
    else showToast('📋 任务面板在右侧栏', 'info');
  });
  document.getElementById('toolbar-usage')?.addEventListener('click', async () => {
    // 轻量用量显示
    const data = await apiGet('/api/usage');
    const daily = data.daily || {};
    showModal(`📊 Token 用量（今日）\n\n• Prompt: ${daily.prompt || 0}\n• Completion: ${daily.completion || 0}\n• 调用次数: ${daily.calls || 0}\n\nProvider: ${Object.keys(data.by_provider || {}).join(', ') || '无记录'}`);
  });

  // 知识库管理器
  document.getElementById('kb-manager-close')?.addEventListener('click', closeKbManager);
  document.getElementById('kb-manager-overlay')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeKbManager();
  });

  document.querySelectorAll('.kb-tab').forEach(tab => {
    tab.addEventListener('click', () => switchKbTab(tab.dataset.tab));
  });

  document.getElementById('kb-wiki-detail-close')?.addEventListener('click', closeWikiDetail);
  document.getElementById('kb-wiki-detail-overlay')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeWikiDetail();
  });

  document.getElementById('kb-wiki-create-stub')?.addEventListener('click', createWikiStub);
  document.getElementById('kb-wiki-filter')?.addEventListener('change', loadKbWiki);

  // 技能管理器
  document.getElementById('skill-manager-close')?.addEventListener('click', closeSkillManager);
  document.getElementById('skill-manager-overlay')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeSkillManager();
  });
  document.getElementById('skill-save-btn')?.addEventListener('click', saveSkillConfig);
  document.getElementById('skill-reset-btn')?.addEventListener('click', resetSkillConfig);
  document.getElementById('skill-search-input')?.addEventListener('input', filterSkillList);
  document.querySelectorAll('input[name="skill-mode"]').forEach(radio => {
    radio.addEventListener('change', onSkillModeChange);
  });
}
