/**
 * chat.js — 消息渲染、SSE 流式发送、文件上传、消息编辑/删除、Agora 导出、文献列表、聊天侧栏
 */

// ============================================
// 消息渲染
// ============================================
function appendMessage(role, rawContent, timestamp, animate = true, msgId = null) {
  const container = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  if (msgId) div.dataset.msgId = msgId;

  const content = (typeof rawContent === 'string') ? rawContent : String(rawContent || '');
  const avatar = role === 'user' ? '你' : '林';
  const time = timestamp ? formatTime(timestamp) : formatTime(new Date().toISOString());

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

  let fullContent = content;
  if (window._kbSelectedFiles.length || window._pendingKbContext) {
    const kbCtx = await injectKbContext();
    if (kbCtx) {
      fullContent = content + '\n' + kbCtx;
      window._kbSelectedFiles = [];
      updateKbContextBadge();
    }
  }

  appendMessage('user', content);
  document.getElementById('message-input').value = '';

  State.isStreaming = true;
  document.getElementById('typing-indicator').style.display = 'flex';
  updateStatus('林赛正在思考…');

  const assistantDiv = appendMessage('assistant', '', null, true);
  const bubble = assistantDiv.querySelector('.message-bubble');
  bubble.innerHTML = '';

  const STREAM_TIMEOUT_MS = 120000;
  let streamTimeoutId = null;

  try {
    const res = await fetch(API_BASE + `/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: fullContent, mode: State.currentMode }),
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
            const token = (typeof data.content === 'string') ? data.content : String(data.content || '');
            fullText += token;
            bubble.innerHTML = renderMarkdown(fullText);
            scrollToBottom();
          } else if (data.type === 'tools') {
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
            break;
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

    bubble.innerHTML = renderMarkdown(fullText);
    updateStatus('就绪');
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
    renderReferenceList([]);
    showToast('加载文献失败: ' + e.message, 'error');
  }
}

function renderReferenceList(refs) {
  const container = document.getElementById('reference-list');
  if (!Array.isArray(refs) || refs.length === 0) {
    container.innerHTML = '<p class="empty">暂无引用</p>';
    return;
  }
  container.innerHTML = refs.slice(0, 10).map(r => {
    const path = (r && typeof r.path === 'string') ? r.path : '';
    const title = (r && typeof r.title === 'string') ? r.title : '';
    const filename = (r && typeof r.filename === 'string') ? r.filename : '';
    return `
    <div class="reference-item" data-path="${escapeHtml(path)}">
      📄 ${escapeHtml(title || filename || '未命名')}
    </div>
  `;
  }).join('');

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
    closeModal('agora-modal');
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
  openModal('edit-message-modal');
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

    const msgDiv = document.querySelector(`.message[data-msg-id="${editingMsgId}"]`);
    if (msgDiv) {
      msgDiv.querySelector('.message-bubble').innerHTML = renderMarkdown(newContent);
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
    closeModal('edit-message-modal');
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
// 聊天侧栏折叠
// ============================================
function initChatSidebar() {
  const sidebar = document.getElementById('chat-sidebar');
  if (!sidebar) return;
  if (localStorage.getItem('chat-collapsed') === 'true') {
    sidebar.classList.add('collapsed');
  }
  document.getElementById('chat-collapse-btn')?.addEventListener('click', () => {
    sidebar.classList.add('collapsed');
    localStorage.setItem('chat-collapsed', 'true');
  });
  document.getElementById('chat-sidebar-toggle')?.addEventListener('click', () => {
    sidebar.classList.remove('collapsed');
    localStorage.setItem('chat-collapsed', 'false');
  });
}
