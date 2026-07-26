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
  openModal('lifecycle-overlay');
  renderLifecycleDashboard();
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

    container.innerHTML = html;

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
    </div>`;
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
// 模块注册
// ============================================
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('lifecycle', () => {
    // 关闭按钮
    const closeBtn = document.getElementById('lifecycle-close');
    if (closeBtn) closeBtn.addEventListener('click', () => closeModal('lifecycle-overlay'));
    // 注册按钮
    const regBtn = document.getElementById('lifecycle-register-btn');
    if (regBtn) regBtn.addEventListener('click', () => lcRegister());
  });
}
