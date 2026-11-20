---
title: "Compact Circuit Models for Nanoantenna-Based Lightwave Electronics"
arxiv_id: "2610.07408"
authors: "Adina Bechhofer, Felix Ritzkowsky, Karl K. Berggren, Phillip D. Keathley"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "光波电子学"
source: "hermes-briefing"
imported_at: "2026-10-07T11:30:06Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Compact Circuit Models for Nanoantenna-Based Lightwave Electronics

## 摘要
As the field of nanoscale lightwave electronics matures from centering around fundamental science to focusing on device engineering, there is a growing need for compact models that can provide rapid and scalable quantitative analysis of the performance of petahertz-frequency optical-field-driven electronics. In this work, we developed a circuit model framework for describing nano-scale lightwave electronics. Our framework captures the physics governing nanoscale optical devices, such as electrically-connected nanoantennas, using compact circuit models that predict their electromagnetic response, their electron emission, and their charge transfer dynamics. This approach allows scalable simulation of large integrated systems containing networks of nanoscale lightwave electronic components, which is not possible using full-wave electromagnetic and particle-in-cell simulation methods. We implemented the compact model in a free commercial circuit solver (LTspice) and validated its electromagnetic response against a full-wave electromagnetic solver (MEEP). We propose an experiment to fully benchmark the model's ability to capture non-linear charge-transfer-based coupling between devices. The circuit model implementation speeds up the electromagnetic analysis from hours to seconds and accounts for charge-driven coupling, enabling rapid quantitative studies of device operation which provide new insights into how femtosecond signals propagate through nanoscale lightwave electronic structures. We anticipate that the methods we introduce here will become essential to the development and performance analysis of nanoscale lightwave electronics for communication, computation, and signal processing at optical frequencies.

## 背景概述与问题引入
纳米光波电子学（lightwave electronics）正从基础科学走向器件工程：用光场的拍赫兹振荡直接驱动纳米天线上的电子发射与电荷转移，实现超快开关与信号处理。但器件设计面临一个工具缺口——全波电磁仿真（FDTD/PIC）对单个器件就要数小时，无法扩展到含多个器件网络的集成系统；而现有电路模型又缺少电子发射与电荷转移这些光波电子学特有的物理。本文的核心问题是：如何建立既保留关键物理、又能在秒级完成仿真、可扩展到器件网络的紧凑电路模型框架。

## 关键发现及核心讨论
1. **三物理合一的紧凑电路框架**：对电学连接的纳米天线等纳尺度光学器件，用紧凑电路模型同时预测 (i) 电磁响应、(ii) 电子发射、(iii) 电荷转移动力学。电荷驱动的器件间耦合（charge-driven coupling）被显式纳入——这是全波/PIC 方法无法负担、而集总模型此前缺失的部分。
2. **小时 → 秒的加速与验证**：模型在免费电路求解器 LTspice 中实现，电磁响应部分与全波求解器 MEEP 对标验证。电磁分析从小时级降到秒级，同时保留飞秒信号在纳米光波电子结构中传播的定量描述。
3. **非线性电荷转移耦合的基准实验方案**：提出一个实验方案以完整检验模型捕捉器件间非线性电荷转移耦合的能力，明确了模型有效性的检验路径。

## 主要方法
- **建模路线**：纳尺度光波电子器件（电学连接纳米天线）→ 紧凑电路模型（电磁响应 + 电子发射 + 电荷转移）
- **工具链**：LTspice（免费商用电路求解器）实现；MEEP 全波仿真做电磁响应验证
- **对象**：含纳米光波电子元件网络的集成系统，飞秒信号传播

## 创新性
首个面向拍赫兹光场驱动电子学器件工程的紧凑电路模型框架：把电子发射和电荷转移动力学装进可扩展的电路仿真，使"多器件网络级"的定量性能分析首次可行；LTspice 实现意味着工具链零门槛。

## 结论与展望
该框架为纳米光波电子学从单器件物理走向通信、计算与光频信号处理的集成系统提供了工程化建模基础。对本组的启示：这是 petahertz switching 方向从"演示"走向"设计"的关键一步——若我们要评估固体 HHG/光波驱动方案在器件层面的开关速度与串扰，这类紧凑模型是与第一性原理计算互补的另一半工具链；电荷转移耦合的处理方式也值得借鉴到我们关心的纳米天线增强固体 HHG 结构分析中。