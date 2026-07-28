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

  const COMMANDS = ['/status', '/config', '/template', '/pipeline'];

  function isSlashCommand(text) {
    return COMMANDS.some(cmd => text.trim().startsWith(cmd));
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
    if (!args) return { handled: true, content: '用法：/template 为重点项目增加"国际合作"章节' };
    return { handled: true, content: `模板修改请求「${args}」已记录。当前前端仅支持调整分数/页数，复杂模板变更请前往设置中心 → 内容/模板配置，或让 agent 在后台执行。` };
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

  // 拦截 sendMessage
  window._interceptSlashCommand = async function(text) {
    if (!isSlashCommand(text)) return null;
    return await handleSlashCommand(text);
  };
})();
