/**
 * 提案生命周期管理（v6.6.0）
 * CoPilot 操作台：仪表盘 + 课题列表 + 流转/优化/反馈操作
 *
 * 后端 API：
 *   GET  /api/lifecycle/dashboard          仪表盘统计
 *   GET  /api/lifecycle/list/{status}      按阶段列出课题
 *   POST /api/lifecycle/register           注册新课题
 *   POST /api/lifecycle/{id}/transition    流转
 *   POST /api/lifecycle/{id}/optimize      执行一轮优化
 *   POST /api/lifecycle/{id}/feedback      提交人工反馈
 *   POST /api/lifecycle/{id}/review-session 创建审核会话
 *   POST /api/lifecycle/{id}/review-verdict 提交审核结论
 *   POST /api/lifecycle/cron-sweep         cron 扫描
 *   GET  /api/lifecycle/agent-scores       writer/critic 奖惩分数
 *   GET  /api/lifecycle/monitor/{id}       monitor 历史与负反馈状态
 *   POST /api/lifecycle/{id}/clear-alert   清除负反馈告警
 */

// ============================================
// 状态
// ============================================
let _lcCurrentFilter = 'all';  // 当前筛选的阶段
let _lcFocusInfo = null;       // v6.8.0: 当前微调度器聚焦信息

// 阶段配置
const LC_STAGES = [
  { key: 'drafts', label: '初稿', icon: '📝', color: 'var(--text-tertiary)', desc: '等待确认思路' },
  { key: 'optimizing', label: '优化中', icon: '🔄', color: 'var(--info-color)', desc: 'writer-critic 对抗' },
  { key: 'pending_review', label: '待校验', icon: '🔍', color: 'var(--warning-color)', desc: '等待人工核验' },
  { key: 'archived', label: '归档', icon: '📦', color: 'var(--success-color)', desc: '已通过·知识库' },
];

const LC_TYPE_LABELS = { general: '面上', key: '重点', major: '重大' };
const LC_TYPE_COLORS = { general: 'var(--info-color)', key: 'var(--accent-color)', major: 'var(--error-color)' };

// v6.8.0: 申请书 5 模块（与后端 proposal_sections.PROPOSAL_SECTIONS 对齐）
const LC_SECTIONS = [
  { key: 'rationale', cn: '立项依据', icon: '📖' },
  { key: 'content', cn: '研究内容', icon: '📋' },
  { key: 'scheme', cn: '研究方案', icon: '🔬' },
  { key: 'full_review', cn: '整体一致性', icon: '🔍' },
  { key: 'references', cn: '参考文献', icon: '📚' },
];
const LC_SECTION_KEY_TO_CN = Object.fromEntries(LC_SECTIONS.map(s => [s.key, s.cn]));

// ============================================
// v6.8.0: 加载微调度器聚焦信息
// ============================================
async function lcLoadFocusInfo() {
  try {
    const result = await apiGet('/api/lifecycle/jobs');
    if (result.status !== 'ok') return;
    // 从 cron jobs 中无法直接获取聚焦，因此通过单独状态接口获取
    const focusRes = await apiGet('/api/lifecycle/focus').catch(() => ({}));
    _lcFocusInfo = focusRes.focus || null;
  } catch (e) {
    _lcFocusInfo = null;
  }
}

// ============================================
// 打开/关闭
// ============================================
function openLifecycle() {
  // v6.7.7: 生命周期已升级为页面
  switchToView('lifecycle');
  renderLifecycleDashboard();
}

// v6.7.7: 页面初始化
function initLifecyclePage() {
  const page = document.getElementById('lifecycle-page');
  if (!page) return;
  // 导航点击由 app.js 统一处理，这里监听页面是否可见并在可见时刷新
  const observer = new MutationObserver(() => {
    if (page.style.display === 'flex') renderLifecycleDashboard();
  });
  observer.observe(page, { attributes: true, attributeFilter: ['style'] });
}

// ============================================
// 仪表盘
// ============================================
// ============================================
// v6.9.58: 想法收件箱 + 周末任务面板
// （此前 5 条 incoming 端点与 weekend 3 端点无 UI，人工立项只能读文件）
// ============================================
function lcToggleInbox() {
  const panel = document.getElementById('lc-inbox-panel');
  if (!panel) return;
  if (panel.style.display === 'none') {
    panel.style.display = 'block';
    lcRenderInbox();
  } else {
    panel.style.display = 'none';
  }
}

async function lcRenderInbox() {
  const panel = document.getElementById('lc-inbox-panel');
  if (!panel) return;
  panel.innerHTML = '<div class="ta-center pad-20 text-tertiary">加载收件箱...</div>';
  try {
    const data = await apiGet('/api/lifecycle/incoming');
    if (data.status !== 'ok') throw new Error(data.error || '获取失败');
    const ideas = data.ideas || [];
    if (!ideas.length) {
      panel.innerHTML = `<div class="lc-card" style="padding:14px;">📭 收件箱为空（周末簇路由 new 动作注册的设想将出现在此，等待人工激活/合并/拒绝）</div>`;
      return;
    }
    let html = `<div class="lc-card" style="padding:12px 14px;"><div style="font-weight:600;margin-bottom:8px;">📥 想法收件箱（${ideas.length}）</div>`;
    for (const idea of ideas) {
      const id = idea.idea_id || idea.id || '';
      const title = idea.title || idea.name || id;
      const dossier = idea.idea_dossier || {};
      const rec = dossier.recommendation || '';
      html += `
        <div style="border:1px solid var(--border-color);border-radius:8px;padding:10px;margin-bottom:8px;">
          <div style="font-weight:600;">${escapeHtml(title)}</div>
          <div class="fs-072 text-tertiary" style="margin:4px 0;">
            ${rec ? `立项预审：<strong>${escapeHtml(rec)}</strong> · ` : ''}${escapeHtml(idea.created_at || '')}
          </div>
          <div class="fs-072 text-tertiary">${escapeHtml((idea.background || idea.summary || '').slice(0, 150))}</div>
          <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
            <button class="btn-text" style="color:var(--success-color);" onclick="lcInboxAccept('${escapeHtml(id)}')">✓ 激活立项</button>
            <button class="btn-text" style="color:var(--info-color);" onclick="lcInboxExpand('${escapeHtml(id)}')">🔍 展开</button>
            <button class="btn-text" style="color:var(--error-color);" onclick="lcInboxReject('${escapeHtml(id)}')">✗ 拒绝</button>
          </div>
        </div>`;
    }
    html += '</div>';
    panel.innerHTML = html;
  } catch (e) {
    panel.innerHTML = `<div class="pad-20 text-error">收件箱加载失败：${escapeHtml(e.message)}</div>`;
  }
}

async function lcInboxAccept(ideaId) {
  if (!confirm(`确认激活该设想为新课题（drafts → 优化管线）？`)) return;
  try {
    const r = await apiPost(`/api/lifecycle/incoming/${encodeURIComponent(ideaId)}/accept`, {});
    if (r.status === 'ok') { showToast('✓ 已激活立项', 'success'); lcRenderInbox(); renderLifecycleDashboard(); }
    else showToast(`✗ ${r.error || '失败'}`, 'error');
  } catch (e) { showToast(`✗ ${e.message}`, 'error'); }
}

async function lcInboxReject(ideaId) {
  if (!confirm('确认拒绝该设想？')) return;
  try {
    const r = await apiPost(`/api/lifecycle/incoming/${encodeURIComponent(ideaId)}/reject`, {});
    if (r.status === 'ok') { showToast('✓ 已拒绝', 'success'); lcRenderInbox(); }
    else showToast(`✗ ${r.error || '失败'}`, 'error');
  } catch (e) { showToast(`✗ ${e.message}`, 'error'); }
}

async function lcInboxExpand(ideaId) {
  try {
    const r = await apiPost('/api/lifecycle/incoming/expand', { idea_id: ideaId });
    if (r.status === 'ok' && r.data) {
      const d = r.data;
      showModal?.(`<h3>🔍 设想详情</h3><pre style="white-space:pre-wrap;font-size:0.8rem;max-height:60vh;overflow:auto;">${escapeHtml(JSON.stringify(d, null, 2))}</pre>`) ||
      alert(JSON.stringify(d, null, 2).slice(0, 2000));
    } else showToast(`✗ ${r.error || '失败'}`, 'error');
  } catch (e) { showToast(`✗ ${e.message}`, 'error'); }
}

function lcToggleWeekend() {
  const panel = document.getElementById('lc-weekend-panel');
  if (!panel) return;
  if (panel.style.display === 'none') {
    panel.style.display = 'block';
    lcRenderWeekend();
  } else {
    panel.style.display = 'none';
  }
}

async function lcRenderWeekend() {
  const panel = document.getElementById('lc-weekend-panel');
  if (!panel) return;
  panel.innerHTML = '<div class="ta-center pad-20 text-tertiary">加载周末任务状态...</div>';
  try {
    const data = await apiGet('/api/lifecycle/weekend/status').catch(() => ({ jobs: {} }));
    const jobs = (data.data && data.data.jobs) || data.jobs || {};
    const defs = [
      { key: 'weekend_input', label: '📥 输入端（检索→聚类→路由）', action: 'input' },
      { key: 'weekend_output', label: '📤 输出端（归档萃取→知识库）', action: 'output' },
      { key: 'weekend_reflection', label: '🪞 反思（链路复盘）', action: 'reflection' },
    ];
    let html = `<div class="lc-card" style="padding:12px 14px;"><div style="font-weight:600;margin-bottom:8px;">🗓️ 周末任务（周六输入/输出，周日反思；工作日可在控制台手动触发）</div>`;
    for (const def of defs) {
      const j = jobs[def.key] || {};
      const status = j.status || 'pending';
      const color = status === 'done' ? 'var(--success-color)' : status === 'failed' || status === 'running' ? 'var(--error-color)' : 'var(--text-tertiary)';
      html += `
        <div style="border:1px solid var(--border-color);border-radius:8px;padding:10px;margin-bottom:8px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
          <div style="flex:1;min-width:200px;">
            <div>${def.label}</div>
            <div class="fs-072 text-tertiary">状态 <strong style="color:${color};">${escapeHtml(status)}</strong>
              · 完成 ${escapeHtml((j.finished_at || '—').slice(0, 16))}
              ${j.last_error ? ` · <span class="text-error">${escapeHtml(j.last_error.slice(0, 60))}</span>` : ''}
              ${j.attempts ? ` · 尝试 ${j.attempts} 次` : ''}</div>
          </div>
          <button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcWeekendRun('${def.action}')">▶ 手动执行</button>
        </div>`;
    }
    html += '</div>';
    panel.innerHTML = html;
  } catch (e) {
    panel.innerHTML = `<div class="pad-20 text-error">周末状态加载失败：${escapeHtml(e.message)}</div>`;
  }
}

async function lcWeekendRun(task) {
  if (!confirm(`手动执行周末${task}任务？（非周末时段执行，产物按当日日期落盘）`)) return;
  try {
    const r = await apiPost(`/api/lifecycle/weekend/${task}`, {});
    if (r.status === 'accepted') { showToast('✓ 已启动（后台执行）', 'success'); setTimeout(lcRenderWeekend, 3000); }
    else showToast(`✗ ${r.error || '失败'}`, 'error');
  } catch (e) { showToast(`✗ ${e.message}`, 'error'); }
}

async function renderLifecycleDashboard() {
  const container = document.getElementById('lifecycle-body');
  if (!container) return;

  container.innerHTML = '<div class="ta-center pad-40 text-tertiary">加载中...</div>';

  try {
    const data = await apiGet('/api/lifecycle/dashboard');
    if (data.status !== 'ok') throw new Error(data.error || '获取失败');
    const d = data.data;

    let html = '';
    html += `<div class="lc-header">
      <h2>🔬 提案生命周期</h2>
      <button class="btn-text" style="color:var(--accent-color);" onclick="lcRegister()">+ 注册新课题</button>
    </div>`;

    // === 四阶段统计卡片 ===
    html += '<div class="lc-stages-grid">';
    for (const stage of LC_STAGES) {
      const count = d.by_status?.[stage.key] || 0;
      const active = _lcCurrentFilter === stage.key;
      html += `
        <div class="lc-stage-card ${active ? 'active' : ''}"
             style="border-left:3px solid ${stage.color};"
             onclick="lcFilterStage('${stage.key}')">
          <div class="lc-stage-label">${stage.icon} ${stage.label}</div>
          <div class="lc-stage-count" style="color:${count > 0 ? stage.color : 'var(--text-tertiary)'};">${count}</div>
          <div class="lc-stage-desc">${stage.desc}</div>
        </div>`;
    }
    html += '</div>';

    // === 类型分布 + 总数 ===
    html += '<div class="lc-meta-bar">';
    html += `<span>总计 <strong>${d.total || 0}</strong> 个课题</span>`;
    html += '<span>·</span>';
    for (const [type, label] of Object.entries(LC_TYPE_LABELS)) {
      const count = d.by_type?.[type] || 0;
      if (count > 0) {
        html += `<span style="color:${LC_TYPE_COLORS[type]};">${label} ${count}</span>`;
      }
    }
    html += `<span class="ml-auto btn-text" onclick="lcFilterStage('all')">显示全部</span>`;
    html += '</div>';

    // v6.7.5: cron 框架操作
    html += `<div class="lc-actions-bar">`;
    html += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcOrchestrate()">🔄 手动编排</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcRepair()">🔧 手动修复</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--text-secondary);" onclick="lcShowJobs()">📋 查看 cron</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcToggleInbox()">📥 想法收件箱</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcToggleWeekend()">🗓️ 周末任务</button>`;
    html += `</div>`;

    // v6.9.58: 想法收件箱（_incoming 人工立项队列）+ 周末任务面板（可折叠）
    html += `<div id="lc-inbox-panel" style="display:none;margin-bottom:12px;"></div>`;
    html += `<div id="lc-weekend-panel" style="display:none;margin-bottom:12px;"></div>`;

    // v6.7.6: agent scores 概览（异步加载）
    html += `<div id="lc-agent-scores" class="lc-scores-bar">加载对抗评审分数...</div>`;

    container.innerHTML = html;

    // 异步加载 agent scores
    lcLoadAgentScores();

    // === 课题列表 ===
    await renderLifecycleList();

  } catch (e) {
    container.innerHTML = `<div class="ta-center pad-40 text-error">加载失败：${escapeHtml(e.message)}</div>`;
  }
}

// ============================================
// 筛选
// ============================================
function lcFilterStage(stage) {
  _lcCurrentFilter = stage;
  renderLifecycleDashboard();
}

// ============================================
// 课题列表
// ============================================
async function renderLifecycleList() {
  const listContainer = document.getElementById('lifecycle-list');
  if (!listContainer) return;

  listContainer.innerHTML = '<div class="ta-center pad-20 text-tertiary">加载课题...</div>';

  try {
    let proposals = [];

    // 统一从 dashboard 获取全部课题，前端筛选
    const [dashData, focusRes] = await Promise.all([
      apiGet('/api/lifecycle/dashboard'),
      apiGet('/api/lifecycle/focus').catch(() => ({ status: 'ok', focus: null })),
    ]);
    _lcFocusInfo = focusRes.focus || null;
    const focusPid = _lcFocusInfo?.focus_proposal;

    const allProposals = dashData.data?.proposals || {};
    // 转换格式：dashboard 返回的是 {pid: {...}} 字典
    proposals = Object.entries(allProposals).map(([pid, data]) => {
      const rawJobs = data.pipeline_jobs || [];
      const pendingJobs = rawJobs.filter(j => j.status === 'pending');
      // 找第一个依赖已满足的 pending job 作为下一任务提示
      const doneIds = new Set(rawJobs.filter(j => j.status === 'done').map(j => j.job_id));
      const nextPending = pendingJobs.find(j => (j.depends_on || []).every(d => doneIds.has(d)));
      return {
        proposal_id: pid,
        status: data.status,
        project_type: data.project_type || 'general',
        optimization_rounds: data.optimization_rounds || 0,
        last_score: data.last_score || 0,
        updated_at: data.updated_at || '',
        section_passes: data.section_passes || {},
        is_focused: pid === focusPid,
        next_pending_job: nextPending || null,
      };
    });

    // 按阶段筛选
    if (_lcCurrentFilter !== 'all') {
      proposals = proposals.filter(p => p.status === _lcCurrentFilter);
    }

    if (proposals.length === 0) {
      listContainer.innerHTML = `
        <div class="ta-center pad-40 text-tertiary">
          <div class="fs-1.2 mb-4">📭 暂无课题</div>
          <div class="fs-082">${_lcCurrentFilter === 'all' ? '点击下方按钮注册新课题' : '该阶段没有课题'}</div>
        </div>`;
      return;
    }

    // 排序：当前聚焦排第一，其余按更新时间倒序
    proposals.sort((a, b) => {
      if (a.is_focused && !b.is_focused) return -1;
      if (!a.is_focused && b.is_focused) return 1;
      return (b.updated_at || '').localeCompare(a.updated_at || '');
    });

    let html = '<div class="lc-proposal-list">';
    for (const p of proposals) {
      html += renderProposalCard(p);
    }
    html += '</div>';

    listContainer.innerHTML = html;

  } catch (e) {
    listContainer.innerHTML = `<div class="ta-center pad-20 text-error">加载失败：${escapeHtml(e.message)}</div>`;
  }
}

// ============================================
// v6.7.6: Agent Scores 概览
// ============================================
async function lcLoadAgentScores() {
  const el = document.getElementById('lc-agent-scores');
  if (!el) return;
  try {
    const result = await apiGet('/api/lifecycle/agent-scores');
    if (result.status !== 'ok') throw new Error(result.error || '获取失败');
    const scores = result.scores || {};
    const writer = scores.writer || {};
    const critic = scores.critic || {};
    const wScore = writer.score ?? 100;
    const cScore = critic.score ?? 100;
    const wColor = wScore >= 100 ? 'var(--success-color)' : wScore >= 70 ? 'var(--warning-color)' : 'var(--error-color)';
    const cColor = cScore >= 100 ? 'var(--success-color)' : cScore >= 70 ? 'var(--warning-color)' : 'var(--error-color)';
    el.innerHTML = `
      <div class="d-flex ai-center gap-12 pad-8 bg-secondary br-6">
        <span class="fw-500">对抗评审分数</span>
        <span>writer: <strong style="color:${wColor};">${wScore.toFixed(1)}</strong></span>
        <span>critic: <strong style="color:${cColor};">${cScore.toFixed(1)}</strong></span>
        <span class="text-tertiary">(${writer.history_count || 0} 轮记录)</span>
      </div>`;
  } catch (e) {
    el.innerHTML = `<span class="text-tertiary">对抗评审分数加载失败：${escapeHtml(e.message)}</span>`;
  }
}

// ============================================
// 单个课题卡片
// ============================================
function renderProposalCard(p) {
  const stage = LC_STAGES.find(s => s.key === p.status) || LC_STAGES[0];
  const typeLabel = LC_TYPE_LABELS[p.project_type] || '?';
  const typeColor = LC_TYPE_COLORS[p.project_type] || 'var(--text-secondary)';
  const score = p.last_score || 0;
  const scoreColor = score >= 0.85 ? 'var(--success-color)' : score >= 0.7 ? 'var(--warning-color)' : 'var(--text-tertiary)';
  const isFocused = p.is_focused;
  const nextJob = p.next_pending_job;

  // 解析课题名称（从 ID 提取）
  const namePart = (p.proposal_id || '').split('-').slice(1, -1).join('-') || p.proposal_id;

  // v6.8.0+: 轮次进度条
  const rounds = p.optimization_rounds || 0;
  const maxRounds = 10;
  const roundPct = Math.min((rounds / maxRounds) * 100, 100);
  let roundBarHtml = '';
  if (p.status === 'optimizing' && rounds > 0) {
    roundBarHtml = `
      <div class="lc-card-round-bar">
        <div class="lc-card-round-track">
          <div class="lc-card-round-fill" style="width:${roundPct}%"></div>
        </div>
        <span class="lc-card-round-text">${rounds}/${maxRounds}</span>
      </div>`;
  }

  // v6.8.0+: 分数指示条
  let scoreBarHtml = '';
  if (score > 0) {
    const scorePct = Math.min(score * 100, 100);
    scoreBarHtml = `
      <div class="lc-card-score-bar">
        <div class="lc-card-score-track">
          <div class="lc-card-score-fill" style="width:${scorePct}%;background:${scoreColor};"></div>
        </div>
        <span class="lc-card-score-text" style="color:${scoreColor};">${(score * 100).toFixed(0)}分</span>
      </div>`;
  }

  // v6.8.0: 5 模块进度
  let sectionBars = '';
  if (p.status === 'optimizing' && p.section_passes) {
    const passes = p.section_passes || {};
    sectionBars = '<div class="lc-section-bars">' +
      LC_SECTIONS.map(s => {
        const passed = passes[s.key] === true;
        return `<span class="lc-section-chip ${passed ? 'passed' : 'pending'}" title="${s.cn}">${s.icon}</span>`;
      }).join('') +
      '</div>';
  }

  let actions = '';
  actions += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcViewDetail('${p.proposal_id}')">👁 详情</button>`;
  actions += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcViewProposalContent('${p.proposal_id}')">📄 申请书</button>`;
  if (p.status === 'optimizing') {
    actions += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcShowMonitor('${p.proposal_id}')">🔍 监察</button>`;
  }
  if (p.status === 'drafts') {
    actions += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcTransition('${p.proposal_id}','optimizing','确认思路可行')">→ 优化中</button>`;
  }
  if (p.status === 'optimizing') {
    actions += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcOptimize('${p.proposal_id}')">⚡ 优化一轮</button>`;
    actions += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcTransition('${p.proposal_id}','pending_review','手动送审')">→ 送审</button>`;
  }
  if (p.status === 'pending_review') {
    actions += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcReview('${p.proposal_id}')">🔍 审核</button>`;
  }

  const focusBadge = isFocused
    ? `<span class="lc-focus-badge" title="当前时段微调度器聚焦此课题">⚡ 当前聚焦</span>`
    : '';
  const nextJobHtml = nextJob
    ? `<span class="lc-next-job">下一任务: ${escapeHtml(nextJob.step || '')} · ${escapeHtml(LC_SECTION_KEY_TO_CN[nextJob.section_key] || nextJob.section_key || '')}</span>`
    : '';

  return `
    <div class="lc-proposal-card ${isFocused ? 'lc-proposal-focused' : ''}" style="border-left:3px solid ${stage.color};">
      <div class="lc-proposal-header">
        <span class="lc-proposal-name">${escapeHtml(namePart)}</span>
        ${focusBadge}
        <span class="lc-proposal-type" style="color:${typeColor};">${typeLabel}</span>
        <span class="lc-proposal-status" style="color:${stage.color};">${stage.icon} ${stage.label}</span>
      </div>
      <div class="lc-proposal-meta">
        ${rounds} 轮优化 · ${(p.updated_at || '').slice(0, 10)}
        ${nextJobHtml}
      </div>
      <div class="lc-card-metrics">
        ${scoreBarHtml}
        ${roundBarHtml}
      </div>
      ${sectionBars}
      <div class="lc-proposal-actions">
        ${actions}
      </div>
      <div id="lc-checkpoints-${p.proposal_id}" class="d-none mt-6 fs-072 text-secondary"></div>
    </div>`;
}

// ============================================
// v6.8.0+: 查看课题详情（优化进度可视化 + 5 模块进度 + 申请书内容）
// ============================================
async function lcViewDetail(proposalId) {
  try {
    const [dashRes, cpRes, monitorRes] = await Promise.all([
      apiGet('/api/lifecycle/dashboard'),
      apiGet(`/api/lifecycle/checkpoints/${encodeURIComponent(proposalId)}`),
      apiGet(`/api/lifecycle/monitor/${encodeURIComponent(proposalId)}`).catch(() => ({ status: 'ok' })),
    ]);

    const data = dashRes.data?.proposals?.[proposalId] || {};
    const checkpoints = cpRes.data || [];
    const monitorAlert = monitorRes.negative_feedback_alert;
    const monitorReasons = monitorRes.negative_feedback_reasons || [];

    const namePart = proposalId.split('-').slice(1, -1).join('-') || proposalId;
    const rounds = data.optimization_rounds || 0;
    const lastScore = data.last_score || 0;
    const scoreHistory = data.score_history || [];
    const dimScores = data.last_dim_scores || {};
    const passes = data.section_passes || {};
    const status = data.status || '';

    // === 轮次进度条 ===
    const maxRounds = 10;
    const roundPct = Math.min((rounds / maxRounds) * 100, 100);
    let roundBarHtml = '';
    if (status === 'optimizing' && rounds > 0) {
      roundBarHtml = `
        <div class="lc-detail-section">
          <div class="lc-detail-label">优化轮次</div>
          <div class="lc-round-bar">
            <div class="lc-round-track">
              <div class="lc-round-fill" style="width:${roundPct}%"></div>
            </div>
            <span class="lc-round-text">${rounds} / ${maxRounds} 轮</span>
          </div>
        </div>`;
    }

    // === 分数趋势（简单色块） ===
    let scoreTrendHtml = '';
    if (scoreHistory.length > 0) {
      const recent = scoreHistory.slice(-8);
      const maxScore = Math.max(...recent.map(s => s.score || 0), 1);
      scoreTrendHtml = `
        <div class="lc-detail-section">
          <div class="lc-detail-label">分数趋势</div>
          <div class="lc-score-trend">
            ${recent.map(s => {
              const h = Math.max((s.score / maxScore) * 100, 8);
              const color = s.score >= 0.80 ? 'var(--success-color)' : s.score >= 0.60 ? 'var(--warning-color)' : 'var(--error-color)';
              return `<div class="lc-score-bar" style="height:${h}%;background:${color};" title="r${s.round}: ${(s.score * 100).toFixed(0)}分"></div>`;
            }).join('')}
          </div>
          <div class="lc-score-labels">${recent.map(s => `<span>r${s.round}</span>`).join('')}</div>
        </div>`;
    }

    // === 当前分数与维度 ===
    const dimNames = { innovation: '创新性', feasibility: '可行性', rigor: '严谨性', completeness: '完整性' };
    let dimHtml = '';
    if (Object.keys(dimScores).length > 0) {
      dimHtml = '<div class="lc-detail-section"><div class="lc-detail-label">维度评分</div><div class="lc-dim-grid">';
      for (const [key, val] of Object.entries(dimScores)) {
        const cn = dimNames[key] || key;
        const color = val >= 0.80 ? 'var(--success-color)' : val >= 0.60 ? 'var(--warning-color)' : 'var(--error-color)';
        const pct = ((val || 0) * 100).toFixed(0);
        dimHtml += `<div class="lc-dim-item"><span class="lc-dim-label">${cn}</span><div class="lc-dim-track"><div class="lc-dim-fill" style="width:${pct}%;background:${color};"></div></div><span class="lc-dim-val" style="color:${color};">${pct}分</span></div>`;
      }
      dimHtml += '</div></div>';
    }

    // === 5 模块进度 ===
    const sectionHtml = LC_SECTIONS.map(s => {
      const passed = passes[s.key] === true;
      return `<span class="lc-section-chip ${passed ? 'passed' : 'pending'}" title="${s.cn}">${s.icon} ${s.cn}</span>`;
    }).join('');

    // === 当前 job 链状态 ===
    const stepOrder = ['critic', 'gap_identify', 'lit_search', 'lit_read', 'lit_note', 'writer'];
    const sectionOrder = ['rationale', 'content', 'scheme', 'full_review', 'references'];
    let jobChainHtml = '';
    if (checkpoints.length > 0) {
      // 找到最新的 round 和当前活跃的 job
      const maxRound = Math.max(...checkpoints.map(j => j.round || 0));
      const currentJobs = checkpoints.filter(j => j.round === maxRound);
      const runningJob = currentJobs.find(j => j.status === 'running');
      const pendingCount = currentJobs.filter(j => j.status === 'pending').length;
      const doneCount = currentJobs.filter(j => j.status === 'done').length;
      const failedCount = currentJobs.filter(j => j.status === 'failed').length;
      const totalInRound = currentJobs.length;

      jobChainHtml = `
        <div class="lc-detail-section">
          <div class="lc-detail-label">当前轮次进度（r${maxRound}）</div>
          <div class="lc-round-summary">
            <span class="lc-round-stat" style="color:var(--success-color);">✓ ${doneCount} 完成</span>
            <span class="lc-round-stat" style="color:var(--info-color);">◐ ${runningJob ? 1 : 0} 进行中</span>
            <span class="lc-round-stat" style="color:var(--text-tertiary);">○ ${pendingCount} 待处理</span>
            ${failedCount > 0 ? `<span class="lc-round-stat" style="color:var(--error-color);">✗ ${failedCount} 失败</span>` : ''}
          </div>
          <div class="lc-job-chain">`;

      // 按模块显示 job 链
      for (const sk of sectionOrder) {
        const secJobs = currentJobs.filter(j => j.section_key === sk);
        if (secJobs.length === 0) continue;
        const secCn = LC_SECTION_KEY_TO_CN[sk] || sk;
        jobChainHtml += `<div class="lc-job-section-label">${secCn}</div><div class="lc-job-row">`;
        for (const step of stepOrder) {
          const job = secJobs.find(j => j.step === step);
          if (!job) continue;
          const statusIcon = job.status === 'done' ? '✓' : job.status === 'running' ? '◐' : job.status === 'failed' ? '✗' : '○';
          const statusColor = job.status === 'done' ? 'var(--success-color)' : job.status === 'running' ? 'var(--info-color)' : job.status === 'failed' ? 'var(--error-color)' : 'var(--text-tertiary)';
          const isActive = job.status === 'running';
          jobChainHtml += `<span class="lc-job-step ${isActive ? 'active' : ''}" style="color:${statusColor};" title="${job.job_id}">${statusIcon} ${step}</span>`;
        }
        jobChainHtml += '</div>';
      }

      jobChainHtml += '</div></div>';

      // 最新失败 job 详情
      const recentFailures = checkpoints.filter(j => j.status === 'failed').slice(-3);
      if (recentFailures.length > 0) {
        jobChainHtml += '<div class="lc-detail-section"><div class="lc-detail-label">最近失败</div>';
        for (const f of recentFailures) {
          jobChainHtml += `<div class="lc-fail-item">✗ <strong>r${f.round}</strong> ${f.step} · ${LC_SECTION_KEY_TO_CN[f.section_key] || f.section_key}${f.last_error ? `<br><span class="fs-072 text-tertiary">${escapeHtml(f.last_error.slice(0, 80))}</span>` : ''}</div>`;
        }
        jobChainHtml += '</div>';
      }
    }

    // === 历史轮次概览 ===
    let roundHistoryHtml = '';
    if (scoreHistory.length > 0) {
      roundHistoryHtml = '<div class="lc-detail-section"><div class="lc-detail-label">各轮次结果</div><div class="lc-round-history">';
      for (const h of scoreHistory) {
        const rColor = h.score >= 0.80 ? 'var(--success-color)' : h.score >= 0.60 ? 'var(--warning-color)' : 'var(--error-color)';
        const sectionPassed = h.section_passed ? '✓' : '○';
        roundHistoryHtml += `<div class="lc-round-row">
          <span class="lc-round-num" style="color:${rColor};">r${h.round}</span>
          <span class="lc-round-score" style="color:${rColor};">${(h.score * 100).toFixed(0)}分</span>
          <span class="lc-round-section">${sectionPassed} ${LC_SECTION_KEY_TO_CN[h.focus_section] || h.focus_section || ''}</span>
          <span class="lc-round-issues">${h.issues_count || 0} issues</span>
          <span class="lc-round-weakest" style="color:var(--warning-color);">短板: ${dimNames[h.weakest_dim] || h.weakest_dim || ''}</span>
        </div>`;
      }
      roundHistoryHtml += '</div></div>';
    }

    // === 负反馈告警 ===
    let alertHtml = '';
    if (monitorAlert) {
      alertHtml = `<div class="pad-10 bg-error br-6" style="color:#fff;margin-bottom:12px;"><div class="fw-600 mb-4">⚠️ 负反馈告警</div><ul class="ma-0 pl-16">${monitorReasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
        <button class="btn-text mt-8" style="color:#fff;text-decoration:underline;" onclick="lcClearAlert('${proposalId}')">清除告警</button>
      </div>`;
    }

    const html = `
      <div class="lc-detail-modal" style="max-height:70vh;overflow-y:auto;">
        ${alertHtml}
        <div class="lc-detail-header">
          <div class="lc-detail-title">${escapeHtml(namePart)}</div>
          <div class="lc-detail-meta">${rounds} 轮优化 · score ${(lastScore * 100).toFixed(0)}分</div>
        </div>
        <div class="lc-section-bars" style="margin-bottom:12px;">${sectionHtml}</div>
        ${roundBarHtml}
        <div class="lc-detail-row">
          ${scoreTrendHtml}
          ${dimHtml}
        </div>
        ${jobChainHtml}
        ${roundHistoryHtml}
        <div class="lc-detail-actions">
          <button class="btn-text" style="color:var(--info-color);font-size:0.85rem;" onclick="lcViewProposalContent('${proposalId}')">📄 查看申请书</button>
          <button class="btn-text" style="color:var(--accent-color);font-size:0.85rem;" onclick="lcShowMonitor('${proposalId}')">🔍 监察详情</button>
          ${status === 'optimizing' ? `<button class="btn-text" style="color:var(--accent-color);font-size:0.85rem;" onclick="lcOptimize('${proposalId}')">⚡ 优化一轮</button>` : ''}
        </div>
      </div>`;

    await confirmModal(html, '课题详情', '关闭');
  } catch (e) {
    showToast(`加载详情失败：${e.message}`, 'error');
  }
}

// ============================================
// v6.8.0+: 查看申请书内容（适用于所有阶段）
// ============================================
async function lcViewProposalContent(proposalId) {
  try {
    const result = await apiGet(`/api/pipeline/${encodeURIComponent(proposalId)}/proposal/sections`);
    if (result.status !== 'ok') throw new Error(result.error || '获取申请书失败');

    const sections = result.sections || [];
    const rawMap = {};
    for (const s of sections) {
      if (s.name && s.content) rawMap[s.name] = s.content;
    }

    // 按 5 模块顺序排列
    const sectionOrder = ['立项依据', '研究内容', '研究方案', '整体一致性', '参考文献'];
    let hasContent = false;
    let html = '<div class="lc-content-modal" style="max-height:70vh;overflow-y:auto;">';

    for (const name of sectionOrder) {
      const content = rawMap[name];
      if (!content) continue;
      hasContent = true;
      html += `
        <div class="lc-content-section">
          <div class="lc-content-section-title">${name}</div>
          <div class="lc-content-body">${renderMarkdown(content)}</div>
        </div>`;
    }

    html += '</div>';

    if (!hasContent) {
      html = '<div class="ta-center pad-40 text-tertiary">暂无申请书内容</div>';
    }

    const namePart = proposalId.split('-').slice(1, -1).join('-') || proposalId;
    await confirmModal(html, `📄 ${escapeHtml(namePart)} - 申请书全文`, '关闭');
  } catch (e) {
    showToast(`✗ 加载申请书失败：${e.message}`, 'error');
  }
}

// ============================================
// 操作：流转
// ============================================
async function lcTransition(proposalId, toStage, reason = '') {
  const confirmed = await confirmModal(
    `确认将课题移入「${LC_STAGES.find(s => s.key === toStage)?.label || toStage}」？`,
    '确认流转', '取消'
  );
  if (!confirmed) return;

  try {
    showToast('流转中...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/transition`, { to_stage: toStage, reason });
    if (result.status === 'ok') {
      showToast(`✓ 已移入${LC_STAGES.find(s => s.key === toStage)?.label}`, 'success');
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '流转失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// 操作：优化一轮
// ============================================
async function lcOptimize(proposalId) {
  const confirmed = await confirmModal(
    `执行一轮 writer-critic 对抗优化？\n（可能需要数分钟）`,
    '开始优化', '取消'
  );
  if (!confirmed) return;

  try {
    showToast('⚡ 优化中（writer-critic 对抗，请等待）...', 'info', 5000);
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/optimize`, {}, 600000);
    if (result.status === 'ok') {
      const d = result.data;
      const score = d.score_after || 0;
      const done = d.done;
      showToast(
        done ? `✓ 优化完成！score ${score.toFixed(2)}，已达标` : `◐ 完成1轮，score ${score.toFixed(2)}`,
        done ? 'success' : 'info'
      );
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '优化失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error', 5000);
  }
}

// ============================================
// 后台任务轮询（feedback / optimize 通用）
// ============================================
function pollLifecycleTask(taskId, proposalId, onDone, onError) {
  const interval = 3000;
  const maxAttempts = 120; // 最多 6 分钟
  let attempts = 0;
  const timer = setInterval(async () => {
    attempts += 1;
    try {
      const status = await apiGet(`/api/task-status/${encodeURIComponent(taskId)}`);
      if (status.status === 'done') {
        clearInterval(timer);
        onDone(status.result);
      } else if (status.status === 'failed') {
        clearInterval(timer);
        onError(status.error || '后台任务失败');
      } else if (attempts >= maxAttempts) {
        clearInterval(timer);
        onError('处理时间较长，请稍后刷新页面查看结果');
      }
    } catch (e) {
      // 继续轮询，除非已超时
      if (attempts >= maxAttempts) {
        clearInterval(timer);
        onError('轮询任务状态失败：' + e.message);
      }
    }
  }, interval);
}

// ============================================
// 操作：通过（归档）
// ============================================
async function lcApprove(proposalId) {
  const comment = await promptModal('审核通过，请输入批准意见：', '思路清晰，同意归档');
  if (comment === null) return;

  try {
    showToast('归档中...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/feedback`, {
      feedback_text: comment,
      verdict: 'approve',
    });
    if (result.status === 'accepted' && result.task_id) {
      showToast('归档已提交，后台处理中...', 'info', 5000);
      pollLifecycleTask(result.task_id, proposalId, (res) => {
        if (res?.success) {
          showToast('✓ 已归档，已纳入知识库', 'success');
        } else {
          showToast('✗ 归档失败：' + (res?.error || '未知错误'), 'error');
        }
        renderLifecycleDashboard();
      }, (err) => {
        showToast('✗ ' + err, 'error');
        renderLifecycleDashboard();
      });
    } else if (result.status === 'ok') {
      showToast('✓ 已归档，已纳入知识库', 'success');
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '归档失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// 操作：退回修改（反馈）
// ============================================
async function lcFeedback(proposalId) {
  const feedback = await promptModal('请输入修改意见（writer 将整理为结构化意见后优化）：', '例如：Q1和Q2的逻辑关联需要加强...');
  if (feedback === null || !feedback.trim()) return;

  try {
    showToast('提交反馈中...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/feedback`, {
      feedback_text: feedback,
      verdict: 'major_revision',
    });
    if (result.status === 'accepted' && result.task_id) {
      showToast('反馈已提交，writer 正在结构化...', 'info', 5000);
      pollLifecycleTask(result.task_id, proposalId, (res) => {
        const sf = res?.structured_feedback;
        const issueCount = sf?.structured?.issues?.length || sf?.issues?.length || 0;
        showToast(`✓ 已退回优化（整理为 ${issueCount} 个 issue）`, 'success');
        renderLifecycleDashboard();
      }, (err) => {
        showToast('✗ ' + err, 'error');
        renderLifecycleDashboard();
      });
    } else if (result.status === 'ok') {
      const sf = result.data?.structured_feedback;
      const issueCount = sf?.structured?.issues?.length || sf?.issues?.length || 0;
      showToast(`✓ 已退回优化（整理为 ${issueCount} 个 issue）`, 'success');
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '反馈失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// v6.7.12: 操作：打开审核会话（分屏：左侧申请书 / 右侧讨论）
// ============================================
async function lcReview(proposalId) {
  try {
    showToast('创建审核会话...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/review-session`, {});
    if (result.status !== 'ok' || !result.session_id) {
      throw new Error(result.error || '创建审核会话失败');
    }
    showToast('✓ 审核会话已创建', 'success');
    await openReviewWorkspace(proposalId, result.session_id);
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// v6.7.12: 打开分屏审核工作区
let _reviewCurrentProposalId = null;
let _reviewCurrentSessionId = null;
let _reviewSections = {};

async function openReviewWorkspace(proposalId, sessionId) {
  _reviewCurrentProposalId = proposalId;
  _reviewCurrentSessionId = sessionId;

  // 展开聊天侧栏
  const chatSidebar = document.getElementById('chat-sidebar');
  if (chatSidebar) {
    chatSidebar.classList.remove('collapsed');
    localStorage.setItem('chat-collapsed', 'false');
  }

  // 切换到审核视图
  if (typeof switchToView === 'function') {
    switchToView('review');
  }

  // 加载会话到右侧讨论区
  if (typeof loadSession === 'function') {
    await loadSession(sessionId);
  } else if (typeof openChat === 'function') {
    openChat(sessionId);
  }

  // 加载左侧申请书内容
  await loadReviewContent(proposalId);

  // 绑定返回按钮
  const backBtn = document.getElementById('review-page-back-btn');
  if (backBtn) {
    backBtn.onclick = () => {
      _reviewCurrentProposalId = null;
      _reviewCurrentSessionId = null;
      _reviewSections = {};
      if (typeof switchToView === 'function') switchToView('lifecycle');
    };
  }
}

// v6.8.0: 加载申请书章节到左侧内容区（固定 5 模块，按顺序显示）
let _reviewDossier = null;      // v6.9.0 R1: 验收决策包
let _reviewActiveSection = null;

async function loadReviewContent(proposalId) {
  const bodyEl = document.getElementById('review-content-body');
  const tabsEl = document.getElementById('review-content-tabs');
  if (!bodyEl || !tabsEl) return;
  _reviewDossier = null;
  _reviewActiveSection = null;

  bodyEl.innerHTML = '<div class="ta-center pad-40 text-tertiary">加载申请书内容...</div>';
  tabsEl.innerHTML = '';

  // v6.9.0 R1: 先注入验收决策包（预审结论 + 可选一键采纳）
  renderReviewDossier(proposalId);

  try {
    const result = await apiGet(`/api/pipeline/${encodeURIComponent(proposalId)}/proposal/sections`);
    if (result.status !== 'ok') throw new Error(result.error || '获取申请书失败');

    const sections = result.sections || [];
    const rawMap = {};
    for (const s of sections) {
      if (s.name && s.content) rawMap[s.name] = s.content;
    }

    // v6.8.0: 只保留 5 模块，并按固定顺序排列
    const sectionOrder = ['立项依据', '研究内容', '研究方案', '整体一致性', '参考文献'];
    _reviewSections = {};
    for (const name of sectionOrder) {
      if (rawMap[name]) _reviewSections[name] = rawMap[name];
    }

    if (Object.keys(_reviewSections).length === 0) {
      bodyEl.innerHTML = '<div class="ta-center pad-40 text-tertiary">暂无申请书内容</div>';
      return;
    }

    // 渲染章节标签
    let first = true;
    for (const name of Object.keys(_reviewSections)) {
      const btn = document.createElement('button');
      btn.className = 'review-content-tab' + (first ? ' active' : '');
      btn.textContent = name;
      btn.onclick = () => {
        tabsEl.querySelectorAll('.review-content-tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        renderReviewSection(name);
      };
      tabsEl.appendChild(btn);
      if (first) renderReviewSection(name);
      first = false;
    }
  } catch (e) {
    bodyEl.innerHTML = `<div class="ta-center pad-40 text-error">加载失败：${escapeHtml(e.message)}</div>`;
  }
}

// v6.7.13: 轻量 Markdown 渲染（支持常用语法，不依赖外部库）
function renderMarkdown(text) {
  if (!text) return '';
  // 先整体 HTML 转义，再逐步替换为 HTML 标签
  let html = escapeHtml(text);

  // 1. 代码块 ```...```
  html = html.replace(/```([\s\S]*?)```/g, (_, code) => {
    return `<pre style="background:var(--bg-tertiary);padding:10px;border-radius:6px;overflow-x:auto;font-size:0.82rem;line-height:1.5;"><code>${code.replace(/^\n|\n$/g, '')}</code></pre>`;
  });

  // 2. 行内代码 `...`
  html = html.replace(/`([^`]+)`/g, '<code style="background:var(--bg-tertiary);padding:2px 4px;border-radius:4px;font-size:0.85em;">$1</code>');

  // 3. 标题 #..######
  html = html.replace(/^#{6}\s+(.*)$/gm, '<h6 style="margin:14px 0 6px;color:var(--text-primary);">$1</h6>');
  html = html.replace(/^#{5}\s+(.*)$/gm, '<h5 style="margin:14px 0 6px;color:var(--text-primary);">$1</h5>');
  html = html.replace(/^#{4}\s+(.*)$/gm, '<h4 style="margin:14px 0 6px;color:var(--text-primary);">$1</h4>');
  html = html.replace(/^#{3}\s+(.*)$/gm, '<h3 style="margin:16px 0 8px;color:var(--text-primary);">$1</h3>');
  html = html.replace(/^#{2}\s+(.*)$/gm, '<h2 style="margin:18px 0 10px;color:var(--text-primary);">$1</h2>');
  html = html.replace(/^#{1}\s+(.*)$/gm, '<h1 style="margin:20px 0 12px;color:var(--text-primary);">$1</h1>');

  // 4. 粗体、斜体
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

  // 5. 链接 [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" style="color:var(--accent-color);">$1</a>');

  // 6. 引用 >
  html = html.replace(/^&gt;\s+(.*)$/gm, '<blockquote style="border-left:3px solid var(--accent-color);padding-left:10px;margin:8px 0;color:var(--text-secondary);">$1</blockquote>');

  // 7. 分隔线 --- / *** / ___
  html = html.replace(/^(\s*[-*_]{3,}\s*)$/gm, '<hr style="border:none;border-top:1px solid var(--border-color);margin:16px 0;">');

  // 8. 列表：先按段落处理
  const paragraphs = html.split(/\n\n+/);
  const processed = paragraphs.map(p => {
    const lines = p.split('\n');
    if (lines.every(l => /^\s*[-*+]\s/.test(l))) {
      const items = lines.map(l => l.replace(/^\s*[-*+]\s+(.*)$/, '<li style="margin:4px 0;">$1</li>')).join('');
      return `<ul style="padding-left:1.5em;margin:8px 0;">${items}</ul>`;
    }
    if (lines.every(l => /^\s*\d+\.\s/.test(l))) {
      const items = lines.map(l => l.replace(/^\s*\d+\.\s+(.*)$/, '<li style="margin:4px 0;">$1</li>')).join('');
      return `<ol style="padding-left:1.5em;margin:8px 0;">${items}</ol>`;
    }
    // 普通段落：将内部单换行转成 <br>
    return `<p style="margin:0 0 0.8em 0;line-height:1.7;">${p.replace(/\n/g, '<br>')}</p>`;
  });

  return processed.join('\n');
}

// v6.9.0 R1: 决策包横幅 + 一键采纳预审（approve_lean 且分数达标时）
async function renderReviewDossier(proposalId) {
  try {
    const result = await apiGet(`/api/lifecycle/${encodeURIComponent(proposalId)}/dossier`);
    if (result.status === 'ok' && result.dossier) {
      _reviewDossier = result.dossier;
      // 章节已渲染时重渲染当前章节以刷新横幅
      if (_reviewActiveSection) renderReviewSection(_reviewActiveSection);
    }
  } catch (e) { /* 决策包缺失不影响人工审核 */ }
}

function reviewDossierBannerHtml() {
  if (!_reviewDossier) return '';
  const d = _reviewDossier;
  const labels = {
    approve_lean: ['建议通过', 'var(--success-color, #1dc981)'],
    attention: ['需人工裁量', 'var(--warning-color, #efaa17)'],
    reject_lean: ['建议退回', 'var(--error-color, #e5484d)'],
  };
  const [label, color] = labels[d.pre_review_verdict] || [d.pre_review_verdict || '未知', 'inherit'];
  const reasons = (d.pre_review_reasons || []).slice(0, 4)
    .map(r => `<div>· ${escapeHtml(String(r))}</div>`).join('');
  const score = d.last_score != null ? ` · 评分 ${Number(d.last_score).toFixed(2)}` : '';
  const adoptBtn = d.can_adopt
    ? '<button id="review-adopt-btn" class="btn btn-primary" style="margin-top:8px;">⚡ 一键采纳预审（通过并归档）</button>'
    : '';
  return `
    <div style="border:1px solid var(--border-color);border-left:3px solid ${color};border-radius:8px;padding:12px;margin-bottom:14px;background:var(--bg-secondary);">
      <div style="font-weight:600;margin-bottom:4px;">📋 验收决策包 · 系统预审：<span style="color:${color};">${escapeHtml(label)}</span>${escapeHtml(score)}</div>
      <div style="font-size:0.85rem;color:var(--text-secondary);">${reasons}</div>
      ${adoptBtn}
    </div>`;
}

function bindReviewAdopt() {
  const btn = document.getElementById('review-adopt-btn');
  if (!btn) return;
  btn.onclick = async () => {
    if (!window.confirm('采纳系统预审（approve_lean）并通过归档该课题？')) return;
    try {
      showToast('◐ 正在采纳预审…', 'info');
      const result = await apiPost(
        `/api/lifecycle/${encodeURIComponent(_reviewCurrentProposalId)}/review-adopt`,
        { session_id: _reviewCurrentSessionId }
      );
      if (result.status !== 'ok') throw new Error(result.error || '采纳失败');
      showToast('✓ 已采纳预审并归档', 'success');
      const back = document.getElementById('review-page-back-btn');
      if (back) back.click();
      else if (typeof switchToView === 'function') switchToView('lifecycle');
      if (typeof loadLifecycle === 'function') loadLifecycle();
    } catch (e) {
      showToast(`✗ ${e.message}`, 'error');
    }
  };
}

function renderReviewSection(name) {
  const bodyEl = document.getElementById('review-content-body');
  if (!bodyEl) return;
  _reviewActiveSection = name;
  const content = _reviewSections[name] || '（本章节暂无内容）';
  bodyEl.innerHTML = `${reviewDossierBannerHtml()}<div class="review-section-title" style="font-weight:600;margin-bottom:12px;color:var(--accent-color);">${escapeHtml(name)}</div><div>${renderMarkdown(content)}</div>`;
  bindReviewAdopt();
}

// ============================================
// v6.7.11: 操作：提交审核结论
// ============================================
async function lcReviewVerdict(proposalId, verdict, reason = '') {
  if (!['approve', 'reject', 'pause'].includes(verdict)) return;
  try {
    showToast('提交审核结论...', 'info');
    const payload = { verdict, reason };
    // v6.8.0: 传递当前审核会话 ID，便于后端归档会话
    if (_reviewCurrentSessionId && proposalId === _reviewCurrentProposalId) {
      payload.session_id = _reviewCurrentSessionId;
    }
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/review-verdict`, payload);
    if (result.status !== 'ok') {
      throw new Error(result.error || '审核结论提交失败');
    }
    const labels = { approve: '✓ 已通过并归档', reject: '↩ 已退回优化', pause: '⏸ 已暂停' };
    showToast(labels[verdict], 'success');
    // v6.8.0: 审核完成后切换回生命周期视图（会话归档由后端在 review-verdict 中处理）
    _reviewCurrentProposalId = null;
    _reviewCurrentSessionId = null;
    _reviewSections = {};
    if (typeof switchToView === 'function') switchToView('lifecycle');
    if (typeof renderLifecycleDashboard === 'function') renderLifecycleDashboard();
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// v6.8.0: 操作：根据对话整理审核意见
// ============================================
async function lcReviewFinalize(proposalId) {
  if (!proposalId || !_reviewCurrentSessionId) {
    showToast('未找到审核会话', 'error');
    return;
  }
  try {
    showToast('正在整理审核意见...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/review-finalize`, {
      session_id: _reviewCurrentSessionId,
    });
    if (result.status !== 'ok') {
      throw new Error(result.error || '整理意见失败');
    }
    const decision = result.decision || {};
    const verdict = decision.verdict || 'pause';
    const reason = decision.reason || '';
    const structured = decision.structured_feedback || {};
    const issues = structured.issues || [];

    let html = '<div class="d-flex fd-col gap-10" style="max-height:50vh;overflow:auto;">';
    html += `<div><strong>结论：</strong><span class="${verdict === 'approve' ? 'text-success' : verdict === 'reject' ? 'text-warning' : 'text-secondary'}">${verdict === 'approve' ? '通过' : verdict === 'reject' ? '退回修改' : '暂停'}</span></div>`;
    if (reason) html += `<div><strong>说明：</strong>${escapeHtml(reason)}</div>`;
    if (structured.overall_comment) html += `<div><strong>整体评价：</strong>${escapeHtml(structured.overall_comment)}</div>`;
    if (issues.length) {
      html += '<div><strong>结构化问题：</strong></div><ul>';
      for (const issue of issues.slice(0, 10)) {
        html += `<li><strong>[${escapeHtml(issue.section || '')}]</strong> ${escapeHtml(issue.description || '')}<br><em>指令：${escapeHtml(issue.instruction || '')}</em></li>`;
      }
      html += '</ul>';
    }
    html += '</div>';

    await confirmModal(html, '整理后的审核意见', '关闭');
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// 注册新课题
// ============================================
async function lcRegister() {
  const html = `
    <div class="d-flex fd-col gap-8 pad-12">
      <div>
        <label class="fs-082 fw-500 d-block mb-4">课题名称（英文缩写，基于科学问题）</label>
        <input id="lc-reg-name" class="w-100 pad-6-10 br-4 border-default bg-primary" 
               placeholder="如 quantum-geometry-inversion" style="font-size:0.85rem;">
        <div class="fs-072 text-tertiary mt-2">取自具体科学问题/核心方法，非研究领域</div>
      </div>
      <div>
        <label class="fs-082 fw-500 d-block mb-4">项目类型</label>
        <select id="lc-reg-type" class="w-100 pad-6-10 br-4 border-default bg-primary" style="font-size:0.85rem;">
          <option value="general">面上项目（general）</option>
          <option value="key">重点项目（key）</option>
          <option value="major">重大项目（major）</option>
        </select>
      </div>
      <div class="fs-072 text-tertiary pad-8 bg-tertiary br-4">
        将自动生成课题 ID：<code>{类型}-{名称}-{YYYYMMDD}</code>
      </div>
    </div>`;

  const confirmed = await confirmModal(html, '注册课题', '取消');
  if (!confirmed) return;

  const name = document.getElementById('lc-reg-name')?.value?.trim();
  const type = document.getElementById('lc-reg-type')?.value;

  if (!name) {
    showToast('请输入课题名称', 'warning');
    return;
  }

  try {
    showToast('注册中...', 'info');
    const result = await apiPost('/api/lifecycle/register', {
      proposal_id: '',  // 自动生成
      project_type: type,
      name: name,
      source: 'manual',
    });
    if (result.status === 'ok') {
      showToast(`✓ 已注册：${result.data?.proposal_id}`, 'success');
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '注册失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// v6.7.5: checkpoint / orchestrate / repair / jobs
// ============================================
async function lcToggleCheckpoints(proposalId) {
  const el = document.getElementById(`lc-checkpoints-${proposalId}`);
  if (!el) return;
  if (!el.classList.contains('d-none')) {
    el.classList.add('d-none');
    el.innerHTML = '';
    return;
  }
  el.classList.remove('d-none');
  el.innerHTML = '<div class="pad-8">加载 checkpoints...</div>';
  try {
    const result = await apiGet(`/api/lifecycle/checkpoints/${encodeURIComponent(proposalId)}`);
    if (result.status !== 'ok') throw new Error(result.error || '获取失败');
    const jobs = result.data || [];
    if (jobs.length === 0) {
      el.innerHTML = '<div class="pad-8">暂无 checkpoint</div>';
      return;
    }
    let html = '<div class="d-flex fd-col gap-4">';
    for (const job of jobs) {
      const statusMap = {
        pending: { icon: '○', color: 'var(--text-tertiary)' },
        running: { icon: '◐', color: 'var(--info-color)' },
        done: { icon: '✓', color: 'var(--success-color)' },
        failed: { icon: '✗', color: 'var(--error-color)' },
      };
      const s = statusMap[job.status] || statusMap.pending;
      html += `
        <div class="d-flex ai-center gap-8">
          <span style="color:${s.color};">${s.icon} ${job.step}</span>
          <span class="text-tertiary">r${job.round} · ${job.section_key}</span>
          <span class="ml-auto text-tertiary">${job.attempts || 0} 次</span>
        </div>`;
    }
    html += '</div>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = `<div class="pad-8 text-error">加载失败：${escapeHtml(e.message)}</div>`;
  }
}

async function lcOrchestrate() {
  try {
    showToast('每日编排已启动（后台执行）', 'info');
    const result = await apiPost('/api/lifecycle/orchestrate', {});
    if (result.status === 'accepted') {
      showToast(`✓ 编排任务已提交：${result.task_id}`, 'success');
    } else {
      throw new Error(result.error || '提交失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

async function lcRepair() {
  try {
    showToast('修复扫描已启动（后台执行）', 'info');
    const result = await apiPost('/api/lifecycle/repair', {});
    if (result.status === 'accepted') {
      showToast(`✓ 修复任务已提交：${result.task_id}`, 'success');
    } else {
      throw new Error(result.error || '提交失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

async function lcShowJobs() {
  try {
    const result = await apiGet('/api/lifecycle/jobs');
    if (result.status !== 'ok') throw new Error(result.error || '获取失败');
    const jobs = result.data || [];
    let html = `<div class="d-flex fd-col gap-4 fs-082" style="max-height:300px;overflow:auto;">`;
    if (jobs.length === 0) {
      html += '<div class="text-tertiary">暂无 lifecycle cron</div>';
    } else {
      for (const job of jobs) {
        html += `<div>${job.status === 'active' ? '🟢' : '⏸'} ${escapeHtml(job.name)} <span class="text-tertiary">${job.schedule}</span></div>`;
      }
    }
    html += '</div>';
    await confirmModal(html, 'Lifecycle Cron Jobs', '关闭');
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// v6.7.6: monitor 详情与负反馈告警
// ============================================
async function lcShowMonitor(proposalId) {
  try {
    const result = await apiGet(`/api/lifecycle/monitor/${encodeURIComponent(proposalId)}`);
    if (result.status !== 'ok') throw new Error(result.error || '获取失败');

    const alert = result.negative_feedback_alert;
    const reasons = result.negative_feedback_reasons || [];
    const history = result.monitor_history || [];

    let html = `<div class="d-flex fd-col gap-8 fs-082" style="max-height:400px;overflow:auto;">`;

    if (alert) {
      html += `
        <div class="pad-10 bg-error br-6" style="color:#fff;">
          <div class="fw-600 mb-4">⚠️ 负反馈告警</div>
          <ul class="ma-0 pl-16">
            ${reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
          </ul>
          <button class="btn-text mt-8" style="color:#fff;text-decoration:underline;" onclick="lcClearAlert('${proposalId}')">清除告警（需人工确认）</button>
        </div>`;
    }

    html += `<div class="fw-500">Monitor 历史（最近 ${history.length} 条）</div>`;
    if (history.length === 0) {
      html += '<div class="text-tertiary">暂无 monitor 记录</div>';
    } else {
      html += '<div class="d-flex fd-col gap-4">';
      for (const h of history.slice().reverse()) {
        const alertClass = h.negative_feedback ? 'text-error fw-600' : 'text-secondary';
        html += `
          <div class="pad-8 bg-tertiary br-4">
            <div class="d-flex ai-center gap-8 ${alertClass}">
              <span>r${h.round} · ${escapeHtml(h.section_key)}</span>
              <span class="ml-auto">monitor ${(h.monitor_independent_score || 0).toFixed(2)}</span>
            </div>
            <div class="fs-072 text-tertiary mt-2">
              writer Δ${h.writer_delta ?? 0} / critic Δ${h.critic_delta ?? 0}
              · 本地 w${h.local_writer_score ?? 100} / c${h.local_critic_score ?? 100}
              · 串通风险 ${h.collusion_risk || 'none'}
            </div>
            ${h.overall_assessment ? `<div class="fs-072 mt-2">${escapeHtml(h.overall_assessment)}</div>` : ''}
          </div>`;
      }
      html += '</div>';
    }

    html += '</div>';
    await confirmModal(html, `监察：${escapeHtml(proposalId)}`, '关闭');
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

async function lcClearAlert(proposalId) {
  const reason = await promptModal('请输入清除负反馈告警的原因（已确认问题已修复）：', '已人工检查，问题已修复');
  if (reason === null) return;

  try {
    showToast('清除告警中...', 'info');
    const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/clear-alert`, { reason });
    if (result.status === 'ok') {
      showToast('✓ 负反馈告警已清除', 'success');
      renderLifecycleDashboard();
    } else {
      throw new Error(result.error || '清除失败');
    }
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// ============================================
// 模块注册
// ============================================
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('lifecycle', () => {
    initLifecyclePage();
  });
}
