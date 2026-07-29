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
 *   POST /api/lifecycle/cron-sweep         cron 扫描
 *   GET  /api/lifecycle/agent-scores       writer/critic 奖惩分数
 *   GET  /api/lifecycle/monitor/{id}       monitor 历史与负反馈状态
 *   POST /api/lifecycle/{id}/clear-alert   清除负反馈告警
 */

// ============================================
// 状态
// ============================================
let _lcCurrentFilter = 'all';  // 当前筛选的阶段

// 阶段配置
const LC_STAGES = [
  { key: 'drafts', label: '初稿', icon: '📝', color: 'var(--text-tertiary)', desc: '等待确认思路' },
  { key: 'optimizing', label: '优化中', icon: '🔄', color: 'var(--info-color)', desc: 'writer-critic 对抗' },
  { key: 'pending_review', label: '待校验', icon: '🔍', color: 'var(--warning-color)', desc: '等待人工核验' },
  { key: 'archived', label: '归档', icon: '📦', color: 'var(--success-color)', desc: '已通过·知识库' },
];

const LC_TYPE_LABELS = { general: '面上', key: '重点', major: '重大' };
const LC_TYPE_COLORS = { general: 'var(--info-color)', key: 'var(--accent-color)', major: 'var(--error-color)' };

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
async function renderLifecycleDashboard() {
  const container = document.getElementById('lifecycle-body');
  if (!container) return;

  container.innerHTML = '<div class="ta-center pad-40 text-tertiary">加载中...</div>';

  try {
    const data = await apiGet('/api/lifecycle/dashboard');
    if (data.status !== 'ok') throw new Error(data.error || '获取失败');
    const d = data.data;

    let html = '';
    html += '<div class="d-flex ai-center jc-between mb-12"><h2 style="margin:0;">🔬 提案生命周期</h2><button class="btn-text" style="color:var(--accent-color);" onclick="lcRegister()">+ 注册新课题</button></div>';

    // === 四阶段统计卡片 ===
    html += '<div class="d-grid gap-8 mb-12" style="grid-template-columns:repeat(4,1fr);">';
    for (const stage of LC_STAGES) {
      const count = d.by_status?.[stage.key] || 0;
      const active = _lcCurrentFilter === stage.key;
      html += `
        <div class="stat-card br-8 pad-12 cursor-pointer" 
             style="border-left:3px solid ${stage.color};${active ? 'background:var(--bg-active);' : ''}"
             onclick="lcFilterStage('${stage.key}')">
          <div class="fs-072 text-tertiary">${stage.icon} ${stage.label}</div>
          <div class="fs-1.4 fw-600" style="color:${count > 0 ? stage.color : 'var(--text-tertiary)'};">${count}</div>
          <div class="fs-072 text-tertiary">${stage.desc}</div>
        </div>`;
    }
    html += '</div>';

    // === 类型分布 + 总数 ===
    html += '<div class="d-flex ai-center gap-12 mb-8 fs-082 text-secondary">';
    html += `<span>总计 <strong>${d.total || 0}</strong> 个课题</span>`;
    html += '<span>·</span>';
    for (const [type, label] of Object.entries(LC_TYPE_LABELS)) {
      const count = d.by_type?.[type] || 0;
      if (count > 0) {
        html += `<span style="color:${LC_TYPE_COLORS[type]};">${label} ${count}</span>`;
      }
    }
    html += `<span class="ml-auto btn-text" onclick="lcFilterStage('all')" style="cursor:pointer;">显示全部</span>`;
    html += '</div>';

    // v6.7.5: cron 框架操作
    html += `<div class="d-flex gap-8 mb-12">`;
    html += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcOrchestrate()">🔄 手动编排</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcRepair()">🔧 手动修复</button>`;
    html += `<button class="btn-text fs-072" style="color:var(--text-secondary);" onclick="lcShowJobs()">📋 查看 cron</button>`;
    html += `</div>`;

    // v6.7.6: agent scores 概览（异步加载）
    html += `<div id="lc-agent-scores" class="mb-12 fs-082 text-secondary">加载对抗评审分数...</div>`;

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
    const dashData = await apiGet('/api/lifecycle/dashboard');
    const allProposals = dashData.data?.proposals || [];
    // 转换格式：dashboard 返回的是 {pid: {...}} 字典
    proposals = Object.entries(allProposals).map(([pid, data]) => ({
      proposal_id: pid,
      status: data.status,
      project_type: data.project_type || 'general',
      optimization_rounds: data.optimization_rounds || 0,
      last_score: data.last_score || 0,
      updated_at: data.updated_at || '',
    }));

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

    // 按更新时间排序
    proposals.sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''));

    let html = '<div class="d-flex fd-col gap-6">';
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

  // 解析课题名称（从 ID 提取）
  const namePart = (p.proposal_id || '').split('-').slice(1, -1).join('-') || p.proposal_id;

  let actions = '';
  // v6.7.8: 查看课题详情（申请书正文 + 反馈 + 操作）
  actions += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcViewDetail('${p.proposal_id}')">👁 查看详情</button>`;
  // v6.7.5: optimizing 状态可查看 checkpoints / monitor
  if (p.status === 'optimizing') {
    actions += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcToggleCheckpoints('${p.proposal_id}')">◐ checkpoints</button>`;
    actions += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcShowMonitor('${p.proposal_id}')">🔍 监察</button>`;
  }
  // 根据状态显示不同操作
  if (p.status === 'drafts') {
    actions += `<button class="btn-text fs-072" style="color:var(--info-color);" onclick="lcTransition('${p.proposal_id}','optimizing','确认思路可行')">→ 优化中</button>`;
  }
  if (p.status === 'optimizing') {
    actions += `<button class="btn-text fs-072" style="color:var(--accent-color);" onclick="lcOptimize('${p.proposal_id}')">⚡ 优化一轮</button>`;
    actions += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcTransition('${p.proposal_id}','pending_review','手动送审')">→ 送审</button>`;
  }
  if (p.status === 'pending_review') {
    actions += `<button class="btn-text fs-072" style="color:var(--success-color);" onclick="lcApprove('${p.proposal_id}')">✓ 通过</button>`;
    actions += `<button class="btn-text fs-072" style="color:var(--warning-color);" onclick="lcFeedback('${p.proposal_id}')">↩ 退回修改</button>`;
  }

  return `
    <div class="bg-secondary border-default br-8 pad-10" style="border-left:3px solid ${stage.color};">
      <div class="d-flex ai-center gap-8 mb-4">
        <span class="fs-082 fw-600">${escapeHtml(namePart)}</span>
        <span class="fs-072 pad-2-6 br-4" style="background:var(--bg-tertiary);color:${typeColor};">${typeLabel}</span>
        <span class="fs-072" style="color:${stage.color};">${stage.icon} ${stage.label}</span>
        ${score > 0 ? `<span class="fs-072 ml-auto" style="color:${scoreColor};">score ${score.toFixed(2)}</span>` : ''}
      </div>
      <div class="fs-072 text-tertiary mb-4">
        ${p.optimization_rounds || 0} 轮优化 · ${(p.updated_at || '').slice(0, 10)}
      </div>
      <div class="d-flex gap-6">
        ${actions}
      </div>
      <div id="lc-checkpoints-${p.proposal_id}" class="d-none mt-6 fs-072 text-secondary"></div>
    </div>`;
}

// ============================================
// v6.7.8: 查看课题详情（打开研究管线申请书面板）
// ============================================
function lcViewDetail(proposalId) {
  if (typeof openPipelineManager === 'function') {
    openPipelineManager(proposalId);
    // 切换到申请书标签页
    if (window.Pipeline && typeof window.Pipeline.switchTo === 'function') {
      setTimeout(() => window.Pipeline.switchTo('proposal'), 50);
    }
  } else {
    showToast('研究管线模块未加载', 'error');
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
    const result = await apiPost(`/api/lifecycle/${proposalId}/transition`, { to_stage: toStage, reason });
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
    const result = await apiPost(`/api/lifecycle/${proposalId}/optimize`, {}, 600000);
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
// 操作：通过（归档）
// ============================================
async function lcApprove(proposalId) {
  const comment = await promptModal('审核通过，请输入批准意见：', '思路清晰，同意归档');
  if (comment === null) return;

  try {
    showToast('归档中...', 'info');
    const result = await apiPost(`/api/lifecycle/${proposalId}/feedback`, {
      feedback_text: comment,
      verdict: 'approve',
    });
    if (result.status === 'ok') {
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
    const result = await apiPost(`/api/lifecycle/${proposalId}/feedback`, {
      feedback_text: feedback,
      verdict: 'major_revision',
    });
    if (result.status === 'ok') {
      const sf = result.data?.structured_feedback;
      const issueCount = sf?.issues?.length || 0;
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
    const result = await apiGet(`/api/lifecycle/checkpoints/${proposalId}`);
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
    const result = await apiGet(`/api/lifecycle/monitor/${proposalId}`);
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
    const result = await apiPost(`/api/lifecycle/${proposalId}/clear-alert`, { reason });
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
