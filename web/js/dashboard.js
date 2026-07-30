/**
 * dashboard.js — v6.7.8 仪表盘首页重设计
 * 目标：结构清晰、美观、行动导向
 * - 顶部统计卡片
 * - 中段六阶段漏斗
 * - 底部"需要你"行动区 + 快捷入口
 */

const DASH_STAGE_ORDER = ['incoming', 'drafts', 'optimizing', 'pending_review', 'archived', 'output'];
const DASH_STAGE_LABELS = {
  incoming: '输入端', drafts: '初稿', optimizing: '优化中',
  pending_review: '待校验', archived: '归档', output: '输出端'
};
const DASH_STAGE_ICONS = {
  incoming: '📥', drafts: '📝', optimizing: '🔄',
  pending_review: '🔍', archived: '📦', output: '📤'
};
const DASH_STAGE_COLORS = {
  incoming: 'var(--info-color)', drafts: 'var(--text-tertiary)',
  optimizing: 'var(--accent-color)', pending_review: 'var(--warning-color)',
  archived: 'var(--success-color)', output: 'var(--info-color)'
};

// 渲染仪表盘
async function renderDashboard() {
  const container = document.getElementById('dashboard-page');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary);">◐ 加载中…</div>';

  try {
    const [data, flowData, alertsData] = await Promise.all([
      apiGet('/api/dashboard'),
      apiGet('/api/console/flow').catch(() => ({ status: 'ok', stages: {} })),
      apiGet('/api/console/alerts').catch(() => ({ alerts: [] })),
    ]);

    const stages = flowData.status === 'ok' ? (flowData.stages || {}) : {};
    const alerts = alertsData.alerts || [];

    // 林赛主动开场
    const hour = new Date().getHours();
    const greeting = hour < 6 ? '夜深了' : hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';
    const totalPending = (data.papers.unseen || 0) + (data.tasks.active || 0) + (data.tasks.backlog || 0) + (data.decisions_total || 0) + alerts.length;

    let html = '';

    // === 顶部问候 ===
    html += `<div class="dash-greeting">
      <div class="dash-greeting-text">${greeting}，林赛在线。</div>
      <div class="dash-greeting-sub">${totalPending > 0 ? `今日有 <strong>${totalPending}</strong> 件事需要你关注` : '目前暂无待处理事项，链路运转正常。'}</div>
    </div>`;

    // === 统计卡片 ===
    html += '<div class="dash-stats-row">';
    html += renderStatCard('📄', '文献待处理', data.papers.unseen || 0, '查看简报', "switchToView('kb')", 'var(--info-color)');
    html += renderStatCard('📋', '任务待办', (data.tasks.active || 0) + (data.tasks.backlog || 0), '查看任务', "switchToView('hermes')", 'var(--warning-color)');
    html += renderStatCard('📌', '待决策', data.decisions_total || 0, '去决策', "dashOpenDecisions()", 'var(--accent-color)');
    html += renderStatCard('🎛️', '告警/异常', alerts.length, '控制台', "switchToView('console')", alerts.length ? 'var(--error-color)' : 'var(--success-color)');
    html += '</div>';

    // === 中段：漏斗 + 行动区 ===
    html += '<div class="dash-main-grid">';

    // 漏斗
    html += '<div class="dash-funnel-panel">';
    html += '<div class="dash-panel-title">🌊 全链路漏斗</div>';
    html += '<div class="dash-funnel">';
    for (const stage of DASH_STAGE_ORDER) {
      const s = stages[stage] || { count: 0, items: [] };
      html += renderFunnelStage(stage, s.count || 0, s.items || []);
    }
    html += '</div>';
    html += '</div>';

    // 行动区
    html += '<div class="dash-action-panel">';
    html += '<div class="dash-panel-title">⚡ 需要你</div>';
    html += renderActionList(data, stages, alerts);
    html += '</div>';

    html += '</div>';

    // === 底部：文献/任务/决策快捷预览 ===
    html += '<div class="dash-preview-grid">';
    html += renderPapersPreview(data.papers);
    html += renderTasksPreview(data.tasks);
    html += renderDecisionsPreview(data.decisions || [], data.decisions_total || 0);
    html += '</div>';

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div style="color:var(--error-color);padding:20px;">加载失败: ${escapeHtml(e.message)}</div>`;
  }
}

function renderStatCard(icon, label, count, actionLabel, action, color) {
  return `
    <div class="dash-stat-card" onclick="${action}">
      <div class="dash-stat-icon" style="color:${color};">${icon}</div>
      <div class="dash-stat-number" style="color:${color};">${count}</div>
      <div class="dash-stat-label">${escapeHtml(label)}</div>
      <div class="dash-stat-action">${escapeHtml(actionLabel)} →</div>
    </div>`;
}

function renderFunnelStage(stage, count, items) {
  const label = DASH_STAGE_LABELS[stage];
  const icon = DASH_STAGE_ICONS[stage];
  const color = DASH_STAGE_COLORS[stage];
  const width = Math.max(20, Math.min(100, 30 + count * 8));
  const preview = items.slice(0, 2).map(i => escapeHtml((i.title || i.proposal_id || '').slice(0, 24))).join('、') || '—';
  return `
    <div class="dash-funnel-stage" onclick="dashOpenStage('${stage}')" style="--stage-color:${color};--stage-width:${width}%;">
      <div class="dash-funnel-bar">
        <span class="dash-funnel-icon">${icon}</span>
        <span class="dash-funnel-name">${label}</span>
        <span class="dash-funnel-count" style="color:${color};">${count}</span>
      </div>
      <div class="dash-funnel-preview" title="${escapeAttr(preview)}">${preview}</div>
    </div>`;
}

function renderActionList(data, stages, alerts) {
  let html = '<div class="dash-action-list">';
  const pendingReview = stages.pending_review?.items || [];
  const drafts = stages.drafts?.items || [];

  // 1. 待校验课题
  if (pendingReview.length) {
    const p = pendingReview[0];
    html += renderActionItem('🔍', '待校验课题', (p.title || p.proposal_id || ''), `dashOpenProposal('${escapeAttr(p.proposal_id || '')}')`, 'var(--warning-color)');
  }
  // 2. 新初稿待确认
  if (drafts.length) {
    const p = drafts[0];
    html += renderActionItem('📝', '新初稿待确认', (p.title || p.proposal_id || ''), `dashOpenProposal('${escapeAttr(p.proposal_id || '')}')`, 'var(--text-tertiary)');
  }
  // 3. 待决策
  if (data.decisions_total) {
    html += renderActionItem('📌', 'NSFC 待决策', `${data.decisions_total} 项待拍板`, "dashOpenDecisions()", 'var(--accent-color)');
  }
  // 4. 告警
  if (alerts.length) {
    const a = alerts[0];
    html += renderActionItem('🎛️', '链路告警', (a.title || a.message || `${alerts.length} 项异常`), "switchToView('console')", 'var(--error-color)');
  }
  // 5. 文献
  if (data.papers.unseen) {
    html += renderActionItem('📄', '文献简报', `${data.papers.unseen} 篇待处理`, "switchToView('kb')", 'var(--info-color)');
  }
  // 6. 任务
  if (data.tasks.backlog) {
    html += renderActionItem('📋', '待办任务', `${data.tasks.backlog} 项待办`, "switchToView('hermes')", 'var(--warning-color)');
  }

  if (pendingReview.length === 0 && drafts.length === 0 && !data.decisions_total && !alerts.length && !data.papers.unseen && !data.tasks.backlog) {
    html += '<div class="dash-action-empty">✓ 当前没有需要你立即处理的事项</div>';
  }
  html += '</div>';
  return html;
}

function renderActionItem(icon, label, desc, action, color) {
  return `
    <div class="dash-action-item" onclick="${action}">
      <div class="dash-action-icon" style="color:${color};">${icon}</div>
      <div class="dash-action-body">
        <div class="dash-action-label">${escapeHtml(label)}</div>
        <div class="dash-action-desc">${escapeHtml(desc)}</div>
      </div>
      <div class="dash-action-arrow">→</div>
    </div>`;
}

function renderPapersPreview(papers) {
  let html = '<div class="dash-preview-card">';
  html += `<div class="dash-preview-header" onclick="switchToView('kb')"><span>📄 文献简报</span><span class="dash-preview-count">${papers.unseen || 0} 待处理</span></div>`;
  if (papers.preview && papers.preview.length) {
    for (const paper of papers.preview) {
      html += `<div class="dash-preview-row" onclick="openPaperDiscussion('${escapeAttr(paper.arxiv_id)}','${escapeAttr(paper.title)}')">
        <div class="dash-preview-title">${escapeHtml(paper.title.slice(0, 40))}</div>
        <div class="dash-preview-meta">${escapeHtml(paper.direction)}${paper.pushed ? ' · 📡已推送' : ''}</div>
      </div>`;
    }
  } else {
    html += '<div class="dash-preview-empty">暂无新文献</div>';
  }
  html += '</div>';
  return html;
}

function renderTasksPreview(tasks) {
  let html = '<div class="dash-preview-card">';
  html += `<div class="dash-preview-header" onclick="switchToView('hermes')"><span>📋 任务</span><span class="dash-preview-count">${tasks.active || 0} 进行中 · ${tasks.backlog || 0} 待办</span></div>`;
  if (tasks.preview && tasks.preview.length) {
    for (const task of tasks.preview) {
      const tag = task.assignee === 'hermes' ? '<span class="dash-preview-tag">hermes</span>' : '';
      html += `<div class="dash-preview-row">
        <div class="dash-preview-title">${task.status === 'active' ? '◐' : '○'} ${escapeHtml(task.title)}</div>
        ${tag}
      </div>`;
    }
  } else {
    html += '<div class="dash-preview-empty">暂无任务</div>';
  }
  html += '</div>';
  return html;
}

function renderDecisionsPreview(decs, total) {
  let html = '<div class="dash-preview-card">';
  html += `<div class="dash-preview-header" onclick="dashOpenDecisions()"><span>📌 NSFC 待决策</span><span class="dash-preview-count">${total} 项</span></div>`;
  if (decs.length) {
    for (const dec of decs) {
      html += `<div class="dash-preview-row dash-decision-row">
        <div class="dash-preview-title">${escapeHtml(dec.title)}</div>
        <div class="dash-preview-actions">
          <button class="dash-preview-btn approve" onclick="event.stopPropagation();quickDecide('${escapeAttr(dec.id)}','approve')">✓</button>
          <button class="dash-preview-btn reject" onclick="event.stopPropagation();quickDecide('${escapeAttr(dec.id)}','reject')">✗</button>
        </div>
      </div>`;
    }
  } else {
    html += '<div class="dash-preview-empty">暂无待决策</div>';
  }
  html += '</div>';
  return html;
}

// 点击漏斗阶段：打开控制台并选中该阶段
function dashOpenStage(stage) {
  switchToView('console');
  if (window.ConsoleState) window.ConsoleState.selectedStage = stage;
}

// 打开课题详情
function dashOpenProposal(proposalId) {
  if (!proposalId) return;
  const opener = (typeof openPipelineManager === 'function')
    ? openPipelineManager
    : (window.Pipeline && typeof window.Pipeline.open === 'function' ? window.Pipeline.open : null);
  if (typeof opener === 'function') {
    opener(proposalId);
    if (window.Pipeline && typeof window.Pipeline.switchTo === 'function') {
      setTimeout(() => window.Pipeline.switchTo('proposal'), 50);
    }
  }
}

// 打开 NSFC 待决策面板
function dashOpenDecisions() {
  if (typeof openProjectsManager === 'function') {
    openProjectsManager();
    if (typeof switchProjectsTab === 'function') {
      setTimeout(() => switchProjectsTab('nsfc'), 50);
    }
  } else {
    showToast('项目总控中心未加载', 'error');
  }
}

// 快速决策（仪表盘上的✓/✗按钮）
async function quickDecide(pid, action) {
  const label = action === 'approve' ? '通过' : '否决';
  showToast(`◐ ${label}中…`, 'info');
  try {
    await apiPost(`/api/projects/nsfc/pending/${pid}`, { action, title: '' });
    showToast(`✓ 已${label}`, 'success');
    renderDashboard(); // 刷新
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// 导航切换（仪表盘/控制台/知识库/生命周期/研究管线/hermes/设置）
function switchToView(view) {
  const views = ['dashboard', 'console', 'kb', 'lifecycle', 'pipeline', 'hermes', 'settings'];
  views.forEach(v => {
    const el = document.getElementById(v + '-page');
    if (el) el.style.display = v === view ? 'flex' : 'none';
  });
  // 更新导航按钮样式
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('nav-btn-active', btn.dataset.view === view);
  });
  // 切到仪表盘时刷新数据
  if (view === 'dashboard') renderDashboard();
}

// 初始化仪表盘（页面加载时调用）
function initDashboard() {
  // 默认显示仪表盘
  switchToView('dashboard');
}
