/**
 * dashboard.js — v8.0.3 仪表盘（工作台导向重写）
 * v7 的六阶段漏斗/聚焦卡片/周末任务面板随优化环退役；v8 数据源：
 * - /api/topics              课题工作台五阶段统计 + needs_human
 * - /api/dashboard           文献/任务概览
 * - /api/topics/daily/status 每日深研 worker 状态
 * - /api/console/alerts      链路告警
 * 法定节点（启动/否决/归档）在课题工作台页执行，仪表盘只做导航与提醒。
 */

async function renderDashboard() {
  const container = document.getElementById('dashboard-page');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary);">◐ 加载中…</div>';

  try {
    const [data, topicsData, alertsData, dailyData] = await Promise.all([
      apiGet('/api/dashboard'),
      apiGet('/api/topics').catch(() => ({ success: false, stages: {}, needs_human: [] })),
      apiGet('/api/console/alerts').catch(() => ({ alerts: [] })),
      apiGet('/api/topics/daily/status').catch(() => ({ running: false })),
    ]);

    const stages = (topicsData.success ? topicsData.stages : {}) || {};
    const needs = topicsData.needs_human || [];
    const alerts = alertsData.alerts || [];
    const st = k => (stages[k] || { count: 0, items: [] });
    const ready = st('ready');
    const active = st('active');
    const kickoff = st('kickoff');
    const questions = st('questions');

    const hour = new Date().getHours();
    const greeting = hour < 6 ? '夜深了' : hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';
    const totalPending = needs.length + ready.count + (data.papers.unseen || 0) + (data.tasks.backlog || 0) + alerts.length;

    let html = '';

    // === 顶部问候 ===
    html += `<div class="dash-greeting">
      <div class="dash-greeting-text">${greeting}，林赛在线。</div>
      <div class="dash-greeting-sub">${totalPending > 0 ? `今日有 <strong>${totalPending}</strong> 件事需要你关注` : '目前暂无待处理事项，工作台运转正常。'}</div>
    </div>`;

    // === 统计卡片（课题工作台五阶段 + 文献 + 告警） ===
    html += '<div class="dash-stats-row">';
    html += renderStatCard('💡', '问题候选', questions.count, '去工作台', "switchToView('workbench')", 'var(--info-color)');
    html += renderStatCard('🔬', '深研中', kickoff.count, '查看缺口', "switchToView('workbench')", 'var(--accent-color)');
    html += renderStatCard('📦', '待你启动', ready.count, ready.count ? '审阅启动包' : '暂无', "switchToView('workbench')", 'var(--warning-color)');
    html += renderStatCard('🚀', '进行中', active.count, '查看课题', "switchToView('workbench')", 'var(--success-color)');
    html += renderStatCard('📄', '文献待处理', data.papers.unseen || 0, '查看简报', "switchToView('kb')", 'var(--info-color)');
    html += renderStatCard('🎛️', '告警/异常', alerts.length, '控制台', "switchToView('console')", alerts.length ? 'var(--error-color)' : 'var(--success-color)');
    html += '</div>';

    // === 深研 worker 状态条 ===
    html += _wbDashDailyBar(dailyData, kickoff);

    // === 主区：课题条 + 行动区 ===
    html += '<div class="dash-main-grid">';
    html += '<div class="dash-funnel-panel">';
    html += '<div class="dash-panel-title">🧪 课题工作台</div>';
    html += _wbDashStages(stages, topicsData.rejected_count);
    html += '</div>';
    html += '<div class="dash-action-panel">';
    html += '<div class="dash-panel-title">⚡ 需要你</div>';
    html += _wbDashActionList(data, topicsData, alerts);
    html += '</div>';
    html += '</div>';

    // === 底部：文献/任务快捷预览 ===
    html += '<div class="dash-preview-grid">';
    html += renderPapersPreview(data.papers);
    html += renderTasksPreview(data.tasks);
    html += '</div>';

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div style="color:var(--error-color);padding:20px;">加载失败: ${escapeHtml(e.message)}</div>`;
  }
}

// 深研 worker 状态条（每日 09:30 自动跑，可手动触发——按钮在工作台页）
function _wbDashDailyBar(dailyData, kickoff) {
  let stateText, stateColor;
  if (dailyData.running) {
    stateText = '◐ 深研 worker 运行中…';
    stateColor = 'var(--accent-color)';
  } else if (dailyData.error) {
    stateText = '✗ 上次深研失败：' + String(dailyData.error).slice(0, 60);
    stateColor = 'var(--error-color)';
  } else if (dailyData.result && dailyData.result.summary) {
    stateText = '✓ 上次深研：' + String(dailyData.result.summary).slice(0, 80);
    stateColor = 'var(--success-color)';
  } else if (dailyData.result && dailyData.result.skipped) {
    stateText = '○ 上次深研：' + dailyData.result.skipped;
    stateColor = 'var(--text-tertiary)';
  } else {
    stateText = '○ 深研 worker 待首次触发（工作日 09:30 自动）';
    stateColor = 'var(--text-tertiary)';
  }
  const gapCount = (kickoff.items || []).filter(t => t.gaps && t.gaps.length).length;
  return `<div class="dash-focus-card" onclick="switchToView('workbench')">
    <div class="dash-focus-icon">🔬</div>
    <div class="dash-focus-body">
      <div class="dash-focus-title">${escapeHtml(stateText)}</div>
      <div class="dash-focus-meta">${gapCount ? `${gapCount} 个课题有缺口待补齐 · ` : ''}配额 1 课题/天（workbench.json 可调）</div>
    </div>
    <div style="color:var(--accent-color);">→</div>
  </div>`;
}

// 五阶段横向条（替代 v7 漏斗；点击进工作台）
function _wbDashStages(stages, rejectedCount) {
  const order = [
    { key: 'questions', icon: '💡', label: '候选', color: 'var(--info-color)' },
    { key: 'kickoff', icon: '🔬', label: '深研中', color: 'var(--accent-color)' },
    { key: 'ready', icon: '📦', label: '待启动', color: 'var(--warning-color)' },
    { key: 'active', icon: '🚀', label: '进行中', color: 'var(--success-color)' },
    { key: 'archive', icon: '📦', label: '归档', color: 'var(--text-tertiary)' },
  ];
  let html = '<div class="dash-funnel">';
  for (const s of order) {
    const st = stages[s.key] || { count: 0 };
    html += `<div class="dash-funnel-stage" onclick="switchToView('workbench')" style="--stage-color:${s.color};--stage-width:60%;">
      <div class="dash-funnel-bar">
        <span class="dash-funnel-icon">${s.icon}</span>
        <span class="dash-funnel-name">${s.label}</span>
        <span class="dash-funnel-count" style="color:${s.color};">${st.count || 0}</span>
      </div>
    </div>`;
  }
  html += '</div>';
  if (rejectedCount) {
    html += `<div style="font-size:.75rem;color:var(--text-tertiary);margin-top:8px;">另有否决台账 ${rejectedCount} 条 · 旧 v7 课题库见「全链路」legacy 只读视图</div>`;
  }
  return html;
}

function _wbDashActionList(data, topicsData, alerts) {
  let html = '<div class="dash-action-list">';
  const stages = topicsData.stages || {};
  const needs = topicsData.needs_human || [];

  // 1. 等人裁决的课题（最高优先）
  for (const tid of needs.slice(0, 2)) {
    const rec = (stages.kickoff?.items || []).concat(stages.ready?.items || [], stages.questions?.items || [])
      .find(x => x.id === tid);
    html += renderActionItem('⚠', '等人裁决', rec?.title || tid, "switchToView('workbench')", 'var(--error-color)');
  }
  // 2. 待启动的启动包
  const readyItems = stages.ready?.items || [];
  for (const t of readyItems.slice(0, 3)) {
    html += renderActionItem('📦', '启动包待审阅', t.title || t.id, "switchToView('workbench')", 'var(--warning-color)');
  }
  // 3. 告警
  if (alerts.length) {
    const a = alerts[0];
    html += renderActionItem('🎛️', '链路告警', (a.title || a.message || `${alerts.length} 项异常`), "switchToView('console')", 'var(--error-color)');
  }
  // 4. 文献
  if (data.papers.unseen) {
    html += renderActionItem('📄', '文献简报', `${data.papers.unseen} 篇待处理`, "switchToView('kb')", 'var(--info-color)');
  }
  // 5. 任务
  if (data.tasks.backlog) {
    html += renderActionItem('📋', '待办任务', `${data.tasks.backlog} 项待办`, "switchToView('console')", 'var(--warning-color)');
  }

  if (!needs.length && !readyItems.length && !alerts.length && !data.papers.unseen && !data.tasks.backlog) {
    html += '<div class="dash-action-empty">✓ 当前没有需要你立即处理的事项</div>';
  }
  html += '</div>';
  return html;
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
  html += `<div class="dash-preview-header" onclick="switchToView('console')"><span>📋 任务</span><span class="dash-preview-count">${tasks.active || 0} 进行中 · ${tasks.backlog || 0} 待办</span></div>`;
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

// 导航切换（工作台/仪表盘/控制台/知识库/全链路/设置/审核）
function switchToView(view) {
  const views = ['workbench', 'dashboard', 'console', 'kb', 'lifecycle', 'settings', 'review'];
  views.forEach(v => {
    const el = document.getElementById(v + '-page');
    if (el) el.style.display = v === view ? 'flex' : 'none';
  });
  // 隐藏已移除的视图（兼容旧页面）
  ['pipeline', 'hermes'].forEach(v => {
    const el = document.getElementById(v + '-page');
    if (el) el.style.display = 'none';
  });
  // 更新导航按钮样式（review 不是主导航，取消全部高亮）
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (view === 'review') {
      btn.classList.remove('nav-btn-active');
    } else {
      btn.classList.toggle('nav-btn-active', btn.dataset.view === view);
    }
  });
  // 切换时刷新数据
  if (view === 'workbench' && typeof renderWorkbench === 'function') renderWorkbench();
  if (view === 'dashboard') renderDashboard();
  if (view === 'lifecycle') renderLifecycleDashboard();
}

// 初始化仪表盘（页面加载时调用）
function initDashboard() {
  // 默认显示仪表盘
  switchToView('dashboard');
}
