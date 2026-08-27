(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var baseAxis = {
    axisLine: { lineStyle: { color: rule } },
    axisLabel: { color: muted, fontSize: 11 },
    splitLine: { lineStyle: { color: rule, type: 'dashed' } },
  };

  // --- Chart 1: 超时率趋势 ---
  var c1 = echarts.init(document.getElementById('chart-timeout'), null, { renderer: 'svg' });
  c1.setOption({
    animation: false,
    grid: { left: 48, right: 24, top: 40, bottom: 36 },
    tooltip: { trigger: 'axis', appendToBody: true, valueFormatter: function (v) { return v + '%'; } },
    xAxis: Object.assign({ type: 'category', data: ['8/23', '8/24', '8/25', '8/26', '8/27 晨'], boundaryGap: false }, baseAxis),
    yAxis: Object.assign({ type: 'value', max: 50, axisLabel: { formatter: '{value}%', color: muted } }, baseAxis),
    series: [{
      type: 'line',
      data: [21.6, 12.0, 6.1, 0.0, 44.0],
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: accent, width: 3 },
      itemStyle: { color: accent },
      areaStyle: { color: accent + '18' },
      markPoint: {
        data: [
          { coord: ['8/27 晨', 44.0], value: 'API 慢速期', itemStyle: { color: accent2 }, label: { color: '#fff', fontSize: 10 } },
          { coord: ['8/26', 0.0], value: '0%', itemStyle: { color: accent } }
        ],
        symbolSize: 54
      },
      label: { show: true, color: ink, fontSize: 11, formatter: '{c}%' }
    }]
  });

  // --- Chart 2: 输入与产物瘦身 ---
  var c2 = echarts.init(document.getElementById('chart-slimming'), null, { renderer: 'svg' });
  c2.setOption({
    animation: false,
    grid: { left: 150, right: 56, top: 30, bottom: 36 },
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    legend: { data: ['治理前', '治理后'], top: 0, textStyle: { color: muted } },
    xAxis: Object.assign({ type: 'value', name: 'KB' }, baseAxis),
    yAxis: Object.assign({ type: 'category', data: [
      'monitor 单次输入（估算）',
      'full_review critic 输入（估算）',
      'critic 报告注入 writer',
      'full_review.md 文件（4 课题均）'
    ] }, { axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontSize: 11 } }),
    series: [
      { name: '治理前', type: 'bar', data: [200, 180, 37, 24], itemStyle: { color: muted }, barWidth: 14, label: { show: true, position: 'right', color: muted, fontSize: 10 } },
      { name: '治理后', type: 'bar', data: [105, 95, 8, 1.5], itemStyle: { color: accent }, barWidth: 14, label: { show: true, position: 'right', color: ink, fontSize: 10 } }
    ]
  });

  // --- Chart 3: 质量门冗余检出（7 课题真实数据） ---
  var c3 = echarts.init(document.getElementById('chart-detection'), null, { renderer: 'svg' });
  c3.setOption({
    animation: false,
    grid: { left: 42, right: 24, top: 44, bottom: 70 },
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    legend: { data: ['跨章节完全重复句', '跨章节高相似句'], top: 0, textStyle: { color: muted } },
    xAxis: Object.assign({ type: 'category', data: ['attosecond', 'berry', 'moire', 'new-idea', 'order-param', 'qg', 'kt'], axisLabel: { rotate: 30, color: muted, fontSize: 11, interval: 0 } }, baseAxis),
    yAxis: Object.assign({ type: 'value', name: '处' }, baseAxis),
    series: [
      { name: '跨章节完全重复句', type: 'bar', stack: 'd', data: [1, 4, 3, 1, 3, 20, 5], itemStyle: { color: accent }, barWidth: 26 },
      { name: '跨章节高相似句', type: 'bar', stack: 'd', data: [4, 16, 17, 3, 9, 0, 11], itemStyle: { color: accent2 }, barWidth: 26 }
    ]
  });

  // --- Chart 4: 回归测试增长 ---
  var c4 = echarts.init(document.getElementById('chart-tests'), null, { renderer: 'svg' });
  c4.setOption({
    animation: false,
    grid: { left: 48, right: 24, top: 44, bottom: 36 },
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    legend: { data: ['机制加固套件断言', '全量 --module 回归'], top: 0, textStyle: { color: muted } },
    xAxis: Object.assign({ type: 'category', data: ['v6.9.53', 'v6.9.54', 'v6.9.55', 'v6.9.60', 'v6.9.61'] }, baseAxis),
    yAxis: Object.assign({ type: 'value', max: 1300 }, baseAxis),
    series: [
      { name: '机制加固套件断言', type: 'bar', data: [138, 152, 163, 189, 209], itemStyle: { color: accent }, barWidth: 26, label: { show: true, position: 'top', color: ink, fontSize: 10 } },
      { name: '全量 --module 回归', type: 'line', data: [1132, 1146, 1157, 1178, 1198], symbol: 'circle', symbolSize: 7, lineStyle: { color: accent2, width: 2.5 }, itemStyle: { color: accent2 } }
    ]
  });

  [c1, c2, c3, c4].forEach(function (ch) {
    window.addEventListener('resize', function () { ch.resize(); });
  });
})();
