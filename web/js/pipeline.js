/**
 * pipeline.js — 研究管线前端模块（v6.1.0）
 * 零框架依赖，原生 JavaScript，复用 core.js 的 apiGet/apiPost/apiPut/apiDelete/
 * escapeHtml/escapeAttr/renderMarkdown/showToast/openModal/closeModal/confirmModal/promptModal/showModal。
 *
 * 用法：
 *   openPipelineManager()        — 打开研究管线面板（默认总览）
 *   closePipelineManager()       — 关闭面板
 *   Pipeline.switchTo(tabName)   — 切换到指定子面板
 *   Pipeline.setProposal(pid)    — 设置当前 proposal
 *   Pipeline.refresh()           — 刷新当前视图
 *
 * API 前缀：/api/pipeline/
 *
 * 九个子面板：
 *   overview    — 管线总览（六阶段进度 + 门禁 + 操作）
 *   gap         — 空白分析（覆盖率图 + 空白列表）
 *   topics      — 课题候选（卡片 + 评分 + 选定/精炼）
 *   questions   — 问题框架（五要素手风琴 + 问题树）
 *   proposal    — 申请书撰写（章节标签 + Markdown 编辑）
 *   methodology — 方法学手册（方法列表 + 详情 + 生成/导出）
 *   inspection  — 自检优化（六维评分 + 问题列表 + 迭代历史）
 *   citations   — 文献引用（引用列表 + 统计 + 导出）
 *   agents      — 智能体团队（三层结构 + 成员卡片 + 任务分配）
 */

(function() {
    'use strict';

    // ============================================
    // 状态
    // ============================================
    let currentProposalId = null;
    let pipelineState = null;
    let activeTab = 'overview';
    let isLoading = false;

    // 子面板内嵌状态
    let gapReport = null;
    let topicsList = [];
    let questionFramework = null;
    let proposalSections = [];
    let inspectionReport = null;
    let citationsList = [];
    let proposalSectionTab = '立项依据';

    // 方法学手册状态（按 proposal_id 缓存）
    let methodologyData = null;
    let methodologyStats = null;
    let methodologySelectedMethod = null;

    // 智能体团队状态（全局，不依赖 proposal_id）
    let agentTeamData = null;
    let agentOverviewStats = null;

    // ============================================
    // 常量
    // ============================================

    // 六阶段管线（与 pipeline_orchestrator.py STAGES 一致）
    const STAGE_NAMES = [
        '方向校准',
        '文献调研',
        '课题凝练',
        '科学问题构建',
        '申请书撰写',
        '自检优化',
    ];

    const STAGE_NAMES_EN = [
        'direction_calibration',
        'literature_research',
        'topic_refinement',
        'question_construction',
        'proposal_writing',
        'self_check_optimization',
    ];

    const STAGE_ICONS = ['🧭', '📚', '🔬', '❓', '✍️', '🔍'];

    // 六道门禁（与 pipeline_orchestrator.py GATES 一致）
    const GATE_NAMES = [
        '方向校准门',
        '文献调研门',
        '课题凝练门',
        '科学问题门',
        '申请书撰写门',
        '自检优化门',
    ];

    // 管线状态标签
    const PIPELINE_STATUS_LABELS = {
        running: { label: '◐ 运行中', color: 'var(--success-color)' },
        paused: { label: '⏸ 已暂停', color: 'var(--warning-color)' },
        completed: { label: '✓ 已完成', color: 'var(--text-tertiary)' },
    };

    // 阶段状态标签
    const STAGE_STATUS_LABELS = {
        pending: { label: '○ 待处理', color: 'var(--text-tertiary)' },
        in_progress: { label: '◐ 进行中', color: 'var(--accent-color)' },
        completed: { label: '✓ 已完成', color: 'var(--success-color)' },
    };

    // 门禁评审类型
    const REVIEW_TYPE_LABELS = {
        rule: '规则评审',
        llm: 'LLM 评审',
        user: '人工评审',
    };

    // 空白类型标签
    const GAP_TYPE_LABELS = {
        concept: { label: '概念', color: 'var(--info-color)' },
        method: { label: '方法', color: 'var(--accent-color)' },
        theory: { label: '理论', color: 'var(--warning-color)' },
        experiment: { label: '实验', color: 'var(--success-color)' },
    };

    // 课题状态标签
    const TOPIC_STATUS_LABELS = {
        draft: { label: '草稿', color: 'var(--text-tertiary)' },
        candidate: { label: '候选', color: 'var(--info-color)' },
        selected: { label: '已选定', color: 'var(--success-color)' },
        refined: { label: '已精炼', color: 'var(--accent-color)' },
        rejected: { label: '已排除', color: 'var(--text-tertiary)' },
    };

    // 问题类型标签
    const QUESTION_TYPE_LABELS = {
        main: { label: '主问题', color: 'var(--accent-color)' },
        sub: { label: '子问题', color: 'var(--info-color)' },
        detail: { label: '细节', color: 'var(--text-tertiary)' },
    };

    // 问题状态标签
    const QUESTION_STATUS_LABELS = {
        draft: { label: '草稿', color: 'var(--text-tertiary)' },
        validated: { label: '已验证', color: 'var(--success-color)' },
        pending: { label: '待验证', color: 'var(--warning-color)' },
    };

    // 申请书章节
    const PROPOSAL_SECTIONS = [
        '立项依据',
        '研究内容',
        '研究方案',
        '特色与创新',
        '年度研究计划',
        '预期研究成果',
    ];

    // 章节状态标签
    const SECTION_STATUS_LABELS = {
        empty: { label: '未撰写', color: 'var(--text-tertiary)' },
        draft: { label: '草稿', color: 'var(--warning-color)' },
        reviewing: { label: '审阅中', color: 'var(--info-color)' },
        final: { label: '定稿', color: 'var(--success-color)' },
    };

    // 自检问题严重度
    const ISSUE_SEVERITY_LABELS = {
        critical: { label: '严重', color: 'var(--error-color)' },
        major: { label: '重要', color: 'var(--warning-color)' },
        minor: { label: '次要', color: 'var(--info-color)' },
        suggestion: { label: '建议', color: 'var(--text-tertiary)' },
    };

    // 引用类型标签
    const CITATION_TYPE_LABELS = {
        journal: { label: '期刊', color: 'var(--accent-color)' },
        conference: { label: '会议', color: 'var(--info-color)' },
        book: { label: '书籍', color: 'var(--success-color)' },
        preprint: { label: '预印本', color: 'var(--warning-color)' },
        thesis: { label: '学位论文', color: 'var(--text-tertiary)' },
        other: { label: '其他', color: 'var(--text-tertiary)' },
    };

    // 子面板定义
    const TABS = [
        { key: 'overview', label: '🧭 总览' },
        { key: 'gap', label: '📊 空白分析' },
        { key: 'topics', label: '🔬 课题候选' },
        { key: 'questions', label: '❓ 问题框架' },
        { key: 'proposal', label: '✍️ 申请书' },
        { key: 'methodology', label: '📖 方法学' },
        { key: 'inspection', label: '🔍 自检' },
        { key: 'citations', label: '📚 文献引用' },
        { key: 'agents', label: '🤖 团队' },
    ];

    // ============================================
    // API 辅助
    // ============================================

    function pidPath() {
        return currentProposalId ? `/api/pipeline/${encodeURIComponent(currentProposalId)}` : '/api/pipeline';
    }

    async function apiCall(method, path, body) {
        if (method === 'GET') return await apiGet(path);
        if (method === 'DELETE') return await apiDelete(path);
        if (method === 'POST') return await apiPost(path, body || {});
        if (method === 'PUT') return await apiPut(path, body || {});
        throw new Error(`不支持的 HTTP 方法: ${method}`);
    }

    // 统一的错误处理
    function handleApiError(e, action) {
        let msg = e.message || '未知错误';
        if (msg.includes('404')) msg = `proposal 不存在（404）`;
        else if (msg.includes('409')) msg = `操作冲突（409）：${msg}`;
        else if (msg.includes('500')) msg = `服务器错误（500）`;
        showToast(`✗ ${action}失败: ${msg}`, 'error', 5000);
    }

    // 设置按钮加载态
    function setLoading(btn, loading, loadingText) {
        if (!btn) return;
        if (loading) {
            btn._origText = btn.textContent;
            btn.disabled = true;
            btn.textContent = loadingText || '◐ 处理中…';
        } else {
            btn.disabled = false;
            if (btn._origText) btn.textContent = btn._origText;
        }
    }

    // ============================================
    // 标签辅助
    // ============================================

    function statusBadge(label, color) {
        return `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.72rem;background:${color};color:#fff;white-space:nowrap;">${escapeHtml(label)}</span>`;
    }

    function pipelineStatusBadge(status) {
        const s = PIPELINE_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function stageStatusBadge(status) {
        const s = STAGE_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function gapTypeBadge(type) {
        const s = GAP_TYPE_LABELS[type] || { label: type || '其他', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function topicStatusBadge(status) {
        const s = TOPIC_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function questionTypeBadge(type) {
        const s = QUESTION_TYPE_LABELS[type] || { label: type || '问题', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function questionStatusBadge(status) {
        const s = QUESTION_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function sectionStatusBadge(status) {
        const s = SECTION_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function issueSeverityBadge(severity) {
        const s = ISSUE_SEVERITY_LABELS[severity] || { label: severity || '建议', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function citationTypeBadge(type) {
        const s = CITATION_TYPE_LABELS[type] || { label: type || '其他', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    // 安全的 onclick 参数转义
    function esc(v) {
        return escapeAttr(String(v ?? ''));
    }

    // ============================================
    // 面板打开 / 关闭
    // ============================================

    function ensureOverlay() {
        let overlay = document.getElementById('pipeline-overlay');
        if (overlay) return overlay;
        overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'pipeline-overlay';
        overlay.style.display = 'none';
        overlay.innerHTML = `
          <div class="modal-content" style="max-width:960px;max-height:92vh;display:flex;flex-direction:column;">
            <div class="modal-header">
              <h3>🧭 研究管线</h3>
              <button class="btn-icon" id="pipeline-close" aria-label="关闭研究管线面板" title="关闭">✕</button>
            </div>
            <div id="pipeline-proposal-bar" style="padding:6px 16px;border-bottom:1px solid var(--border-color);display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:0.82rem;">
              <span class="text-secondary">Proposal:</span>
              <input type="text" id="pipeline-proposal-input" placeholder="输入 proposal ID…" style="flex:1;min-width:120px;padding:4px 8px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-primary);color:var(--text-primary);font-size:0.82rem;" aria-label="proposal ID 输入框">
              <button id="pipeline-proposal-load" class="btn-outline btn-outline--accent" style="padding:4px 10px;font-size:0.78rem;" tabindex="0" role="button" aria-label="加载 proposal">加载</button>
              <span id="pipeline-proposal-info" class="text-tertiary" style="font-size:0.75rem;"></span>
            </div>
            <div class="kb-tabs" id="pipeline-tabs" style="display:flex;gap:4px;padding:0 16px;border-bottom:1px solid var(--border-color);flex-wrap:wrap;"></div>
            <div id="pipeline-body" style="flex:1;overflow-y:auto;padding:16px;font-size:0.9rem;">
              <p class="state-loading">请先加载一个 proposal</p>
            </div>
          </div>
        `;
        document.body.appendChild(overlay);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closePipelineManager();
        });
        document.getElementById('pipeline-close').addEventListener('click', closePipelineManager);
        document.getElementById('pipeline-proposal-load').addEventListener('click', () => {
            const input = document.getElementById('pipeline-proposal-input');
            const pid = input.value.trim();
            if (pid) {
                Pipeline.setProposal(pid);
            } else {
                showToast('请输入 proposal ID', 'warning');
            }
        });
        document.getElementById('pipeline-proposal-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const pid = e.target.value.trim();
                if (pid) Pipeline.setProposal(pid);
            }
        });
        renderTabs();
        return overlay;
    }

    function renderTabs() {
        const tabsEl = document.getElementById('pipeline-tabs');
        if (!tabsEl) return;
        let html = '';
        for (const t of TABS) {
            const isActive = activeTab === t.key;
            html += `<button class="kb-tab ${isActive ? 'active' : ''}" data-tab="${t.key}" onclick="Pipeline.switchTo('${t.key}')" tabindex="0" role="tab" aria-selected="${isActive}" aria-label="${t.label}">${t.label}</button>`;
        }
        tabsEl.innerHTML = html;
    }

    function openPipelineManager(proposalId) {
        ensureOverlay();
        openModal('pipeline-overlay');
        if (proposalId) {
            const input = document.getElementById('pipeline-proposal-input');
            if (input) input.value = proposalId;
            Pipeline.setProposal(proposalId);
        } else {
            renderBody();
        }
    }

    function closePipelineManager() {
        closeModal('pipeline-overlay');
    }

    // ============================================
    // 主体渲染
    // ============================================

    function renderBody() {
        const body = document.getElementById('pipeline-body');
        if (!body) return;
        // agents 面板为全局团队管理，不依赖 proposal_id
        if (!currentProposalId && activeTab !== 'agents') {
            body.innerHTML = '<div class="state-empty"><div style="font-size:2rem;margin-bottom:8px;">🧭</div><p>请输入 proposal ID 并点击「加载」</p><p class="meta-sm" style="margin-top:4px;">proposal 对应一个研究管线的完整工作目录</p><p class="meta-sm" style="margin-top:8px;">或切换到「🤖 团队」查看智能体团队</p></div>';
            return;
        }
        body.innerHTML = '<p class="state-loading">◐ 加载中…</p>';
        renderTab();
    }

    async function renderTab() {
        const body = document.getElementById('pipeline-body');
        if (!body) return;
        // agents 面板为全局团队管理，不依赖 proposal_id
        if (!currentProposalId && activeTab !== 'agents') return;
        try {
            if (activeTab === 'overview') await renderOverview(body);
            else if (activeTab === 'gap') await renderGapAnalysis(body);
            else if (activeTab === 'topics') await renderTopics(body);
            else if (activeTab === 'questions') await renderQuestions(body);
            else if (activeTab === 'proposal') await renderProposal(body);
            else if (activeTab === 'methodology') await renderMethodology(body);
            else if (activeTab === 'inspection') await renderInspection(body);
            else if (activeTab === 'citations') await renderCitations(body);
            else if (activeTab === 'agents') await renderAgents(body);
        } catch (e) {
            body.innerHTML = `<p class="state-error">加载失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    // ============================================
    // 1. 管线总览面板
    // ============================================

    async function renderOverview(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载管线状态…</p>';
        try {
            const [state, progress] = await Promise.all([
                apiGet(`${pidPath()}/state`),
                apiGet(`${pidPath()}/progress`),
            ]);
            pipelineState = state;

            const current = state.current_stage ?? 0;
            const status = state.status || 'running';
            const stageStatus = state.stage_status || {};
            const gateResults = state.gate_results || {};
            const completionPct = progress.completion_pct ?? 0;
            const completedStages = progress.completed_stages ?? 0;
            const totalStages = progress.total_stages ?? 6;
            const blockedItems = progress.blocked_items || [];

            let html = '';

            // 状态栏
            html += '<div class="d-flex ai-center gap-10 mb-14 fw-wrap">';
            html += `<span class="label-bold">管线状态</span>`;
            html += pipelineStatusBadge(status);
            html += `<span class="meta-sm">当前阶段: ${escapeHtml(STAGE_NAMES[current] || String(current))}</span>`;
            html += `<span class="meta-sm">完成度: ${escapeHtml(String(completionPct))}%</span>`;
            html += '</div>';

            // 进度条
            html += `<div style="margin-bottom:16px;">`;
            html += `<div style="height:8px;background:var(--bg-tertiary);border-radius:4px;overflow:hidden;"><div style="height:100%;width:${completionPct}%;background:var(--accent-color);border-radius:4px;transition:width 0.3s;"></div></div>`;
            html += `<div class="meta-xs-mt">${escapeHtml(String(completedStages))}/${escapeHtml(String(totalStages))} 阶段完成</div>`;
            html += `</div>`;

            // 六阶段横向进度条
            html += '<div style="margin-bottom:20px;">';
            html += '<div class="label-sm-mb8">六阶段进度</div>';
            html += '<div style="display:flex;align-items:flex-start;gap:2px;overflow-x:auto;padding-bottom:8px;">';
            for (let i = 0; i < STAGE_NAMES.length; i++) {
                const isCurrent = i === current && status !== 'completed';
                const isCompleted = stageStatus[String(i)] === 'completed' || (status === 'completed');
                const isPending = stageStatus[String(i)] === 'pending' || (!isCurrent && !isCompleted);
                const gate = gateResults[String(i)];
                const gatePassed = gate && gate.passed;
                const gateFailed = gate && !gate.passed;

                let bg = 'var(--bg-tertiary)';
                let icon = STAGE_ICONS[i] || '';
                let indicator = '';
                if (isCompleted) {
                    bg = 'var(--success-color)';
                    indicator = '✓';
                } else if (isCurrent) {
                    bg = 'var(--accent-color)';
                    indicator = '▶';
                } else if (gateFailed) {
                    bg = 'var(--warning-color)';
                    indicator = '⚠';
                }

                html += `<div style="flex:1;min-width:100px;text-align:center;padding:10px 4px;background:${bg};color:#fff;border-radius:6px 6px 0 0;position:relative;cursor:pointer;" onclick="Pipeline._showStageDetail(${i})" tabindex="0" role="button" aria-label="阶段${i}: ${esc(STAGE_NAMES[i])}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();Pipeline._showStageDetail(${i})}">`;
                html += `<div style="font-size:1.2rem;">${icon}</div>`;
                html += `<div style="font-size:0.72rem;font-weight:600;margin-top:2px;">${escapeHtml(STAGE_NAMES[i])}</div>`;
                if (indicator) html += `<div style="position:absolute;top:2px;right:4px;font-size:0.7rem;">${indicator}</div>`;
                html += `</div>`;
                if (i < STAGE_NAMES.length - 1) {
                    html += `<div style="display:flex;align-items:center;color:var(--text-tertiary);padding:0 2px;font-size:0.8rem;">→</div>`;
                }
            }
            html += '</div>';
            html += '</div>';

            // 门禁状态
            html += '<div style="margin-bottom:20px;">';
            html += '<div class="label-sm-mb8">门禁状态</div>';
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;">';
            for (let i = 0; i < GATE_NAMES.length; i++) {
                const gate = gateResults[String(i)];
                let gateLabel = '未评审';
                let gateColor = 'var(--text-tertiary)';
                let gateIcon = '○';
                if (gate) {
                    if (gate.passed) { gateLabel = '通过'; gateColor = 'var(--success-color)'; gateIcon = '✓'; }
                    else { gateLabel = '未通过'; gateColor = 'var(--error-color)'; gateIcon = '✗'; }
                }
                html += `<div class="pad-10 bg-secondary br-6 border-default" style="border-left:3px solid ${gateColor};">`;
                html += `<div class="meta-xs">门禁 ${i}</div>`;
                html += `<div style="font-size:0.8rem;font-weight:600;color:var(--text-primary);">${escapeHtml(GATE_NAMES[i])}</div>`;
                html += `<div style="font-size:0.75rem;color:${gateColor};margin-top:2px;">${gateIcon} ${escapeHtml(gateLabel)}</div>`;
                if (gate && gate.score !== undefined) {
                    html += `<div class="meta-xs-mt">评分: ${escapeHtml(String(gate.score))}</div>`;
                }
                html += `</div>`;
            }
            html += '</div>';
            html += '</div>';

            // 阻塞项
            if (blockedItems.length) {
                html += '<div style="margin-bottom:20px;padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--warning-color);">';
                html += '<div class="label-bold" style="color:var(--warning-color);">⚠ 阻塞项</div>';
                for (const item of blockedItems) {
                    if (item.type === 'gate') {
                        html += `<div class="meta-sm">门禁 ${escapeHtml(String(item.stage))}: ${escapeHtml((item.issues || []).join('; '))}</div>`;
                    } else if (item.type === 'paused') {
                        html += `<div class="meta-sm">已暂停: ${escapeHtml(item.reason || '')}</div>`;
                    }
                }
                html += '</div>';
            }

            // 操作按钮
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:16px;">';
            const canAdvance = status === 'running';
            const canRollback = status === 'running' && current > 0;
            const canPause = status === 'running';
            const canResume = status === 'paused';
            html += `<button id="pl-advance-btn" onclick="Pipeline._handleAdvance()" class="btn-top-action" ${canAdvance ? '' : 'disabled style="opacity:0.5;cursor:not-allowed;"'} tabindex="0" role="button" aria-label="推进到下一阶段">▶ 推进</button>`;
            html += `<button id="pl-rollback-btn" onclick="Pipeline._handleRollback()" class="btn-outline btn-outline--warning" ${canRollback ? '' : 'disabled style="opacity:0.5;cursor:not-allowed;"'} tabindex="0" role="button" aria-label="回滚到上一阶段">◀ 回滚</button>`;
            html += `<button id="pl-pause-btn" onclick="Pipeline._handlePause()" class="btn-outline btn-outline--warning-var" ${canPause ? '' : 'disabled style="opacity:0.5;cursor:not-allowed;"'} tabindex="0" role="button" aria-label="暂停管线">⏸ 暂停</button>`;
            html += `<button id="pl-resume-btn" onclick="Pipeline._handleResume()" class="btn-outline btn-outline--success" ${canResume ? '' : 'disabled style="opacity:0.5;cursor:not-allowed;"'} tabindex="0" role="button" aria-label="恢复管线">▶ 恢复</button>`;
            html += '</div>';

            // 门禁操作
            html += '<div style="margin-bottom:16px;">';
            html += '<div class="label-sm-mb8">门禁操作</div>';
            html += '<div style="display:flex;gap:6px;flex-wrap:wrap;">';
            for (let i = 0; i < GATE_NAMES.length; i++) {
                html += `<button onclick="Pipeline._handleGateCheck(${i})" class="btn-outline btn-outline--info" style="padding:4px 10px;font-size:0.75rem;" tabindex="0" role="button" aria-label="运行门禁${i}评审">门禁${i}: ${esc(GATE_NAMES[i])}</button>`;
            }
            html += '</div>';
            html += '</div>';

            // 时间线
            const history = state.history || [];
            if (history.length) {
                html += '<div>';
                html += '<div class="label-sm-mb8">执行时间线</div>';
                html += '<div style="max-height:240px;overflow-y:auto;padding-left:20px;position:relative;">';
                html += '<div style="position:absolute;left:7px;top:4px;bottom:4px;width:2px;background:var(--border-color);"></div>';
                const recent = history.slice(-30).reverse();
                for (const ev of recent) {
                    const evTime = (ev.timestamp || '').slice(0, 16);
                    html += '<div style="position:relative;padding-bottom:10px;">';
                    html += `<div style="position:absolute;left:-17px;top:4px;width:10px;height:10px;border-radius:50%;background:var(--accent-color);border:2px solid var(--bg-primary);"></div>`;
                    html += `<div class="meta-xs">${escapeHtml(evTime)}</div>`;
                    html += `<div style="font-size:0.78rem;color:var(--text-primary);">${escapeHtml(ev.detail || ev.event || '')}</div>`;
                    html += '</div>';
                }
                html += '</div>';
                html += '</div>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载管线状态失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    // 阶段详情弹窗
    function _showStageDetail(stage) {
        const info = STAGE_NAMES[stage] ? {
            name: STAGE_NAMES[stage],
            name_en: STAGE_NAMES_EN[stage],
            gate: GATE_NAMES[stage],
        } : null;
        if (!info) return;
        const gate = pipelineState && pipelineState.gate_results ? pipelineState.gate_results[String(stage)] : null;
        let html = `<div class="modal--lg"><h3 class="modal-title">${escapeHtml(STAGE_ICONS[stage] || '')} 阶段 ${stage}: ${escapeHtml(info.name)}</h3>`;
        html += `<div style="margin-bottom:10px;"><span class="meta-sm">英文名: ${escapeHtml(info.name_en)}</span></div>`;
        html += `<div style="margin-bottom:10px;"><span class="meta-sm">门禁: ${escapeHtml(info.gate)}</span></div>`;
        if (gate) {
            const verdict = gate.passed ? '✓ 通过' : '✗ 未通过';
            const color = gate.passed ? 'var(--success-color)' : 'var(--error-color)';
            html += `<div style="padding:8px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${color};margin-bottom:10px;">`;
            html += `<div style="font-size:0.82rem;color:${color};font-weight:600;">${verdict}</div>`;
            html += `<div class="meta-sm">评分: ${escapeHtml(String(gate.score ?? 'N/A'))} · 评审: ${escapeHtml(REVIEW_TYPE_LABELS[gate.review_type] || gate.review_type || '')}</div>`;
            if (gate.issues && gate.issues.length) {
                html += '<div style="margin-top:6px;font-size:0.78rem;color:var(--text-secondary);">问题:</div><ul style="margin:4px 0 0 16px;font-size:0.75rem;">';
                for (const iss of gate.issues) html += `<li>${escapeHtml(iss)}</li>`;
                html += '</ul>';
            }
            html += '</div>';
        }
        html += `<button onclick="closeModal('modal-overlay')" class="btn-confirm">关闭</button></div>`;
        showModal(html);
    }

    // ============================================
    // 管线操作处理
    // ============================================

    async function _handleAdvance() {
        const btn = document.getElementById('pl-advance-btn');
        setLoading(btn, true, '◐ 推进中…');
        try {
            const result = await apiPost(`${pidPath()}/advance`, {});
            if (result.advanced) {
                if (result.completed) {
                    showToast('🎉 管线全部完成！', 'success', 5000);
                } else {
                    showToast(`✓ 已推进到阶段 ${result.current_stage}`, 'success');
                }
            } else {
                showToast(`⚠ 推进被阻: ${result.reason || '门禁未通过'}`, 'warning', 5000);
                if (result.gate) {
                    _showStageDetail(result.current_stage);
                }
            }
            await renderTab();
        } catch (e) {
            handleApiError(e, '推进');
        } finally {
            setLoading(btn, false);
        }
    }

    async function _handleRollback() {
        const reason = await promptModal('请输入回滚原因（必填）:', '回滚原因');
        if (!reason) return;
        const btn = document.getElementById('pl-rollback-btn');
        setLoading(btn, true, '◐ 回滚中…');
        try {
            const result = await apiPost(`${pidPath()}/rollback`, { reason });
            if (result.rolled_back) {
                showToast(`✓ 已回滚到阶段 ${result.current_stage}`, 'success');
                await renderTab();
            } else {
                showToast(`⚠ 回滚失败: ${result.reason || ''}`, 'warning');
            }
        } catch (e) {
            handleApiError(e, '回滚');
        } finally {
            setLoading(btn, false);
        }
    }

    async function _handlePause() {
        const reason = await promptModal('请输入暂停原因（可选）:', '暂停原因');
        if (reason === null) return;
        const btn = document.getElementById('pl-pause-btn');
        setLoading(btn, true, '◐ 暂停中…');
        try {
            const result = await apiPost(`${pidPath()}/pause`, { reason: reason || '' });
            if (result.paused) {
                showToast('⏸ 管线已暂停', 'success');
                await renderTab();
            } else {
                showToast(`⚠ 暂停失败: ${result.reason || ''}`, 'warning');
            }
        } catch (e) {
            handleApiError(e, '暂停');
        } finally {
            setLoading(btn, false);
        }
    }

    async function _handleResume() {
        const btn = document.getElementById('pl-resume-btn');
        setLoading(btn, true, '◐ 恢复中…');
        try {
            const result = await apiPost(`${pidPath()}/resume`, {});
            if (result.resumed) {
                showToast('▶ 管线已恢复运行', 'success');
                await renderTab();
            } else {
                showToast(`⚠ 恢复失败: ${result.reason || ''}`, 'warning');
            }
        } catch (e) {
            handleApiError(e, '恢复');
        } finally {
            setLoading(btn, false);
        }
    }

    async function _handleGateCheck(stage) {
        if (!await confirmModal(`运行门禁 ${stage}（${GATE_NAMES[stage]}）评审？`, '运行评审')) return;
        showToast(`◐ 正在评审门禁 ${stage}…`, 'info');
        try {
            const result = await apiPost(`${pidPath()}/gate/${stage}`, { review_type: 'rule' });
            if (result.passed) {
                showToast(`✓ 门禁 ${stage} 通过（评分 ${result.score}）`, 'success');
            } else {
                showToast(`✗ 门禁 ${stage} 未通过（评分 ${result.score}）`, 'warning', 5000);
            }
            await renderTab();
        } catch (e) {
            handleApiError(e, '门禁评审');
        }
    }

    // ============================================
    // 2. 空白分析面板
    // ============================================

    async function renderGapAnalysis(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载空白分析…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/gap-analysis`);
                gapReport = data;
            } catch (e) {
                if (e.message.includes('404')) {
                    gapReport = null;
                } else {
                    throw e;
                }
            }

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._handleAnalyzeGaps()" class="btn-top-action" tabindex="0" role="button" aria-label="运行空白分析">🔄 运行分析</button>`;
            html += `<button onclick="Pipeline._exportGap('markdown')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 Markdown">📄 导出 MD</button>`;
            html += `<button onclick="Pipeline._exportGap('json')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 JSON">📋 导出 JSON</button>`;
            html += '</div>';

            if (!gapReport) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">📊</div><p>暂无空白分析结果</p><p class="meta-sm" style="margin-top:4px;">点击「运行分析」基于文献调研结果识别研究空白</p></div>';
                container.innerHTML = html;
                return;
            }

            // 覆盖率图
            const coverage = gapReport.coverage || {};
            const conceptsCovered = coverage.concepts_covered || [];
            const conceptsMissing = coverage.concepts_missing || [];
            const methodsEstablished = coverage.methods_established || [];
            const methodsEmerging = coverage.methods_emerging || [];

            html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">';
            // 概念覆盖
            html += '<div class="pad-12 bg-secondary br-6 border-default">';
            html += '<div class="label-bold-mb4">📐 概念覆盖</div>';
            html += `<div class="meta-sm">已覆盖 ${conceptsCovered.length} · 缺失 ${conceptsMissing.length}</div>`;
            if (conceptsCovered.length) {
                html += '<div style="margin-top:6px;"><span class="meta-xs">已覆盖:</span></div>';
                html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">';
                for (const c of conceptsCovered.slice(0, 15)) {
                    html += `<span class="chip" style="background:var(--success-color);color:#fff;">${escapeHtml(c)}</span>`;
                }
                html += '</div>';
            }
            if (conceptsMissing.length) {
                html += '<div style="margin-top:6px;"><span class="meta-xs">缺失:</span></div>';
                html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">';
                for (const c of conceptsMissing.slice(0, 15)) {
                    html += `<span class="chip" style="background:var(--error-color);color:#fff;">${escapeHtml(c)}</span>`;
                }
                html += '</div>';
            }
            html += '</div>';

            // 方法覆盖
            html += '<div class="pad-12 bg-secondary br-6 border-default">';
            html += '<div class="label-bold-mb4">🛠️ 方法覆盖</div>';
            html += `<div class="meta-sm">已建立 ${methodsEstablished.length} · 新兴 ${methodsEmerging.length}</div>`;
            if (methodsEstablished.length) {
                html += '<div style="margin-top:6px;"><span class="meta-xs">已建立:</span></div>';
                html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">';
                for (const m of methodsEstablished.slice(0, 10)) {
                    html += `<span class="chip" style="background:var(--accent-color);color:#fff;">${escapeHtml(m)}</span>`;
                }
                html += '</div>';
            }
            if (methodsEmerging.length) {
                html += '<div style="margin-top:6px;"><span class="meta-xs">新兴:</span></div>';
                html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">';
                for (const m of methodsEmerging.slice(0, 10)) {
                    html += `<span class="chip" style="background:var(--warning-color);color:#fff;">${escapeHtml(m)}</span>`;
                }
                html += '</div>';
            }
            html += '</div>';
            html += '</div>';

            // 空白列表
            const gaps = gapReport.gaps || [];
            html += `<div class="label-bold-mb4">🔍 研究空白（${gaps.length}）</div>`;
            if (gaps.length) {
                html += '<div class="col-gap8">';
                for (const gap of gaps) {
                    const priority = gap.priority ?? gap.score ?? 0;
                    const priorityColor = priority >= 0.7 ? 'var(--error-color)' : priority >= 0.4 ? 'var(--warning-color)' : 'var(--text-tertiary)';
                    html += `<div class="pad-10 bg-secondary br-6 border-default" style="border-left:3px solid ${priorityColor};">`;
                    html += '<div class="row-between-top">';
                    html += `<div style="font-size:0.85rem;font-weight:600;color:var(--text-primary);">${escapeHtml(gap.title || gap.description || '')}</div>`;
                    html += gapTypeBadge(gap.type || 'concept');
                    html += '</div>';
                    if (gap.description) {
                        html += `<div class="meta-sm-mt">${escapeHtml(gap.description)}</div>`;
                    }
                    html += '<div class="d-flex gap-8 mt-6 fw-wrap ai-center">';
                    html += `<span class="meta-xs">优先级: <span style="color:${priorityColor};font-weight:600;">${escapeHtml(String(Math.round(priority * 100)))}%</span></span>`;
                    if (gap.directions || gap.direction_tags) {
                        const dirs = gap.directions || gap.direction_tags || [];
                        for (const d of dirs.slice(0, 3)) {
                            html += `<span class="chip">${escapeHtml(d)}</span>`;
                        }
                    }
                    html += '</div>';
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<p class="meta-sm-pad8">暂无识别到的研究空白</p>';
            }

            // 分析元信息
            if (gapReport.analyzed_at || gapReport.summary) {
                html += '<div style="margin-top:12px;padding:8px;background:var(--bg-secondary);border-radius:6px;font-size:0.78rem;color:var(--text-secondary);">';
                if (gapReport.summary) html += `<div>${escapeHtml(gapReport.summary)}</div>`;
                if (gapReport.analyzed_at) html += `<div class="meta-xs-mt">分析时间: ${escapeHtml(gapReport.analyzed_at)}</div>`;
                html += '</div>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载空白分析失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    async function _handleAnalyzeGaps() {
        showToast('◐ 正在运行空白分析…', 'info');
        try {
            const result = await apiPost(`${pidPath()}/gap-analysis/run`, {});
            showToast(`✓ 空白分析完成，识别 ${result.gaps ? result.gaps.length : 0} 个空白`, 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '空白分析');
        }
    }

    async function _exportGap(format) {
        try {
            const data = await apiGet(`${pidPath()}/gap-analysis/export?format=${format}`);
            const content = data.content || '';
            const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `gap-analysis-${currentProposalId}.${format === 'json' ? 'json' : 'md'}`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出空白分析', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 3. 课题候选面板
    // ============================================

    async function renderTopics(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载课题候选…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/topics`);
                topicsList = data.topics || [];
            } catch (e) {
                if (e.message.includes('404')) {
                    topicsList = [];
                } else {
                    throw e;
                }
            }

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._handleGenerateTopics()" class="btn-top-action" tabindex="0" role="button" aria-label="生成课题候选">🔄 生成课题</button>`;
            html += `<button onclick="Pipeline._exportTopics()" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出课题列表">📤 导出</button>`;
            html += '</div>';

            if (!topicsList.length) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">🔬</div><p>暂无课题候选</p><p class="meta-sm" style="margin-top:4px;">点击「生成课题」基于空白分析凝练课题方向</p></div>';
                container.innerHTML = html;
                return;
            }

            html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;">';
            for (const t of topicsList) {
                const total = t.scores?.total ?? t.total_score ?? 0;
                const taste = t.scores?.taste ?? '?';
                const novelty = t.scores?.novelty ?? '?';
                const feasibility = t.scores?.feasibility ?? '?';
                html += `<div class="pad-12 bg-secondary br-8 border-default" style="border-left:3px solid var(--accent-color);">`;
                html += '<div class="row-between-top mb-6">';
                html += `<div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);flex:1;">${escapeHtml(t.title || t.name || '')}</div>`;
                html += topicStatusBadge(t.status || 'draft');
                html += '</div>';
                if (t.direction) {
                    html += `<div class="meta-sm-mb">${escapeHtml(t.direction)}</div>`;
                }
                // 评分
                html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px;margin:8px 0;">';
                html += `<div style="text-align:center;padding:4px;background:var(--bg-tertiary);border-radius:4px;"><div class="meta-xs">品味</div><div style="font-size:0.82rem;font-weight:600;">${escapeHtml(String(taste))}</div></div>`;
                html += `<div style="text-align:center;padding:4px;background:var(--bg-tertiary);border-radius:4px;"><div class="meta-xs">新颖</div><div style="font-size:0.82rem;font-weight:600;">${escapeHtml(String(novelty))}</div></div>`;
                html += `<div style="text-align:center;padding:4px;background:var(--bg-tertiary);border-radius:4px;"><div class="meta-xs">可行</div><div style="font-size:0.82rem;font-weight:600;">${escapeHtml(String(feasibility))}</div></div>`;
                html += `<div style="text-align:center;padding:4px;background:var(--accent-color);border-radius:4px;color:#fff;"><div style="font-size:0.65rem;">总分</div><div style="font-size:0.82rem;font-weight:600;">${escapeHtml(String(total))}</div></div>`;
                html += '</div>';
                // 操作
                html += '<div class="d-flex gap-6 fw-wrap">';
                html += `<button onclick="Pipeline._selectTopic('${esc(t.topic_id || t.id)}')" class="btn-xs btn-outline--success" tabindex="0" role="button" aria-label="选定课题">✓ 选定</button>`;
                html += `<button onclick="Pipeline._refineTopic('${esc(t.topic_id || t.id)}')" class="btn-xs btn-outline--accent" tabindex="0" role="button" aria-label="精炼课题">✎ 精炼</button>`;
                html += `<button onclick="Pipeline._viewTopicDetail('${esc(t.topic_id || t.id)}')" class="btn-xs" tabindex="0" role="button" aria-label="查看课题详情">📋 详情</button>`;
                html += '</div>';
                html += '</div>';
            }
            html += '</div>';
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载课题候选失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    async function _handleGenerateTopics() {
        if (!await confirmModal('生成课题候选？将基于空白分析结果使用 LLM 凝练课题方向。', '生成')) return;
        showToast('◐ 正在生成课题候选…', 'info');
        try {
            const result = await apiPost(`${pidPath()}/topics/generate`, {});
            const count = result.topics ? result.topics.length : 0;
            showToast(`✓ 已生成 ${count} 个课题候选`, 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '生成课题');
        }
    }

    async function _selectTopic(topicId) {
        if (!await confirmModal('选定该课题作为研究目标？', '选定')) return;
        try {
            await apiPost(`${pidPath()}/topics/${encodeURIComponent(topicId)}/select`, {});
            showToast('✓ 课题已选定', 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '选定课题');
        }
    }

    async function _refineTopic(topicId) {
        const instruction = await promptModal('请输入精炼指令（可选）:', '如：更聚焦固体HHG方向');
        if (instruction === null) return;
        showToast('◐ 正在精炼课题…', 'info');
        try {
            await apiPost(`${pidPath()}/topics/${encodeURIComponent(topicId)}/refine`, { instruction });
            showToast('✓ 课题已精炼', 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '精炼课题');
        }
    }

    async function _viewTopicDetail(topicId) {
        try {
            const data = await apiGet(`${pidPath()}/topics/${encodeURIComponent(topicId)}`);
            const t = data.topic || data;
            let html = `<div class="modal--xl"><h3 class="modal-title">📋 课题详情</h3>`;
            html += `<div style="font-size:0.95rem;font-weight:600;margin-bottom:8px;">${escapeHtml(t.title || t.name || '')}</div>`;
            html += `<div class="meta-sm-mb">${escapeHtml(t.direction || '')}</div>`;
            if (t.rationale || t.description) {
                html += `<div style="padding:8px;background:var(--bg-secondary);border-radius:6px;margin-bottom:10px;font-size:0.82rem;">${renderMarkdown(t.rationale || t.description || '')}</div>`;
            }
            if (t.gap_evidence || t.evidence) {
                html += '<div class="label-bold-mb4">空白证据</div>';
                const evs = t.gap_evidence || t.evidence || [];
                if (Array.isArray(evs)) {
                    html += '<ul style="margin:0 0 10px 16px;font-size:0.8rem;">';
                    for (const ev of evs) html += `<li>${escapeHtml(typeof ev === 'string' ? ev : JSON.stringify(ev))}</li>`;
                    html += '</ul>';
                }
            }
            if (t.scores) {
                html += '<div class="label-bold-mb4">评分</div>';
                html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:6px;margin-bottom:10px;">';
                for (const [k, v] of Object.entries(t.scores)) {
                    html += `<div class="pad-8 bg-secondary br-6 ta-center"><div class="meta-xs">${escapeHtml(k)}</div><div style="font-size:0.9rem;font-weight:600;">${escapeHtml(String(v))}</div></div>`;
                }
                html += '</div>';
            }
            html += `<button onclick="closeModal('modal-overlay')" class="btn-confirm">关闭</button></div>`;
            showModal(html);
        } catch (e) {
            handleApiError(e, '查看课题详情');
        }
    }

    async function _exportTopics() {
        try {
            const data = await apiGet(`${pidPath()}/topics/export`);
            const content = data.content || '';
            const blob = new Blob([content], { type: 'text/markdown' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `topics-${currentProposalId}.md`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出课题列表', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 4. 问题框架面板
    // ============================================

    async function renderQuestions(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载问题框架…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/questions`);
                questionFramework = data;
            } catch (e) {
                if (e.message.includes('404')) {
                    questionFramework = null;
                } else {
                    throw e;
                }
            }

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._handleConstructQuestions()" class="btn-top-action" tabindex="0" role="button" aria-label="构建问题框架">🔄 构建问题</button>`;
            html += `<button onclick="Pipeline._exportQuestions()" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出问题框架">📤 导出</button>`;
            html += '</div>';

            if (!questionFramework) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">❓</div><p>暂无问题框架</p><p class="meta-sm" style="margin-top:4px;">点击「构建问题」基于选定课题构建层次化科学问题</p></div>';
                container.innerHTML = html;
                return;
            }

            // 五要素手风琴
            const elements = [
                { key: 'rationale', label: '立项依据', icon: '📝' },
                { key: 'scientific_question', label: '科学问题', icon: '❓' },
                { key: 'research_content', label: '研究内容', icon: '📋' },
                { key: 'research_plan', label: '研究方案', icon: '🛠️' },
                { key: 'innovation', label: '特色与创新', icon: '💡' },
            ];

            for (const elem of elements) {
                const elemData = questionFramework[elem.key] || {};
                const questions = elemData.questions || elemData.items || [];
                html += `<details style="margin-bottom:8px;" ${elem.key === 'scientific_question' ? 'open' : ''}>`;
                html += `<summary style="cursor:pointer;padding:8px 10px;background:var(--bg-secondary);border-radius:6px;font-size:0.85rem;font-weight:600;color:var(--text-primary);">${elem.icon} ${escapeHtml(elem.label)}（${questions.length}）</summary>`;
                html += '<div style="padding:8px 10px 8px 20px;">';
                if (questions.length) {
                    html += _renderQuestionTree(questions, 0);
                } else if (elemData.summary || elemData.content) {
                    html += `<div style="font-size:0.82rem;color:var(--text-secondary);">${renderMarkdown(elemData.summary || elemData.content)}</div>`;
                } else {
                    html += '<p class="meta-sm">暂无内容</p>';
                }
                html += '</div>';
                html += '</details>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载问题框架失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    function _renderQuestionTree(questions, depth) {
        let html = '';
        for (const q of questions) {
            const qId = q.question_id || q.id || '';
            const qType = q.type || (depth === 0 ? 'main' : depth === 1 ? 'sub' : 'detail');
            const qStatus = q.status || 'draft';
            const children = q.children || q.sub_questions || [];
            html += `<div style="margin-left:${depth * 16}px;padding:6px 8px;border-left:2px solid var(--border-color);margin-bottom:4px;">`;
            html += '<div class="d-flex ai-start gap-6 fw-wrap">';
            html += `<div style="flex:1;min-width:200px;font-size:0.82rem;color:var(--text-primary);">${escapeHtml(q.text || q.title || q.question || '')}</div>`;
            html += questionTypeBadge(qType);
            html += questionStatusBadge(qStatus);
            html += '</div>';
            // 验证评分
            if (q.validation || q.scores) {
                const val = q.validation || q.scores || {};
                const valScore = val.score ?? val.total ?? '';
                if (valScore !== '') {
                    html += `<div class="meta-xs-mt">验证评分: ${escapeHtml(String(valScore))}</div>`;
                }
            }
            // 操作
            html += '<div class="d-flex gap-4 mt-4 fw-wrap">';
            html += `<button onclick="Pipeline._refineQuestion('${esc(qId)}')" class="btn-xs btn-outline--accent" tabindex="0" role="button" aria-label="精炼问题">✎ 精炼</button>`;
            html += `<button onclick="Pipeline._viewQuestionEvidence('${esc(qId)}')" class="btn-xs" tabindex="0" role="button" aria-label="查看证据">📋 证据</button>`;
            html += '</div>';
            // 子问题
            if (children.length) {
                html += _renderQuestionTree(children, depth + 1);
            }
            html += '</div>';
        }
        return html;
    }

    async function _handleConstructQuestions() {
        if (!await confirmModal('构建问题框架？将基于选定课题使用 LLM 构建层次化科学问题。', '构建')) return;
        showToast('◐ 正在构建问题框架…', 'info');
        try {
            const result = await apiPost(`${pidPath()}/questions/construct`, {});
            showToast(`✓ 问题框架已构建${result.question_count ? '（' + result.question_count + ' 个问题）' : ''}`, 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '构建问题');
        }
    }

    async function _refineQuestion(qId) {
        const instruction = await promptModal('请输入精炼指令（可选）:', '如：更聚焦物理机制');
        if (instruction === null) return;
        showToast('◐ 正在精炼问题…', 'info');
        try {
            await apiPost(`${pidPath()}/questions/${encodeURIComponent(qId)}/refine`, { instruction });
            showToast('✓ 问题已精炼', 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '精炼问题');
        }
    }

    async function _viewQuestionEvidence(qId) {
        try {
            const data = await apiGet(`${pidPath()}/questions/${encodeURIComponent(qId)}/evidence`);
            let html = `<div class="modal--lg"><h3 class="modal-title">📋 问题证据</h3>`;
            const evidence = data.evidence || data.items || [];
            if (evidence.length) {
                html += '<div class="col-gap6">';
                for (const ev of evidence) {
                    html += `<div class="pad-8 bg-secondary br-6 border-default"><div style="font-size:0.82rem;">${escapeHtml(ev.text || ev.summary || JSON.stringify(ev))}</div>`;
                    if (ev.source) html += `<div class="meta-xs-mt">来源: ${escapeHtml(ev.source)}</div>`;
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<p class="meta-sm-pad8">暂无证据</p>';
            }
            html += `<button onclick="closeModal('modal-overlay')" class="btn-confirm">关闭</button></div>`;
            showModal(html);
        } catch (e) {
            handleApiError(e, '查看证据');
        }
    }

    async function _exportQuestions() {
        try {
            const data = await apiGet(`${pidPath()}/questions/export`);
            const content = data.content || '';
            const blob = new Blob([content], { type: 'text/markdown' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `questions-${currentProposalId}.md`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出问题框架', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 5. 申请书撰写面板
    // ============================================

    async function renderProposal(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载申请书…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/proposal/sections`);
                proposalSections = data.sections || [];
            } catch (e) {
                if (e.message.includes('404')) {
                    proposalSections = [];
                } else {
                    throw e;
                }
            }

            // 构建章节映射
            const sectionMap = {};
            for (const s of proposalSections) {
                const name = s.section || s.name || s.title || '';
                sectionMap[name] = s;
            }

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._handleWriteAll()" class="btn-top-action" tabindex="0" role="button" aria-label="撰写全部章节">✍️ 撰写全部</button>`;
            html += `<button onclick="Pipeline._exportProposal()" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出申请书">📤 导出</button>`;
            html += '</div>';

            // 章节标签：先显示 7 个标准名，再显示 API 返回的其他非标准章节
            html += '<div class="d-flex gap-6 mb-14 fw-wrap bb-default" style="padding-bottom:8px;">';
            const displayedSections = [];
            for (const secName of PROPOSAL_SECTIONS) {
                displayedSections.push(secName);
                const isActive = proposalSectionTab === secName;
                const sec = sectionMap[secName];
                const hasContent = sec && sec.content && sec.content.length > 0;
                const dot = hasContent ? '●' : '○';
                html += `<button class="research-tab-btn" data-section="${escapeAttr(secName)}" onclick="Pipeline._switchSection('${escapeAttr(secName)}')" style="padding:6px 12px;border:none;border-bottom:2px solid ${isActive ? 'var(--accent-color)' : 'transparent'};background:transparent;color:${isActive ? 'var(--accent-color)' : 'var(--text-secondary)'};cursor:pointer;font-size:0.82rem;" tabindex="0" role="tab" aria-selected="${isActive}">${dot} ${escapeHtml(secName)}</button>`;
            }
            // 追加 API 返回但未在标准 7 个中的章节
            for (const s of proposalSections) {
                const secName = s.section || s.name || s.title || '';
                if (!secName || displayedSections.includes(secName)) continue;
                if (!s.content || s.content.length === 0) continue;
                displayedSections.push(secName);
                const isActive = proposalSectionTab === secName;
                html += `<button class="research-tab-btn" data-section="${escapeAttr(secName)}" onclick="Pipeline._switchSection('${escapeAttr(secName)}')" style="padding:6px 12px;border:none;border-bottom:2px solid ${isActive ? 'var(--accent-color)' : 'transparent'};background:transparent;color:${isActive ? 'var(--text-secondary)' : 'var(--text-secondary)'};cursor:pointer;font-size:0.82rem;" tabindex="0" role="tab" aria-selected="${isActive}">● ${escapeHtml(secName)}</button>`;
            }
            html += '</div>';

            // 若当前选中的章节不存在或无内容，默认切换到第一个有内容的章节
            if (!sectionMap[proposalSectionTab] || !sectionMap[proposalSectionTab].content) {
                const firstWithContent = proposalSections.find(s => s.content && s.content.length > 0);
                if (firstWithContent) {
                    proposalSectionTab = firstWithContent.section || firstWithContent.name || firstWithContent.title || '立项依据';
                }
            }

            // 当前章节内容
            const currentSec = sectionMap[proposalSectionTab] || {};
            const content = currentSec.content || '';
            const wordCount = currentSec.word_count ?? (content ? content.length : 0);
            const citationCount = currentSec.citation_count ?? 0;
            const version = currentSec.version ?? 'v0.1';
            const status = currentSec.status || 'empty';

            html += '<div id="proposal-section-content">';
            html += '<div class="d-flex gap-8 mb-10 fw-wrap ai-center">';
            html += `<span class="label-bold">${escapeHtml(proposalSectionTab)}</span>`;
            html += sectionStatusBadge(status);
            html += `<span class="meta-sm">字数: ${escapeHtml(String(wordCount))}</span>`;
            html += `<span class="meta-sm">引用: ${escapeHtml(String(citationCount))}</span>`;
            html += `<span class="meta-sm">版本: ${escapeHtml(String(version))}</span>`;
            html += `<button onclick="Pipeline._writeSection('${escapeAttr(proposalSectionTab)}')" class="btn-outline btn-outline--accent" style="padding:4px 10px;font-size:0.78rem;margin-left:auto;" tabindex="0" role="button" aria-label="撰写该章节">✍️ 撰写</button>`;
            html += `<button onclick="Pipeline._editSection('${escapeAttr(proposalSectionTab)}')" class="btn-outline" style="padding:4px 10px;font-size:0.78rem;" tabindex="0" role="button" aria-label="编辑章节">✎ 编辑</button>`;
            html += '</div>';

            if (content) {
                html += `<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;font-size:0.85rem;line-height:1.7;color:var(--text-primary);max-height:400px;overflow-y:auto;">${renderMarkdown(content)}</div>`;
            } else {
                html += '<div class="state-empty" style="padding:30px;"><div style="font-size:1.4rem;margin-bottom:6px;">✍️</div><p>该章节尚未撰写</p><p class="meta-sm" style="margin-top:4px;">点击「撰写」生成初稿，或「编辑」手动输入</p></div>';
            }
            html += '</div>';

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载申请书失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    function _switchSection(secName) {
        proposalSectionTab = secName;
        // 更新标签高亮
        document.querySelectorAll('[data-section]').forEach(btn => {
            const isActive = btn.dataset.section === secName;
            btn.style.borderBottom = isActive ? '2px solid var(--accent-color)' : '2px solid transparent';
            btn.style.color = isActive ? 'var(--accent-color)' : 'var(--text-secondary)';
        });
        // 重新渲染章节内容
        const container = document.getElementById('pipeline-body');
        if (container) renderProposal(container);
    }

    async function _writeSection(secName) {
        if (!await confirmModal(`撰写章节「${secName}」？将使用 LLM 基于问题框架和文献生成初稿。`, '撰写')) return;
        showToast(`◐ 正在撰写「${secName}」…`, 'info');
        try {
            const result = await apiPost(`${pidPath()}/proposal/sections/${encodeURIComponent(secName)}/write`, {});
            showToast(`✓ 章节已撰写${result.word_count ? '（' + result.word_count + ' 字）' : ''}`, 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '撰写章节');
        }
    }

    async function _handleWriteAll() {
        if (!await confirmModal('撰写全部章节？这将依次生成所有申请书章节，可能需要较长时间。', '撰写全部')) return;
        showToast('◐ 正在撰写全部章节…', 'info', 5000);
        try {
            const result = await apiPost(`${pidPath()}/proposal/write-all`, {});
            const count = result.written ? result.written.length : 0;
            showToast(`✓ 已撰写 ${count} 个章节`, 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '撰写全部');
        }
    }

    function _editSection(secName) {
        // 先获取当前章节内容
        const sectionMap = {};
        for (const s of proposalSections) {
            const name = s.section || s.name || s.title || '';
            sectionMap[name] = s;
        }
        const sec = sectionMap[secName] || {};
        const content = sec.content || '';

        const html = `<div class="modal--xl">
            <h3 class="modal-title">✎ 编辑章节: ${escapeHtml(secName)}</h3>
            <div class="modal-form">
                <textarea id="pl-section-editor" rows="16" class="field-textarea" style="font-family:monospace;font-size:0.82rem;" aria-label="章节内容编辑器">${escapeHtml(content)}</textarea>
                <div class="meta-sm">支持 Markdown 格式</div>
                <div class="modal-btn-row">
                    <button id="pl-section-save" class="btn-confirm">💾 保存</button>
                    <button id="pl-section-cancel" class="btn-ghost-cancel">取消</button>
                </div>
            </div>
        </div>`;
        showModal(html);
        document.getElementById('pl-section-cancel').onclick = () => closeModal('modal-overlay');
        document.getElementById('pl-section-save').onclick = async () => {
            const newContent = document.getElementById('pl-section-editor').value;
            const btn = document.getElementById('pl-section-save');
            setLoading(btn, true, '◐ 保存中…');
            try {
                await apiPut(`${pidPath()}/proposal/sections/${encodeURIComponent(secName)}`, { content: newContent });
                showToast('✓ 章节已保存', 'success');
                closeModal('modal-overlay');
                await renderTab();
            } catch (e) {
                handleApiError(e, '保存章节');
                setLoading(btn, false);
            }
        };
    }

    async function _exportProposal() {
        try {
            const data = await apiGet(`${pidPath()}/proposal/export`);
            const content = data.content || '';
            const blob = new Blob([content], { type: 'text/markdown' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `proposal-${currentProposalId}.md`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出申请书', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 6. 自检优化面板
    // ============================================

    async function renderInspection(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载自检报告…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/inspection/report`);
                inspectionReport = data;
            } catch (e) {
                if (e.message.includes('404')) {
                    inspectionReport = null;
                } else {
                    throw e;
                }
            }

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._handleRunInspection()" class="btn-top-action" tabindex="0" role="button" aria-label="运行自检">🔄 运行自检</button>`;
            html += `<button onclick="Pipeline._exportInspection()" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出自检报告">📤 导出</button>`;
            html += '</div>';

            if (!inspectionReport) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">🔍</div><p>暂无自检报告</p><p class="meta-sm" style="margin-top:4px;">点击「运行自检」对申请书进行多维度检查</p></div>';
                container.innerHTML = html;
                return;
            }

            // 六维评分
            const dimensions = inspectionReport.dimensions || inspectionReport.scores || {};
            const dimKeys = Object.keys(dimensions);
            if (dimKeys.length) {
                html += '<div style="margin-bottom:16px;">';
                html += '<div class="label-bold-mb4">📊 六维评分</div>';
                html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;">';
                for (const [k, v] of Object.entries(dimensions)) {
                    const score = typeof v === 'object' ? (v.score ?? 0) : v;
                    const scoreNum = typeof score === 'number' ? score : parseFloat(score) || 0;
                    const color = scoreNum >= 0.8 ? 'var(--success-color)' : scoreNum >= 0.6 ? 'var(--warning-color)' : 'var(--error-color)';
                    html += `<div class="stat-card--sm" style="--card-edge:${color};">`;
                    html += `<div class="meta-xs">${escapeHtml(k)}</div>`;
                    html += `<div style="font-size:1.1rem;font-weight:600;color:${color};">${escapeHtml(String(score))}</div>`;
                    if (typeof v === 'object' && v.max) {
                        html += `<div class="meta-xs">/${escapeHtml(String(v.max))}</div>`;
                    }
                    html += '</div>';
                }
                html += '</div>';

                // 评分条形图
                html += '<div style="margin-top:12px;padding:12px;background:var(--bg-secondary);border-radius:6px;">';
                for (const [k, v] of Object.entries(dimensions)) {
                    const score = typeof v === 'object' ? (v.score ?? 0) : v;
                    const scoreNum = typeof score === 'number' ? score : parseFloat(score) || 0;
                    const pct = Math.round(scoreNum * 100);
                    const color = scoreNum >= 0.8 ? 'var(--success-color)' : scoreNum >= 0.6 ? 'var(--warning-color)' : 'var(--error-color)';
                    html += `<div style="margin-bottom:6px;">`;
                    html += `<div class="d-flex jc-between ai-center" style="margin-bottom:2px;"><span class="meta-sm">${escapeHtml(k)}</span><span class="meta-sm" style="color:${color};font-weight:600;">${pct}%</span></div>`;
                    html += `<div style="height:6px;background:var(--bg-tertiary);border-radius:3px;overflow:hidden;"><div style="height:100%;width:${pct}%;background:${color};border-radius:3px;transition:width 0.3s;"></div></div>`;
                    html += `</div>`;
                }
                html += '</div>';
                html += '</div>';
            }

            // 策略建议
            if (inspectionReport.strategy || inspectionReport.recommendation) {
                html += '<div style="margin-bottom:16px;padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--accent-color);">';
                html += '<div class="label-bold-mb4">💡 策略建议</div>';
                html += `<div style="font-size:0.82rem;color:var(--text-primary);">${renderMarkdown(inspectionReport.strategy || inspectionReport.recommendation || '')}</div>`;
                html += '</div>';
            }

            // 问题列表
            const issues = inspectionReport.issues || [];
            html += `<div class="label-bold-mb4">⚠ 问题列表（${issues.length}）</div>`;
            if (issues.length) {
                html += '<div class="col-gap8">';
                for (const iss of issues) {
                    const severity = iss.severity || 'suggestion';
                    html += `<div class="pad-10 bg-secondary br-6 border-default">`;
                    html += '<div class="d-flex gap-8 ai-center fw-wrap mb-4">';
                    html += issueSeverityBadge(severity);
                    if (iss.section) html += `<span class="chip">${escapeHtml(iss.section)}</span>`;
                    if (iss.id) html += `<span class="meta-xs">#${escapeHtml(String(iss.id))}</span>`;
                    html += '</div>';
                    html += `<div style="font-size:0.82rem;color:var(--text-primary);">${escapeHtml(iss.description || iss.message || '')}</div>`;
                    if (iss.suggestion || iss.fix) {
                        html += `<div class="meta-sm-mt" style="color:var(--accent-color);">建议: ${escapeHtml(iss.suggestion || iss.fix || '')}</div>`;
                    }
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<p class="meta-sm-pad8">未发现问题</p>';
            }

            // 迭代历史
            const iterations = inspectionReport.iterations || inspectionReport.history || [];
            if (iterations.length) {
                html += '<div style="margin-top:16px;">';
                html += `<div class="label-bold-mb4">📅 迭代历史（${iterations.length}）</div>`;
                html += '<div style="max-height:200px;overflow-y:auto;padding-left:20px;position:relative;">';
                html += '<div style="position:absolute;left:7px;top:4px;bottom:4px;width:2px;background:var(--border-color);"></div>';
                for (const it of iterations.slice(-15).reverse()) {
                    const itTime = (it.timestamp || it.time || '').slice(0, 16);
                    html += '<div style="position:relative;padding-bottom:8px;">';
                    html += `<div style="position:absolute;left:-17px;top:4px;width:10px;height:10px;border-radius:50%;background:var(--accent-color);border:2px solid var(--bg-primary);"></div>`;
                    html += `<div class="meta-xs">${escapeHtml(itTime)}</div>`;
                    const summary = it.summary || it.action || it.event || '';
                    html += `<div style="font-size:0.78rem;color:var(--text-primary);">${escapeHtml(summary)}</div>`;
                    if (it.issue_count !== undefined) {
                        html += `<div class="meta-xs">问题数: ${escapeHtml(String(it.issue_count))}</div>`;
                    }
                    html += '</div>';
                }
                html += '</div>';
                html += '</div>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载自检报告失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    async function _handleRunInspection() {
        if (!await confirmModal('运行自检？将对申请书进行六维度检查，可能需要较长时间。', '运行自检')) return;
        showToast('◐ 正在运行自检…', 'info', 5000);
        try {
            const result = await apiPost(`${pidPath()}/inspection/run`, {});
            const issueCount = result.issues ? result.issues.length : 0;
            showToast(`✓ 自检完成，发现 ${issueCount} 个问题`, issueCount > 0 ? 'warning' : 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '运行自检');
        }
    }

    async function _exportInspection() {
        try {
            const data = await apiGet(`${pidPath()}/inspection/export`);
            const content = data.content || '';
            const blob = new Blob([content], { type: 'text/markdown' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `inspection-${currentProposalId}.md`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出自检报告', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 7. 文献引用面板
    // ============================================

    async function renderCitations(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载文献引用…</p>';
        try {
            let data;
            try {
                data = await apiGet(`${pidPath()}/citations`);
                citationsList = data.citations || [];
            } catch (e) {
                if (e.message.includes('404')) {
                    citationsList = [];
                } else {
                    throw e;
                }
            }

            // 统计
            const total = citationsList.length;
            const cited = citationsList.filter(c => c.cited || c.cited_in).length;
            const uncited = total - cited;

            let html = '<div class="d-flex gap-8 mb-14 fw-wrap">';
            html += `<button onclick="Pipeline._addCitation()" class="btn-top-action" tabindex="0" role="button" aria-label="添加文献">+ 添加文献</button>`;
            html += `<button onclick="Pipeline._exportCitations('json')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 JSON">📋 JSON</button>`;
            html += `<button onclick="Pipeline._exportCitations('markdown')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 Markdown">📄 MD</button>`;
            html += `<button onclick="Pipeline._exportCitations('bibtex')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 BibTeX">🏷️ BibTeX</button>`;
            html += '</div>';

            // 统计卡
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:16px;">';
            html += `<div class="stat-card--sm" style="--card-edge:var(--info-color);"><div class="meta-xs">总引用</div><div class="stat-card__value">${escapeHtml(String(total))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--success-color);"><div class="meta-xs">已引用</div><div class="stat-card__value">${escapeHtml(String(cited))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--warning-color);"><div class="meta-xs">未引用</div><div class="stat-card__value">${escapeHtml(String(uncited))}</div></div>`;
            html += '</div>';

            // 引用列表
            if (citationsList.length) {
                html += '<div class="col-gap6">';
                for (const c of citationsList) {
                    const cType = c.type || 'other';
                    const cId = c.citation_id || c.id || '';
                    const isCited = c.cited || c.cited_in;
                    html += `<div class="pad-8 bg-secondary br-6 border-default" style="border-left:3px solid ${isCited ? 'var(--success-color)' : 'var(--text-tertiary)'};">`;
                    html += '<div class="d-flex gap-8 ai-start fw-wrap">';
                    html += citationTypeBadge(cType);
                    if (isCited) {
                        html += `<span class="chip" style="background:var(--success-color);color:#fff;">✓ 已引用</span>`;
                    } else {
                        html += `<span class="chip">○ 未引用</span>`;
                    }
                    if (c.year) html += `<span class="meta-xs">${escapeHtml(String(c.year))}</span>`;
                    html += '</div>';
                    // 格式化引用
                    const citation = c.formatted || c.citation || c.title || '';
                    if (citation) {
                        html += `<div style="font-size:0.82rem;color:var(--text-primary);margin-top:4px;">${escapeHtml(citation)}</div>`;
                    }
                    if (c.authors) {
                        html += `<div class="meta-xs-mt">作者: ${escapeHtml(c.authors)}</div>`;
                    }
                    if (c.doi || c.url) {
                        html += `<div class="meta-xs">`;
                        if (c.doi) html += `DOI: ${escapeHtml(c.doi)} `;
                        if (c.url) html += `<a href="${escapeAttr(c.url)}" target="_blank" rel="noopener noreferrer">链接</a>`;
                        html += `</div>`;
                    }
                    // 操作
                    html += '<div class="d-flex gap-4 mt-4 fw-wrap">';
                    html += `<button onclick="Pipeline._editCitation('${esc(cId)}')" class="btn-xs" tabindex="0" role="button" aria-label="编辑文献">✎ 编辑</button>`;
                    html += `<button onclick="Pipeline._deleteCitation('${esc(cId)}')" class="btn-xs btn-outline--danger" tabindex="0" role="button" aria-label="删除文献">✕ 删除</button>`;
                    html += '</div>';
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">📚</div><p>暂无文献引用</p><p class="meta-sm" style="margin-top:4px;">点击「添加文献」手动添加，或撰写章节时自动关联</p></div>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载文献引用失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    function _addCitation() {
        const html = `<div class="modal--lg">
            <h3 class="modal-title">📚 添加文献</h3>
            <div class="modal-form">
                <select id="pc-type" class="field-select" aria-label="文献类型">
                    <option value="journal">期刊</option>
                    <option value="conference">会议</option>
                    <option value="book">书籍</option>
                    <option value="preprint">预印本</option>
                    <option value="thesis">学位论文</option>
                    <option value="other">其他</option>
                </select>
                <input type="text" id="pc-title" placeholder="标题（必填）" class="field-input" aria-label="文献标题">
                <input type="text" id="pc-authors" placeholder="作者（逗号分隔）" class="field-input" aria-label="作者">
                <div class="d-flex gap-8">
                    <input type="text" id="pc-year" placeholder="年份" class="field-input" style="flex:1;" aria-label="年份">
                    <input type="text" id="pc-doi" placeholder="DOI" class="field-input" style="flex:2;" aria-label="DOI">
                </div>
                <input type="text" id="pc-url" placeholder="URL（可选）" class="field-input" aria-label="URL">
                <textarea id="pc-formatted" placeholder="格式化引用（可选，留空则自动生成）" rows="2" class="field-textarea" aria-label="格式化引用"></textarea>
                <div class="modal-btn-row">
                    <button id="pc-confirm" class="btn-confirm">✓ 添加</button>
                    <button id="pc-cancel" class="btn-ghost-cancel">取消</button>
                </div>
            </div>
        </div>`;
        showModal(html);
        document.getElementById('pc-cancel').onclick = () => closeModal('modal-overlay');
        document.getElementById('pc-confirm').onclick = async () => {
            const title = document.getElementById('pc-title').value.trim();
            if (!title) { showToast('请填写标题', 'warning'); return; }
            const citation = {
                type: document.getElementById('pc-type').value,
                title,
                authors: document.getElementById('pc-authors').value.trim(),
                year: document.getElementById('pc-year').value.trim(),
                doi: document.getElementById('pc-doi').value.trim(),
                url: document.getElementById('pc-url').value.trim(),
                formatted: document.getElementById('pc-formatted').value.trim(),
            };
            const btn = document.getElementById('pc-confirm');
            setLoading(btn, true, '◐ 添加中…');
            try {
                await apiPost(`${pidPath()}/citations`, citation);
                showToast('✓ 文献已添加', 'success');
                closeModal('modal-overlay');
                await renderTab();
            } catch (e) {
                handleApiError(e, '添加文献');
                setLoading(btn, false);
            }
        };
    }

    async function _editCitation(cId) {
        try {
            const data = await apiGet(`${pidPath()}/citations/${encodeURIComponent(cId)}`);
            const c = data.citation || data;
            const html = `<div class="modal--lg">
                <h3 class="modal-title">✎ 编辑文献</h3>
                <div class="modal-form">
                    <select id="pc-type" class="field-select" aria-label="文献类型">
                        <option value="journal" ${c.type === 'journal' ? 'selected' : ''}>期刊</option>
                        <option value="conference" ${c.type === 'conference' ? 'selected' : ''}>会议</option>
                        <option value="book" ${c.type === 'book' ? 'selected' : ''}>书籍</option>
                        <option value="preprint" ${c.type === 'preprint' ? 'selected' : ''}>预印本</option>
                        <option value="thesis" ${c.type === 'thesis' ? 'selected' : ''}>学位论文</option>
                        <option value="other" ${c.type === 'other' ? 'selected' : ''}>其他</option>
                    </select>
                    <input type="text" id="pc-title" placeholder="标题" class="field-input" value="${escapeAttr(c.title || '')}" aria-label="文献标题">
                    <input type="text" id="pc-authors" placeholder="作者" class="field-input" value="${escapeAttr(c.authors || '')}" aria-label="作者">
                    <div class="d-flex gap-8">
                        <input type="text" id="pc-year" placeholder="年份" class="field-input" style="flex:1;" value="${escapeAttr(c.year || '')}" aria-label="年份">
                        <input type="text" id="pc-doi" placeholder="DOI" class="field-input" style="flex:2;" value="${escapeAttr(c.doi || '')}" aria-label="DOI">
                    </div>
                    <input type="text" id="pc-url" placeholder="URL" class="field-input" value="${escapeAttr(c.url || '')}" aria-label="URL">
                    <textarea id="pc-formatted" placeholder="格式化引用" rows="2" class="field-textarea" aria-label="格式化引用">${escapeHtml(c.formatted || c.citation || '')}</textarea>
                    <div class="modal-btn-row">
                        <button id="pc-confirm" class="btn-confirm">💾 保存</button>
                        <button id="pc-cancel" class="btn-ghost-cancel">取消</button>
                    </div>
                </div>
            </div>`;
            showModal(html);
            document.getElementById('pc-cancel').onclick = () => closeModal('modal-overlay');
            document.getElementById('pc-confirm').onclick = async () => {
                const citation = {
                    type: document.getElementById('pc-type').value,
                    title: document.getElementById('pc-title').value.trim(),
                    authors: document.getElementById('pc-authors').value.trim(),
                    year: document.getElementById('pc-year').value.trim(),
                    doi: document.getElementById('pc-doi').value.trim(),
                    url: document.getElementById('pc-url').value.trim(),
                    formatted: document.getElementById('pc-formatted').value.trim(),
                };
                const btn = document.getElementById('pc-confirm');
                setLoading(btn, true, '◐ 保存中…');
                try {
                    await apiPut(`${pidPath()}/citations/${encodeURIComponent(cId)}`, citation);
                    showToast('✓ 文献已更新', 'success');
                    closeModal('modal-overlay');
                    await renderTab();
                } catch (e) {
                    handleApiError(e, '更新文献');
                    setLoading(btn, false);
                }
            };
        } catch (e) {
            handleApiError(e, '加载文献');
        }
    }

    async function _deleteCitation(cId) {
        if (!await confirmModal('确定删除该文献引用？', '删除')) return;
        try {
            await apiDelete(`${pidPath()}/citations/${encodeURIComponent(cId)}`);
            showToast('✓ 文献已删除', 'success');
            await renderTab();
        } catch (e) {
            handleApiError(e, '删除文献');
        }
    }

    async function _exportCitations(format) {
        try {
            const data = await apiGet(`${pidPath()}/citations/export?format=${encodeURIComponent(format)}`);
            const content = data.content || '';
            const mimeMap = { json: 'application/json', markdown: 'text/markdown', bibtex: 'application/x-bibtex' };
            const extMap = { json: 'json', markdown: 'md', bibtex: 'bib' };
            const blob = new Blob([content], { type: mimeMap[format] || 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `citations-${currentProposalId}.${extMap[format] || 'txt'}`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出文献引用', 'success');
        } catch (e) {
            handleApiError(e, '导出');
        }
    }

    // ============================================
    // 8. 智能体团队面板
    // ============================================

    // 智能体状态标签
    const AGENT_STATUS_LABELS = {
        idle: { label: '空闲', color: 'var(--success-color)', icon: '○' },
        working: { label: '工作中', color: 'var(--accent-color)', icon: '◐' },
        blocked: { label: '阻塞', color: 'var(--warning-color)', icon: '⚠' },
        offline: { label: '离线', color: 'var(--text-tertiary)', icon: '✗' },
    };

    // 团队层级标签
    const AGENT_TIER_LABELS = {
        core: { label: '核心管线', desc: '六阶段管线核心智能体', icon: '🧭' },
        support: { label: '支撑团队', desc: '辅助与质量保障智能体', icon: '🛠️' },
        growth: { label: '成长槽位', desc: '可激活的扩展智能体', icon: '🌱' },
    };

    function agentStatusBadge(status) {
        const s = AGENT_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)', icon: '○' };
        return statusBadge(s.label, s.color);
    }

    function agentTierBadge(tier) {
        const s = AGENT_TIER_LABELS[tier] || { label: tier || '其他', color: 'var(--text-tertiary)' };
        return `<span class="chip" style="background:var(--bg-tertiary);color:var(--text-secondary);">${escapeHtml(s.icon || '')} ${escapeHtml(s.label)}</span>`;
    }

    // 渲染单个智能体卡片
    function _renderAgentCard(agent, isGrowth) {
        const aId = agent.agent_id || agent.id || '';
        const name = agent.name || agent.name_zh || '未命名';
        const nameEn = agent.name_en || agent.role || '';
        const desc = agent.description || agent.desc || '';
        const status = agent.status || 'idle';
        const tier = agent.tier || 'core';
        const stage = agent.stage !== undefined ? agent.stage : null;
        const capabilities = agent.capabilities || agent.skills || [];
        const currentTask = agent.current_task || agent.task || '';
        const blockReason = agent.block_reason || agent.reason || '';
        const tasksCompleted = agent.tasks_completed ?? agent.completed ?? 0;
        const tasksFailed = agent.tasks_failed ?? agent.failed ?? 0;
        const successRate = agent.success_rate !== undefined ? agent.success_rate : (tasksCompleted + tasksFailed > 0 ? Math.round(tasksCompleted / (tasksCompleted + tasksFailed) * 100) : 100);
        const dimStyle = isGrowth ? 'opacity:0.65;' : '';

        let html = `<div class="pad-10 bg-secondary br-6 border-default" style="border-left:3px solid var(--accent-color);${dimStyle}">`;
        // 头部：名称 + 状态
        html += '<div class="d-flex jc-between ai-start gap-6 fw-wrap">';
        html += `<div><div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);">${escapeHtml(name)}</div>`;
        if (nameEn) html += `<div class="meta-xs">${escapeHtml(nameEn)}</div></div>`;
        else html += '</div>';
        html += agentStatusBadge(status);
        html += '</div>';

        // 描述
        if (desc) {
            html += `<div class="meta-sm" style="margin-top:4px;color:var(--text-secondary);">${escapeHtml(desc)}</div>`;
        }

        html += '<div style="border-top:1px solid var(--border-color);margin:6px 0;"></div>';

        // 阶段
        if (stage !== null) {
            const stageName = STAGE_NAMES[stage] || `阶段 ${stage}`;
            html += `<div class="meta-xs">阶段: ${escapeHtml(String(stage))} ${escapeHtml(stageName)}</div>`;
        }
        // 当前任务 / 阻塞原因
        if (status === 'working' && currentTask) {
            html += `<div class="meta-xs" style="color:var(--accent-color);">当前任务: ${escapeHtml(currentTask)}</div>`;
        } else if (status === 'blocked' && blockReason) {
            html += `<div class="meta-xs" style="color:var(--warning-color);">阻塞原因: ${escapeHtml(blockReason)}</div>`;
        }

        // 能力
        if (capabilities && capabilities.length) {
            html += '<div class="meta-xs" style="margin-top:4px;">能力:</div>';
            html += '<div style="margin:2px 0 4px 0;">';
            for (const cap of capabilities) {
                html += `<span class="chip" style="font-size:0.7rem;">${escapeHtml(cap)}</span> `;
            }
            html += '</div>';
        }

        html += '<div style="border-top:1px solid var(--border-color);margin:6px 0;"></div>';

        // 任务统计
        html += `<div class="meta-xs">任务: ${escapeHtml(String(tasksCompleted))} 完成 | ${escapeHtml(String(successRate))}% 成功率</div>`;

        // 操作按钮
        html += '<div class="d-flex gap-4 mt-4 fw-wrap">';
        if (isGrowth) {
            html += `<button onclick="Pipeline._activateAgent('${esc(aId)}')" class="btn-xs btn-outline--accent" tabindex="0" role="button" aria-label="激活智能体">⚡ 激活</button>`;
            html += `<button onclick="Pipeline._viewAgentDetail('${esc(aId)}')" class="btn-xs" tabindex="0" role="button" aria-label="查看智能体详情">📋 详情</button>`;
        } else {
            html += `<button onclick="Pipeline._assignAgentTask('${esc(aId)}')" class="btn-xs btn-outline--accent" tabindex="0" role="button" aria-label="分配任务">📥 分配任务</button>`;
            html += `<button onclick="Pipeline._viewAgentDetail('${esc(aId)}')" class="btn-xs" tabindex="0" role="button" aria-label="查看智能体详情">📋 详情</button>`;
        }
        html += '</div>';
        html += '</div>';
        return html;
    }

    async function renderAgents(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载智能体团队…</p>';
        try {
            let team, overview;
            try {
                [team, overview] = await Promise.all([
                    apiGet('/api/pipeline/agents'),
                    apiGet('/api/pipeline/agents/overview'),
                ]);
            } catch (e) {
                // 后端尚未实现时给出友好提示
                if (e.message.includes('404') || e.message.includes('500')) {
                    container.innerHTML = `<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">🤖</div><p>智能体团队接口暂未启用</p><p class="meta-sm" style="margin-top:4px;">请确认后端已实现 /api/pipeline/agents 路由</p></div>`;
                    return;
                }
                throw e;
            }
            agentTeamData = team;
            agentOverviewStats = overview;

            const agents = team.agents || team.members || team || [];
            const stats = overview || team.overview || {};
            const total = stats.total ?? agents.length;
            const idle = stats.idle ?? agents.filter(a => (a.status || 'idle') === 'idle').length;
            const working = stats.working ?? agents.filter(a => a.status === 'working').length;
            const offline = stats.offline ?? agents.filter(a => a.status === 'offline').length;

            // 分层
            const coreAgents = agents.filter(a => (a.tier || 'core') === 'core');
            const supportAgents = agents.filter(a => a.tier === 'support');
            const growthAgents = agents.filter(a => a.tier === 'growth');

            let html = '';

            // 团队概览头部
            html += '<div style="margin-bottom:16px;">';
            html += '<div class="d-flex ai-center gap-10 mb-10 fw-wrap">';
            html += '<span style="font-size:1rem;font-weight:600;">🤖 林赛研究管线团队</span>';
            html += `<button onclick="Pipeline._refreshAgents()" class="btn-outline btn-outline--info" style="padding:4px 10px;font-size:0.78rem;" tabindex="0" role="button" aria-label="刷新团队数据">🔄 刷新</button>`;
            html += `<button onclick="Pipeline._addAgent()" class="btn-top-action" style="padding:4px 10px;font-size:0.78rem;" tabindex="0" role="button" aria-label="添加团队成员">+ 添加成员</button>`;
            html += '</div>';
            // 统计卡
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;">';
            html += `<div class="stat-card--sm" style="--card-edge:var(--info-color);"><div class="meta-xs">总成员数</div><div class="stat-card__value">${escapeHtml(String(total))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--success-color);"><div class="meta-xs">空闲</div><div class="stat-card__value">${escapeHtml(String(idle))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--accent-color);"><div class="meta-xs">工作中</div><div class="stat-card__value">${escapeHtml(String(working))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--text-tertiary);"><div class="meta-xs">离线</div><div class="stat-card__value">${escapeHtml(String(offline))}</div></div>`;
            html += '</div>';
            html += '</div>';

            // 核心管线层
            html += _renderAgentTierGroup('core', coreAgents, false);
            // 支撑团队层
            html += _renderAgentTierGroup('support', supportAgents, false);
            // 成长槽位层
            html += _renderAgentTierGroup('growth', growthAgents, true);

            if (!agents.length) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">🤖</div><p>暂无团队成员</p><p class="meta-sm" style="margin-top:4px;">点击「添加成员」创建新的智能体</p></div>';
            }

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载智能体团队失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    function _renderAgentTierGroup(tier, agents, isGrowth) {
        const t = AGENT_TIER_LABELS[tier] || { label: tier || '其他', desc: '', icon: '▸' };
        let html = '<div style="margin-bottom:16px;">';
        html += `<div class="label-sm-mb8">${escapeHtml(t.icon || '')} ${escapeHtml(t.label)}`;
        html += `<span class="meta-xs" style="margin-left:6px;">${escapeHtml(t.desc || '')} (${escapeHtml(String(agents.length))})</span>`;
        html += '</div>';
        if (agents.length) {
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px;">';
            for (const a of agents) {
                html += _renderAgentCard(a, isGrowth);
            }
            html += '</div>';
        } else {
            html += `<div class="state-empty" style="padding:16px;"><p class="meta-sm">暂无${escapeHtml(t.label)}成员</p></div>`;
        }
        html += '</div>';
        return html;
    }

    async function _refreshAgents() {
        agentTeamData = null;
        agentOverviewStats = null;
        await renderTab();
        showToast('✓ 团队数据已刷新', 'success');
    }

    async function _viewAgentDetail(aId) {
        try {
            const data = await apiGet(`/api/pipeline/agents/${encodeURIComponent(aId)}`);
            const agent = data.agent || data;
            const name = agent.name || agent.name_zh || '未命名';
            const nameEn = agent.name_en || agent.role || '';
            const desc = agent.description || agent.desc || '';
            const status = agent.status || 'idle';
            const tier = agent.tier || 'core';
            const stage = agent.stage !== undefined ? agent.stage : null;
            const capabilities = agent.capabilities || agent.skills || [];
            const currentTask = agent.current_task || agent.task || '';
            const blockReason = agent.block_reason || agent.reason || '';
            const tasksCompleted = agent.tasks_completed ?? agent.completed ?? 0;
            const tasksFailed = agent.tasks_failed ?? agent.failed ?? 0;
            const successRate = agent.success_rate !== undefined ? agent.success_rate : (tasksCompleted + tasksFailed > 0 ? Math.round(tasksCompleted / (tasksCompleted + tasksFailed) * 100) : 100);
            const avgDuration = agent.avg_duration ?? agent.average_duration ?? '';
            const recentTasks = agent.recent_tasks || agent.tasks || [];

            let html = `<div class="modal--lg"><h3 class="modal-title">🤖 ${escapeHtml(name)}</h3>`;
            if (nameEn) html += `<div class="meta-sm" style="margin-bottom:8px;">${escapeHtml(nameEn)}</div>`;
            html += '<div class="d-flex gap-6 fw-wrap mb-10">';
            html += agentStatusBadge(status);
            html += agentTierBadge(tier);
            if (stage !== null) html += `<span class="chip">阶段 ${escapeHtml(String(stage))}: ${escapeHtml(STAGE_NAMES[stage] || '')}</span>`;
            html += '</div>';

            if (desc) {
                html += `<div style="padding:8px;background:var(--bg-secondary);border-radius:6px;margin-bottom:10px;font-size:0.82rem;">${escapeHtml(desc)}</div>`;
            }

            // 当前状态详情
            if (status === 'working' && currentTask) {
                html += `<div style="padding:6px 8px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--accent-color);margin-bottom:10px;"><div class="meta-xs">当前任务</div><div class="meta-sm">${escapeHtml(currentTask)}</div></div>`;
            } else if (status === 'blocked' && blockReason) {
                html += `<div style="padding:6px 8px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--warning-color);margin-bottom:10px;"><div class="meta-xs">阻塞原因</div><div class="meta-sm">${escapeHtml(blockReason)}</div></div>`;
            }

            // 能力列表
            if (capabilities && capabilities.length) {
                html += '<div class="label-sm-mb8">能力</div><div style="margin-bottom:10px;">';
                for (const cap of capabilities) {
                    html += `<span class="chip">${escapeHtml(cap)}</span> `;
                }
                html += '</div>';
            }

            // 性能指标
            html += '<div class="label-sm-mb8">性能指标</div>';
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px;margin-bottom:10px;">';
            html += `<div class="stat-card--sm" style="--card-edge:var(--success-color);"><div class="meta-xs">已完成</div><div class="stat-card__value">${escapeHtml(String(tasksCompleted))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--error-color);"><div class="meta-xs">失败</div><div class="stat-card__value">${escapeHtml(String(tasksFailed))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--accent-color);"><div class="meta-xs">成功率</div><div class="stat-card__value">${escapeHtml(String(successRate))}%</div></div>`;
            if (avgDuration) {
                html += `<div class="stat-card--sm" style="--card-edge:var(--info-color);"><div class="meta-xs">平均耗时</div><div class="stat-card__value">${escapeHtml(String(avgDuration))}</div></div>`;
            }
            html += '</div>';

            // 近期任务
            if (recentTasks && recentTasks.length) {
                html += '<div class="label-sm-mb8">近期任务</div>';
                html += '<div style="max-height:160px;overflow-y:auto;margin-bottom:10px;">';
                for (const t of recentTasks) {
                    const tDesc = typeof t === 'string' ? t : (t.description || t.task || t.title || '');
                    const tStatus = typeof t === 'object' ? (t.status || '') : '';
                    const tColor = tStatus === 'completed' ? 'var(--success-color)' : tStatus === 'failed' ? 'var(--error-color)' : 'var(--text-tertiary)';
                    html += `<div style="padding:4px 8px;background:var(--bg-secondary);border-radius:4px;margin-bottom:4px;font-size:0.78rem;border-left:2px solid ${tColor};">${escapeHtml(tDesc)}${tStatus ? ` <span class="meta-xs">[${escapeHtml(tStatus)}]</span>` : ''}</div>`;
                }
                html += '</div>';
            }

            // 操作按钮
            html += '<div class="d-flex gap-6 fw-wrap">';
            html += `<button id="ad-assign-btn" onclick="Pipeline._assignAgentTask('${esc(aId)}')" class="btn-confirm" tabindex="0" role="button" aria-label="分配任务">📥 分配任务</button>`;
            html += `<button id="ad-complete-btn" onclick="Pipeline._completeAgentTask('${esc(aId)}')" class="btn-outline btn-outline--success" tabindex="0" role="button" aria-label="标记任务完成">✓ 标记完成</button>`;
            html += `<button id="ad-upgrade-btn" onclick="Pipeline._upgradeAgent('${esc(aId)}')" class="btn-outline btn-outline--accent" tabindex="0" role="button" aria-label="升级能力">⬆ 升级能力</button>`;
            html += `<button onclick="closeModal('modal-overlay')" class="btn-ghost-cancel" tabindex="0" role="button" aria-label="关闭">关闭</button>`;
            html += '</div>';
            html += '</div>';

            showModal(html);
        } catch (e) {
            handleApiError(e, '加载智能体详情');
        }
    }

    async function _assignAgentTask(aId) {
        const task = await promptModal('请输入要分配的任务描述:', '任务描述');
        if (!task) return;
        try {
            await apiPost(`/api/pipeline/agents/${encodeURIComponent(aId)}/assign`, { task });
            showToast('✓ 任务已分配', 'success');
            closeModal('modal-overlay');
            await renderTab();
        } catch (e) {
            handleApiError(e, '分配任务');
        }
    }

    async function _completeAgentTask(aId) {
        if (!await confirmModal('确认将该智能体的当前任务标记为完成？', '标记完成')) return;
        try {
            await apiPost(`/api/pipeline/agents/${encodeURIComponent(aId)}/complete`, {});
            showToast('✓ 任务已标记完成', 'success');
            closeModal('modal-overlay');
            await renderTab();
        } catch (e) {
            handleApiError(e, '标记完成');
        }
    }

    async function _upgradeAgent(aId) {
        const cap = await promptModal('请输入要新增的能力（多个用逗号分隔）:', '新能力');
        if (!cap) return;
        const capabilities = cap.split(/[,，]/).map(s => s.trim()).filter(Boolean);
        try {
            await apiPost(`/api/pipeline/agents/${encodeURIComponent(aId)}/upgrade`, { capabilities });
            showToast('✓ 能力已升级', 'success');
            closeModal('modal-overlay');
            await renderTab();
        } catch (e) {
            handleApiError(e, '升级能力');
        }
    }

    async function _activateAgent(aId) {
        // 成长槽位激活需要委托模块和能力
        const html = `<div class="modal--lg">
            <h3 class="modal-title">⚡ 激活成长槽位智能体</h3>
            <div class="modal-form">
                <input type="text" id="ag-delegate" placeholder="委托模块（必填，如 deepxiv_knowledge）" class="field-input" aria-label="委托模块">
                <textarea id="ag-caps" placeholder="能力列表（每行一个）" rows="4" class="field-textarea" aria-label="能力列表"></textarea>
                <div class="modal-btn-row">
                    <button id="ag-confirm" class="btn-confirm">⚡ 激活</button>
                    <button id="ag-cancel" class="btn-ghost-cancel">取消</button>
                </div>
            </div>
        </div>`;
        showModal(html);
        document.getElementById('ag-cancel').onclick = () => closeModal('modal-overlay');
        document.getElementById('ag-confirm').onclick = async () => {
            const delegateModule = document.getElementById('ag-delegate').value.trim();
            if (!delegateModule) { showToast('请填写委托模块', 'warning'); return; }
            const capsText = document.getElementById('ag-caps').value.trim();
            const capabilities = capsText ? capsText.split('\n').map(s => s.trim()).filter(Boolean) : [];
            const btn = document.getElementById('ag-confirm');
            setLoading(btn, true, '◐ 激活中…');
            try {
                await apiPost(`/api/pipeline/agents/${encodeURIComponent(aId)}/activate`, { delegate_module: delegateModule, capabilities });
                showToast('✓ 智能体已激活', 'success');
                closeModal('modal-overlay');
                await renderTab();
            } catch (e) {
                handleApiError(e, '激活智能体');
                setLoading(btn, false);
            }
        };
    }

    function _addAgent() {
        const html = `<div class="modal--lg">
            <h3 class="modal-title">🤖 添加团队成员</h3>
            <div class="modal-form">
                <input type="text" id="aa-name" placeholder="智能体名称（必填，中文）" class="field-input" aria-label="智能体名称">
                <input type="text" id="aa-role" placeholder="角色/英文名（可选）" class="field-input" aria-label="角色">
                <select id="aa-tier" class="field-select" aria-label="团队层级">
                    <option value="core">核心管线</option>
                    <option value="support">支撑团队</option>
                    <option value="growth">成长槽位</option>
                </select>
                <select id="aa-stage" class="field-select" aria-label="负责阶段">
                    <option value="">- 无固定阶段 -</option>
                    <option value="0">0 方向校准</option>
                    <option value="1">1 文献调研</option>
                    <option value="2">2 课题凝练</option>
                    <option value="3">3 科学问题构建</option>
                    <option value="4">4 申请书撰写</option>
                    <option value="5">5 自检优化</option>
                </select>
                <textarea id="aa-desc" placeholder="描述（可选）" rows="2" class="field-textarea" aria-label="描述"></textarea>
                <textarea id="aa-caps" placeholder="能力列表（每行一个，可选）" rows="3" class="field-textarea" aria-label="能力列表"></textarea>
                <div class="modal-btn-row">
                    <button id="aa-confirm" class="btn-confirm">✓ 添加</button>
                    <button id="aa-cancel" class="btn-ghost-cancel">取消</button>
                </div>
            </div>
        </div>`;
        showModal(html);
        document.getElementById('aa-cancel').onclick = () => closeModal('modal-overlay');
        document.getElementById('aa-confirm').onclick = async () => {
            const name = document.getElementById('aa-name').value.trim();
            if (!name) { showToast('请填写智能体名称', 'warning'); return; }
            const role = document.getElementById('aa-role').value.trim();
            const tier = document.getElementById('aa-tier').value;
            const stageVal = document.getElementById('aa-stage').value;
            const stage = stageVal === '' ? null : parseInt(stageVal, 10);
            const desc = document.getElementById('aa-desc').value.trim();
            const capsText = document.getElementById('aa-caps').value.trim();
            const capabilities = capsText ? capsText.split('\n').map(s => s.trim()).filter(Boolean) : [];
            const payload = { name, role, tier, description: desc, capabilities };
            if (stage !== null) payload.stage = stage;
            const btn = document.getElementById('aa-confirm');
            setLoading(btn, true, '◐ 添加中…');
            try {
                await apiPost('/api/pipeline/agents/add', payload);
                showToast('✓ 成员已添加', 'success');
                closeModal('modal-overlay');
                await renderTab();
            } catch (e) {
                handleApiError(e, '添加成员');
                setLoading(btn, false);
            }
        };
    }

    // ============================================
    // 9. 方法学手册面板
    // ============================================

    // 方法分类标签
    const METHOD_CATEGORY_LABELS = {
        theory: { label: '理论', color: 'var(--warning-color)' },
        computation: { label: '计算', color: 'var(--accent-color)' },
        experiment: { label: '实验', color: 'var(--success-color)' },
        analysis: { label: '分析', color: 'var(--info-color)' },
    };

    // 方法状态标签
    const METHOD_STATUS_LABELS = {
        generated: { label: '已生成', color: 'var(--info-color)' },
        reviewed: { label: '已审核', color: 'var(--success-color)' },
        enriched: { label: '已丰富', color: 'var(--accent-color)' },
        draft: { label: '草稿', color: 'var(--text-tertiary)' },
    };

    function methodCategoryBadge(category) {
        const s = METHOD_CATEGORY_LABELS[category] || { label: category || '其他', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    function methodStatusBadge(status) {
        const s = METHOD_STATUS_LABELS[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
        return statusBadge(s.label, s.color);
    }

    async function renderMethodology(container) {
        container.innerHTML = '<p class="state-loading">◐ 加载方法学手册…</p>';
        try {
            let data, stats;
            try {
                [data, stats] = await Promise.all([
                    apiGet(`${pidPath()}/methodology`),
                    apiGet(`${pidPath()}/methodology/stats`),
                ]);
            } catch (e) {
                if (e.message.includes('404')) {
                    methodologyData = null;
                    methodologyStats = null;
                } else {
                    throw e;
                }
            }
            if (data) {
                methodologyData = data;
                methodologyStats = stats;
            }

            const methods = (methodologyData && (methodologyData.methods || methodologyData)) || [];
            const methodList = Array.isArray(methods) ? methods : [];
            const s = methodologyStats || {};
            const methodCount = s.method_count ?? s.total ?? methodList.length;
            const totalWords = s.total_words ?? s.word_count ?? 0;
            const refCount = s.reference_count ?? s.citations ?? 0;

            let html = '';

            // 头部
            html += '<div class="d-flex gap-8 mb-14 fw-wrap ai-center">';
            html += '<span style="font-size:1rem;font-weight:600;">📖 方法学手册</span>';
            html += `<button onclick="Pipeline._generateMethodology()" class="btn-top-action" tabindex="0" role="button" aria-label="生成方法学手册">🔄 生成手册</button>`;
            html += `<button onclick="Pipeline._exportMethodology('markdown')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 Markdown">📄 MD</button>`;
            html += `<button onclick="Pipeline._exportMethodology('json')" class="btn-outline btn-outline--info" style="padding:6px 14px;font-size:0.82rem;" tabindex="0" role="button" aria-label="导出为 JSON">📋 JSON</button>`;
            html += '</div>';

            // 统计卡
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:16px;">';
            html += `<div class="stat-card--sm" style="--card-edge:var(--info-color);"><div class="meta-xs">方法数</div><div class="stat-card__value">${escapeHtml(String(methodCount))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--accent-color);"><div class="meta-xs">总字数</div><div class="stat-card__value">${escapeHtml(String(totalWords))}</div></div>`;
            html += `<div class="stat-card--sm" style="--card-edge:var(--success-color);"><div class="meta-xs">引用数</div><div class="stat-card__value">${escapeHtml(String(refCount))}</div></div>`;
            html += '</div>';

            if (!methodList.length) {
                html += '<div class="state-empty"><div style="font-size:1.6rem;margin-bottom:6px;">📖</div><p>暂无方法学内容</p><p class="meta-sm" style="margin-top:4px;">点击「生成手册」基于申请书研究方案自动生成</p></div>';
                container.innerHTML = html;
                return;
            }

            // 左右布局：方法列表 + 详情
            html += '<div style="display:flex;gap:12px;min-height:300px;">';
            // 左侧方法列表
            html += '<div style="flex:0 0 220px;max-width:220px;border-right:1px solid var(--border-color);padding-right:8px;overflow-y:auto;max-height:480px;">';
            html += '<div class="label-sm-mb8">方法列表</div>';
            for (const m of methodList) {
                const mName = m.name || m.method_name || m.title || '未命名';
                const mId = m.method_id || m.id || mName;
                const mCat = m.category || '';
                const mStatus = m.status || 'generated';
                const isActive = methodologySelectedMethod === mId || methodologySelectedMethod === mName;
                html += `<div onclick="Pipeline._selectMethod('${esc(mId)}')" style="padding:6px 8px;border-radius:4px;cursor:pointer;margin-bottom:4px;background:${isActive ? 'var(--bg-tertiary)' : 'transparent'};border-left:3px solid ${isActive ? 'var(--accent-color)' : 'transparent'};" tabindex="0" role="button" aria-label="选择方法 ${esc(mName)}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();Pipeline._selectMethod('${esc(mId)}')}">`;
                html += `<div style="font-size:0.82rem;font-weight:${isActive ? '600' : '400'};color:var(--text-primary);">${escapeHtml(mName)}</div>`;
                html += '<div class="d-flex gap-4 mt-2 fw-wrap">';
                if (mCat) html += methodCategoryBadge(mCat);
                html += methodStatusBadge(mStatus);
                html += '</div>';
                html += '</div>';
            }
            html += '</div>';

            // 右侧方法详情
            html += '<div style="flex:1;min-width:0;overflow-y:auto;max-height:480px;">';
            html += _renderMethodDetail(methodList, methodologySelectedMethod);
            html += '</div>';

            html += '</div>';

            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = `<p class="state-error">加载方法学手册失败: ${escapeHtml(e.message)}</p>`;
        }
    }

    function _renderMethodDetail(methodList, selectedId) {
        // 查找选中的方法
        let method = null;
        if (selectedId) {
            method = methodList.find(m => (m.method_id || m.id || m.name) === selectedId) || methodList.find(m => m.name === selectedId);
        }
        if (!method) method = methodList[0]; // 默认显示第一个
        if (!method) return '<div class="state-empty"><p class="meta-sm">请选择一个方法查看详情</p></div>';

        const mName = method.name || method.method_name || method.title || '未命名';
        const mNameEn = method.name_en || method.english_name || '';
        const mCat = method.category || '';
        const mExpertise = method.expertise_level || method.expertise || '';
        const mStatus = method.status || 'generated';
        const mBackground = method.theoretical_background || method.background || '';
        const mImpl = method.implementation || method.implementation_details || '';
        const mAnalysis = method.data_analysis || method.analysis_procedure || '';
        const mLimitations = method.limitations || '';
        const mRefs = method.references || method.key_references || [];
        const mKbLinks = method.kb_links || method.knowledge_base_links || [];
        const mRelated = method.related_methods || [];

        let html = '';
        // 标题
        html += '<div class="d-flex gap-6 fw-wrap ai-center mb-10">';
        html += `<span style="font-size:0.95rem;font-weight:600;color:var(--text-primary);">${escapeHtml(mName)}</span>`;
        if (mNameEn) html += `<span class="meta-sm">${escapeHtml(mNameEn)}</span>`;
        html += '</div>';

        // 标签
        html += '<div class="d-flex gap-6 fw-wrap mb-10">';
        if (mCat) html += methodCategoryBadge(mCat);
        html += methodStatusBadge(mStatus);
        if (mExpertise) html += `<span class="chip">熟练度: ${escapeHtml(mExpertise)}</span>`;
        html += `<button onclick="Pipeline._editMethod('${esc(mName)}')" class="btn-outline" style="padding:3px 8px;font-size:0.75rem;margin-left:auto;" tabindex="0" role="button" aria-label="编辑方法">✎ 编辑</button>`;
        html += '</div>';

        // 理论背景
        if (mBackground) {
            html += '<div class="label-sm-mb8">理论背景</div>';
            html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;margin-bottom:10px;font-size:0.82rem;line-height:1.6;max-height:200px;overflow-y:auto;">${renderMarkdown(mBackground)}</div>`;
        }

        // 实现细节
        if (mImpl) {
            html += '<div class="label-sm-mb8">实现细节</div>';
            html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;margin-bottom:10px;font-size:0.82rem;line-height:1.6;max-height:200px;overflow-y:auto;">${renderMarkdown(mImpl)}</div>`;
        }

        // 数据分析流程
        if (mAnalysis) {
            html += '<div class="label-sm-mb8">数据分析流程</div>';
            html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;margin-bottom:10px;font-size:0.82rem;line-height:1.6;max-height:200px;overflow-y:auto;">${renderMarkdown(mAnalysis)}</div>`;
        }

        // 局限性
        if (mLimitations) {
            html += '<div class="label-sm-mb8">局限性</div>';
            html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--warning-color);margin-bottom:10px;font-size:0.82rem;line-height:1.6;">${escapeHtml(mLimitations)}</div>`;
        }

        // 关键引用
        if (mRefs && mRefs.length) {
            html += '<div class="label-sm-mb8">关键引用</div>';
            html += '<div style="margin-bottom:10px;">';
            for (let i = 0; i < mRefs.length; i++) {
                const r = mRefs[i];
                const rText = typeof r === 'string' ? r : (r.citation || r.formatted || r.title || '');
                const rAnno = typeof r === 'object' ? (r.annotation || r.note || '') : '';
                html += `<div style="padding:4px 8px;background:var(--bg-secondary);border-radius:4px;margin-bottom:4px;font-size:0.78rem;">[${escapeHtml(String(i + 1))}] ${escapeHtml(rText)}`;
                if (rAnno) html += `<div class="meta-xs" style="margin-top:2px;color:var(--text-secondary);">${escapeHtml(rAnno)}</div>`;
                html += '</div>';
            }
            html += '</div>';
        }

        // KB 链接
        if (mKbLinks && mKbLinks.length) {
            html += '<div class="label-sm-mb8">知识库链接</div>';
            html += '<div class="d-flex gap-4 fw-wrap mb-10">';
            for (const link of mKbLinks) {
                const linkText = typeof link === 'string' ? link : (link.title || link.name || link.path || '');
                const linkPath = typeof link === 'object' ? (link.path || link.url || '') : '';
                if (linkPath) {
                    html += `<a href="${escapeAttr(linkPath)}" class="chip" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">🔗 ${escapeHtml(linkText)}</a> `;
                } else {
                    html += `<span class="chip">🔗 ${escapeHtml(linkText)}</span> `;
                }
            }
            html += '</div>';
        }

        // 相关方法
        if (mRelated && mRelated.length) {
            html += '<div class="label-sm-mb8">相关方法</div>';
            html += '<div class="d-flex gap-4 fw-wrap">';
            for (const rel of mRelated) {
                const relText = typeof rel === 'string' ? rel : (rel.name || rel.method || '');
                html += `<span class="chip">🔗 ${escapeHtml(relText)}</span> `;
            }
            html += '</div>';
        }

        if (!mBackground && !mImpl && !mAnalysis && !mLimitations && !mRefs.length && !mKbLinks.length && !mRelated.length) {
            html += '<div class="state-empty" style="padding:20px;"><p class="meta-sm">该方法暂无详细内容</p></div>';
        }

        return html;
    }

    function _selectMethod(mId) {
        methodologySelectedMethod = mId;
        // 仅重新渲染右侧详情，避免完整重载
        const container = document.getElementById('pipeline-body');
        if (container) renderMethodology(container);
    }

    async function _generateMethodology() {
        if (!await confirmModal('生成方法学手册？将基于申请书研究方案和文献调研自动生成，可能需要较长时间。', '生成')) return;
        showToast('◐ 正在生成方法学手册…', 'info', 5000);
        try {
            const result = await apiPost(`${pidPath()}/methodology/generate`, {});
            const count = result.method_count || result.generated || 0;
            showToast(`✓ 手册已生成${count ? '（' + count + ' 个方法）' : ''}`, 'success');
            methodologySelectedMethod = null;
            await renderTab();
        } catch (e) {
            handleApiError(e, '生成方法学手册');
        }
    }

    async function _exportMethodology(format) {
        try {
            const data = await apiGet(`${pidPath()}/methodology/export?format=${encodeURIComponent(format)}`);
            const content = data.content || '';
            const mimeMap = { json: 'application/json', markdown: 'text/markdown' };
            const extMap = { json: 'json', markdown: 'md' };
            const blob = new Blob([content], { type: mimeMap[format] || 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `methodology-${currentProposalId}.${extMap[format] || 'txt'}`;
            a.click();
            URL.revokeObjectURL(a.href);
            showToast('✓ 已导出方法学手册', 'success');
        } catch (e) {
            handleApiError(e, '导出方法学手册');
        }
    }

    function _editMethod(mName) {
        // 从缓存中查找方法
        const methods = (methodologyData && (methodologyData.methods || methodologyData)) || [];
        const methodList = Array.isArray(methods) ? methods : [];
        const method = methodList.find(m => (m.name || m.method_name || m.title) === mName) || {};
        const mBackground = method.theoretical_background || method.background || '';
        const mImpl = method.implementation || method.implementation_details || '';
        const mAnalysis = method.data_analysis || method.analysis_procedure || '';
        const mLimitations = method.limitations || '';

        const html = `<div class="modal--xl">
            <h3 class="modal-title">✎ 编辑方法: ${escapeHtml(mName)}</h3>
            <div class="modal-form">
                <div class="label-sm-mb4">理论背景</div>
                <textarea id="me-background" rows="4" class="field-textarea" style="font-size:0.8rem;" aria-label="理论背景">${escapeHtml(mBackground)}</textarea>
                <div class="label-sm-mb4">实现细节</div>
                <textarea id="me-impl" rows="4" class="field-textarea" style="font-size:0.8rem;" aria-label="实现细节">${escapeHtml(mImpl)}</textarea>
                <div class="label-sm-mb4">数据分析流程</div>
                <textarea id="me-analysis" rows="4" class="field-textarea" style="font-size:0.8rem;" aria-label="数据分析流程">${escapeHtml(mAnalysis)}</textarea>
                <div class="label-sm-mb4">局限性</div>
                <textarea id="me-limitations" rows="3" class="field-textarea" style="font-size:0.8rem;" aria-label="局限性">${escapeHtml(mLimitations)}</textarea>
                <div class="meta-sm">支持 Markdown 格式</div>
                <div class="modal-btn-row">
                    <button id="me-save" class="btn-confirm">💾 保存</button>
                    <button id="me-cancel" class="btn-ghost-cancel">取消</button>
                </div>
            </div>
        </div>`;
        showModal(html);
        document.getElementById('me-cancel').onclick = () => closeModal('modal-overlay');
        document.getElementById('me-save').onclick = async () => {
            const payload = {
                theoretical_background: document.getElementById('me-background').value,
                implementation: document.getElementById('me-impl').value,
                data_analysis: document.getElementById('me-analysis').value,
                limitations: document.getElementById('me-limitations').value,
            };
            const btn = document.getElementById('me-save');
            setLoading(btn, true, '◐ 保存中…');
            try {
                await apiPut(`${pidPath()}/methodology/${encodeURIComponent(mName)}`, payload);
                showToast('✓ 方法已更新', 'success');
                closeModal('modal-overlay');
                await renderTab();
            } catch (e) {
                handleApiError(e, '保存方法');
                setLoading(btn, false);
            }
        };
    }

    // ============================================
    // 模块定义
    // ============================================

    const Pipeline = {
        // 初始化（由 ModuleLoader 调用）
        init: function() {
            // 绑定工具栏按钮（如存在）
            const toolbarBtn = document.getElementById('toolbar-pipeline');
            if (toolbarBtn) {
                toolbarBtn.addEventListener('click', () => openPipelineManager());
            }
            // 绑定导航按钮（如存在）
            const navBtn = document.querySelector('[data-view="pipeline"]');
            if (navBtn) {
                navBtn.addEventListener('click', () => openPipelineManager());
            }
        },

        // 渲染当前面板
        render: function() {
            renderBody();
        },

        // 切换子面板
        switchTo: function(tabName) {
            activeTab = tabName;
            renderTabs();
            renderTab();
        },

        // 设置当前 proposal
        setProposal: function(proposalId) {
            currentProposalId = proposalId;
            const infoEl = document.getElementById('pipeline-proposal-info');
            if (infoEl) infoEl.textContent = `已加载: ${proposalId}`;
            activeTab = 'overview';
            // 方法学数据按 proposal_id 缓存，切换时重置
            methodologyData = null;
            methodologyStats = null;
            methodologySelectedMethod = null;
            renderTabs();
            renderBody();
        },

        // 刷新当前视图
        refresh: function() {
            renderTab();
        },

        // 打开面板
        open: function(proposalId) {
            openPipelineManager(proposalId);
        },

        // 关闭面板
        close: function() {
            closePipelineManager();
        },

        // ====== 内部方法（通过 Pipeline._xxx 调用） ======
        _showStageDetail: _showStageDetail,
        _handleAdvance: _handleAdvance,
        _handleRollback: _handleRollback,
        _handlePause: _handlePause,
        _handleResume: _handleResume,
        _handleGateCheck: _handleGateCheck,
        _handleAnalyzeGaps: _handleAnalyzeGaps,
        _exportGap: _exportGap,
        _handleGenerateTopics: _handleGenerateTopics,
        _selectTopic: _selectTopic,
        _refineTopic: _refineTopic,
        _viewTopicDetail: _viewTopicDetail,
        _exportTopics: _exportTopics,
        _handleConstructQuestions: _handleConstructQuestions,
        _refineQuestion: _refineQuestion,
        _viewQuestionEvidence: _viewQuestionEvidence,
        _exportQuestions: _exportQuestions,
        _switchSection: _switchSection,
        _writeSection: _writeSection,
        _handleWriteAll: _handleWriteAll,
        _editSection: _editSection,
        _exportProposal: _exportProposal,
        _handleRunInspection: _handleRunInspection,
        _exportInspection: _exportInspection,
        _addCitation: _addCitation,
        _editCitation: _editCitation,
        _deleteCitation: _deleteCitation,
        _exportCitations: _exportCitations,
        // ====== 方法学手册 ======
        _selectMethod: _selectMethod,
        _generateMethodology: _generateMethodology,
        _exportMethodology: _exportMethodology,
        _editMethod: _editMethod,
        // ====== 智能体团队 ======
        _refreshAgents: _refreshAgents,
        _viewAgentDetail: _viewAgentDetail,
        _assignAgentTask: _assignAgentTask,
        _completeAgentTask: _completeAgentTask,
        _upgradeAgent: _upgradeAgent,
        _activateAgent: _activateAgent,
        _addAgent: _addAgent,
    };

    // 暴露全局函数（与 research.js 的 openResearchManager 模式一致）
    window.openPipelineManager = openPipelineManager;
    window.closePipelineManager = closePipelineManager;

    // ============================================
    // 注册模块
    // ============================================
    if (typeof ModuleLoader !== 'undefined') {
        ModuleLoader.register('pipeline', () => {
            if (typeof Pipeline.init === 'function') Pipeline.init();
        });
    } else {
        window.Pipeline = Pipeline;
    }

    // 即使 ModuleLoader 存在，也暴露 Pipeline 对象供 onclick 调用
    window.Pipeline = Pipeline;

})();
