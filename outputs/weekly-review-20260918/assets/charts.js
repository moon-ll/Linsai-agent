/* 周报图表 — 全部使用 Business Blue 调色板 token */
(function () {
  function token(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  var C = {
    s1: token('--chart-series-1', '#0969DA'),
    s2: token('--chart-series-2', '#8250DF'),
    s3: token('--chart-series-3', '#06B6D4'),
    s4: token('--chart-series-4', '#BF3989'),
    other: token('--chart-other', '#D8DEE6'),
    accent: token('--chart-accent', '#8250DF'),
    positive: token('--chart-positive', '#1A7F37'),
    warning: token('--chart-warning', '#BC4C00'),
    negative: token('--chart-negative', '#D1242F'),
    grid: token('--chart-grid', 'rgba(28,36,48,0.12)'),
    axis: token('--chart-axis', '#66707D'),
    label: token('--chart-label', '#66707D'),
    tooltipBg: token('--chart-tooltip-bg', '#FFFFFF'),
    ink: token('--ink', '#1C2430')
  };

  var base = {
    renderer: 'svg',
    animation: false,
    textStyle: { fontFamily: 'InstrumentSans, "PingFang SC", "Microsoft YaHei", sans-serif' },
    grid: { left: 12, right: 16, top: 44, bottom: 8, containLabel: true },
    tooltip: {
      appendToBody: true,
      backgroundColor: C.tooltipBg,
      borderColor: C.grid,
      textStyle: { color: C.ink, fontSize: 12 }
    }
  };

  function init(el) {
    var chart = echarts.init(el, null, { renderer: 'svg' });
    window.addEventListener('resize', function () { chart.resize(); });
    return chart;
  }

  /* ── 图1：最新轮次得分横向条形图（含 0.85 达标线） ── */
  /* v6.10.27: 最新轮次得分改用章节 4 维均值口径（旧数据为 last_score，
     每轮 references 收尾时被 2 维分覆盖——key-transient/moire 显示
     0.59/0.56 实为 references 收尾分，章节均值 0.775/0.802 更真实） */
  var barData = [
    { name: 'order-parameter', v: 0.81, note: 'R4 章节均值' },
    { name: 'moire', v: 0.802, note: 'R3 章节均值' },
    { name: 'attosecond', v: 0.80, note: 'R7 进行中' },
    { name: 'new-idea', v: 0.795, note: 'R7 章节均值' },
    { name: 'quantum-geometry', v: 0.795, note: 'R7 章节均值' },
    { name: 'mos2', v: 0.78, note: 'R4 章节均值' },
    { name: 'key-transient', v: 0.775, note: 'R6 章节均值' },
    { name: 'mnps3', v: 0.772, note: 'R2 章节均值' },
    { name: 'bsv-driven', v: 0.75, note: 'R4 章节均值' }
  ];

  var el1 = document.getElementById('chart-current');
  if (el1) {
    var ch1 = init(el1);
    var names = barData.map(function (d) { return d.name; }).reverse();
    var vals = barData.map(function (d) { return +(d.v * 100).toFixed(1); }).reverse();
    ch1.setOption(Object.assign({}, base, {
      tooltip: Object.assign({}, base.tooltip, {
        formatter: function (p) {
          var d = barData[barData.length - 1 - p.dataIndex];
          return '<b>' + d.name + '</b><br/>轮次得分 ' + d.v.toFixed(3) + ' · ' + d.note;
        }
      }),
      xAxis: {
        type: 'value', min: 0, max: 100,
        axisLabel: { formatter: '{value}%', color: C.label, fontSize: 11 },
        axisLine: { lineStyle: { color: C.grid } },
        splitLine: { lineStyle: { color: C.grid, type: 'dashed' } }
      },
      yAxis: {
        type: 'category', data: names,
        axisLabel: { color: C.label, fontSize: 12 },
        axisLine: { show: false },
        axisTick: { show: false }
      },
      series: [{
        type: 'bar',
        data: vals.map(function (v, i) {
          var isRunning = barData[barData.length - 1 - i].note.indexOf('进行中') > -1;
          var color = isRunning ? C.accent : C.s1;
          return { value: v, itemStyle: { color: color, borderRadius: [0, 4, 4, 0] } };
        }),
        barWidth: 16,
        label: {
          show: true, position: 'right',
          formatter: function (p) { return p.value.toFixed(1) + '%'; },
          color: C.ink, fontSize: 12
        },
        markLine: {
          symbol: 'none',
          data: [{ xAxis: 85, name: '面上 0.85 达标线' }],
          lineStyle: { color: C.negative, type: 'dashed', width: 1.5 },
          label: { formatter: '0.85 达标线', color: C.negative, fontSize: 11, position: 'insideEndTop' }
        }
      }]
    }));
  }

  /* ── 图2：关键课题轮次得分轨迹（按评审口径分型，v6.10.27） ──
     实线：章节评审口径（section_4d，innovation/feasibility/rigor/expression
     四维加权，每轮取 rationale/content/scheme/full_review 四章均值）；
     虚线：引用审校口径（references_2d，rigor/completeness 二维等权）。
     两口径不可混读——旧图混绘造成伪波动（如 attosecond R5 0.665 实为
     references 报告被误读为 rationale 分，已修复为 0.80）。 */
  var el2 = document.getElementById('chart-trend');
  if (el2) {
    var ch2 = init(el2);
    var trendData = [
      {
        name: 'attosecond', color: C.s1,
        sec: [0.765, 0.745, 0.7225, 0.69, 0.77, 0.7975, 0.8],
        ref: [0.83, 0.80, 0.88, 0.905, 0.665, 0.835, null]
      },
      {
        name: 'mnps3（整改后）', color: C.s2,
        sec: [0.7675, 0.7725],
        ref: [0.815, 0.785]
      },
      {
        name: 'moire', color: C.s3,
        sec: [0.7575, 0.79, 0.8025],
        ref: [0.615, 0.585, 0.56]
      },
      {
        name: 'new-idea', color: C.s4,
        sec: [0.7415, 0.7625, 0.7975, 0.78, 0.795],
        ref: [0.575, 0.7, 0.78, 0.62, 0.78]
      },
      {
        name: 'key-transient', color: C.other,
        sec: [0.765, 0.765, 0.7556, 0.78, 0.7512, 0.775],
        ref: [0.45, 0.7, 0.51, 0.49, 0.82, 0.59]
      }
    ];
    var xLabels = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'];
    var series2 = [];
    trendData.forEach(function (t) {
      series2.push({
        name: t.name + '·章节', type: 'line', data: t.sec,
        smooth: false, symbolSize: 6,
        lineStyle: { color: t.color, width: 2 },
        itemStyle: { color: t.color },
        emphasis: { focus: 'series' }
      });
      series2.push({
        name: t.name + '·引用', type: 'line', data: t.ref,
        smooth: false, symbolSize: 4, symbol: 'diamond',
        lineStyle: { color: t.color, width: 1.2, type: 'dashed' },
        itemStyle: { color: t.color },
        emphasis: { focus: 'series' },
        connectNulls: true
      });
    });
    ch2.setOption(Object.assign({}, base, {
      legend: {
        top: 0, right: 0, type: 'scroll',
        textStyle: { color: C.label, fontSize: 11 },
        itemWidth: 18, itemHeight: 10
      },
      xAxis: {
        type: 'category', data: xLabels,
        axisLabel: { color: C.label, fontSize: 11 },
        axisLine: { lineStyle: { color: C.grid } }
      },
      yAxis: {
        type: 'value', min: 0.4, max: 1.0,
        axisLabel: { formatter: function (v) { return v.toFixed(1); }, color: C.label, fontSize: 11 },
        axisLine: { lineStyle: { color: C.grid } },
        splitLine: { lineStyle: { color: C.grid, type: 'dashed' } }
      },
      series: series2
    }));
  }
})();
