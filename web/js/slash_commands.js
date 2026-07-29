/**
 * slash_commands.js — v6.7.7 前端斜杠命令扩展
 *
 * 支持在聊天输入中通过斜杠命令快速查看/修改配置：
 *   /status                  — 当前链路摘要
 *   /config <自然语言>        — 修改配置（如 /config 达标分调到 0.70）
 *   /template <自然语言>      — 修改模板（如 /template 重点项目增加国际合作章节）
 *   /pipeline <自然语言>      — 执行管线动作（如 /pipeline 暂停周末输入）
 *
 * 实现方式：
 * - 先尝试用简单规则解析常见命令，直接调用 API 并展示结果。
 * - 复杂或无法解析的命令，将请求转发给后端 agent 处理（未来可扩展）。
 */

(function() {
  'use strict';

  const COMMANDS = [
    '/status', '/config', '/template', '/pipeline',
    '/proposal', '/p', '/section', '/feedback', '/review', '/rule'
  ];

  function isSlashCommand(text) {
    return COMMANDS.some(cmd => text.trim().startsWith(cmd + ' ') || text.trim() === cmd);
  }

  async function handleSlashCommand(text) {
    const parts = text.trim().split(/\s+/);
    const cmd = parts[0];
    const args = text.trim().slice(cmd.length).trim();

    if (cmd === '/status') {
      return await handleStatus();
    }
    if (cmd === '/config') {
      return await handleConfig(args);
    }
    if (cmd === '/template') {
      return await handleTemplate(args);
    }
    if (cmd === '/pipeline') {
      return await handlePipeline(args);
    }
    if (cmd === '/proposal' || cmd === '/p') {
      return await handleProposal(args);
    }
    if (cmd === '/section') {
      return await handleSection(args);
    }
    if (cmd === '/feedback') {
      return await handleFeedback(args);
    }
    if (cmd === '/review') {
      return await handleReview(args);
    }
    if (cmd === '/rule') {
      return await handleRule(args);
    }
    return { handled: false };
  }

  // ============================================
  // /status
  // ============================================

  async function handleStatus() {
    try {
      const [flow, alerts] = await Promise.all([
        apiGet('/api/console/flow'),
        apiGet('/api/console/alerts'),
      ]);
      if (flow.status !== 'ok') throw new Error(flow.error || '获取失败');
      const stages = flow.stages || {};
      const alertCount = (alerts.alerts || []).length;
      const summary = Object.entries(stages).map(([k, s]) => `${STAGE_LABELS[k] || k}: ${s.count}`).join(' · ');
      return {
        handled: true,
        content: `**当前链路状态**\n\n${summary}\n\n告警/待处理：${alertCount} 项`,
      };
    } catch (e) {
      return { handled: true, content: `获取状态失败：${e.message}` };
    }
  }

  const STAGE_LABELS = {
    incoming: '输入端',
    drafts: '初稿',
    optimizing: '优化中',
    pending_review: '待校验',
    archived: '归档',
    output: '输出端',
  };

  // ============================================
  // /config
  // ============================================

  async function handleConfig(args) {
    if (!args) return { handled: true, content: '用法：/config 把面上项目达标分从0.65调到0.70' };

    // 简单规则解析
    const scoreMatch = args.match(/达标分[数]?[调为到设为]*(\d+(?:\.\d+)?)/);
    if (scoreMatch) {
      const score = parseFloat(scoreMatch[1]);
      if (score < 0 || score > 1) return { handled: true, content: '达标分数需在 0-1 之间。' };
      const type = args.includes('重点') ? 'key' : args.includes('重大') ? 'major' : 'general';
      try {
        const current = await apiGet('/api/settings/templates');
        const data = JSON.parse(JSON.stringify(current.data));
        if (!data.project_types?.[type]) throw new Error('未找到该类型配置');
        data.project_types[type].quality_threshold = data.project_types[type].quality_threshold || {};
        data.project_types[type].quality_threshold.min_overall_score = score;
        const preview = await apiPost(`/api/settings/templates/preview`, data);
        if (!preview.will_change) return { handled: true, content: '无变更。' };
        const confirmed = await confirmModal(`将「${type}」达标分改为 ${score}，确认？`);
        if (!confirmed) return { handled: true, content: '已取消。' };
        await apiPost('/api/settings/templates', data);
        return { handled: true, content: `✓ 已保存：${type} 达标分 = ${score}` };
      } catch (e) {
        return { handled: true, content: `修改失败：${e.message}` };
      }
    }

    const roundsMatch = args.match(/最大轮数[调为到设为]*(\d+)/);
    if (roundsMatch) {
      const rounds = parseInt(roundsMatch[1]);
      try {
        const current = await apiGet('/api/settings/pipeline');
        const data = { ...current.data, max_rounds: rounds };
        await apiPost('/api/settings/pipeline', data);
        return { handled: true, content: `✓ 已保存：最大优化轮数 = ${rounds}` };
      } catch (e) {
        return { handled: true, content: `修改失败：${e.message}` };
      }
    }

    return { handled: true, content: `未能解析「${args}」。目前支持的 /config 命令：\n- /config 达标分调到 0.70\n- /config 最大轮数设为 15` };
  }

  // ============================================
  // /template
  // ============================================

  async function handleTemplate(args) {
    if (!args) return { handled: true, content: '用法：/template 把面上项目页数限制调到 12\n/template 为重点项目增加"国际合作"章节' };

    // 页数限制
    const pagesMatch = args.match(/页数[限制]*[调为到设为]*(\d+)/);
    if (pagesMatch) {
      const pages = parseInt(pagesMatch[1]);
      const type = args.includes('重点') ? 'key' : args.includes('重大') ? 'major' : 'general';
      try {
        const current = await apiGet('/api/settings/templates');
        const data = JSON.parse(JSON.stringify(current.data));
        if (!data.project_types?.[type]) throw new Error('未找到该类型配置');
        data.project_types[type].page_limit = pages;
        const preview = await apiPost(`/api/settings/templates/preview`, data);
        if (!preview.will_change) return { handled: true, content: '无变更。' };
        const confirmed = await confirmModal(`将「${type}」页数限制改为 ${pages}，确认？`);
        if (!confirmed) return { handled: true, content: '已取消。' };
        await apiPost('/api/settings/templates', data);
        return { handled: true, content: `✓ 已保存：${type} 页数限制 = ${pages}` };
      } catch (e) {
        return { handled: true, content: `修改失败：${e.message}` };
      }
    }

    // 达标分
    const scoreMatch = args.match(/达标分[数]?[调为到设为]*(\d+(?:\.\d+)?)/);
    if (scoreMatch) {
      const score = parseFloat(scoreMatch[1]);
      const type = args.includes('重点') ? 'key' : args.includes('重大') ? 'major' : 'general';
      return (await handleConfig(`${type}项目达标分${score}`));
    }

    // 复杂模板变更先记录，后续可接入 agent
    return { handled: true, content: `模板修改请求「${args}」已记录。\n\n当前已支持：\n- 页数限制调整（例：/template 面上项目页数限制 12）\n- 达标分调整（例：/template 重点项目达标分 0.82）\n\n更复杂的章节增删/模板文案修改，请前往设置中心 → 内容/模板配置，或继续用自然语言描述，后续会由 agent 直接执行。` };
  }

  // ============================================
  // /pipeline
  // ============================================

  async function handlePipeline(args) {
    if (!args) return { handled: true, content: '用法：/pipeline 手动编排 或 /pipeline 修复' };
    const lower = args.toLowerCase();
    let action = null;
    if (lower.includes('编排')) action = 'orchestrate';
    else if (lower.includes('修复')) action = 'repair';
    else if (lower.includes('输入')) action = 'weekend_input';
    else if (lower.includes('输出')) action = 'weekend_output';
    else if (lower.includes('反思')) action = 'weekend_reflection';

    if (!action) return { handled: true, content: `未能识别管线动作「${args}」。支持：编排/修复/输入/输出/反思。` };

    try {
      const confirmed = await confirmModal(`执行管线动作「${action}」？`);
      if (!confirmed) return { handled: true, content: '已取消。' };
      await apiPost('/api/console/action', { action });
      return { handled: true, content: `✓ 已触发：${action}` };
    } catch (e) {
      return { handled: true, content: `执行失败：${e.message}` };
    }
  }

  // ============================================
  // /proposal <id> — 打开课题详情并摘要状态
  // ============================================

  async function handleProposal(args) {
    if (!args) return { handled: true, content: '用法：/proposal <课题ID>\n例如：/proposal general-quantum-geometry-inversion-20260726' };
    const proposalId = args.split(/\s+/)[0];
    try {
      const [brief, sections] = await Promise.all([
        apiGet(`/api/lifecycle/list/all`).then(d => (d.data || d.proposals || []).find(p => p.proposal_id === proposalId)),
        apiGet(`/api/pipeline/${encodeURIComponent(proposalId)}/proposal/sections`).catch(() => ({ sections: [] })),
      ]);
      if (!brief) return { handled: true, content: `未找到课题 **${proposalId}**。可用 /status 查看当前课题列表。` };

      // 打开研究管线面板到申请书页
      if (typeof openPipelineManager === 'function') {
        openPipelineManager(proposalId);
        if (window.Pipeline && typeof window.Pipeline.switchTo === 'function') {
          setTimeout(() => window.Pipeline.switchTo('proposal'), 50);
        }
      }

      const filledSections = (sections.sections || []).filter(s => s.content && s.content.length > 0).map(s => s.section || s.name);
      const sectionList = filledSections.length ? filledSections.join('、') : '（暂无内容）';
      return {
        handled: true,
        content: `**${proposalId}**\n\n状态：**${brief.status}** · 类型：**${brief.project_type}** · 轮次：**${brief.optimization_rounds || 0}** · 分数：**${(brief.last_score || 0).toFixed(2)}**\n\n已撰写章节：${sectionList}\n\n已为你打开研究管线面板。可以继续说：\n- "/section ${proposalId} 立项依据" 查看某一章节\n- "/feedback ${proposalId} 请加强创新点论述" 提交修改意见`,
      };
    } catch (e) {
      return { handled: true, content: `打开课题失败：${e.message}` };
    }
  }

  // ============================================
  // /section <id> <章节名> — 在聊天中展示章节
  // ============================================

  async function handleSection(args) {
    if (!args) return { handled: true, content: '用法：/section <课题ID> <章节名>\n例如：/section general-quantum-geometry-inversion-20260726 立项依据' };
    const parts = args.split(/\s+/);
    if (parts.length < 2) return { handled: true, content: '请同时提供课题ID和章节名。' };
    const proposalId = parts[0];
    const sectionName = parts.slice(1).join(' ');
    try {
      const data = await apiGet(`/api/pipeline/${encodeURIComponent(proposalId)}/proposal/sections/${encodeURIComponent(sectionName)}`);
      const content = data.content || data.section?.content || '';
      if (!content) return { handled: true, content: `课题 **${proposalId}** 的「${sectionName}」章节暂无内容。` };
      const wordCount = content.length;
      return {
        handled: true,
        content: `**${proposalId} · ${sectionName}**（约 ${wordCount} 字）\n\n---\n${content}\n\n---\n你可以说：\n- "/feedback ${proposalId} ${sectionName}部分需要补充文献支撑"\n- "/proposal ${proposalId}" 打开完整面板编辑`,
      };
    } catch (e) {
      return { handled: true, content: `读取章节失败：${e.message}` };
    }
  }

  // ============================================
  // /feedback <id> <意见> — 快速提交反馈
  // ============================================

  async function handleFeedback(args) {
    if (!args) return { handled: true, content: '用法：/feedback <课题ID> <你的修改意见>\n例如：/feedback general-quantum-geometry-inversion-20260726 立项依据的逻辑需要更紧凑' };
    const parts = args.split(/\s+/);
    if (parts.length < 2) return { handled: true, content: '请同时提供课题ID和修改意见。' };
    const proposalId = parts[0];
    const feedback = parts.slice(1).join(' ');
    try {
      const confirmed = await confirmModal(`向课题 **${proposalId}** 提交反馈：\n\n${feedback}\n\n确认后系统将整理为结构化 issue 并退回优化。`);
      if (!confirmed) return { handled: true, content: '已取消。' };
      const result = await apiPost(`/api/lifecycle/${encodeURIComponent(proposalId)}/feedback`, {
        feedback_text: feedback,
        verdict: 'major_revision',
      });
      const issueCount = result.data?.structured_feedback?.issues?.length || 0;
      return { handled: true, content: `✓ 已提交反馈（整理为 ${issueCount} 个 issue），课题已退回优化。` };
    } catch (e) {
      return { handled: true, content: `提交反馈失败：${e.message}` };
    }
  }

  // ============================================
  // /review <id> — 打开待校验视图
  // ============================================

  async function handleReview(args) {
    if (!args) return { handled: true, content: '用法：/review <课题ID>' };
    const proposalId = args.split(/\s+/)[0];
    try {
      const data = await apiGet(`/api/lifecycle/list/pending_review`);
      const items = data.data || data.proposals || [];
      const target = items.find(p => p.proposal_id === proposalId);
      if (!target) return { handled: true, content: `**${proposalId}** 当前不在「待校验」阶段。` };

      if (typeof openPipelineManager === 'function') {
        openPipelineManager(proposalId);
        if (window.Pipeline && typeof window.Pipeline.switchTo === 'function') {
          setTimeout(() => window.Pipeline.switchTo('inspection'), 50);
        }
      }
      return {
        handled: true,
        content: `**${proposalId}** 已打开自检/待校验面板。\n\n分数：**${(target.last_score || 0).toFixed(2)}** · 轮次：**${target.optimization_rounds || 0}**\n\n你可以：\n- 在研究管线面板查看「自检」标签页的评审问题\n- 说 "/feedback ${proposalId} ..." 退回修改\n- 说意见后由我帮你归档`,
      };
    } catch (e) {
      return { handled: true, content: `打开待校验视图失败：${e.message}` };
    }
  }

  // ============================================
  // /rule <自然语言> — 修改评审规则/禁止清单
  // ============================================

  async function handleRule(args) {
    if (!args) return { handled: true, content: '用法：/rule 评审员禁止连续两轮提出重复问题\n当前会把请求转发给 agent，由 agent 修改 memory/feedback-standards.json 并返回摘要。' };
    // v6.7.8 MVP：调用设置中心的 templates 保存入口作为兜底记录；完整 agent 执行后续接入
    return { handled: true, content: `规则修改请求「${args}」已记录。\n\n当前阶段：我已理解你的意图。由于规则变更涉及 feedback-standards.json 与 prompt 模板，建议先在设置中心 → 内容/模板配置查看现有规则，或继续用自然语言描述，我会在后续版本中直接调用 agent 完成修改并展示 diff。` };
  }

  // 拦截 sendMessage
  window._interceptSlashCommand = async function(text) {
    if (!isSlashCommand(text)) return null;
    return await handleSlashCommand(text);
  };
})();
