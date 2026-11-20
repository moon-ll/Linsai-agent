# 启动包裁决速览（decision brief）

> 生成：2026-11-20T06:05Z（整点轮6，零 LLM 机械汇总）　适用：ready 包 16 个的人工裁决（activate / reject）
> 启动方式：工作台看板或 `python3 scripts/topic_pipeline.py --activate <id>`；否决 `--reject <id> --reason "..."`

| 课题 ID | 笔记/近24月 | A2相似度 | 方案步骤 | bib(溯源) | 报告字数 | 跨包最高相似 |
|---|---|---|---|---|---|---|
| `attosecond-streaking-20260822`<br>阿秒条纹技术：从超短脉冲表征到量子相位测量 | 22/17 | 0.1389 | 4✓ | 17(17) | 5537 | 0.14→general-bsv-driven-h |
| `berry-berry-20261107`<br>拓扑材料中Berry曲率驱动的非线性霍尔效应：非平衡分布 | 9/6 | 0.1451 | 4✓ | 39(39) | 4129 | 0.14→general-berry-mnps3- |
| `berry-mnps3-rashba-20260816`<br>二维材料中交变磁性磁态的自旋-能谷耦合与滑移调控 | 10/10 | 0.1512 | 4✓ | 47(47) | 4161 | 0.15→general-moire-strong |
| `bsv-driven-hhg-quantum-20260726`<br>量子光场驱动固体高次谐波产生：BSV-HHG 作为多体态 | 8/8 | 0.188 | 4✓ | 40(40) | 2911 | 0.19→general-ssh-weyl-202 |
| `chiral-hhg-20261101`<br>亚周期手性光场工程与手性高次谐波：场手性-材料手性甄别协 | 11/10 | 0.1124 | 4✓ | 54(54) | 3831 | 0.11→general-moire-strong |
| `floquet-20261107`<br>Floquet工程诱导共线磁体中的奇宇称自旋与磁振子劈裂 | 9/9 | 0.1388 | 4✓ | 40(40) | 3789 | 0.14→general-phonon-hhg-2 |
| `houston-kronig-penney-landau-zener-20261004`<br>固体高次谐波产生：带内/带间/反常电流机制分解与多尺度全 | 10/10 | 0.1919 | 4✓ | 62(62) | 3983 | 0.19→general-moire-strong |
| `keldysh-schottky-20261115`<br>纳米针尖强场光电子发射的量子干涉谱学与发射机制诊断 | 9/6 | 0.1447 | 4✓ | 5(5) | 4042 | 0.14→general-ssh-weyl-202 |
| `moire-strong-field-probe-20260726`<br>基于固体高次谐波产生（HHG）与光 Floquet 工程 | 9/7 | 0.1919 | 4✓ | 40(40) | 4129 | 0.19→general-houston-kron |
| `order-parameter-ultrafast-readout-20260727`<br>altermagnet HHG 序参量可辨识性研究——磁 | 8/7 | 0.1148 | 4✓ | 45(45) | 2959 | 0.11→general-houston-kron |
| `phonon-hhg-20261101`<br>相干声子调控的固体高次谐波：晶格自由度进入强场非线性与电 | 11/9 | 0.1515 | 4✓ | 40(40) | 3904 | 0.15→general-houston-kron |
| `ssh-weyl-20260920`<br>固态高次谐波探测拓扑物态：高阶拓扑绝缘体、SSH边界态与 | 10/6 | 0.188 | 4✓ | 40(40) | 3403 | 0.19→general-bsv-driven-h |
| `t-tise2-2-2-2-cdw-20261108`<br>电荷密度波序参量的非平衡动力学：幅度-相位-关联长度解耦 | 9/9 | 0.1445 | 4✓ | 40(40) | 3261 | 0.14→general-moire-strong |
| `tdse-tddft-20261115`<br>机器学习赋能强场量子动力学：TDSE/TDDFT代理加速 | 9/6 | 0.1209 | 4✓ | 10(10) | 3768 | 0.12→general-ssh-weyl-202 |
| `tmd-bic-mie-anapole-20261107`<br>TMD共振非线性超表面：准BIC/Mie/Anapole | 9/8 | 0.1412 | 4✓ | 47(47) | 3750 | 0.14→general-berry-mnps3- |
| `key:transient-quantum-phase-optical-20260726`<br>瞬态量子相的全光读写与时序反演 | 8/7 | 0.0873 | 4✓ | 41(41) | 3731 | 0.09→general-berry-mnps3- |

## 跨包方向重叠

120 对两两 2-gram Jaccard 全部 <0.30（详见 cross-similarity-2026-11-19.json）——16 包方向分散、无重叠簇，逐一裁决互不影响。

## 法定节点提醒（v8 人机分工）

- activate / reject 仅用户可触发；自动化不代做。reject 落 `_rejected-questions` 台账（可复用素材回流文献链）。
- 全部 16 包 `--check-all` 六项判据 2026-11-20 05:40 复跑全过。
