/* 日报图表 — daily-report-20260815 */
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var bad = style.getPropertyValue('--bad').trim();

  var baseText = { color: muted, fontSize: 12 };

  /* ── 图 1：今日 CoPilot 网关 LLM 调用结果分布 ── */
  var el1 = document.getElementById('chart-llm');
  if (el1) {
    var c1 = echarts.init(el1, null, { renderer: 'svg' });
    c1.setOption({
      animation: false,
      grid: { left: 90, right: 40, top: 40, bottom: 30 },
      legend: {
        data: ['调用成功', '被限流(429)'],
        top: 0,
        textStyle: { color: muted, fontSize: 12 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        appendToBody: true,
        formatter: function (p) {
          return p.map(function (it) {
            return it.marker + ' ' + it.seriesName + '：<b>' + it.value + '</b> 次';
          }).join('<br>');
        }
      },
      xAxis: {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: muted, fontSize: 11 },
        axisLabel: baseText,
        splitLine: { lineStyle: { color: rule } },
        axisLine: { show: false }
      },
      yAxis: {
        type: 'category',
        data: ['minimax', 'kimi', 'glm'],
        axisLabel: { color: ink, fontSize: 13, fontFamily: 'Menlo, monospace' },
        axisTick: { show: false },
        axisLine: { lineStyle: { color: rule } }
      },
      series: [
        {
          name: '调用成功',
          type: 'bar',
          barWidth: 18,
          data: [0, 1, 8],
          itemStyle: { color: accent, borderRadius: [0, 3, 3, 0] },
          label: {
            show: true, position: 'right', color: ink, fontSize: 12,
            formatter: function (p) { return p.value > 0 ? p.value + ' 次' : ''; }
          }
        },
        {
          name: '被限流(429)',
          type: 'bar',
          barWidth: 18,
          data: [14, 0, 0],
          itemStyle: { color: bad, opacity: 0.75, borderRadius: [0, 3, 3, 0] },
          label: {
            show: true, position: 'right', color: bad, fontSize: 12,
            formatter: function (p) { return p.value > 0 ? p.value + ' 次' : ''; }
          }
        }
      ]
    });
    window.addEventListener('resize', function () { c1.resize(); });
  }

  /* ── 图 2：KB 蒸馏积压消化路径与预测 ── */
  var el2 = document.getElementById('chart-distill');
  if (el2) {
    var c2 = echarts.init(el2, null, { renderer: 'svg' });
    var actual = [
      ['08-10', 508], ['08-11', 508], ['08-12', 508],
      ['08-13', 508], ['08-14', 508], ['08-15', 350]
    ];
    var forecast = [
      ['08-15', 350], ['08-22', 315], ['08-29', 280], ['09-05', 245],
      ['09-12', 210], ['09-19', 175], ['09-26', 140], ['10-03', 105],
      ['10-10', 70], ['10-17', 35], ['10-24', 0]
    ];
    c2.setOption({
      animation: false,
      grid: { left: 55, right: 30, top: 45, bottom: 45 },
      legend: {
        data: ['实际积压', '消化预测（5 篇/天）'],
        top: 0,
        textStyle: { color: muted, fontSize: 12 }
      },
      tooltip: {
        trigger: 'axis',
        appendToBody: true,
        formatter: function (ps) {
          var lines = ['<b>' + ps[0].axisValue + '</b>（2026 年）'];
          ps.forEach(function (p) {
            if (p.value !== undefined && p.value !== null && p.value[1] !== null && p.value[1] !== undefined) {
              lines.push(p.marker + ' ' + p.seriesName + '：<b>' + p.value[1] + '</b> 项');
            }
          });
          return lines.join('<br>');
        }
      },
      xAxis: {
        type: 'category',
        data: ['08-10', '08-11', '08-12', '08-13', '08-14', '08-15', '08-22',
               '08-29', '09-05', '09-12', '09-19', '09-26', '10-03',
               '10-10', '10-17', '10-24'],
        axisLabel: Object.assign({ interval: 0, rotate: 40 }, baseText),
        axisLine: { lineStyle: { color: rule } },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        name: '待蒸馏项数',
        nameTextStyle: { color: muted, fontSize: 11 },
        axisLabel: baseText,
        splitLine: { lineStyle: { color: rule, type: 'dashed' } }
      },
      series: [
        {
          name: '实际积压',
          type: 'line',
          data: actual,
          lineStyle: { color: accent, width: 3 },
          itemStyle: { color: accent },
          symbolSize: 7,
          z: 3,
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { color: bad, type: 'dashed', width: 1 },
            label: { color: bad, fontSize: 11, formatter: '告警阈值 300' },
            data: [{ yAxis: 300 }]
          }
        },
        {
          name: '消化预测（5 篇/天）',
          type: 'line',
          data: forecast,
          lineStyle: { color: accent2, width: 2, type: 'dashed' },
          itemStyle: { color: accent2 },
          symbolSize: 5
        }
      ]
    });
    window.addEventListener('resize', function () { c2.resize(); });
  }
})();
