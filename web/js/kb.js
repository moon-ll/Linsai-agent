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
  kbSource: 'all',  // 知识库来源：all|raw|wiki
};

// ============================================
// KB 搜索状态（统一搜索+筛选+分页）
// ============================================
const KbSearchState = {
  query: '',
  offset: 0,
  limit: 10,
  filters: { type: '', stage: '', project: '', tag: '' },
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

    // 复用 core.js 的 renderMarkdown（内部已 escapeHtml + 标题/列表/加粗/斜体/代码/引用/链接）
    let renderedBody = renderMarkdown(body);
    // wikilink 双链 [[xxx]]：renderMarkdown 不支持，单独追加
    // 注意：name 已被 renderMarkdown 转义（[ ] 不受 escapeHtml 影响，但名称内的 < & " 已转义），
    // 此处直接使用即可，切勿再次 escapeHtml 以免二次转义破坏 data 属性读取
    renderedBody = renderedBody.replace(/\[\[([^\]]+)\]\]/g, (m, name) => {
      return `<a class="kb-wikilink" data-wiki-title="${name}" title="点击跳转">${name}</a>`;
    });

    const relatedHtml = (fm.related || []).map(r => {
      // P1-8: 使用 data 属性替代 onclick 拼接
      return `<span class="kb-related-chip" data-wiki-title="${escapeHtml(String(r))}" title="点击跳转">${escapeHtml(r)}</span>`;
    }).join(' ') || '-';

    bodyEl.innerHTML = `
      <div class="kb-detail-actions">
        <button class="btn-text" data-open-path="${escapeHtml(wikiPath)}">📂 在编辑器中打开</button>
        <button class="btn-text" data-copy-path="${escapeHtml(wikiPath)}">📋 复制路径</button>
      </div>
      <div class="kb-frontmatter">
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">类型</span><span class="kb-frontmatter-value">${escapeHtml(fm.type || '-')}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">生长阶段</span><span class="kb-frontmatter-value">${stage}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">确信度</span><span class="kb-frontmatter-value">${((fm.confidence ?? 0) * 100).toFixed(0)}%</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">标签</span><span class="kb-frontmatter-value">${escapeHtml((fm.tags || []).join(', ') || '-')}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">关联</span><span class="kb-frontmatter-value">${relatedHtml}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">更新</span><span class="kb-frontmatter-value">${fm.updated ? new Date(fm.updated).toLocaleString() : '-'}</span></div>
        <div class="kb-frontmatter-item"><span class="kb-frontmatter-key">路径</span><span class="kb-frontmatter-value">${escapeHtml(wikiPath)}</span></div>
      </div>
      ${renderTagEditor(fm, wikiPath)}
      <div id="kb-backlinks-region"></div>
      <div class="kb-wiki-body">${renderedBody}</div>
    `;

    bindTagEditor(fm, wikiPath);
    loadBacklinks(fm.title || '');
  } catch (e) {
    bodyEl.innerHTML = `<div class="kb-empty">✗ 加载失败: ${escapeHtml(e.message)}</div>`;
  }
}

function openWikiByTitle(title) {
  const pages = KBManager.wikiPages || [];
  if (!pages.length) {
    apiGet('/api/knowledge/wiki').then(data => {
      KBManager.wikiPages = data.pages || [];
      openWikiByTitle(title);
    }).catch(e => { console.warn('加载 wiki 列表失败:', e.message); });
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
      region.innerHTML = `<div class="m-8-0 pad-6-10 bg-tertiary br-6">
        <span class="fs-078 text-secondary">↩️ 被以下笔记关联：</span>
        ${related.map(r => {
          // P1-8: 使用 data 属性替代 onclick 拼接
          return `<span class="kb-related-chip" data-wiki-title="${escapeHtml(String(r))}" title="点击跳转">${escapeHtml(r)}</span>`;
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
  bodyEl.innerHTML = '<span class="text-tertiary">◐ 加载中…</span>';

  try {
    const data = await apiGet(`/api/knowledge/file-content?path=${encodeURIComponent(rawPath)}`);
    if (data.content) {
      // P1-14: renderMarkdown 内部已先 escapeHtml 再做 Markdown 替换，防止 raw HTML/SVG XSS
      let rendered = renderMarkdown(data.content);
      // P1-2: 使用 data 属性 + 事件委托替代 onclick 拼接，防止属性闭合注入
      bodyEl.innerHTML = `<div class="mb-8"><button class="btn-text" data-open-path="${escapeHtml(rawPath)}" class="pad-4-10 border-default br-4 cursor-pointer fs-08">📂 在编辑器中打开</button></div>${rendered.slice(0, 6000)}${data.size > 6000 ? '\n\n<p class="text-tertiary">... (截断)</p>' : ''}`;
    } else {
      bodyEl.innerHTML = '<span class="state-error">无法读取（' + escapeHtml(data.error || '未知错误') + '）</span>';
    }
  } catch (e) {
    bodyEl.innerHTML = '<span class="state-error">加载失败: ' + escapeHtml(e.message) + '</span>';
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
  showModal('<div class="mw-480"><h3 class="mb-8">🗂️ 选择知识库文件注入讨论</h3><p class="text-secondary fs-082 mb-12">勾选要讨论的知识库内容，发送消息时会自动注入林赛上下文。</p><div id="kb-file-list" class="maxh-350 overflow-y-auto"><p class="text-tertiary">◐ 加载中…</p></div><div class="d-flex gap-8 mt-12"><button id="kb-pick-confirm" class="flex-1 pad-8 bg-accent text-white border-none br-6 cursor-pointer">确认选择</button><button id="kb-pick-cancel" class="pad-8-16 border-default br-6 cursor-pointer">取消</button></div></div>');
  try {
    const files = await apiGet('/api/knowledge/files');
    const list = document.getElementById('kb-file-list');
    if (!list) return;
    if (!files.length) { list.innerHTML = '<p class="text-tertiary">知识库为空</p>'; return; }
    const groups = {};
    files.forEach(f => { (groups[f.type] = groups[f.type] || []).push(f); });
    let html = '';
    for (const [type, items] of Object.entries(groups)) {
      html += `<div style="font-size:0.8rem;font-weight:600;color:var(--text-secondary);margin:8px 0 4px;">${type} (${items.length})</div>`;
      items.forEach(f => {
        const checked = window._kbSelectedFiles.some(s => s.path === f.path) ? 'checked' : '';
        html += `<label style="display:flex;align-items:center;gap:6px;padding:3px 0;font-size:0.82rem;cursor:pointer;"><input type="checkbox" class="kb-file-cb" data-path="${escapeHtml(f.path)}" data-title="${escapeHtml(f.title)}" ${checked}><span>${escapeHtml(f.title)}</span><span class="text-tertiary fs-072">${f.project ? '['+escapeHtml(f.project)+']' : ''}</span></label>`;
      });
    }
    list.innerHTML = html;
  } catch (e) { document.getElementById('kb-file-list').innerHTML = `<p class="state-error">加载失败: ${escapeHtml(e.message)}</p>`; }
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

  // P2-3: 渲染 chip 列表显示已注入文件
  const chipsContainer = document.getElementById('kb-context-chips');
  if (chipsContainer) {
    if (window._kbSelectedFiles.length) {
      chipsContainer.style.display = 'flex';
      chipsContainer.innerHTML = window._kbSelectedFiles.map((f, i) => {
        return `<span class="kb-context-chip">📎 ${escapeHtml(f.title)}<span class="chip-remove" data-idx="${i}">✕</span></span>`;
      }).join('');
      // 绑定移除事件
      chipsContainer.querySelectorAll('.chip-remove').forEach(btn => {
        btn.onclick = () => {
          const idx = parseInt(btn.dataset.idx);
          window._kbSelectedFiles.splice(idx, 1);
          updateKbContextBadge();
        };
      });
    } else {
      chipsContainer.style.display = 'none';
      chipsContainer.innerHTML = '';
    }
  }
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

  // 事件委托：确保 <details>/<summary> 点击切换始终生效 + P1-8: data 属性事件委托
  document.getElementById('kb-tree-content')?.addEventListener('click', (e) => {
    // 分页按钮点击 → 跳转到对应页
    const pageBtn = e.target.closest('.kb-page-btn[data-page]');
    if (pageBtn && !pageBtn.disabled) {
      e.preventDefault();
      const page = parseInt(pageBtn.dataset.page, 10);
      const newOffset = (page - 1) * KbSearchState.limit;
      searchKbToTree(KbSearchState.query, newOffset);
      return;
    }
    // P2-1: 交叉链接 → 打开项目面板
    const projectsLink = e.target.closest('[data-action="open-projects"]');
    if (projectsLink) {
      e.preventDefault();
      if (typeof openProjectsManager === 'function') openProjectsManager();
      return;
    }
    // P1-8: 处理 data-wiki-path / data-raw-path 点击（替代 onclick 拼接）
    const wikiItem = e.target.closest('[data-wiki-path]');
    if (wikiItem) {
      e.preventDefault();
      openWikiDetail(wikiItem.dataset.wikiPath);
      return;
    }
    const rawItem = e.target.closest('[data-raw-path]');
    if (rawItem) {
      e.preventDefault();
      openRawDetail(rawItem.dataset.rawPath);
      return;
    }
    // P3-3: details/summary 使用原生切换，不再 JS 接管
    // （CSS 已隐藏原生 marker 并用 ::before 替代，原生 toggle 自动更新 [open] 属性）
  });

  // P3-5: 键盘可达 — Enter/Space 触发点击
  document.getElementById('kb-tree-content')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      const item = e.target.closest('[data-wiki-path], [data-raw-path], [data-action], .kb-page-btn[data-page]');
      if (item) {
        e.preventDefault();
        item.click();
      }
    }
  });

  let treeSearchTimer;
  document.getElementById('kb-tree-search')?.addEventListener('input', (e) => {
    clearTimeout(treeSearchTimer);
    const q = e.target.value.trim();
    if (!q) {
      // 搜索框清空 → 若有筛选走筛选列表，否则恢复文件树
      applyKbFilters();
      return;
    }
    treeSearchTimer = setTimeout(() => searchKbToTree(q, 0), 300);
  });

  // P1-8: 预览面板事件委托（wikilinks + related chips + backlinks + P1-2: 打开/复制按钮）
  document.getElementById('kb-preview-body')?.addEventListener('click', (e) => {
    // P1-2: 事件委托处理"打开本地文件"和"复制路径"按钮（替代 onclick 拼接）
    const openBtn = e.target.closest('[data-open-path]');
    if (openBtn) {
      e.preventDefault();
      openLocalFile(openBtn.dataset.openPath);
      return;
    }
    const copyBtn = e.target.closest('[data-copy-path]');
    if (copyBtn) {
      e.preventDefault();
      copyToClipboard(copyBtn.dataset.copyPath);
      return;
    }
    const link = e.target.closest('[data-wiki-title]');
    if (link) {
      e.preventDefault();
      openWikiByTitle(link.dataset.wikiTitle);
    }
  });
  document.getElementById('kb-backlinks-region')?.addEventListener('click', (e) => {
    const link = e.target.closest('[data-wiki-title]');
    if (link) {
      e.preventDefault();
      openWikiByTitle(link.dataset.wikiTitle);
    }
  });

  document.getElementById('kb-sync-btn')?.addEventListener('click', handleKbSync);
  document.getElementById('kb-health-btn')?.addEventListener('click', handleKbHealth);
  document.getElementById('kb-category-btn')?.addEventListener('click', handleKbCategory);
  document.getElementById('kb-filter-clear')?.addEventListener('click', clearKbFilters);
  ['kb-filter-type', 'kb-filter-stage', 'kb-filter-project', 'kb-filter-tag'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', applyKbFilters);
  });
  document.getElementById('kb-partition-select')?.addEventListener('change', applyKbPartition);
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
    // P2-6: 用 showModal 替代 alert
    showModal(`<div style="white-space:pre-wrap;font-size:0.85rem;line-height:1.8;">${msg}</div>`);
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
  // 读取当前筛选值
  const type = document.getElementById('kb-filter-type')?.value;
  const stage = document.getElementById('kb-filter-stage')?.value;
  const project = document.getElementById('kb-filter-project')?.value;
  const tag = document.getElementById('kb-filter-tag')?.value;
  const hasFilter = !!(type || stage || project || tag);

  const filterBar = document.getElementById('kb-filter-bar');
  if (filterBar) filterBar.style.display = hasFilter ? 'flex' : 'none';

  // 搜索框有内容 → 带筛选统一搜索（重置到第一页）
  const searchBox = document.getElementById('kb-tree-search');
  const query = searchBox?.value?.trim() || '';
  if (query) {
    searchKbToTree(query, 0);
    return;
  }

  // 无搜索词 → 走原有 filter 列表
  if (!hasFilter) {
    renderKbTree();
    return;
  }

  const filters = {};
  if (type) filters.type = type;
  if (stage) filters.stage = stage;
  if (project) filters.project = project;
  if (tag) filters.tag = tag;

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
  const partitionSel = document.getElementById('kb-partition-select');
  if (partitionSel) partitionSel.value = 'all';
  const filterBar = document.getElementById('kb-filter-bar');
  if (filterBar) filterBar.style.display = 'none';
  // 重置搜索状态
  KbSearchState.query = '';
  KbSearchState.offset = 0;
  renderKbTree();
}

// 分区快捷选择器：设置对应筛选参数并触发搜索/刷新
function applyKbPartition() {
  const sel = document.getElementById('kb-partition-select');
  if (!sel) return;
  const value = sel.value;

  // 先清除所有筛选下拉框
  ['kb-filter-type', 'kb-filter-stage', 'kb-filter-project', 'kb-filter-tag'].forEach(id => {
    const s = document.getElementById(id);
    if (s) s.value = '';
  });

  if (value && value !== 'all') {
    // value 格式: key:val（如 project:NSFC-强场超快 / type:concepts）
    const idx = value.indexOf(':');
    if (idx > 0) {
      const key = value.slice(0, idx);
      const val = value.slice(idx + 1);
      const targetId = key === 'project' ? 'kb-filter-project' : 'kb-filter-type';
      const targetSel = document.getElementById(targetId);
      if (targetSel) {
        // 若下拉框中无此选项，动态添加（分区值可能不在 filters 接口返回的列表中）
        if (!Array.from(targetSel.options).some(o => o.value === val)) {
          const o = document.createElement('option');
          o.value = val;
          o.textContent = val;
          targetSel.appendChild(o);
        }
        targetSel.value = val;
      }
    }
  }

  // 显示/隐藏筛选条
  const filterBar = document.getElementById('kb-filter-bar');
  if (filterBar) filterBar.style.display = (value && value !== 'all') ? 'flex' : 'none';

  // 触发搜索/刷新（搜索框有内容则带筛选搜索，否则走筛选列表/文件树）
  applyKbFilters();
}

function renderFilteredTree(pages) {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  if (!pages.length) {
    container.innerHTML = '<div class="pad-20 ta-center text-tertiary">无匹配结果</div>';
    return;
  }
  const html = pages.map(p => {
    const stageIcon = STAGE_ICONS[p.growth_stage] || '○';
    // P1-8: 使用 data 属性替代 onclick 字符串拼接
    return `<div class="kb-tree-item pad-4-8 cursor-pointer br-4 fs-082" data-wiki-path="${escapeHtml(p.path)}" tabindex="0" role="button" aria-label="${escapeHtml(p.title)}">${stageIcon} ${escapeHtml(p.title)} <span class="text-tertiary fs-07">${escapeHtml(p.type || '')}</span></div>`;
  }).join('');
  container.innerHTML = `<div class="pad-4-8 fs-075 text-tertiary">筛选结果 (${pages.length})</div>` + html;
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
      <button class="kb-toolbar-btn" id="cat-create-btn" class="w-100 mt-4">➕ 创建分类</button>
    </div>
    <button class="kb-toolbar-btn" id="cat-rescan-btn" class="w-100 mt-6">🔄 重新扫描全部</button>
    <button class="kb-toolbar-btn" id="cat-close-btn" class="w-100 mt-4">关闭</button>
  `;
  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  const refreshList = async () => {
    const listEl = document.getElementById('cat-list');
    try {
      const data = await apiGet('/api/knowledge/categories');
      const cats = data.categories || [];
      if (!cats.length) {
        listEl.innerHTML = '<div class="text-tertiary fs-082">暂无自定义分类</div>';
        return;
      }
      listEl.innerHTML = cats.map(c => `
        <div class="kb-category-item">
          <span class="cat-name">📂 ${escapeHtml(c.name)}</span>
          <span class="cat-count">${(c.matched_paths || []).length} 篇</span>
          <span class="cat-delete" data-name="${escapeAttr(c.name)}">✕</span>
        </div>
      `).join('');
      listEl.querySelectorAll('.cat-delete').forEach(btn => {
        btn.onclick = async () => {
          const name = btn.dataset.name;
          if (!await confirmModal(`删除分类 "${name}"？`)) return;
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
    <span class="kb-tag-chip">${escapeHtml(t)}<span class="tag-remove" data-tag="${escapeAttr(t)}" data-type="tag">✕</span></span>
  `).join('');
  const projChips = projectList.map(p => `
    <span class="kb-tag-chip" style="background:var(--accent);color:white;border-color:var(--accent);">${escapeHtml(p)}<span class="tag-remove" data-tag="${escapeAttr(p)}" data-type="project">✕</span></span>
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
      if (!await confirmModal(`移除 ${type === 'project' ? '子库' : '标签'} "${tag}"？`)) return;
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
        // P1-15: 刷新文件树计数和搜索索引
        if (typeof renderKbTree === 'function') renderKbTree();
      } catch (e) {
        showToast('✗ 更新失败', 'error');
      }
    };
  });

  document.getElementById('kb-tag-add-btn')?.addEventListener('click', async () => {
    const tag = await promptModal('输入新标签：', '例如: #topic/HHG');
    if (!tag || !tag.trim()) return;
    try {
      const fm = { ...frontmatter };
      fm.tags = [...(Array.isArray(fm.tags) ? fm.tags : []), tag.trim()];
      await apiPost('/api/knowledge/wiki', { path: pagePath, meta: fm });
      showToast('✓ 标签已添加');
      openWikiDetail(pagePath);
      // P1-15: 刷新文件树计数和搜索索引
      if (typeof renderKbTree === 'function') renderKbTree();
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
        // P1-8: 使用 data 属性替代 onclick 字符串拼接
        // P3-5: 加 tabindex 和 role 使键盘可聚焦
        html += `<div class="kb-tree-item is-moc" data-wiki-path="${escapeHtml(p.path)}" tabindex="0" role="button" aria-label="${escapeHtml(p.title.replace('🗺️ ',''))}">${escapeHtml(p.title.replace('🗺️ ',''))}</div>`;
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
        const stageIcon = STAGE_ICONS[p.growth_stage] || '○';
        html += `<div class="kb-tree-item" data-wiki-path="${escapeHtml(p.path)}" tabindex="0" role="button" aria-label="${escapeHtml(p.title)}">${stageIcon} ${escapeHtml(p.title)}</div>`;
      });
      html += `</details></div>`;
    }

    try {
      const rawData = await apiGet('/api/knowledge/raw');
      const rawFiles = (rawData.files || []).filter(f => f.category === 'papers');
      if (rawFiles.length) {
        html += `<div class="kb-tree-group"><details><summary>📄 论文库 (${rawFiles.length})</summary>`;
        rawFiles.slice(0, 30).forEach(f => {
          html += `<div class="kb-tree-item" data-raw-path="${escapeHtml(f.path)}" tabindex="0" role="button" aria-label="${escapeHtml(f.name)}" title="${escapeHtml(f.name)}">${escapeHtml(f.name.replace(/\.md$/, '').slice(0, 28))}</div>`;
        });
        if (rawFiles.length > 30) html += `<div class="kb-tree-item text-tertiary" aria-hidden="true">... 共 ${rawFiles.length} 篇</div>`;
        // P2-1: 交叉链接提示
        html += `<div class="kb-tree-item" data-action="open-projects" tabindex="0" role="button" aria-label="打开项目面板查看待决策文献" style="color:var(--accent-color);font-size:0.72rem;border-top:1px dashed var(--border-color);margin-top:4px;padding-top:4px;">📂 待决策文献 → 项目面板</div>`;
        html += `</details></div>`;
      }
    } catch (e) {}

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<div class="text-error fs-08 pad-8">加载失败</div>';
  }
}

async function searchKbToTree(query, offset = 0) {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  container.innerHTML = '◐ 搜索中…';

  // 读取当前筛选值（与 4 个下拉框联动）
  const typeFilter = document.getElementById('kb-filter-type')?.value || '';
  const stageFilter = document.getElementById('kb-filter-stage')?.value || '';
  const projectFilter = document.getElementById('kb-filter-project')?.value || '';
  const tagFilter = document.getElementById('kb-filter-tag')?.value || '';

  // 保存搜索状态（供分页复用）
  KbSearchState.query = query;
  KbSearchState.offset = offset;
  KbSearchState.filters = { type: typeFilter, stage: stageFilter, project: projectFilter, tag: tagFilter };

  const params = new URLSearchParams({
    q: query,
    top_k: String(KbSearchState.limit),
    source: KBManager.kbSource || 'all',
  });
  if (offset) params.set('offset', String(offset));
  if (typeFilter) params.set('type', typeFilter);
  if (stageFilter) params.set('stage', stageFilter);
  if (projectFilter) params.set('project', projectFilter);
  if (tagFilter) params.set('tag', tagFilter);

  try {
    // data 格式: {results: [...], total: N, offset: 0, limit: 10}
    const data = await apiGet(`/api/knowledge/search?${params}`);
    renderKbSearchResults(data);
  } catch (e) {
    container.innerHTML = '<div class="text-error fs-08">搜索失败</div>';
  }
}

// 渲染搜索结果（含分页控件）
function renderKbSearchResults(data) {
  const container = document.getElementById('kb-tree-content');
  if (!container) return;
  const results = data.results || [];
  const total = data.total || 0;
  const limit = data.limit || KbSearchState.limit;
  const offset = data.offset || 0;

  if (!results.length) {
    const activeFilters = Object.entries(KbSearchState.filters).filter(([, v]) => v);
    const filterDesc = activeFilters.length ? `（筛选: ${activeFilters.map(([, v]) => v).join('/')}）` : '';
    container.innerHTML = `<div class="text-tertiary fs-08 pad-8">🔍 未找到「${escapeHtml(KbSearchState.query)}」${filterDesc}</div>`;
    return;
  }

  // 筛选描述
  const activeFilters = Object.entries(KbSearchState.filters).filter(([, v]) => v);
  const filterDesc = activeFilters.length ? ` · 筛选 ${activeFilters.map(([, v]) => v).join('/')}` : '';

  let html = `<div class="fs-078 text-secondary pad-4-8">🔍 共 ${total} 条结果${filterDesc}</div>`;
  results.forEach(r => {
    const docPath = r.doc || r.path || '';
    // P1-8: 使用 data 属性替代 onclick 字符串拼接
    const attr = r.source === 'wiki' ? `data-wiki-path="${escapeHtml(docPath)}"` : `data-raw-path="${escapeHtml(docPath)}"`;
    const stageIcon = STAGE_ICONS[r.growth_stage] || (r.source === 'wiki' ? '📝' : '📄');
    html += `<div class="kb-tree-item" ${attr} tabindex="0" role="button" aria-label="${escapeHtml(r.title || r.doc)}" title="${escapeHtml((r.text||'').slice(0,60))}">${stageIcon} ${escapeHtml(r.title || r.doc)}</div>`;
  });

  // 分页控件
  if (total > limit) {
    html += renderKbPagination(total, offset, limit);
  }

  container.innerHTML = html;
}

// 渲染分页控件（上一页/页码/下一页）
function renderKbPagination(total, offset, limit) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  const buttons = [];
  // 上一页
  const prevDisabled = currentPage <= 1;
  buttons.push(`<button class="kb-page-btn${prevDisabled ? ' disabled' : ''}" data-page="${currentPage - 1}" ${prevDisabled ? 'disabled' : ''} tabindex="0" aria-label="上一页">‹</button>`);

  // 页码窗口（最多 5 个，当前页居中）
  let startPage = Math.max(1, currentPage - 2);
  let endPage = Math.min(totalPages, startPage + 4);
  if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

  if (startPage > 1) {
    buttons.push(`<button class="kb-page-btn" data-page="1" tabindex="0" aria-label="第1页">1</button>`);
    if (startPage > 2) buttons.push(`<span class="kb-page-ellipsis" aria-hidden="true">…</span>`);
  }
  for (let p = startPage; p <= endPage; p++) {
    const isCurrent = p === currentPage;
    buttons.push(`<button class="kb-page-btn${isCurrent ? ' active' : ''}" data-page="${p}" tabindex="0" aria-label="第${p}页"${isCurrent ? ' aria-current="page"' : ''}>${p}</button>`);
  }
  if (endPage < totalPages) {
    if (endPage < totalPages - 1) buttons.push(`<span class="kb-page-ellipsis" aria-hidden="true">…</span>`);
    buttons.push(`<button class="kb-page-btn" data-page="${totalPages}" tabindex="0" aria-label="第${totalPages}页">${totalPages}</button>`);
  }

  // 下一页
  const nextDisabled = currentPage >= totalPages;
  buttons.push(`<button class="kb-page-btn${nextDisabled ? ' disabled' : ''}" data-page="${currentPage + 1}" ${nextDisabled ? 'disabled' : ''} tabindex="0" aria-label="下一页">›</button>`);

  return `<div class="kb-pagination" role="navigation" aria-label="搜索结果分页">${buttons.join('')}<span class="kb-page-info">${currentPage}/${totalPages}</span></div>`;
}

// v3.5.1: 注册模块初始化
// kb.js 的 initKbMain() 已在 app.js init() 中手动调用，此处不重复注册以避免双重初始化
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('kb', () => {
    // 知识库模块初始化由 app.js initKbMain() 统一处理，此处保留接口供未来迁移
  });
}
