/**
 * projects.js — 项目面板前端逻辑（NSFC 仪表盘 + 文献候选 + 多端同步）
 * 零框架依赖，原生 JavaScript，复用 app.js 的 apiGet/showToast。
 */

// ============================================
// 项目面板状态
// ============================================
const ProjectsState = {
  currentTab: 'nsfc',
};

// ============================================
// 面板打开/关闭
// ============================================
function openProjectsManager() {
  const overlay = document.getElementById('projects-overlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  loadProjectsTab(ProjectsState.currentTab);
}

function closeProjectsManager() {
  const overlay = document.getElementById('projects-overlay');
  if (overlay) overlay.style.display = 'none';
}

// ============================================
// Tab 切换
// ============================================
function switchProjectsTab(tab) {
  ProjectsState.currentTab = tab;
  // 更新按钮样式
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    if (btn.dataset.tab === tab) {
      btn.style.background = 'var(--bg-active)';
    } else {
      btn.style.background = 'transparent';
    }
  });
  loadProjectsTab(tab);
}

// ============================================
// 数据加载（按 tab）
// ============================================
async function loadProjectsTab(tab) {
  const body = document.getElementById('projects-body');
  if (!body) return;
  body.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">加载中...</p>';

  try {
    if (tab === 'nsfc') await renderNsfcDashboard(body);
    else if (tab === 'papers') await renderPapersTab(body);
    else if (tab === 'sync') await renderSyncTab(body);
  } catch (e) {
    body.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// NSFC 仪表盘
// ============================================
async function renderNsfcDashboard(container) {
  const [dashboard, decisions] = await Promise.all([
    apiGet('/api/projects/nsfc/dashboard'),
    apiGet('/api/projects/nsfc/decisions?limit=5'),
  ]);

  if (!dashboard.available) {
    container.innerHTML = '<p style="color:var(--text-tertiary);">NSFC 项目数据不可用</p>';
    return;
  }

  let html = '';

  // 当前阶段
  html += `<div style="margin-bottom:16px;">
    <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:4px;">当前阶段</div>
    <div style="font-weight:600;font-size:1rem;">${escapeHtml(String(dashboard.phase || '未知').slice(0, 80))}</div>
  </div>`;

  // 待决策项
  if (dashboard.pending_decisions && dashboard.pending_decisions.length) {
    html += `<div style="margin-bottom:16px;">
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">📌 待决策（${dashboard.pending_decisions.length}）</div>`;
    dashboard.pending_decisions.forEach(d => {
      html += `<div style="padding:6px 10px;margin:4px 0;background:var(--bg-secondary);border-radius:6px;font-size:0.85rem;border-left:3px solid var(--warning-color);">${escapeHtml(String(d).slice(0, 100))}</div>`;
    });
    html += '</div>';
  }

  // 风险
  if (dashboard.risks && dashboard.risks.length) {
    html += `<div style="margin-bottom:16px;">
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">⚠️ 风险（${dashboard.risks.length}）</div>`;
    dashboard.risks.forEach(r => {
      html += `<div style="padding:6px 10px;margin:4px 0;background:var(--bg-secondary);border-radius:6px;font-size:0.85rem;border-left:3px solid var(--error-color);">${escapeHtml(String(r).slice(0, 100))}</div>`;
    });
    html += '</div>';
  }

  // 路线图
  if (dashboard.roadmap && dashboard.roadmap.length) {
    html += `<div style="margin-bottom:16px;">
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">📅 路线图</div>`;
    const statusIcon = { done: '✅', in_progress: '⏳', risk: '⚠️', pending_decision: '📌', blocked: '❌' };
    dashboard.roadmap.forEach(r => {
      const icon = statusIcon[r.status] || '○';
      html += `<div style="padding:3px 0;font-size:0.85rem;">${icon} ${escapeHtml(r.task)}</div>`;
    });
    html += '</div>';
  }

  // 最近决策
  if (decisions.decisions && decisions.decisions.length) {
    html += `<div style="margin-bottom:16px;">
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">🧠 最近决策</div>`;
    decisions.decisions.forEach(d => {
      html += `<div style="padding:8px 10px;margin:4px 0;background:var(--bg-secondary);border-radius:6px;">
        <div style="font-size:0.8rem;color:var(--text-tertiary);">[${d.date}]</div>
        <div style="font-weight:500;font-size:0.88rem;">${escapeHtml(d.title)}</div>`;
      if (d.overridable_window) {
        html += `<div style="font-size:0.78rem;color:var(--warning-color);margin-top:2px;">⏰ ${escapeHtml(d.overridable_window)}</div>`;
      }
      html += '</div>';
    });
    html += '</div>';
  }

  html += `<div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:8px;">最后更新: ${escapeHtml(dashboard.last_updated || '?')}</div>`;
  container.innerHTML = html;
}

// ============================================
// 文献候选
// ============================================
async function renderPapersTab(container) {
  const [candidates, briefings] = await Promise.all([
    apiGet('/api/projects/papers/candidates'),
    apiGet('/api/projects/papers/briefings'),
  ]);

  let html = '';

  // 候选列表
  if (candidates.available) {
    html += `<div style="margin-bottom:20px;">
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">📄 今日候选（${candidates.total} 篇，${escapeHtml(candidates.date || '?')}）</div>`;
    if (candidates.papers && candidates.papers.length) {
      html += '<div style="display:flex;flex-direction:column;gap:6px;">';
      candidates.papers.forEach(p => {
        const scorePct = Math.round((p.score || 0) * 100);
        const analysisTag = p.has_analysis ? '<span style="color:var(--success-color);font-size:0.75rem;">✓已解析</span>' : '';
        html += `<div style="padding:8px 10px;background:var(--bg-secondary);border-radius:6px;">
          <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">
            <div style="flex:1;">
              <div style="font-size:0.85rem;font-weight:500;">${escapeHtml(p.title)}</div>
              <div style="font-size:0.75rem;color:var(--text-tertiary);margin-top:2px;">${escapeHtml(p.authors)} | ${escapeHtml(p.direction)} | 评分 ${scorePct}% ${analysisTag}</div>
            </div>
            <div style="display:flex;gap:4px;flex-shrink:0;">
              <button onclick="importPaper('${p.arxiv_id}', false)" style="padding:3px 8px;font-size:0.75rem;cursor:pointer;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-primary);">导入</button>
              ${p.has_analysis ? `<button onclick="importPaper('${p.arxiv_id}', true)" style="padding:3px 8px;font-size:0.75rem;cursor:pointer;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-primary);">+解析</button>` : ''}
            </div>
          </div>
          ${p.tldr ? `<div style="font-size:0.78rem;color:var(--text-secondary);margin-top:4px;">${escapeHtml(p.tldr)}</div>` : ''}
        </div>`;
      });
      html += '</div>';
    }
    html += '</div>';
  }

  // 已有简报
  if (briefings.briefings && briefings.briefings.length) {
    html += `<div>
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">📚 历史简报（${briefings.briefings.length}）</div>`;
    briefings.briefings.slice(0, 10).forEach(b => {
      html += `<div style="padding:6px 10px;margin:3px 0;background:var(--bg-secondary);border-radius:6px;font-size:0.82rem;">
        <span style="color:var(--text-tertiary);">[${b.date}]</span> ${escapeHtml(b.title)}
      </div>`;
    });
    html += '</div>';
  }

  container.innerHTML = html || '<p style="color:var(--text-tertiary);">暂无文献数据</p>';
}

// ============================================
// 多端同步
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

  // 绑定同步按钮
  const syncBtn = document.getElementById('sync-run-btn');
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      syncBtn.disabled = true;
      syncBtn.textContent = '同步中...';
      try {
        const result = await apiPost('/api/sync/run', {});
        showToast(`✓ 同步完成：会话 +${result.result.new_sessions}，文献 +${result.result.new_papers}`, 'success');
        renderSyncTab(container);
      } catch (e) {
        showToast(`✗ 同步失败: ${e.message}`, 'error');
      } finally {
        syncBtn.disabled = false;
        syncBtn.textContent = '🔄 立即同步';
      }
    });
  }
}

// ============================================
// 导入文献
// ============================================
async function importPaper(arxivId, withAnalysis) {
  showToast(`◐ 导入 ${arxivId}...`, 'info');
  try {
    const result = await apiPost('/api/import/paper', { arxiv_id: arxivId, with_analysis: withAnalysis });
    showToast(`✓ 导入成功：${result.results.candidate || '已存在'}`, 'success');
  } catch (e) {
    showToast(`✗ 导入失败: ${e.message}`, 'error');
  }
}

// ============================================
// 初始化绑定（由 app.js 调用）
// ============================================
function bindProjectsEvents() {
  // 工具栏按钮
  document.getElementById('toolbar-projects')?.addEventListener('click', openProjectsManager);
  // 关闭
  document.getElementById('projects-close')?.addEventListener('click', closeProjectsManager);
  document.getElementById('projects-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeProjectsManager();
  });
  // Tab 切换
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchProjectsTab(btn.dataset.tab));
  });
  // 刷新
  document.getElementById('proj-refresh')?.addEventListener('click', () => loadProjectsTab(ProjectsState.currentTab));
}

// HTML 转义（若 app.js 未提供则本地实现）
if (typeof escapeHtml === 'undefined') {
  window.escapeHtml = function(s) {
    const div = document.createElement('div');
    div.textContent = String(s);
    return div.innerHTML;
  };
}
