/**
 * workbench.js — v8.0.0 课题工作台
 * 自动化产出课题启动包，人负责法定节点：启动 / 否决 / 归档。
 * 四列看板（questions/kickoff/ready/active）+ archive 折叠 + 启动包详情抽屉。
 * 依赖 core.js 的 apiGet / apiPost / escapeHtml（与 dashboard/lifecycle 同惯例）。
 */

const WB_STAGES = [
  { key: 'questions', icon: '💡', color: 'var(--info-color)' },
  { key: 'kickoff', icon: '🔬', color: 'var(--accent-color)' },
  { key: 'ready', icon: '📦', color: 'var(--warning-color)' },
  { key: 'active', icon: '🚀', color: 'var(--success-color)' },
];

async function renderWorkbench() {
  const container = document.getElementById('workbench-page');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary);">◐ 加载中…</div>';
  try {
    const data = await apiGet('/api/topics');
    if (!data.success) throw new Error(data.error || '加载失败');
    container.innerHTML = _wbRenderBoard(data);
    _wbBindActions();
  } catch (e) {
    container.innerHTML = `<div style="padding:40px;color:var(--error-color);">✗ 课题工作台加载失败：${escapeHtml(String(e.message || e))}</div>`;
  }
}

function _wbRenderBoard(data) {
  const stages = data.stages || {};
  const needs = data.needs_human || [];
  let html = `<div class="dash-greeting"><div class="dash-greeting-text">🧪 课题工作台</div>
    <div class="dash-greeting-sub">自动化到 ready 为止——启动与否由你决定。${needs.length ? `<strong style="color:var(--warning-color);">${needs.length} 个课题等待你裁决</strong>` : '当前无需人工干预。'}</div></div>`;

  // 深研 worker 状态 + 手动触发
  html += `<div style="display:flex;gap:8px;margin:8px 0 16px;flex-wrap:wrap;">
    <button class="btn-text" id="wb-daily-btn" title="对队首问题候选执行单遍深研（耗时数分钟，后台执行）">▶ 手动触发深研</button>
    <span id="wb-daily-status" style="font-size:.8rem;color:var(--text-tertiary);align-self:center;"></span>
  </div>`;

  // 四列看板
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;">';
  for (const st of WB_STAGES) {
    const s = stages[st.key] || { label: st.key, count: 0, items: [] };
    html += `<div style="background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:10px;padding:12px;min-height:160px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-weight:600;">${st.icon} ${escapeHtml(s.label)}</span>
        <span style="color:${st.color};font-size:.85rem;">${s.count}</span>
      </div>
      ${s.items.length === 0
        ? '<div style="color:var(--text-tertiary);font-size:.8rem;padding:8px 0;">（空）</div>'
        : s.items.map(t => _wbTopicCard(t)).join('')}
    </div>`;
  }
  html += '</div>';

  // archive 折叠区
  const arch = stages.archive || { label: 'archive', count: 0, items: [] };
  if (arch.count > 0) {
    html += `<details style="margin-top:16px;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:10px;padding:12px;">
      <summary style="cursor:pointer;font-weight:600;">📦 已归档（${arch.count}）</summary>
      <div style="margin-top:8px;">${arch.items.map(t => _wbTopicCard(t)).join('')}</div>
    </details>`;
  }
  if (data.rejected_count > 0) {
    html += `<div style="margin-top:8px;font-size:.78rem;color:var(--text-tertiary);">另有否决台账 ${data.rejected_count} 条（_rejected-questions/）</div>`;
  }
  html += `<div id="wb-detail" style="display:none;margin-top:16px;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:10px;padding:16px;"></div>`;
  return html;
}

function _wbTopicCard(t) {
  const warn = t.needs_human ? ' <span style="color:var(--warning-color);">⚠等人</span>' : '';
  const gaps = (t.gaps && t.gaps.length) ? `<div style="font-size:.72rem;color:var(--text-tertiary);margin-top:2px;">◐ ${escapeHtml(t.gaps.slice(0, 2).join('；'))}</div>` : '';
  return `<div class="wb-topic-card" data-id="${escapeAttr(t.id)}" style="background:var(--bg-tertiary);border-radius:8px;padding:8px 10px;margin-bottom:6px;cursor:pointer;">
    <div style="font-size:.85rem;font-weight:500;">${escapeHtml(t.title || t.id)}${warn}</div>
    ${t.problem ? `<div style="font-size:.75rem;color:var(--text-tertiary);margin-top:2px;">${escapeHtml(t.problem)}</div>` : ''}
    ${gaps}
  </div>`;
}

function _wbBindActions() {
  document.querySelectorAll('.wb-topic-card').forEach(el => {
    el.addEventListener('click', () => _wbShowDetail(el.dataset.id));
  });
  const dailyBtn = document.getElementById('wb-daily-btn');
  if (dailyBtn) dailyBtn.addEventListener('click', _wbTriggerDaily);
  _wbPollDailyStatus();
}

async function _wbShowDetail(tid) {
  const box = document.getElementById('wb-detail');
  if (!box) return;
  box.style.display = 'block';
  box.innerHTML = '<div style="color:var(--text-tertiary);">◐ 加载启动包…</div>';
  try {
    const d = await apiGet('/api/topics/' + encodeURIComponent(tid));
    if (!d.success) throw new Error(d.error || '加载失败');
    const rec = d.record || {};
    const check = d.check || {};
    const verdict = check.results || [];
    const stage = d.stage || '';
    let html = `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
      <div>
        <div style="font-size:1.05rem;font-weight:600;">${escapeHtml(rec.title || tid)}</div>
        <div style="font-size:.78rem;color:var(--text-tertiary);margin-top:2px;">
          ${escapeHtml(tid)} · 阶段 ${escapeHtml(stage)} · 来源 ${escapeHtml((d.card && d.card.source) || '-')}
          ${rec.migrated_from ? ' · 迁移自 v7' : ''}
        </div>
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;">
        <button class="btn-text" data-wb-act="check" data-id="${escapeAttr(tid)}">🔎 验收自检</button>
        ${stage === 'ready' || stage === 'kickoff' || stage === 'questions'
          ? `<button class="btn-text" data-wb-act="activate" data-id="${escapeAttr(tid)}" style="color:var(--success-color);">🚀 启动</button>` : ''}
        ${stage === 'questions'
          ? `<button class="btn-text" data-wb-act="reject" data-id="${escapeAttr(tid)}" style="color:var(--error-color);">✗ 否决</button>` : ''}
        ${stage === 'active'
          ? `<button class="btn-text" data-wb-act="archive" data-id="${escapeAttr(tid)}">📦 归档</button>` : ''}
        <button class="btn-text" data-wb-act="close">收起</button>
      </div>
    </div>`;

    // 自检结果
    if (verdict.length) {
      html += `<div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;">` + verdict.map(r =>
        `<span style="font-size:.75rem;padding:3px 8px;border-radius:6px;background:${r.passed ? 'var(--bg-tertiary)' : 'rgba(255,120,80,.15)'};color:${r.passed ? 'var(--success-color)' : 'var(--error-color)'};">
          ${r.passed ? '✓' : '✗'} ${escapeHtml(r.code)} ${escapeHtml(r.name)}</span>`).join('') + `</div>`;
      if (check.gaps && check.gaps.length) {
        html += `<div style="font-size:.78rem;color:var(--warning-color);margin-bottom:8px;">缺口：${escapeHtml(check.gaps.join('；'))}</div>`;
      }
    }
    if (rec.needs_human) {
      html += `<div style="font-size:.8rem;color:var(--warning-color);margin-bottom:8px;">⚠ 多次补齐未果，等待人工裁决。</div>`;
    }

    // 报告正文（等宽渲染为 pre-wrap 文本，保持简洁）
    if (d.report) {
      html += `<div style="white-space:pre-wrap;font-size:.82rem;line-height:1.6;color:var(--text-secondary);max-height:420px;overflow-y:auto;border-top:1px solid var(--border-color);padding-top:10px;">${escapeHtml(d.report.slice(0, 12000))}${d.report.length > 12000 ? '\n…（节选，全文见课题目录）' : ''}</div>`;
      html += `<div style="font-size:.72rem;color:var(--text-tertiary);margin-top:6px;">报告 ${d.report_chars} 字符 · 目录 ${escapeHtml(d.dir)}</div>`;
    } else {
      html += `<div style="font-size:.8rem;color:var(--text-tertiary);margin-top:10px;">○ 尚无课题报告（深研完成后自动组装）。</div>`;
    }
    box.innerHTML = html;
    box.querySelectorAll('[data-wb-act]').forEach(btn => {
      btn.addEventListener('click', () => _wbAction(btn.dataset.wbAct, btn.dataset.id));
    });
  } catch (e) {
    box.innerHTML = `<div style="color:var(--error-color);">✗ ${escapeHtml(String(e.message || e))}</div>`;
  }
}

async function _wbAction(act, tid) {
  if (act === 'close') {
    document.getElementById('wb-detail').style.display = 'none';
    return;
  }
  let body = {};
  if (act === 'reject') {
    const reason = prompt('否决理由（进台账防重复立项）：');
    if (!reason) return;
    body = { reason };
  }
  if (act === 'activate' && !confirm('确认启动该课题进入正式研究？')) return;
  try {
    const res = await apiPost('/api/topics/' + encodeURIComponent(tid) + '/' + act, body);
    if (!res.success) throw new Error(res.error || '操作失败');
    renderWorkbench();
  } catch (e) {
    alert('操作失败：' + (e.message || e));
  }
}

async function _wbTriggerDaily() {
  const statusEl = document.getElementById('wb-daily-status');
  try {
    const res = await apiPost('/api/topics/daily', {});
    if (!res.success) throw new Error(res.error || '触发失败');
    if (statusEl) statusEl.textContent = '◐ 深研 worker 已后台启动…';
  } catch (e) {
    if (statusEl) statusEl.textContent = '✗ ' + (e.message || e);
  }
}

function _wbPollDailyStatus() {
  const statusEl = document.getElementById('wb-daily-status');
  if (!statusEl) return;
  apiGet('/api/topics/daily/status').then(d => {
    if (d.running) {
      statusEl.textContent = '◐ 深研 worker 运行中（' + (d.started_at || '') + ' 启动）…';
      setTimeout(_wbPollDailyStatus, 15000);
    } else if (d.result) {
      statusEl.textContent = '✓ 上次深研：' + (d.result.summary || d.result.skipped || '完成');
    } else if (d.error) {
      statusEl.textContent = '✗ 上次失败：' + d.error;
    }
  }).catch(() => {});
}
