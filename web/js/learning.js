/**
 * learning.js — 学习管理器（学习日志、待审队列、统计面板）
 */

const LearningManager = { activeTab: 'learning-log' };

function openLearningManager() {
  if (!document.getElementById('learning-manager-overlay')) return;
  openModal('learning-manager-overlay');
  LearningManager.activeTab = 'learning-log';
  document.querySelectorAll('#learning-manager-overlay .kb-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === 'learning-log');
  });
  document.querySelectorAll('#learning-manager-overlay .kb-panel').forEach(p => {
    p.classList.toggle('active', p.id === 'kb-panel-learning-log');
  });
  renderLearningManager();
}

function closeLearningManager() {
  closeModal('learning-manager-overlay');
}

async function renderLearningManager() {
  const tab = LearningManager.activeTab;
  if (tab === 'learning-log') await loadLearningLog();
  else if (tab === 'learning-review') await loadLearningReview();
  else if (tab === 'learning-stats') await loadLearningStats();
}

function switchLearningTab(tab) {
  LearningManager.activeTab = tab;
  document.querySelectorAll('#learning-manager-overlay .kb-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  document.querySelectorAll('#learning-manager-overlay .kb-panel').forEach(p => {
    p.classList.toggle('active', p.id === `kb-panel-${tab}`);
  });
  renderLearningManager();
}

async function loadLearningLog() {
  const el = document.getElementById('learning-log-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/log');
    const log = (data && data.log) || [];
    if (!log.length) {
      el.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">暂无学习记录</p>';
      return;
    }
    el.innerHTML = log.slice(-20).reverse().map(item => {
      const time = (item.timestamp || item.time || '').slice(0, 16);
      const action = escapeHtml(item.action || item.type || '学习');
      const target = escapeHtml(item.target || item.title || item.concept || '');
      const status = item.success === false ? '⚠️' : '✓';
      return `<div style="padding:6px 0;border-bottom:1px solid var(--border-color);font-size:0.85rem;">
        ${status} <span style="color:var(--text-tertiary);">${time}</span> ${action} → <strong>${target}</strong>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}
  
  async function loadLearningReview() {
  const el = document.getElementById('learning-review-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/queue');
    const queue = (data && (data.queue || data.items)) || [];
    if (!queue.length) {
      el.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">无待审内容</p>';
      return;
    }
    el.innerHTML = queue.map(item => {
      const title = escapeHtml(item.title || item.concept || '未知');
      const stage = escapeHtml(item.growth_stage || '');
      return `<div style="padding:8px;margin:4px 0;background:var(--bg-secondary);border-radius:6px;">
        <div style="font-size:0.88rem;font-weight:500;">${title}</div>
        <div style="font-size:0.75rem;color:var(--text-tertiary);">${stage}</div>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// v3.5.1: 学习成本 SVG 趋势图
// 兼容两种数据格式：{date: number(cost)} 和 {date: {tokens, cost}}
function renderCostChart(container, costData) {
  if (!costData || !costData.daily) {
    container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">暂无成本数据</p>';
    return;
  }

  // 取最近14天数据
  const days = Object.keys(costData.daily).sort().slice(-14);
  if (days.length === 0) {
    container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">暂无成本数据</p>';
    return;
  }

  // 兼容两种数据格式：{date: number(cost)} 和 {date: {tokens, cost}}
  const getDayCost = (d) => {
    const v = costData.daily[d];
    if (typeof v === 'number') return v;
    return (v && v.cost) || 0;
  };
  const getDayTokens = (d) => {
    const v = costData.daily[d];
    if (typeof v === 'number') return 0;
    return (v && v.tokens) || 0;
  };

  // 优先用 tokens 作柱高，无 tokens 时用 cost(×1000) 作柱高
  const hasTokens = days.some(d => getDayTokens(d) > 0);
  const values = days.map(d => hasTokens ? getDayTokens(d) : getDayCost(d) * 1000);
  const maxVal = Math.max(...values, 1);
  const dailyBudget = costData.daily_budget || 0;
  const monthlyBudget = costData.monthly_budget || 0;

  // SVG 尺寸
  const W = 600, H = 180, padding = 40, barW = (W - padding * 2) / days.length;

  // 绘制柱状图
  let bars = '';
  days.forEach((day, i) => {
    const val = values[i];
    const barH = (val / maxVal) * (H - padding * 2);
    const x = padding + i * barW;
    const y = H - padding - barH;
    const isOverBudget = dailyBudget > 0 && getDayCost(day) > dailyBudget;
    const color = isOverBudget ? 'var(--error-color)' : 'var(--accent-color)';
    bars += `<rect x="${x + 2}" y="${y}" width="${barW - 4}" height="${barH}" fill="${color}" rx="2" opacity="0.8">
      <title>${day}: ${hasTokens ? getDayTokens(day) + ' tokens' : ''} $${getDayCost(day).toFixed(4)}</title>
    </rect>`;
    // X 轴标签（每隔几个显示一次）
    if (i % 3 === 0 || i === days.length - 1) {
      bars += `<text x="${x + barW/2}" y="${H - padding + 15}" fill="var(--text-tertiary)" font-size="10" text-anchor="middle">${day.slice(5)}</text>`;
    }
  });

  // 预算线
  let budgetLine = '';
  if (dailyBudget > 0) {
    const budgetVal = dailyBudget * 1000; // 假设 1000 tokens = $1
    const budgetY = H - padding - (Math.min(budgetVal, maxVal) / maxVal) * (H - padding * 2);
    budgetLine = `<line x1="${padding}" y1="${budgetY}" x2="${W - padding}" y2="${budgetY}" stroke="var(--warning-color)" stroke-width="1" stroke-dasharray="4,4">
      <title>日预算线</title>
    </line>
    <text x="${W - padding}" y="${budgetY - 5}" fill="var(--warning-color)" font-size="10" text-anchor="end">日预算 $${dailyBudget}</text>`;
  }

  // Y 轴
  const yLabels = [0, Math.round(maxVal * 0.5), maxVal].map((v, i) => {
    const y = H - padding - (v / maxVal) * (H - padding * 2);
    return `<text x="${padding - 8}" y="${y + 4}" fill="var(--text-tertiary)" font-size="10" text-anchor="end">${v > 1000 ? (v/1000).toFixed(1) + 'k' : v}</text>`;
  }).join('');

  // 月度汇总（兼容 number 和 object 格式）
  const monthKeys = Object.keys(costData.monthly || {}).sort();
  const currentMonth = monthKeys[monthKeys.length - 1];
  let monthSummary = '';
  if (currentMonth) {
    const mv = costData.monthly[currentMonth];
    const mTokens = typeof mv === 'number' ? 0 : (mv && mv.tokens) || 0;
    const mCost = typeof mv === 'number' ? mv : (mv && mv.cost) || 0;
    monthSummary = `${currentMonth}: ${mTokens} tokens / $${mCost.toFixed(4)}${monthlyBudget > 0 ? ' / $' + monthlyBudget : ''}`;
  }

  container.innerHTML = `
    <div style="margin-bottom:12px;">
      <h4 style="color:var(--text-primary);font-size:0.85rem;margin-bottom:4px;">Token 消耗趋势（最近14天）</h4>
      ${monthSummary ? `<p style="color:var(--text-secondary);font-size:0.75rem;">${monthSummary}</p>` : ''}
    </div>
    <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-secondary);">
      ${yLabels}
      <line x1="${padding}" y1="${H - padding}" x2="${W - padding}" y2="${H - padding}" stroke="var(--border-color)" stroke-width="1"/>
      ${bars}
      ${budgetLine}
    </svg>
  `;
}

async function loadLearningStats() {
  const el = document.getElementById('learning-stats-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/status');
    const stats = data || {};
    let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">';
    const fields = [
      ['自动学习', stats.auto_enabled ? '✓ 开启' : '○ 关闭'],
      ['总学习数', stats.total_learned || 0],
      ['今日学习', stats.today_count || 0],
      ['待审', stats.pending_count || 0],
      ['本月成本', `$${(stats.month_cost || 0).toFixed(4)}`],
      ['策略', escapeHtml(stats.strategy || 'balanced')],
    ];
    fields.forEach(([k, v]) => {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;">
        <div style="font-size:0.75rem;color:var(--text-tertiary);">${escapeHtml(k)}</div>
        <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${v}</div>
      </div>`;
    });
    html += '</div>';
    // v3.5.1: 成本趋势图容器
    html += '<div id="learning-cost-chart" style="margin-top:16px;"></div>';
    el.innerHTML = html;
    // v3.5.1: 渲染成本趋势图
    const chartContainer = document.getElementById('learning-cost-chart');
    if (chartContainer) {
      const costData = {
        daily: stats.cost_daily || {},
        monthly: stats.cost_monthly || {},
        daily_budget: stats.daily_budget || 0,
        monthly_budget: 0,
      };
      renderCostChart(chartContainer, costData);
    }
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// v3.5.1: 注册模块初始化
// learning.js 无独立 bind 函数，事件绑定在 app.js bindKbManagerEvents() 中完成
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('learning', () => {
    // 学习模块事件绑定由 app.js 统一处理，此处保留接口供未来迁移
  });
}
