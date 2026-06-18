/**
 * projects.js — 项目面板前端（v2.9.0：层次树 + 卡片流 + 反馈 + 确认）
 * 零框架依赖，原生 JavaScript，复用 app.js 的 apiGet/apiPost/showToast/escapeHtml。
 */

const ProjectsState = { currentTab: 'papers' };  // 默认文献简报（最常用）

function openProjectsManager() {
  const overlay = document.getElementById('projects-overlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  // 默认激活 papers tab
  ProjectsState.currentTab = 'papers';
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.style.background = btn.dataset.tab === 'papers' ? 'var(--bg-active)' : 'transparent';
  });
  loadProjectsTab('papers');
}

function closeProjectsManager() {
  document.getElementById('projects-overlay').style.display = 'none';
}

function switchProjectsTab(tab) {
  ProjectsState.currentTab = tab;
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.style.background = btn.dataset.tab === tab ? 'var(--bg-active)' : 'transparent';
  });
  loadProjectsTab(tab);
}

async function loadProjectsTab(tab) {
  const body = document.getElementById('projects-body');
  if (!body) return;
  body.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">◐ 加载中…</p>';
  try {
    if (tab === 'nsfc') await renderNsfcTree(body);
    else if (tab === 'papers') await renderPapersCards(body);
    else if (tab === 'sync') await renderSyncTab(body);
  } catch (e) {
    body.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// NSFC 层次折叠树（v2.9.0）
// ============================================
async function renderNsfcTree(container) {
  const data = await apiGet('/api/projects/nsfc/tree');
  if (!data.available) {
    container.innerHTML = '<p style="color:var(--text-tertiary);">NSFC 项目数据不可用</p>';
    return;
  }

  let html = `<div style="margin-bottom:12px;padding:8px 12px;background:var(--bg-secondary);border-radius:6px;font-size:0.8rem;color:var(--text-secondary);">
    📅 最后更新: ${escapeHtml(data.last_updated || '?')} | 点击区块展开/折叠，点击文件路径查看内容
  </div>`;

  const statusColors = {
    done: 'var(--success-color)', in_progress: 'var(--info-color)',
    risk: 'var(--error-color)', pending_decision: 'var(--warning-color)',
    blocked: 'var(--error-color)',
  };
  const statusIcons = { done: '✅', in_progress: '⏳', risk: '⚠️', pending_decision: '📌', blocked: '❌' };

  for (const sec of data.sections) {
    const openAttr = sec.default_open ? 'open' : '';
    html += `<details ${openAttr} style="margin-bottom:8px;border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">
      <summary style="padding:8px 12px;cursor:pointer;font-weight:600;font-size:0.9rem;background:var(--bg-secondary);user-select:none;">
        ${escapeHtml(sec.icon)} ${escapeHtml(sec.title.replace(/^[\u{1F000}-\u{1FFFF}✅⏳⚠📌❌📋🎯📊🧠🔁📅🔗📚]+\s*/u, ''))}
        <span style="font-weight:400;color:var(--text-tertiary);font-size:0.78rem;"> (${sec.rows.length})</span>
      </summary>
      <div style="padding:8px 12px;">`;

    if (sec.summary) {
      html += `<div style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:8px;padding:4px 8px;background:var(--bg-tertiary);border-radius:4px;">${escapeHtml(sec.summary)}</div>`;
    }

    for (const row of sec.rows) {
      const color = statusColors[row.status] || 'inherit';
      const icon = statusIcons[row.status] || '○';

      if (row.type === 'table') {
        html += `<div style="display:flex;align-items:start;gap:6px;padding:4px 0;font-size:0.82rem;border-bottom:1px solid var(--border-color);">`;
        html += `<span style="flex-shrink:0;">${icon}</span>`;
        html += `<span style="flex:1;color:${color};">${row.cells.map(c => escapeHtml(c).replace(/`([^`]+)`/g, '<code style="background:var(--bg-tertiary);padding:1px 4px;border-radius:3px;font-size:0.78rem;">$1</code>')).join(' | ')}</span>`;
        // 文件路径按钮
        for (const fp of row.file_paths) {
          html += `<button onclick="loadNsfcFile('${escapeHtml(fp)}')" style="flex-shrink:0;padding:2px 6px;font-size:0.72rem;border:1px solid var(--border-color);border-radius:3px;cursor:pointer;background:var(--bg-primary);">📄</button>`;
        }
        html += `</div>`;
      } else if (row.type === 'list') {
        html += `<div style="display:flex;align-items:start;gap:6px;padding:3px 0;font-size:0.82rem;">`;
        html += `<span style="flex-shrink:0;color:${color};">${icon}</span>`;
        html += `<span style="flex:1;">${row.cells.map(c => escapeHtml(c).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code style="background:var(--bg-tertiary);padding:1px 4px;border-radius:3px;font-size:0.78rem;">$1</code>')).join(' ')}</span>`;
        for (const fp of row.file_paths) {
          html += `<button onclick="loadNsfcFile('${escapeHtml(fp)}')" style="flex-shrink:0;padding:1px 5px;font-size:0.72rem;border:1px solid var(--border-color);border-radius:3px;cursor:pointer;">📄</button>`;
        }
        html += `</div>`;
      } else if (row.type === 'text') {
        html += `<div style="padding:6px 0;font-size:0.82rem;font-weight:500;color:var(--text-secondary);border-top:1px dashed var(--border-color);">${escapeHtml(row.cells[0] || '')}</div>`;
      }
    }
    html += `</div></details>`;
  }

  html += `<div id="nsfc-file-viewer" style="margin-top:12px;display:none;"></div>`;
  container.innerHTML = html;
}

// 加载 NSFC 文件内容（第3层展开）
async function loadNsfcFile(filePath) {
  const viewer = document.getElementById('nsfc-file-viewer');
  if (!viewer) return;
  viewer.style.display = 'block';
  viewer.innerHTML = `<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;"><p style="color:var(--text-tertiary);">◐ 加载 ${escapeHtml(filePath)}…</p></div>`;
  try {
    // 从文件路径推断 topic（如 topics/T3_xxx/ → T3）
    const topicMatch = filePath.match(/topics\/(T\d)/);
    const topic = topicMatch ? topicMatch[1] : '';
    const data = await apiGet(`/api/projects/nsfc/proposal?topic=${topic || filePath}`);
    if (data.available && data.content) {
      viewer.innerHTML = `<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--accent-color);">
        <div style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:6px;">📄 ${escapeHtml(data.path)} (${data.size_kb}KB)</div>
        <div style="font-size:0.82rem;max-height:400px;overflow-y:auto;white-space:pre-wrap;line-height:1.5;">${escapeHtml(data.content.slice(0, 3000))}${data.content.length > 3000 ? '\n\n... (截断，共 ' + data.content.length + ' 字符)' : ''}</div>
      </div>`;
    } else {
      viewer.innerHTML = `<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;"><p style="color:var(--text-tertiary);">无法读取 ${escapeHtml(filePath)}（可能是非 topics 路径）</p></div>`;
    }
  } catch (e) {
    viewer.innerHTML = `<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;"><p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p></div>`;
  }
}

// ============================================
// 文献卡小红书式卡片流（v2.9.0）
// ============================================
async function renderPapersCards(container) {
  const candidates = await apiGet('/api/projects/papers/candidates');

  let html = '';
  if (candidates.available) {
    html += `<div style="margin-bottom:12px;padding:8px 12px;background:var(--bg-secondary);border-radius:6px;font-size:0.8rem;color:var(--text-secondary);">
      📄 今日候选 <strong>${candidates.total}</strong> 篇 (${escapeHtml(candidates.date || '?')}) — 👍感兴趣(归档+深分析) · 👎跳过 · 📥仅归档
    </div>`;
    html += '<div id="papers-card-list" style="display:flex;flex-direction:column;gap:10px;">';
    for (const p of (candidates.papers || [])) {
      const scorePct = Math.round((p.score || 0) * 100);
      const analysisBadge = p.has_analysis ? '<span style="color:var(--success-color);font-size:0.72rem;">✓已解析</span>' : '';
      html += `<div class="paper-card" id="card-${escapeHtml(p.arxiv_id)}" style="padding:12px;background:var(--bg-secondary);border-radius:8px;border:1px solid var(--border-color);transition:opacity 0.3s;">`;
      html += `<div style="font-size:0.88rem;font-weight:600;line-height:1.4;margin-bottom:4px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(p.title)}</div>`;
      html += `<div style="font-size:0.75rem;color:var(--text-tertiary);margin-bottom:6px;">${escapeHtml(p.authors)} · ${escapeHtml(p.direction)} · 评分 ${scorePct}% ${analysisBadge}</div>`;
      if (p.tldr) {
        html += `<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">${escapeHtml(p.tldr)}</div>`;
      }
      html += `<div style="display:flex;gap:8px;">`;
      html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','interested',this)" style="flex:1;padding:6px;border:1px solid var(--success-color);border-radius:6px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.82rem;">👍 感兴趣</button>`;
      html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','skip',this)" style="flex:1;padding:6px;border:1px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-tertiary);cursor:pointer;font-size:0.82rem;">👎 跳过</button>`;
      html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','archive',this)" style="flex:1;padding:6px;border:1px solid var(--border-color);border-radius:6px;background:transparent;cursor:pointer;font-size:0.82rem;">📥 归档</button>`;
      html += `</div></div>`;
    }
    html += '</div>';
  } else {
    html = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">暂无候选数据</p>';
  }
  container.innerHTML = html;
}

// 文献反馈处理
async function paperFeedback(arxivId, action, btn) {
  const card = btn.closest('.paper-card');
  if (action === 'interested') {
    btn.textContent = '◐ 处理中…'; btn.disabled = true;
  }
  try {
    const resp = await apiPost('/api/projects/papers/feedback', { arxiv_id: arxivId, action });
    const r = resp.result || {};

    if (action === 'interested') {
      let msg = `✓ 已归档: ${r.archived || '已存在'}`;
      if (r.has_analysis) msg += ' + 深度解析已导入';
      showToast(msg, 'success');

      // 展示 wiki 建议确认
      if (r.wiki_suggestion && r.wiki_suggestion.available) {
        showWikiGrowConfirm(r.wiki_suggestion);
      }
    } else if (action === 'archive') {
      showToast(`✓ 已归档: ${r.archived || '已存在'}`, 'success');
    } else if (action === 'skip') {
      showToast('👎 已记录偏好', 'info');
    }

    // 卡片淡出移除
    if (card) {
      card.style.opacity = '0.3';
      setTimeout(() => card.remove(), 400);
    }
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
    if (action === 'interested') { btn.textContent = '👍 感兴趣'; btn.disabled = false; }
  }
}

// wiki 笔记生成确认弹窗
function showWikiGrowConfirm(suggestion) {
  const concepts = suggestion.concepts || [];
  const methods = suggestion.methods || [];
  const relations = suggestion.relations || [];
  if (!concepts.length && !methods.length && !relations.length) {
    return;  // 无建议，不弹窗
  }

  let html = `<div style="max-width:500px;">
    <h3 style="margin-bottom:8px;">📚 知识库生长建议</h3>
    <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">已归档 <strong>${escapeHtml(suggestion.title)}</strong>，以下内容可提取为知识库笔记：</p>`;

  // concept 建议
  if (concepts.length) {
    html += '<div style="margin-bottom:10px;"><div style="font-size:0.8rem;font-weight:600;margin-bottom:4px;">概念笔记：</div>';
    concepts.slice(0, 6).forEach((c, i) => {
      const checked = c.existing ? '' : 'checked';
      const tag = c.existing ? `<span style="color:var(--info-color);font-size:0.72rem;">→ 连接已有「${escapeHtml(c.existing_title)}」</span>` : '<span style="color:var(--success-color);font-size:0.72rem;">新建</span>';
      html += `<label style="display:flex;align-items:center;gap:6px;padding:3px 0;font-size:0.82rem;">
        <input type="checkbox" id="grow-c-${i}" ${checked} ${c.existing ? '' : ''}> 
        <span>${escapeHtml(c.name)}</span> ${tag}
      </label>`;
    });
    html += '</div>';
  }

  // relation 建议
  if (relations.length) {
    html += '<div style="margin-bottom:10px;"><div style="font-size:0.8rem;font-weight:600;margin-bottom:4px;">图谱关联：</div>';
    relations.slice(0, 4).forEach((rel, i) => {
      html += `<label style="display:flex;align-items:center;gap:6px;padding:2px 0;font-size:0.8rem;">
        <input type="checkbox" id="grow-r-${i}" checked> 
        <span>${escapeHtml(rel.from)} → ${escapeHtml(rel.to)}</span>
      </label>`;
    });
    html += '</div>';
  }

  html += `<div style="display:flex;gap:8px;margin-top:12px;">
    <button id="grow-confirm-btn" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 确认生成</button>
    <button id="grow-skip-btn" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">跳过</button>
  </div></div>`;

  showModal(html);

  // 绑定按钮
  setTimeout(() => {
    const confirmBtn = document.getElementById('grow-confirm-btn');
    const skipBtn = document.getElementById('grow-skip-btn');
    if (skipBtn) skipBtn.onclick = closeModal;
    if (confirmBtn) confirmBtn.onclick = async () => {
      const confirmed = { concepts: [], relations: [], project: suggestion.project };
      concepts.forEach((c, i) => {
        const cb = document.getElementById(`grow-c-${i}`);
        if (cb && cb.checked) confirmed.concepts.push({ name: c.name, generate: true, type: 'concepts' });
      });
      relations.forEach((rel, i) => {
        const cb = document.getElementById(`grow-r-${i}`);
        if (cb && cb.checked) confirmed.relations.push({ from: rel.from, to: rel.to, confirm: true });
      });
      confirmBtn.textContent = '◐ 生成中…'; confirmBtn.disabled = true;
      try {
        const result = await apiPost('/api/knowledge/grow', { arxiv_id: suggestion.arxiv_id, confirmed });
        showToast(`✓ 生成 ${result.generated_concepts.length} 篇笔记 + ${result.generated_relations.length} 条关联`, 'success');
        closeModal();
      } catch (e) {
        showToast(`✗ 生成失败: ${e.message}`, 'error');
        confirmBtn.textContent = '✓ 确认生成'; confirmBtn.disabled = false;
      }
    };
  }, 100);
}

// ============================================
// 多端同步（沿用现有）
// ============================================
async function renderSyncTab(container) {
  const status = await apiGet('/api/sync/status');
  let html = '<div style="margin-bottom:16px;">';
  html += `<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">同步状态</div>`;
  html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;">
    <div style="font-size:0.85rem;">已同步会话: <strong>${status.synced_sessions_count}</strong></div>
    <div style="font-size:0.85rem;margin-top:4px;">已同步文献: <strong>${status.synced_papers_count}</strong></div>
    <div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:4px;">上次同步: ${escapeHtml(status.last_sync || '从未')}</div>
  </div>`;
  html += `<button id="sync-run-btn" style="margin-top:10px;padding:8px 16px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">🔄 立即同步</button>`;
  html += '</div>';
  if (status.history && status.history.length) {
    html += '<div><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">同步历史</div>';
    status.history.forEach(h => {
      html += `<div style="padding:4px 0;font-size:0.78rem;color:var(--text-tertiary);">${h.timestamp.slice(0,16)} | 会话+${h.new_sessions} 文献+${h.new_papers}</div>`;
    });
    html += '</div>';
  }
  container.innerHTML = html;
  const syncBtn = document.getElementById('sync-run-btn');
  if (syncBtn) syncBtn.addEventListener('click', async () => {
    syncBtn.disabled = true; syncBtn.textContent = '同步中…';
    try {
      const result = await apiPost('/api/sync/run', {});
      showToast(`✓ 同步完成：会话 +${result.result.new_sessions}，文献 +${result.result.new_papers}`, 'success');
      renderSyncTab(container);
    } catch (e) { showToast(`✗ 同步失败: ${e.message}`, 'error'); }
    finally { syncBtn.disabled = false; syncBtn.textContent = '🔄 立即同步'; }
  });
}

// ============================================
// 初始化
// ============================================
function bindProjectsEvents() {
  document.getElementById('toolbar-projects')?.addEventListener('click', openProjectsManager);
  document.getElementById('projects-close')?.addEventListener('click', closeProjectsManager);
  document.getElementById('projects-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeProjectsManager();
  });
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchProjectsTab(btn.dataset.tab));
  });
  document.getElementById('proj-refresh')?.addEventListener('click', () => loadProjectsTab(ProjectsState.currentTab));
}

if (typeof escapeHtml === 'undefined') {
  window.escapeHtml = function(s) { const d = document.createElement('div'); d.textContent = String(s); return d.innerHTML; };
}
