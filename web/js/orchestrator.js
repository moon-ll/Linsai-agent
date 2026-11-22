/**
 * orchestrator.js — 林赛总控前端模块（v6.7）
 *
 * 4 个子面板：
 *   dashboard  — 总仪表盘（profile 健康 + 失败 + 策略 + 链路）
 *   profiles   — 7 个 profile 详细健康度
 *   failures   — 失败模式聚类 + 修正建议
 *   strategies — 调度策略建议 + 应用
 *   pipeline   — 链路质量监控
 *
 * 用法：
 *   openOrchestrator()           — 打开总控面板
 *   closeOrchestrator()          — 关闭面板
 *   Orchestrator.refresh()       — 刷新当前面板
 *
 * API 前缀：/api/orchestrator/
 */

(function() {
    'use strict';

    // ============================================
    // 状态
    // ============================================
    let orchState = {
        activeTab: 'dashboard',
        dashboard: null,
        profiles: null,
        failures: null,
        strategies: null,
        pipeline: null,
        lastRefresh: 0,
    };

    // ============================================
    // 工具
    // ============================================
    function $(id) { return document.getElementById(id); }

    function timeAgo(iso) {
        if (!iso) return '—';
        const t = new Date(iso).getTime();
        const diff = (Date.now() - t) / 1000;
        if (diff < 60) return Math.round(diff) + ' 秒前';
        if (diff < 3600) return Math.round(diff / 60) + ' 分钟前';
        if (diff < 86400) return Math.round(diff / 3600) + ' 小时前';
        return Math.round(diff / 86400) + ' 天前';
    }

    function statusColor(status) {
        switch (status) {
            case 'working': return '#5b9a5b';
            case 'idle': return '#5b9a8b';
            case 'degraded': return '#b08a3d'; // v6.8.54: 降级但存活（单次瞬时失败）
            case 'blocked': return '#c46b3d';
            case 'offline': return '#aa3a3a';
            default: return '#888';
        }
    }

    // ============================================
    // 主入口
    // ============================================
    async function openOrchestrator() {
        // 避免重复打开
        if ($('orchestrator-overlay')) {
            $('orchestrator-overlay').remove();
        }

        const overlay = document.createElement('div');
        overlay.id = 'orchestrator-overlay';
        overlay.className = 'modal-overlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9000;display:flex;align-items:center;justify-content:center;';

        overlay.innerHTML = `
            <div class="modal-content" style="width:90%;max-width:1200px;height:90%;max-height:800px;background:var(--bg2);border-radius:8px;display:flex;flex-direction:column;overflow:hidden;">
                <div class="modal-header" style="padding:16px 24px;border-bottom:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <h2 style="margin:0;">🎛️ 林赛总控台</h2>
                        <div style="font-size:0.8rem;color:var(--muted);margin-top:4px;">
                            跨 profile 监控 + 调度策略自调优 + 失败模式分析 + Pipeline 状态机成长
                        </div>
                    </div>
                    <div style="display:flex;gap:8px;">
                        <button id="orch-refresh-btn" class="btn-secondary">↻ 刷新</button>
                        <button id="orch-close-btn" class="btn-secondary">✕ 关闭</button>
                    </div>
                </div>
                <div class="orch-tabs" style="display:flex;border-bottom:1px solid var(--rule);background:var(--bg3);">
                    <button data-tab="dashboard" class="orch-tab orch-tab-active">📊 总仪表盘</button>
                    <button data-tab="profiles" class="orch-tab">👤 Profile 健康</button>
                    <button data-tab="failures" class="orch-tab">⚠️ 失败模式</button>
                    <button data-tab="strategies" class="orch-tab">⚙️ 调度策略</button>
                    <button data-tab="pipeline" class="orch-tab">🔗 链路质量</button>
                </div>
                <div id="orch-content" class="modal-body" style="flex:1;overflow:auto;padding:20px;">
                    <div style="text-align:center;color:var(--muted);padding:40px;">加载中…</div>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        // tab 切换
        overlay.querySelectorAll('.orch-tab').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                orchState.activeTab = tab;
                overlay.querySelectorAll('.orch-tab').forEach(b => b.classList.remove('orch-tab-active'));
                btn.classList.add('orch-tab-active');
                renderActiveTab();
            });
        });

        // 关闭 / 刷新
        $('orch-close-btn').addEventListener('click', closeOrchestrator);
        $('orch-refresh-btn').addEventListener('click', () => refresh(true));

        await refresh(false);
    }

    function closeOrchestrator() {
        const overlay = $('orchestrator-overlay');
        if (overlay) overlay.remove();
    }

    async function refresh(force) {
        const now = Date.now();
        if (!force && (now - orchState.lastRefresh) < 10000) return;
        orchState.lastRefresh = now;

        try {
            const r = await fetch('/api/orchestrator/dashboard?window_hours=24');
            if (!r.ok) throw new Error('HTTP ' + r.status);
            orchState.dashboard = await r.json();

            const r2 = await fetch('/api/orchestrator/strategies?window_hours=168');
            if (r2.ok) orchState.strategies = await r2.json();

            const r3 = await fetch('/api/orchestrator/failures/patterns?window_hours=168');
            if (r3.ok) orchState.failures = await r3.json();

            const r4 = await fetch('/api/orchestrator/pipeline/quality');
            if (r4.ok) orchState.pipeline = await r4.json();

            renderActiveTab();
        } catch (e) {
            $('orch-content').innerHTML = `<div style="text-align:center;color:#aa3a3a;padding:40px;">加载失败：${e.message}</div>`;
        }
    }

    function renderActiveTab() {
        const tab = orchState.activeTab;
        if (tab === 'dashboard') renderDashboard();
        else if (tab === 'profiles') renderProfiles();
        else if (tab === 'failures') renderFailures();
        else if (tab === 'strategies') renderStrategies();
        else if (tab === 'pipeline') renderPipeline();
    }

    // ============================================
    // 渲染：总仪表盘
    // ============================================
    function renderDashboard() {
        const d = orchState.dashboard;
        if (!d) return;
        const profiles = d.profiles?.profiles || {};
        const failures = d.failures || {};
        const strategies = d.strategies || {};
        const pipeline = d.pipeline_quality || {};

        let html = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="orch-card">
                <h3>👤 Profile 健康度</h3>
                <div class="orch-mini-list">
                    ${Object.entries(profiles).map(([name, h]) => `
                        <div class="orch-mini-row">
                            <span class="orch-dot" style="background:${statusColor(h.status)}"></span>
                            <span class="orch-mini-name">${name}</span>
                            <span class="orch-mini-val">${h.success_rate_24h !== null ? (h.success_rate_24h * 100).toFixed(0) + '%' : '—'}</span>
                        </div>
                    `).join('')}
                </div>
                <div style="font-size:0.8rem;color:var(--muted);margin-top:8px;">窗口 24h</div>
            </div>
            <div class="orch-card">
                <h3>⚠️ 失败模式 Top</h3>
                <div class="orch-mini-list">
                    ${(failures.patterns || []).slice(0, 5).map(p => `
                        <div class="orch-mini-row">
                            <span class="orch-mini-name">${escapeHtml(p.label)}</span>
                            <span class="orch-mini-val" style="color:#c46b3d;">${p.occurrences}</span>
                        </div>
                    `).join('') || '<div style="color:var(--muted);padding:8px;">无失败</div>'}
                </div>
                <div style="font-size:0.8rem;color:var(--muted);margin-top:8px;">${failures.summary?.total_errors || 0} 错误 / ${failures.summary?.total_warnings || 0} 警告</div>
            </div>
            <div class="orch-card">
                <h3>⚙️ 策略建议</h3>
                <div style="font-size:0.85rem;color:var(--muted);margin-bottom:8px;">风险：<span style="color:${strategies.risk === 'high' ? '#aa3a3a' : strategies.risk === 'medium' ? '#c46b3d' : '#5b9a5b'};">${strategies.risk}</span></div>
                <div class="orch-mini-list">
                    ${(strategies.reasons || []).slice(0, 3).map(r => `
                        <div style="font-size:0.82rem;padding:4px 0;border-bottom:1px dashed var(--rule);">${escapeHtml(r)}</div>
                    `).join('') || '<div style="color:var(--muted);padding:8px;">当前策略合理，无需调整</div>'}
                </div>
            </div>
            <div class="orch-card">
                <h3>🔗 Pipeline 质量</h3>
                <div class="orch-mini-list">
                    ${(pipeline.proposals || []).slice(0, 5).map(p => `
                        <div class="orch-mini-row">
                            <span class="orch-mini-name">${escapeHtml(p.proposal_id.slice(0, 40))}</span>
                            <span class="orch-mini-val">${(p.overall_quality * 100).toFixed(0)}%</span>
                        </div>
                    `).join('') || '<div style="color:var(--muted);padding:8px;">无活跃 proposal</div>'}
                </div>
                <div style="font-size:0.8rem;color:var(--muted);margin-top:8px;">${pipeline.growth_actions_total || 0} 项成长建议</div>
            </div>
        </div>
        <div style="margin-top:16px;color:var(--muted);font-size:0.8rem;">计算于 ${timeAgo(d.computed_at)}</div>
        `;
        $('orch-content').innerHTML = html;
    }

    // ============================================
    // 渲染：Profile 健康
    // ============================================
    function renderProfiles() {
        const profiles = orchState.dashboard?.profiles?.profiles || {};
        let html = `<h3>7 个 Profile 详细健康度</h3>
        <table class="orch-table">
            <thead>
                <tr>
                    <th>Profile</th><th>状态</th><th>成功率 24h</th><th>派活数</th><th>平均耗时</th><th>最近错误</th><th>建议</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(profiles).map(([name, h]) => `
                    <tr>
                        <td><strong>${name}</strong></td>
                        <td><span class="orch-dot" style="background:${statusColor(h.status)}"></span> ${h.status}</td>
                        <td>${h.success_rate_24h !== null ? (h.success_rate_24h * 100).toFixed(0) + '%' : '—'}</td>
                        <td>${h.dispatch_count_24h}</td>
                        <td>${h.avg_duration_s ? h.avg_duration_s + 's' : '—'}</td>
                        <td style="font-size:0.78rem;color:var(--muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(h.recent_error || '')}">${escapeHtml(h.recent_error || '—')}</td>
                        <td style="font-size:0.82rem;">${escapeHtml(h.suggestion || '—')}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>`;
        $('orch-content').innerHTML = html;
    }

    // ============================================
    // 渲染：失败模式
    // ============================================
    function renderFailures() {
        const failures = orchState.failures || {};
        let html = `<h3>失败模式聚类 + 修正建议</h3>
        <div style="margin-bottom:12px;color:var(--muted);">
            窗口 168h（7 天） · 错误 ${failures.summary?.total_errors || 0} · 警告 ${failures.summary?.total_warnings || 0}
        </div>
        ${(failures.patterns || []).map(p => `
            <div class="orch-card" style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <strong>${escapeHtml(p.label)}</strong>
                        <span style="color:var(--muted);font-size:0.8rem;margin-left:8px;">${escapeHtml(p.category)}</span>
                    </div>
                    <div style="background:${p.occurrences > 5 ? '#c46b3d' : '#5b9a5b'};color:white;padding:2px 10px;border-radius:12px;font-size:0.85rem;">
                        ${p.occurrences} 次
                    </div>
                </div>
                <div style="margin-top:10px;padding:10px;background:var(--bg3);border-radius:6px;font-size:0.85rem;">
                    <div style="color:var(--accent);font-weight:600;margin-bottom:4px;">💡 建议修改：</div>
                    <div style="line-height:1.6;">${escapeHtml(p.suggested_prompt_change)}</div>
                </div>
                <div style="margin-top:6px;font-size:0.78rem;color:var(--muted);">
                    预期效果：${escapeHtml(p.expected_impact)}
                </div>
                ${p.sample_errors && p.sample_errors.length ? `
                    <details style="margin-top:8px;">
                        <summary style="cursor:pointer;color:var(--muted);font-size:0.8rem;">样本错误 (${p.sample_errors.length})</summary>
                        <pre style="background:var(--bg);padding:8px;border-radius:4px;font-size:0.75rem;margin-top:6px;overflow:auto;max-height:150px;">${escapeHtml(p.sample_errors.join('\n'))}</pre>
                    </details>
                ` : ''}
            </div>
        `).join('') || '<div style="color:var(--muted);padding:40px;text-align:center;">✓ 7 天内无失败模式</div>'}`;
        $('orch-content').innerHTML = html;
    }

    // ============================================
    // 渲染：调度策略
    // ============================================
    function renderStrategies() {
        const s = orchState.strategies || {};
        const cur = s.current || {};
        const sug = s.suggested || {};
        const changed = Object.keys(sug).filter(k => cur[k] !== sug[k]);

        let html = `<h3>调度策略建议（建议模式，需人工确认）</h3>
        <div style="margin-bottom:12px;">
            风险：<span style="color:${s.risk === 'high' ? '#aa3a3a' : s.risk === 'medium' ? '#c46b3d' : '#5b9a5b'};font-weight:600;">${s.risk}</span>
            · 基于 ${s.activity?.days || 0} 天活动数据
        </div>

        <table class="orch-table">
            <thead>
                <tr><th>参数</th><th>当前</th><th>建议</th><th>变化</th></tr>
            </thead>
            <tbody>
                ${Object.keys(cur).map(k => {
                    const changedNow = cur[k] !== sug[k];
                    return `<tr ${changedNow ? 'style="background:rgba(196,107,61,0.1);"' : ''}>
                        <td><strong>${k}</strong></td>
                        <td>${cur[k]}</td>
                        <td>${sug[k] !== undefined ? sug[k] : cur[k]}${changedNow ? ' <span style="color:#c46b3d;font-weight:600;">←</span>' : ''}</td>
                        <td>${changedNow ? (typeof cur[k] === 'number' ? (sug[k] - cur[k] > 0 ? '+' : '') + (sug[k] - cur[k]) : '修改') : '—'}</td>
                    </tr>`;
                }).join('')}
            </tbody>
        </table>

        <div style="margin-top:16px;">
            <h4>调整理由</h4>
            ${(s.reasons || []).length ? `
                <ul style="line-height:1.7;">
                    ${s.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            ` : '<div style="color:var(--muted);">当前参数合理，无需调整</div>'}
        </div>

        <div style="margin-top:16px;">
            <h4>活动统计</h4>
            <div style="font-size:0.85rem;line-height:1.7;color:var(--muted);">
                平均派活：${s.activity?.avg_dispatch_per_day || 0} 次/天 ·
                平均耗时：${s.activity?.avg_duration_s || 0}s ·
                成功率：${s.activity?.success_rate !== null && s.activity?.success_rate !== undefined ? (s.activity.success_rate * 100).toFixed(0) + '%' : '—'} ·
                超时：${s.activity?.total_timeout || 0} 次
            </div>
        </div>

        <div style="margin-top:16px;">
            <h4>评分分布</h4>
            <div style="font-size:0.85rem;line-height:1.7;color:var(--muted);">
                平均：${s.score_stats?.avg_score || 0} ·
                最高：${s.score_stats?.max_score || 0} ·
                通过率：${s.score_stats?.pass_rate !== undefined ? (s.score_stats.pass_rate * 100).toFixed(0) + '%' : '—'} ·
                样本：${s.score_stats?.samples || 0}
            </div>
        </div>

        ${changed.length ? `
            <div style="margin-top:24px;padding:16px;background:var(--bg3);border-radius:8px;">
                <div style="margin-bottom:12px;color:var(--muted);font-size:0.85rem;">
                    ⚠️ 建议仅推荐，应用需人工确认
                </div>
                <button id="orch-apply-btn" class="btn-primary">应用建议</button>
                <button id="orch-skip-btn" class="btn-secondary" style="margin-left:8px;">暂不调整</button>
            </div>
        ` : ''}
        `;
        $('orch-content').innerHTML = html;

        const applyBtn = $('orch-apply-btn');
        if (applyBtn) {
            applyBtn.addEventListener('click', async () => {
                if (!confirm('确认应用建议策略？')) return;
                try {
                    const r = await fetch('/api/orchestrator/strategies/apply', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ strategies: sug, confirmed_by: 'web_user' }),
                    });
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    const result = await r.json();
                    showToast('已应用策略：' + JSON.stringify(result.applied), 'success');
                    refresh(true);
                } catch (e) {
                    showToast('应用失败：' + e.message, 'error');
                }
            });
        }
    }

    // ============================================
    // 渲染：Pipeline 质量
    // ============================================
    function renderPipeline() {
        const p = orchState.pipeline || {};
        let html = `<h3>Pipeline 状态机质量监控</h3>
        <div style="margin-bottom:12px;color:var(--muted);">
            监控 ${(p.proposals || []).length} 个 proposal · ${p.growth_actions_total || 0} 项成长建议
        </div>
        ${(p.proposals || []).map(prop => `
            <div class="orch-card" style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <strong>${escapeHtml(prop.proposal_id)}</strong>
                    <div>
                        整体质量：<span style="color:${prop.overall_quality > 0.7 ? '#5b9a5b' : prop.overall_quality > 0.4 ? '#c46b3d' : '#aa3a3a'};font-weight:600;">${(prop.overall_quality * 100).toFixed(0)}%</span>
                        ${prop.growth_actions.length ? `<span style="background:#c46b3d;color:white;padding:2px 8px;border-radius:8px;margin-left:8px;font-size:0.8rem;">${prop.growth_actions.length} 项成长</span>` : ''}
                    </div>
                </div>
                <div style="margin-top:10px;display:grid;grid-template-columns:repeat(6,1fr);gap:6px;">
                    ${prop.stages.map(s => `
                        <div class="orch-stage" style="padding:8px;background:${s.score > 0.7 ? 'rgba(91,154,91,0.15)' : s.score > 0.4 ? 'rgba(196,107,61,0.15)' : s.exists ? 'rgba(170,58,58,0.15)' : 'var(--bg3)'};border-radius:4px;text-align:center;">
                            <div style="font-size:0.7rem;color:var(--muted);">${s.label}</div>
                            <div style="font-size:0.9rem;font-weight:600;">${(s.score * 100).toFixed(0)}%</div>
                            <div style="font-size:0.65rem;color:var(--muted);">${s.size}B</div>
                        </div>
                    `).join('')}
                </div>
                ${prop.growth_actions.length ? `
                    <div style="margin-top:10px;font-size:0.85rem;">
                        <strong style="color:#c46b3d;">成长建议：</strong>
                        <ul style="margin-top:4px;">
                            ${prop.growth_actions.map(a => `<li>${escapeHtml(a.label)}: ${escapeHtml(a.reason)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `).join('') || '<div style="color:var(--muted);padding:40px;text-align:center;">无活跃 proposal</div>'}`;
        $('orch-content').innerHTML = html;
    }

    // ============================================
    // 暴露到全局
    // ============================================
    window.Orchestrator = { open: openOrchestrator, close: closeOrchestrator, refresh };

})();
