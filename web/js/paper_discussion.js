/**
 * paper_discussion.js — 文献独立讨论窗口（v4.1）
 * 围绕单篇论文的深度讨论，支持检索增强，讨论后归档到知识库。
 */

const PD = {
  arxivId: '', title: '', authors: '', direction: '',
  messages: [],        // 讨论消息 [{role, content, timestamp}]
  searchResults: [],   // 检索结果
  isOpen: false,
};

// 打开讨论弹窗
async function openPaperDiscussion(arxivId, title) {
  PD.arxivId = arxivId;
  PD.title = title;
  PD.messages = [];
  PD.searchResults = [];
  PD.isOpen = true;

  document.getElementById('pd-title').textContent = '📄 ' + title.slice(0, 50);
  document.getElementById('paper-discussion-overlay').style.display = 'flex';

  // 加载论文信息
  const infoDiv = document.getElementById('pd-paper-info');
  infoDiv.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载论文信息…</span>';
  try {
    const data = await apiGet(`/api/knowledge/file-content?path=${encodeURIComponent('raw/papers/' + _findPaperFilename(arxivId))}`);
    if (data.content) {
      // 提取摘要前200字
      const abstract = data.content.match(/## 摘要\s*\n([\s\S]*?)(?:\n##|$)/i);
      infoDiv.innerHTML = `<strong>arXiv:${arxivId}</strong> · ${escapeHtml((abstract ? abstract[1] : data.content).slice(0, 150))}…`;
      // 注入论文上下文作为首条系统消息
      PD.messages.push({ role: 'system', content: `我们正在讨论论文：${title}\n\n论文内容摘要：\n${data.content.slice(0, 3000)}`, timestamp: Date.now() });
    }
  } catch (e) {
    infoDiv.innerHTML = `<strong>arXiv:${arxivId}</strong> · ${escapeHtml(title)}`;
  }

  // 林赛开场
  PD.messages.push({ role: 'assistant', content: `我是林赛。这篇 ${title.slice(0, 40)} 我们来深入讨论。\n\n你可以问我这篇论文的任何问题——物理机制、实验方法、与你研究的关联。我也可以帮你检索相关文献补充信息。\n\n讨论结束后，点「📚一键归档」把讨论沉淀到知识库。`, timestamp: Date.now() });
  renderPdMessages();
}

// 渲染讨论消息
function renderPdMessages() {
  const container = document.getElementById('pd-messages');
  if (!container) return;
  let html = '';
  for (const m of PD.messages) {
    if (m.role === 'system') continue;  // 系统消息不显示
    const isUser = m.role === 'user';
    html += `<div class="message ${isUser ? 'user' : 'assistant'}" style="margin-bottom:12px;">
      <div class="message-bubble ${isUser ? 'message-user' : 'message-assistant'}" style="padding:8px 12px;border-radius:8px;max-width:85%;${isUser ? 'background:var(--accent-color);color:#fff;margin-left:auto;' : 'background:var(--bg-secondary);'}">
        <div style="font-size:0.82rem;line-height:1.5;white-space:pre-wrap;">${escapeHtml(m.content)}</div>
      </div>
    </div>`;
  }
  container.innerHTML = html;
  container.scrollTop = container.scrollHeight;
}

// 发送讨论消息
async function pdSendMessage() {
  const input = document.getElementById('pd-input');
  const content = input.value.trim();
  if (!content) return;
  input.value = '';

  PD.messages.push({ role: 'user', content, timestamp: Date.now() });
  renderPdMessages();

  // typing 指示
  const container = document.getElementById('pd-messages');
  const typing = document.createElement('div');
  typing.id = 'pd-typing';
  typing.innerHTML = '<div style="color:var(--text-tertiary);font-size:0.8rem;padding:4px;">◐ 林赛思考中…</div>';
  container.appendChild(typing);

  try {
    // 构建对话上下文（含论文+历史讨论+检索结果）
    const sysPrompt = '你是林赛，强场超快光学独立PI。用户正在和你讨论一篇论文。基于你的专业知识库和论文内容回答。如果需要补充信息，建议用户用右侧检索面板搜索。';
    const context = PD.messages.filter(m => m.role !== 'system').map(m => ({ role: m.role, content: m.content }));
    // 加入论文系统消息
    const sysMsg = PD.messages.find(m => m.role === 'system');
    const fullSys = sysPrompt + (sysMsg ? '\n\n' + sysMsg.content : '');

    const resp = await fetch('/api/chat/simple', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ system_prompt: fullSys, messages: context }),
    });
    const data = await resp.json();
    typing.remove();
    PD.messages.push({ role: 'assistant', content: data.response || data.error || '(无响应)', timestamp: Date.now() });
    renderPdMessages();
  } catch (e) {
    typing.remove();
    PD.messages.push({ role: 'assistant', content: '抱歉，响应出错: ' + e.message, timestamp: Date.now() });
    renderPdMessages();
  }
}

// 检索（本地知识库 / deepxiv）
async function pdSearch(type) {
  const query = document.getElementById('pd-search-input').value.trim();
  if (!query) { showToast('请输入检索关键词', 'warning'); return; }
  const resultsDiv = document.getElementById('pd-search-results');
  resultsDiv.innerHTML = '<span style="color:var(--text-tertiary);">◐ 检索中…</span>';

  try {
    if (type === 'local') {
      const data = await apiGet(`/api/knowledge/search?q=${encodeURIComponent(query)}&top_k=8`);
      const results = data.results || [];
      if (!results.length) { resultsDiv.innerHTML = '<p style="color:var(--text-tertiary);">未找到相关内容</p>'; return; }
      resultsDiv.innerHTML = results.map(r => `<div style="padding:6px;margin-bottom:4px;background:var(--bg-tertiary);border-radius:5px;cursor:pointer;" onclick="pdInjectResult('${escapeAttr(r.title || r.doc).slice(0,40)}')">
        <div style="font-size:0.8rem;font-weight:500;">${escapeHtml(r.title || r.doc)}</div>
        <div style="font-size:0.72rem;color:var(--text-tertiary);">${escapeHtml((r.text || '').slice(0, 80))}</div>
      </div>`).join('');
    } else {
      // deepxiv / web 检索
      resultsDiv.innerHTML = '<span style="color:var(--text-tertiary);">◐ 通过 hermes 检索中（可能需要 30s+）…</span>';
      const resp = await fetch('/api/hermes/run', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: `检索关于"${query}"的最新arXiv论文，列出3-5篇最相关的（标题/arXiv ID/一句话摘要）。`, timeout: 120 }),
      });
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let full = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split('\n')) {
          if (line.startsWith('data: ')) {
            try { const evt = JSON.parse(line.slice(6)); if (evt.type === 'token') full += evt.content; } catch {}
          }
        }
      }
      resultsDiv.innerHTML = `<div style="padding:8px;background:var(--bg-tertiary);border-radius:5px;font-size:0.8rem;white-space:pre-wrap;">${escapeHtml(full.slice(0, 1500))}</div>
        <button onclick="pdInjectResult('检索结果')" style="margin-top:4px;padding:3px 8px;font-size:0.75rem;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;">📥 注入讨论</button>`;
    }
  } catch (e) {
    resultsDiv.innerHTML = '<span style="color:var(--error-color);">检索失败: ' + escapeHtml(e.message) + '</span>';
  }
}

// 注入检索结果到讨论
function pdInjectResult(label) {
  PD.messages.push({ role: 'user', content: `[检索补充] ${label}（见右侧检索面板结果）`, timestamp: Date.now() });
  renderPdMessages();
  showToast('已注入讨论上下文', 'success');
}

// 归档：全自动
async function pdArchiveAuto() {
  if (PD.messages.length < 3) { showToast('讨论内容太少，无法归档', 'warning'); return; }
  const btn = document.getElementById('pd-archive-auto');
  btn.disabled = true; btn.textContent = '◐ 归档中…';
  try {
    const result = await apiPost('/api/paper-discussion/archive', {
      arxiv_id: PD.arxivId, title: PD.title,
      messages: PD.messages.filter(m => m.role !== 'system'),
      mode: 'auto',
    });
    if (result.success) {
      showToast(`✓ 归档完成：讨论记录 + ${result.concepts_generated || 0} 概念笔记`, 'success');
      closePaperDiscussion();
    } else {
      showToast('✗ ' + (result.error || '归档失败'), 'error');
    }
  } catch (e) {
    showToast('✗ 归档失败: ' + e.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = '📚 一键归档';
  }
}

// 归档：分步（半自动）
async function pdArchiveStep() {
  if (PD.messages.length < 3) { showToast('讨论内容太少', 'warning'); return; }
  // 第一步：AI 整理讨论为摘要
  const btn = document.getElementById('pd-archive-step');
  btn.disabled = true; btn.textContent = '◐ 整理中…(1/3)';
  try {
    const result = await apiPost('/api/paper-discussion/archive', {
      arxiv_id: PD.arxivId, title: PD.title,
      messages: PD.messages.filter(m => m.role !== 'system'),
      mode: 'step1_summarize',
    });
    if (result.success && result.summary) {
      // 显示整理结果供用户确认
      const confirmHtml = `<div style="max-width:520px;">
        <h3 style="margin-bottom:8px;">📝 讨论整理结果</h3>
        <p style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:8px;">确认后将继续凝练核心观点并提取概念条目。</p>
        <div style="background:var(--bg-secondary);padding:10px;border-radius:6px;font-size:0.82rem;max-height:300px;overflow-y:auto;white-space:pre-wrap;margin-bottom:12px;">${escapeHtml(result.summary)}</div>
        ${result.concepts_suggested ? `<div style="margin-bottom:8px;"><strong>建议提取概念：</strong>${result.concepts_suggested.map(c => `<span style="display:inline-block;padding:2px 8px;margin:2px;background:var(--bg-tertiary);border-radius:10px;font-size:0.78rem;">${escapeHtml(c)}</span>`).join('')}</div>` : ''}
        <div style="display:flex;gap:8px;">
          <button id="pd-step-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;">✓ 确认并归档</button>
          <button onclick="closeModal()" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;">取消</button>
        </div></div>`;
      showModal(confirmHtml);
      document.getElementById('pd-step-confirm').onclick = async () => {
        document.getElementById('pd-step-confirm').textContent = '◐ 凝练+归档中…';
        try {
          const final = await apiPost('/api/paper-discussion/archive', {
            arxiv_id: PD.arxivId, title: PD.title, mode: 'step2_finalize',
            summary: result.summary, concepts_suggested: result.concepts_suggested || [],
          });
          showToast(`✓ 归档完成：${final.concepts_generated || 0} 概念笔记`, 'success');
          closeModal();
          closePaperDiscussion();
        } catch (e) { showToast('✗ ' + e.message, 'error'); }
      };
    }
  } catch (e) {
    showToast('✗ 整理失败: ' + e.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = '📝 分步归档';
  }
}

// 关闭讨论
function closePaperDiscussion() {
  document.getElementById('paper-discussion-overlay').style.display = 'none';
  PD.isOpen = false;
}

// 工具：根据 arxiv_id 找文件名
function _findPaperFilename(arxivId) {
  // 简单拼接（实际文件名格式：year-arxivid-slug.md）
  return `${arxivId}.md`;  // 后端会做模糊匹配
}

// 绑定事件
function bindPaperDiscussionEvents() {
  document.getElementById('pd-close')?.addEventListener('click', closePaperDiscussion);
  document.getElementById('paper-discussion-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closePaperDiscussion();
  });
  document.getElementById('pd-send')?.addEventListener('click', pdSendMessage);
  document.getElementById('pd-input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); pdSendMessage(); }
  });
  document.getElementById('pd-search-local')?.addEventListener('click', () => pdSearch('local'));
  document.getElementById('pd-search-web')?.addEventListener('click', () => pdSearch('web'));
  document.getElementById('pd-archive-auto')?.addEventListener('click', pdArchiveAuto);
  document.getElementById('pd-archive-step')?.addEventListener('click', pdArchiveStep);
}
