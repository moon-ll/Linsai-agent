/**
 * kb.js — 知识库管理（文件树、Wiki 预览、双向链接、@知识库上下文、同步、健康检查、筛选、分类、标签编辑）
 */

// ============================================
// 知识库管理器状态
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
  openWikiByTitle('🗺️ HHG 知识地图');
}

// ============================================
// Wiki 详情预览
// ============================================
async function openWikiDetail(wikiPath) {
  const titleEl = document.getElementById('kb-preview-title');
  const bodyEl = document.getElementById('kb-preview-body');
  const defaultEl = document.getElementById('kb-preview-default');
  const detailEl = document.getElementById('kb-preview-detail');
  if (!titleEl || !bodyEl) return;

  if (defaultEl) defaultEl.style.display = 'none';
  if (detailEl) detailEl.style.display = 'block';
  titleEl.textContent = '◐ 加载中…';
  bodyEl.innerHTML = '';

  document.querySelectorAll('.kb-tree-item').forEach(el => el.classList.remove('active'));

  try {
    const relPath = wikiPath.replace(/^wiki\//, '');
    const data = await apiGet(`/api/knowledge/wiki/${encodeURIComponent(relPath)}`);
    const fm = data.frontmatter || {};
    const body = data.body || '';

    titleEl.textContent = fm.title || relPath;
    const stage = STAGE_LABELS_FULL[fm.growth_stage] || fm.growth_stage || '未知';

    let renderedBody = body
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\[\[([^\]]+)\]\]/g, (m, name) => {
        const safe = name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        return `<a class="kb-wikilink" onclick="openWikiByTitle('${safe}')" title="点击跳转">${escapeHtml(name)}</a>`;
      });

    renderedBody = renderedBody.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

    const relatedHtml = (fm.related || []).map(r => {
      const safe = String(r).replace(/'/g, "\\'").replace(/"/g, '&quot;');
      return `<span class="kb-related-chip" onclick="openWikiByTitle('${safe}')" title="点击跳转">${escapeHtml(r)}</span>`;
    }).join(' ') || '-';

    bodyEl.innerHTML = `
      <div class="kb-detail-actions">
        <button class="btn-text" onclick="openLocalFile('${wikiPath.replace(/'/g, "\\'")}')">📂 在编辑器中打开</button>
        <button class="btn-text" onclick="copyToClipboard('${wikiPath.replace(/'/g, "\\'")}')">📋 复制路径</button>
      </div>
      <div class="kb-frontmatter">
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">类型</span><span class="kb-frontmatter-value">${fm.type || '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">生长阶段</span><span class="kb-frontmatter-value">${stage}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">确信度</span><span class="kb-frontmatter-value">${((fm.confidence ?? 0) * 100).toFixed(0)}%</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">标签</span><span class="kb-frontmatter-value">${(fm.tags || []).join(', ') || '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">关联</span><span class="kb-frontmatter-value">${relatedHtml}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">更新</span><span class="kb-frontmatter-value">${fm.updated ? new Date(fm.updated).toLocaleString() : '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">路径</span><span class="kb-frontmatter-value">${wikiPath}</span></div>
      </div>
      ${renderTagEditor(fm, wikiPath)}
      <div id="kb-backlinks-region"></div>
      <div class="kb-wiki-body">${renderedBody}</div>
    `;

    bindTagEditor(fm, wikiPath);
    loadBacklinks(fm.title || '');
  } catch (e) {
    bodyEl.innerHTML = `<div class="kb-empty">✗ 加载失败: ${e.message}</div>`;
  }
}

function openWikiByTitle(title) {
  const pages = KBManager.wikiPages || [];
  if (!pages.length) {
    apiGet('/api/knowledge/wiki').then(data => {
      KBManager.wikiPages = data.pages || [];
      openWikiByTitle(title);
    });
    return;
  }
  let found = pages.find(p => p.title === title);
  if (!found) found = pages.find(p => p.path && p.path.replace(/.*\//, '').replace('.md', '') === title);
  if (!found) found = pages.find(p => p.title && p.title.includes(title));
  if (found) {
    openWikiDetail(found.path);
  } else {
    showToast('未找到笔记: ' + title, 'info');
  }
}

async function loadBacklinks(title) {
  if (!title) return;
  const region = document.getElementById('kb-backlinks-region');
  if (!region) return;
  try {
    const data = await apiGet(`/api/knowledge/related?q=${encodeURIComponent(title)}`);
    const related = (data.concepts || data.related || []).filter(r => r !== title);
    if (related.length) {
      region.innerHTML = `<div style="margin:8px 0;padding:6px 10px;background:var(--bg-tertiary);border-radius:6px;">
        <span style="font-size:0.78rem;color:var(--text-secondary);">↩️ 被以下笔记关联：</span>
        ${related.map(r => {
          const safe = String(r).replace(/'/g, "\\'").replace(/"/g, '&quot;');
          return `<span class="kb-related-chip" onclick="openWikiByTitle('${safe}')" title="点击跳转">${escapeHtml(r)}</span>`;
        }).join(' ')}
      </div>`;
    }
  } catch (e) { /* 静默 */ }
}

async function openRawDetail(rawPath) {
  const titleEl = document.getElementById('kb-preview-title');
  const bodyEl = document.getElementById('kb-preview-body');
  const defaultEl = document.getElementById('kb-preview-default');
  const detailEl = document.getElementById('kb-preview-detail');
  if (!titleEl || !bodyEl) return;
  if (defaultEl) defaultEl.style.display = 'none';
  if (detailEl) detailEl.style.display = 'block';
  titleEl.textContent = '📄 ' + rawPath.split('/').pop();
  bodyEl.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';

  try {
    const data = await apiGet(`/api/knowledge/file-content?path=${encodeURIComponent(rawPath)}`);
    if (data.content) {
      let rendered = data.content
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
      const safePath = rawPath.replace(/'/g, "\\'");
      bodyEl.innerHTML = `<div style="margin-bottom:8px;"><button class="btn-text" onclick="openLocalFile('${safePath}')" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;font-size:0.8rem;">📂 在编辑器中打开</button></div>${rendered.slice(0, 6000)}${data.size > 6000 ? '\n\n<p style="color:var(--text-tertiary);">... (截断)</p>' : ''}`;
    } else {
      bodyEl.innerHTML = '<span style="color:var(--error-color);">无法读取（' + escapeHtml(data.error || '未知错误') + '）</span>';
    }
  } catch (e) {
    bodyEl.innerHTML = '<span style="color:var(--error-color);">加载失败: ' + escapeHtml(e.message) + '</span>';
  }
}

async function openLocalFile(relPath) {
  try {
    let fullPath = relPath;
    if (fullPath && fullPath !== 'knowledge' && !fullPath.startsWith('knowledge/') && !fullPath.startsWith('knowledge\\')) {
      fullPath = 'knowledge/' + fullPath;
    }
    const data = await apiPost('/api/open-local', { path: fullPath });
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
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('✓ 已复制到剪贴板', 'success');
  }
}

// ============================================
// @知识库文件讨论
// ============================================
window._kbSelectedFiles = [];
window._pendingKbContext = null;

async function openKbFilePicker() {
  showModal('<div style="max-width:480px;"><h3 style="margin-bottom:8px;">🗂️ 选择知识库文件注入讨论</h3><p style="color:var(--text-secondary);font-size:0.82rem;margin-bottom:12px;">勾选要讨论的知识库内容，发送消息时会自动注入林赛上下文。</p><div id="kb-file-list" style="max-height:350px;overflow-y:auto;"><p style="color:var(--text-tertiary);">◐ 加载中…</p></div><div style="display:flex;gap:8px;margin-top:12px;"><button id="kb-pick-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;">确认选择</button><button id="kb-pick-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;">取消</button></div></div>');
  try {
    const files = await apiGet('/api/knowledge/files');
    const list = document.getElementById('kb-file-list');
    if (!list) return;
    if (!files.length) { list.innerHTML = '<p style="color:var(--text-tertiary);">知识库为空</p>'; return; }
    const groups = {};
    files.forEach(f => { (groups[f.type] = groups[f.type] || []).push(f); });
    let html = '';
    for (const [type, items] of Object.entries(groups)) {
      html += `<div style="font-size:0.8rem;font-weight:600;color:var(--text-secondary);margin:8px 0 4px;">${type} (${items.length})</div>`;
      items.forEach(f => {
        const checked = window._kbSelectedFiles.some(s => s.path === f.path) ? 'checked' : '';
        html += `<label style="display:flex;align-items:center;gap:6px;padding:3px 0;font-size:0.82rem;cursor:pointer;"><input type="checkbox" class="kb-file-cb" data-path="${escapeHtml(f.path)}" data-title="${escapeHtml(f.title)}" ${checked}><span>${escapeHtml(f.title)}</span><span style="color:var(--text-tertiary);font-size:0.72rem;">${f.project ? '['+f.project+']' : ''}</span></label>`;
      });
    }
    list.innerHTML = html;
  } catch (e) { document.getElementById('kb-file-list').innerHTML = `<p style="color:var(--error-color);">加载失败: ${e.message}</p>`; }
  document.getElementById('kb-pick-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('kb-pick-confirm').onclick = () => {
    window._kbSelectedFiles = Array.from(document.querySelectorAll('.kb-file-cb:checked')).map(cb => ({path: cb.dataset.path, title: cb.dataset.title}));
    closeModal('modal-overlay');
    updateKbContextBadge();
  };
}

function handleKbMention(e) {
  const input = e.target;
  const val = input.value;
  const pos = input.selectionStart;
  const before = val.slice(0, pos);
  const atMatch = before.match(/@([^\s@]*)$/);
  const existing = document.getElementById('kb-mention-popup');
  if (!atMatch) { if (existing) existing.remove(); return; }
  const query = atMatch[1];
  if (!window._kbFileCache) return;
  const matches = window._kbFileCache.filter(f => f.title.toLowerCase().includes(query.toLowerCase())).slice(0, 6);
  if (!matches.length) { if (existing) existing.remove(); return; }
  if (existing) existing.remove();
  const popup = document.createElement('div');
  popup.id = 'kb-mention-popup';
  popup.style.cssText = 'position:absolute;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:6px;padding:4px;box-shadow:var(--shadow-md);z-index:9999;max-width:300px;font-size:0.82rem;';
  matches.forEach(f => {
    const item = document.createElement('div');
    item.style.cssText = 'padding:4px 8px;cursor:pointer;border-radius:4px;';
    item.textContent = `${f.title} [${f.type}]`;
    item.onmouseenter = () => item.style.background = 'var(--bg-active)';
    item.onmouseleave = () => item.style.background = '';
    item.onclick = () => {
      input.value = val.slice(0, before.lastIndexOf('@')) + `[${f.title}] ` + val.slice(pos);
      window._kbSelectedFiles.push({path: f.path, title: f.title});
      updateKbContextBadge();
      popup.remove();
      input.focus();
    };
    popup.appendChild(item);
  });
  input.parentElement.style.position = 'relative';
  input.parentElement.appendChild(popup);
}

function updateKbContextBadge() {
  let badge = document.getElementById('kb-context-badge');
  if (!window._kbSelectedFiles.length) { if (badge) badge.remove(); return; }
  if (!badge) {
    badge = document.createElement('span');
    badge.id = 'kb-context-badge';
    badge.style.cssText = 'position:absolute;top:-8px;right:-8px;background:var(--accent-color);color:#fff;border-radius:10px;font-size:0.65rem;padding:1px 5px;';
    document.getElementById('kb-context-btn')?.appendChild(badge);
  }
  badge.textContent = window._kbSelectedFiles.length;
  badge.title = window._kbSelectedFiles.map(f => f.title).join('\n');
}

async function injectKbContext() {
  if (!window._kbSelectedFiles.length && !window._pendingKbContext) return '';
  let context = '';
  const files = window._pendingKbContext ? window._kbSelectedFiles.concat(window._pendingKbContext.map(r => ({path: r.path || r.doc, title: r.title}))) : window._kbSelectedFiles;
  for (const f of files.slice(0, 3)) {
    if (!f.path) continue;
    try {
      const data = await apiGet(`/api/knowledge/file-content?path=${encodeURIComponent(f.path)}`);
      if (data.content) {
        context += `\n\n--- 知识库参考: ${f.title} ---\n${data.content.slice(0, 2000)}\n---\n`;
      }
    } catch (e) { /* 静默 */ }
  }
  window._pendingKbContext = null;
  return context;
}

async function ensureKbFileCache() {
  if (window._kbFileCache) return;
  try { window._kbFileCache = await apiGet('/api/knowledge/files'); } catch (e) { window._kbFileCache = []; }
}

// ============================================
// v3.0.0: 知识库常驻主区（文件树 + 预览）
// ============================================
async function initKbMain() {
  await renderKbTree();

  // 事件委托：确保 <details>/<summary> 点击切换始终生效
  document.getElementById('kb-tree-content')?.addEventListener('click', (e) => {
    const summary = e.target.closest('summary');
    if (!summary) return;
    const details = summary.parentElement;
    if (details && details.tagName === 'DETAILS') {
      e.preventDefault();
      if (details.hasAttribute('open')) {
        details.removeAttribute('open');
      } else {
        details.setAttribute('open', '');
      }
    }
  });

  let treeSearchTimer;
  document.getElementById('kb-tree-search')?.addEventListener('input', (e) => {
    clearTimeout(treeSearchTimer);
    const q = e.target.value.trim();
    if (!q) { renderKbTree(); return; }
    treeSearchTimer = setTimeout(() => searchKbToTree(q), 300);
  });

  document.getElementById('kb-sync-btn')?.addEventListener('click', handleKbSync);
  document.getElementById('kb-health-btn')?.addEventListener('click', handleKbHealth);
  document.getElementById('kb-category-btn')?.addEventListener('click', handleKbCategory);
  document.getElementById('kb-filter-clear')?.addEventListener('click', clearKbFilters);
  ['kb-filter-type', 'kb-filter-stage', 'kb-filter-project', 'kb-filter-tag'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', applyKbFilters);
  });
  loadSyncIndicator();
  loadKbFilters();
}

async function handleKbSync() {
  const btn = document.getElementById('kb-sync-btn');
  if (!btn) return;
  btn.classList.add('syncing');
  btn.textContent = '🔄 同步中…';
  try {
    const result = await apiPost('/api/sync/run', {});
    const r = result.result || result;
    const total = (r.new_sessions || 0) + (r.new_papers || 0);
    if (total > 0) {
      showToast(`✓ 同步完成：新增 ${r.new_sessions || 0} 会话 + ${r.new_papers || 0} 文献，索引和图谱已更新`);
      await renderKbTree();
    } else {
      showToast('✓ 同步完成：无新增（已是最新）');
    }
  } catch (e) {
    showToast('✗ 同步失败: ' + (e.message || e), 'error');
  } finally {
    btn.classList.remove('syncing');
    btn.textContent = '🔄 同步';
    loadSyncIndicator();
  }
}

async function handleKbHealth() {
  const btn = document.getElementById('kb-health-btn');
  if (!btn) return;
  btn.classList.add('syncing');
  try {
    const data = await apiGet('/api/knowledge/health');
    const h = data.health || data;
    const conn = h.graph_connectivity || 0;
    const cov = h.category_coverage || {};
    const alias = h.alias_hit_rate || {};
    const msg = `📊 知识库健康度\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `  📁 raw: ${h.raw_count || 0}  wiki: ${h.wiki_count || 0}\n` +
      `  🕸️ 图谱: ${h.graph_nodes || 0} 节点 / ${h.graph_edges || 0} 边\n` +
      `  🔗 连通性: ${(conn * 100).toFixed(0)}%  孤儿: ${h.graph_orphans || 0}\n` +
      `  🏷️ 分类: ${cov.total_categories || 0} 个，覆盖 ${(cov.coverage_rate * 100).toFixed(0)}%\n` +
      `  📝 别名: ${alias.total_aliases || 0} 个，命中率 ${(alias.hit_rate * 100).toFixed(0)}%\n` +
      `  🌱 待蒸馏: ${h.pending_distill || 0}  晋升候选: ${h.growth_candidates || 0}\n` +
      `  📈 本周新增: ${h.week_new || 0}`;
    alert(msg);
  } catch (e) {
    showToast('✗ 健康检查失败: ' + (e.message || e), 'error');
  } finally {
    btn.classList.remove('syncing');
  }
}

async function loadSyncIndicator() {
  const indicator = document.getElementById('kb-sync-indicator');
  if (!indicator) return;
  try {
    const data = await apiGet('/api/sync/auto-status');
    if (data.launchagent_installed) {
      indicator.className = 'kb-sync-indicator active';
      const history = data.auto_sync_history || [];
      if (history.length > 0) {
        const last = history[history.length - 1];
        const ts = (last.timestamp || '').slice(0, 10);
        indicator.textContent = `自动同步 ${ts}`;
      } else {
        indicator.textContent = '自动同步已开启';
      }
    } else {
      indicator.className = 'kb-sync-indicator inactive';
      indicator.textContent = '手动同步';
    }
  } catch (e) {
    indicator.className = 'kb-sync-indicator inactive';
    indicator.textContent = '';
  }
}

async function loadKbFilters() {
  try {
    const data = await apiGet('/api/knowledge/filters');
    const fillSelect = (id, options) => {
      const sel = document.getElementById(id);
      if (!sel) return;
      const current = sel.value;
      sel.innerHTML = `<option value="">${sel.title || '全部'}</option>`;
      options.forEach(opt => {
        const o = document.createElement('option');
        o.value = opt; o.textContent = opt;
        sel.appendChild(o);
      });
      sel.value = current;
    };
    fillSelect('kb-filter-type', data.types || []);
    fillSelect('kb-filter-stage', data.stages || []);
    fillSelect('kb-filter-project', data.projects || []);
    fillSelect('kb-filter-tag', data.tags || []);
  } catch (e) { /* 静默失败 */ }
}

async function applyKbFilters() {
  const filters = {};
  const type = document.getElementById('kb-filter-type')?.value;
  const stage = document.getElementById('kb-filter-stage')?.value;
  const project = document.getElementById('kb-filter-project')?.value;
  const tag = document.getElementById('kb-filter-tag')?.value;
  if (type) filters.type = type;
  if (stage) filters.stage = stage;
  if (project) filters.project = project;
  if (tag) filters.tag = tag;

  const hasFilter = Object.keys(filters).length > 0;
  const filterBar = document.getElementById('kb-filter-bar');
  if (filterBar) filterBar.style.display = hasFilter ? 'flex' : 'none';

  if (!hasFilter) {
    renderKbTree();
    return;
  }

  const container = document.getElementById('kb-tree-content');
  if (container) container.innerHTML = '◐ 筛选中…';
  try {
    const data = await apiPost('/api/knowledge/filter', { filters });
    renderFilteredTree(data.pages || []);
  } catch (e) {
    if (container) container.innerHTML = '✗ 筛选失败';
  }
}

function clearKbFilters() {
  ['kb-filter-type', 'kb-filter-stage', 'kb-filter-project', 'kb-filter-tag'].forEach(id => {
    const sel = document.getElementById(id);
    if (sel) sel.value = '';
  });
  document.getElementById('kb-filter-bar').style.display = 'none';
  renderKbTree();
}

function renderFilteredTree(pages) {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  if (!pages.length) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-tertiary);">无匹配结果</div>';
    return;
  }
  const html = pages.map(p => {
    const stageIcon = STAGE_ICONS[p.growth_stage] || '○';
    return `<div class="kb-tree-item" data-path="${p.path}" onclick="openWikiDetail('${p.path}')" style="padding:4px 8px;cursor:pointer;border-radius:4px;font-size:0.82rem;">
      ${stageIcon} ${p.title}
      <span style="color:var(--text-tertiary);font-size:0.7rem;">${p.type}</span>
    </div>`;
  }).join('');
  container.innerHTML = `<div style="padding:4px 8px;font-size:0.75rem;color:var(--text-tertiary);">筛选结果 (${pages.length})</div>` + html;
}

async function handleKbCategory() {
  const overlay = document.createElement('div');
  overlay.className = 'kb-modal-overlay';
  overlay.onclick = () => overlay.remove();

  const modal = document.createElement('div');
  modal.className = 'kb-category-modal';
  modal.onclick = e => e.stopPropagation();
  modal.innerHTML = `
    <h3>🏷️ 分类管理</h3>
    <div class="kb-category-list" id="cat-list">加载中…</div>
    <div class="kb-category-form">
      <label>新建分类</label>
      <input type="text" id="cat-name-input" placeholder="分类名称（如：水窗成像）">
      <input type="text" id="cat-keywords-input" placeholder="关键词，逗号分隔（如：水窗,water window,成像）">
      <select id="cat-logic-select">
        <option value="any">任一关键词匹配</option>
        <option value="all">全部关键词匹配</option>
      </select>
      <input type="text" id="cat-desc-input" placeholder="描述（可选）">
      <button class="kb-toolbar-btn" id="cat-create-btn" style="width:100%;margin-top:4px;">➕ 创建分类</button>
    </div>
    <button class="kb-toolbar-btn" id="cat-rescan-btn" style="width:100%;margin-top:6px;">🔄 重新扫描全部</button>
    <button class="kb-toolbar-btn" id="cat-close-btn" style="width:100%;margin-top:4px;">关闭</button>
  `;
  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  const refreshList = async () => {
    const listEl = document.getElementById('cat-list');
    try {
      const data = await apiGet('/api/knowledge/categories');
      const cats = data.categories || [];
      if (!cats.length) {
        listEl.innerHTML = '<div style="color:var(--text-tertiary);font-size:0.82rem;">暂无自定义分类</div>';
        return;
      }
      listEl.innerHTML = cats.map(c => `
        <div class="kb-category-item">
          <span class="cat-name">📂 ${c.name}</span>
          <span class="cat-count">${(c.matched_paths || []).length} 篇</span>
          <span class="cat-delete" data-name="${c.name}">✕</span>
        </div>
      `).join('');
      listEl.querySelectorAll('.cat-delete').forEach(btn => {
        btn.onclick = async () => {
          const name = btn.dataset.name;
          if (!confirm(`删除分类 "${name}"？`)) return;
          await apiPost('/api/knowledge/categories/delete', { name });
          refreshList();
        };
      });
    } catch (e) {
      listEl.innerHTML = '✗ 加载失败';
    }
  };

  document.getElementById('cat-create-btn').onclick = async () => {
    const name = document.getElementById('cat-name-input').value.trim();
    const keywords = document.getElementById('cat-keywords-input').value
      .split(',').map(s => s.trim()).filter(Boolean);
    const logic = document.getElementById('cat-logic-select').value;
    const description = document.getElementById('cat-desc-input').value.trim();
    if (!name || !keywords.length) {
      showToast('请填写分类名称和关键词', 'error');
      return;
    }
    try {
      await apiPost('/api/knowledge/categories/create', { name, keywords, logic, description });
      showToast(`✓ 分类 "${name}" 已创建`);
      document.getElementById('cat-name-input').value = '';
      document.getElementById('cat-keywords-input').value = '';
      document.getElementById('cat-desc-input').value = '';
      refreshList();
    } catch (e) {
      showToast('✗ 创建失败: ' + (e.message || e), 'error');
    }
  };

  document.getElementById('cat-rescan-btn').onclick = async () => {
    try {
      await apiPost('/api/knowledge/categories/scan', {});
      showToast('✓ 全部分类已重新扫描');
      refreshList();
    } catch (e) {
      showToast('✗ 扫描失败', 'error');
    }
  };

  document.getElementById('cat-close-btn').onclick = () => overlay.remove();
  refreshList();
}

function renderTagEditor(frontmatter, pagePath) {
  const tags = Array.isArray(frontmatter.tags) ? frontmatter.tags : [];
  const project = frontmatter.project || '';
  const projectList = typeof project === 'string' ? (project ? [project] : []) : project;

  const tagChips = tags.map(t => `
    <span class="kb-tag-chip">${t}<span class="tag-remove" data-tag="${t}" data-type="tag">✕</span></span>
  `).join('');
  const projChips = projectList.map(p => `
    <span class="kb-tag-chip" style="background:var(--accent);color:white;border-color:var(--accent);">${p}<span class="tag-remove" data-tag="${p}" data-type="project">✕</span></span>
  `).join('');

  return `<div class="kb-tag-editor" id="kb-tag-editor">
    ${projChips}${tagChips}
    <button class="kb-tag-add" id="kb-tag-add-btn">+ 标签</button>
  </div>`;
}

function bindTagEditor(frontmatter, pagePath) {
  const editor = document.getElementById('kb-tag-editor');
  if (!editor) return;

  editor.querySelectorAll('.tag-remove').forEach(btn => {
    btn.onclick = async () => {
      const tag = btn.dataset.tag;
      const type = btn.dataset.type;
      if (!confirm(`移除 ${type === 'project' ? '子库' : '标签'} "${tag}"？`)) return;
      try {
        const fm = { ...frontmatter };
        if (type === 'tag') {
          fm.tags = (Array.isArray(fm.tags) ? fm.tags : []).filter(t => t !== tag);
        } else {
          const proj = typeof fm.project === 'string' ? [fm.project] : (fm.project || []);
          fm.project = proj.filter(p => p !== tag);
          if (fm.project.length === 1) fm.project = fm.project[0];
          else if (fm.project.length === 0) fm.project = '';
        }
        await apiPost('/api/knowledge/wiki', { path: pagePath, meta: fm });
        showToast('✓ 标签已更新');
        openWikiDetail(pagePath);
      } catch (e) {
        showToast('✗ 更新失败', 'error');
      }
    };
  });

  document.getElementById('kb-tag-add-btn')?.addEventListener('click', async () => {
    const tag = prompt('输入新标签：');
    if (!tag || !tag.trim()) return;
    try {
      const fm = { ...frontmatter };
      fm.tags = [...(Array.isArray(fm.tags) ? fm.tags : []), tag.trim()];
      await apiPost('/api/knowledge/wiki', { path: pagePath, meta: fm });
      showToast('✓ 标签已添加');
      openWikiDetail(pagePath);
    } catch (e) {
      showToast('✗ 添加失败', 'error');
    }
  });
}

// ============================================
// 文件树渲染
// ============================================
const KB_TREE_TYPES = [
  {key: 'concepts', label: '📐 概念', mocFirst: true},
  {key: 'methods', label: '🛠️ 方法'},
  {key: 'people', label: '👤 人物'},
  {key: 'papers', label: '📚 综述'},
  {key: 'projects', label: '📁 项目'},
];

async function renderKbTree() {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  container.innerHTML = '◐ 加载中…';
  try {
    const data = await apiGet('/api/knowledge/wiki');
    const pages = data.pages || [];
    KBManager.wikiPages = pages;

    const mocs = pages.filter(p => p.title && p.title.includes('🗺️'));
    const normal = pages.filter(p => !(p.title && p.title.includes('🗺️')));

    let html = '';
    if (mocs.length) {
      html += `<div class="kb-tree-group"><details open><summary>🗺️ 知识地图</summary>`;
      mocs.forEach(p => {
        const safePath = (p.path || '').replace(/'/g, "\\'");
        html += `<div class="kb-tree-item is-moc" onclick="openWikiDetail('${safePath}')">${escapeHtml(p.title.replace('🗺️ ',''))}</div>`;
      });
      html += `</details></div>`;
    }

    const groups = {};
    normal.forEach(p => { (groups[p.type] = groups[p.type] || []).push(p); });
    const stageOrder = { mature: 0, growing: 1, seedling: 2, archived: 3, unknown: 4 };
    for (const t of KB_TREE_TYPES) {
      const items = (groups[t.key] || []).sort((a, b) => (stageOrder[a.growth_stage] ?? 9) - (stageOrder[b.growth_stage] ?? 9));
      if (!items.length) continue;
      html += `<div class="kb-tree-group"><details><summary>${t.label} (${items.length})</summary>`;
      items.forEach(p => {
        const safePath = (p.path || '').replace(/'/g, "\\'");
        const stageIcon = STAGE_ICONS[p.growth_stage] || '○';
        html += `<div class="kb-tree-item" onclick="openWikiDetail('${safePath}')">${stageIcon} ${escapeHtml(p.title)}</div>`;
      });
      html += `</details></div>`;
    }

    try {
      const rawData = await apiGet('/api/knowledge/raw');
      const rawFiles = (rawData.files || []).filter(f => f.category === 'papers');
      if (rawFiles.length) {
        html += `<div class="kb-tree-group"><details><summary>📄 论文库 (${rawFiles.length})</summary>`;
        rawFiles.slice(0, 30).forEach(f => {
          const safePath = (f.path || '').replace(/'/g, "\\'");
          html += `<div class="kb-tree-item" onclick="openRawDetail('${safePath}')" title="${escapeHtml(f.name)}">${escapeHtml(f.name.replace(/\.md$/, '').slice(0, 28))}</div>`;
        });
        if (rawFiles.length > 30) html += `<div class="kb-tree-item" style="color:var(--text-tertiary);">... 共 ${rawFiles.length} 篇</div>`;
        html += `</details></div>`;
      }
    } catch (e) {}

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<div style="color:var(--error-color);font-size:0.8rem;padding:8px;">加载失败</div>';
  }
}

async function searchKbToTree(query) {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  container.innerHTML = '◐ 搜索中…';
  try {
    const data = await apiGet(`/api/knowledge/search?q=${encodeURIComponent(query)}&top_k=20`);
    const results = data.results || [];
    if (!results.length) {
      container.innerHTML = `<div style="color:var(--text-tertiary);font-size:0.8rem;padding:8px;">🔍 未找到「${escapeHtml(query)}」</div>`;
      return;
    }
    let html = `<div style="font-size:0.78rem;color:var(--text-secondary);padding:4px 8px;">🔍 ${results.length} 条结果</div>`;
    results.forEach(r => {
      const safeDoc = (r.doc || r.path || '').replace(/'/g, "\\'");
      const onclick = r.source === 'wiki' ? `openWikiDetail('${safeDoc}')` : `openRawDetail('${safeDoc}')`;
      html += `<div class="kb-tree-item" onclick="${onclick}" title="${escapeHtml(r.text||'').slice(0,60)}">${r.source === 'wiki' ? '📝' : '📄'} ${escapeHtml(r.title || r.doc)}</div>`;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<div style="color:var(--error-color);font-size:0.8rem;">搜索失败</div>';
  }
}
