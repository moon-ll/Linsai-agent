## 2509.06414

**标题**：Quasidegenerate charge-density wave states in 1T-TiSe₂
**作者**：Seungrok Mun, Woojin Choi, Hayoon Im, Sung-Kwan Mo, Choongyu Hwang, Jinwoong Hwang, Heung-Sik Kim（江原大学、韩国能源技术院、釜山大学）
**arXiv**：2509.06414 [cond-mat.mtrl-sci]，2025-09-08 提交，8页3图

### 研究问题（Research Question）
1T-TiSe₂ 在 200 K 发生公认的 2×2×2 电荷密度波（CDW）相变，但其真实基态结构对称性长期存在争议（此前文献分别报道 P-3c1、C2/m、以及更特殊的低对称/手性相）。本文要回答的核心问题是：2×2×2 超胞中究竟存在多少种物理可实现的 CDW 堆积构型，它们之间的能量差有多大，以及能否用统一的准简并图像同时解释"基态对称性冲突"和"165 K 附近的电阻率峰"这两个悬案。

### 研究背景（Background）
TMDC（MX₂）中 CDW 的起源机制有费米面嵌套、电子-声子耦合、激子凝聚三种长期争论。1T-TiSe₂ 的基态 CDW 构型在 XRD、偏振拉曼等实验中反复给出互相矛盾的空间群归属。更关键的是，作者自己的温度依赖电阻率测量显示除 200 K 主转变外，165 K 附近还有第二个转变（电阻率峰，实测在 169 K），此前被归因于电子-空穴型输运转换、费米面重构或相干-不相干交叉，但均无定论；此外报道的 CDW 空间不均匀性（area-selective electron diffraction）、面内各向异性起伏、以及 Xu 等 2020 Nature 与 Kim 等 2024 Nature Physics 提出的手性 CDW 态，都缺乏统一的结构解释。

### 研究方法（Methods）
第一性原理 DFT（VASP）为主：在 2×2×2 六方超胞中随机施加任意 Ti 位移模式后做无对称约束的全结构弛豫（PBE+optB86b，能量截断 400 eV、996 k 点、含 SOC 的全相对论赝势，Rydberg 判据 10⁻⁸ eV、力判据 10⁻⁴ eV/Å），收敛出七种 CDW 相；用 findsym 判定空间群（容差 10⁻³ Å）；用 DFT-D2、Tkatchenko-Scheffler、r²SCAN+rVV10 交叉验证能量序。用 band unfolding（Ku-Berlijn-La-Plonetta/VaspBandUnfolding）将超胞能带折回原胞，与实验比对。实验包括 ALS Beamline 10.0.1 HERS 站 ARPES（Scienta R4000，π偏振，18–25 meV能量分辨率、0.1° 角分辨率，20 K 原位解理），以及釜山大学 Quantum Matter Core Facility 四探针电阻率（TeslatronPT 12 T，恒流 5 mA，Lakeshore M81 锁相 13.333 Hz，4–300 K，1 atm，0.8 K/min）。

### 主要发现与核心结论（Main Results）
在 2×2×2 超胞中弛豫出七种互不相同的 CDW 相，其中除 A、B 外均为此前未被报道：A(C2)、B(P-3c1)、C(C2/m)、D(C2)、E(C2)、F(P2/c)、G(C2)。所有相的晶格参数几乎一致，总能量差极小——optB86b 下最大仅 1.41 meV/f.u.（A=0、B=0.25、C=−0.30、D=0.03、E=0.13、F=1.41、G=1.16 meV/f.u.），DFT-D2/TS 与 r²SCAN+rVV10 亦复现"准简并"（r²SCAN 下 B=−0.65、C=−0.68 meV/f.u.最低）。Ti 簇形貌上 A、B 为 Y 形，C、D 为 Y/菱形交替，E/F/G 呈 W 形或 L 形复合网络。ARPES 对照判定：180 K 时 L 点导带平坦、价带带 CDW 隙，与 C 相（C2/m）最匹配；20 K 时 L 点导带变为 V 形且价导无隙，与 B 相（P-3c1）最匹配，即存在 165–200 K 的中间 C2/m CDW 序。DOS 计算显示 C 相在费米能级附近出现赝隙、费米能级 DOS 降低，可解释 165 K 处的电阻率峰（半导型）与 165 K 以下 B 相的金属型。模拟粉末 XRD 显示七相的衍射图谱仅分三组（A,B,C,D）、(E,G)、(F)，A 与 D 几乎不可分辨，故 XRD 无法定相，必须借助 ARPES。

### 潜在研究方向（Future Directions）
由于各相能量差极小且 pXRD 几乎不可分辨，单靠 DFT 或衍射难以判定真实基态；作者指出需引入 GW、混合泛函（HSE06）等非局域交换更强的方法来判定低能电子结构与 CDW 微观起源（电子-声子 vs 激子凝聚），虽认为 r²SCAN+rVV10 与 PBE 的结论一致性已支持准简并结论的稳健性。物理图像上，近简并相的混合可产生三斜/手性 CDW、空间不均匀 CDW 纹理与畴壁，这一框架与 Xu 等的手性 CDW 提议、Yeom 组的手性 CDW 微观起源（arXiv:2401.01669）以及电子衍射观测到的面内各向异性起伏相容。残余开放问题包括：为何在近乎零能量差的"平坦势能面"下仍能在 150–200 K 出现明确转变与交叉（作者推测强耦合区 CDW 隙的存在与长程库仑作用抑制了不同 CDW 相之间的涨落），以及动态 CDW 涨落对电子结构的影响。作者建议开展纳米尺度分辨实验（nano-ARPES、非线性纳米光学）辨识 CDW 畴与畴壁，并利用浅能量势能面通过静电栅压、单/双轴应变、界面工程、光场驱动实现 150–200 K 窗口内可逆甚至滞回的相切换。

---

## arXiv:2606.31298

**阅读日期**：2026-11-16
**标题**：Phonon-induced pseudogap phase in TiSe₂
**作者**：Sotirios Fragkos, Nina Girotto Erhardt, Evgenia Symeonidou, Hibiki Orio, Dominique Descamps, Stéphane Petit, Polychronis Tsipas, Kai Rossnagel, Jakub Schusser, Athanasios Dimoulas, Samuel Beaulieu, Dino Novko
**来源**：arXiv:2606.31298 [cond-mat.str-el]，2026-06-30 提交，v1，9 页 3 图 + SM（arXiv 声明 CC BY 4.0）

### 核心结论
以时间分辨与角分辨极紫外光电子能谱（21.6 eV 探针、1.2 eV 红外泵浦）配合从头算电子-声子计算，对 1T-TiSe₂、HfTe₂、ZrTe₂ 三种 1T 型 TMDC 在室温下做激发态能带测绘。核心发现三条：
（1）中等电子-声子耦合体系（HfTe₂、ZrTe₂）中热涨落只导致谱展宽与带重整化；
（2）强耦合体系 TiSe₂ 中出现软声子诱导的动量依赖谱权重压制即赝隙，延伸至费米能级**以上约 1 eV**，此前 ARPES 只能探测费米能级以下（既有问题隙上限约 150 meV）；
（3）据此确立 TiSe₂ 正常态为**软声子诱导的赝隙相**，由强 CDW 涨落支配。
机理层面给出：Γ 点 Se-p 态顶部的带隙与 M 点 Ti-d 口袋的赝隙同源于**软声子介导的带间散射**；DFT 计算（计入声子贡献的自能与含小周期晶格畸变的 DFT）复现 M 点口袋的谱压制位置。

### 与课题的关联
这是立项依据 §一.2 讨论 TiSe₂ 正常态赝隙相的原始工作，此前申请书该句的角标错挂在 Grüner 1988 的 CDW 动力学综述上。本轮核实后改挂本条（参考文献表 [38]）。对课题的作用有两层：
（1）立项依据侧：赝隙相是"正常态一侧天平倾向电声机制"这条论证链的支点，该文把赝隙上界推到 1 eV 量级，支撑"电声耦合主导"的机制背景判断，与 Fragkos 等涨落区电声耦合主导一文（参考文献表 [2]）同属一个课题组的两项工作，物理上互为呼应；
（2）内容三侧：该文的"软声子介导带间散射"给出了模式选择性激发的具体物理对象——本项目要驱动的是 CDW 软模，该文指出赝隙开合与软声子涨落直接相关，即软模选择并非任意挑选而是有赝隙开闭这一可观测后果，这是方案侧"模式选择性激发"可行性的补充依据。
注意：该文与 Fragkos 等涨落区一文共用第一作者 Fragkos 且同属 Rossnagel/Descamps/Petit/Novko 团队，两条在正文中须分别引用、不可混用。

### 已引用位置
- 立项依据 §一.2 第二段（准二维硫族化合物段）："正常态一侧的天平也在倾斜：时间分辨与角分辨极紫外光电子能谱配合从头算电子-声子计算给出激发态能带测绘，软声子在费米能级上下约 1 eV 范围内诱导动量依赖的谱权重压制，TiSe₂ 的正常态被确定为强 CDW 涨落支配的赝隙相（据预印本）[38]。"
- 参考文献表 [38]（arXiv:2606.31298，2026，截至本轮未见刊出版）
- 课题设想 00_research_idea.md「来源与可靠性」段

---

## arXiv:2402.02931 / Phys. Rev. B 110, 085155

**阅读日期**：2026-11-16
**标题**：Femtosecond trimer quench in the unconventional charge-density-wave material 1T′-TaTe₂
**作者**：Till Domröse, Claus Ropers
**来源**：arXiv:2402.02931 [cond-mat.mtrl-sci]，2024-02-05 提交；已刊出于 Physical Review B 110, 085155 (2024)，DOI: 10.1103/PhysRevB.110.085155（CrossRef 内容协商核验，卷 110、期 8、文章号 085155、出版日 2024-08-28）。**刊出题名与预印本题名不同**（预印本为 "Femtosecond trimer quench cycled at megahertz rates in..."，刊出删去 "cycled at megahertz rates"），按本项目文献纪律以刊出题名为准。

### 核心结论
用超快纳米束电子衍射（120 keV 电子脉冲、200 fs 脉宽、670 nm 束径，配合定制样品支撑结构与可调重复频率）研究 1T′-TaTe₂ 的低温三聚体超晶格（3×3）向室温 3×1 结构的转变。核心发现三条：
（1）以 **2 MHz 重复率**（高于此前任何结构相变探测）实现光激发的可逆三聚体淬灭循环；
（2）一维协同原子运动驱动的淬灭在 **500 fs 以内**完成（接近阈值激发时约 470 ± 20 fs，瞬态完全抑制最快达 200 fs），比此前报道的 1.4 ps 快十倍以上；淬灭时间随激发通量与相变阈值的接近而延长，对应结构模的软化；
（3）高温 3×1 超结构对高密度电子激发异常稳健，与低温相形成鲜明对照，说明同一材料中外观相似但起源完全不同的两类结构序可以共存。
作者据此认为 1T′-TaTe₂ 可作为光诱导结构控制的可调平台。

### 与课题的关联
立项依据 §一.2 讨论"超快与理论侧的进展"时，此前该句的角标错挂在 Erasmus 等 2012 的 4Hb-TaSe₂ 公度-非公度相变条目上，而句中描述的"1T′-TaTe₂ 中三聚体 CDW 的循环淬灭"与"兆赫兹重复频率工作"两要素实为本条。本轮核实后改挂本条（参考文献表 [39]）。
对课题的作用：立项依据用来说明超快衍射的可采窗口已拓展到高频累积模式，从而支撑"多时窗拼接"在仪器层面可实现——即 fs–ps 段的衍射探测可以借助兆赫兹级累积把信噪比提到足以分辨单个弛豫通道。该文与 [4] 的 150 ps 重建时标形成两个不同的时间窗口参照，共同构成"单一时窗不足"的论据链。

### 已引用位置
- 立项依据 §一.2 第三段（超快与理论侧段）："同一构型以兆赫兹重复频率工作，可跟踪 1T′-TaTe₂ 中三聚体 CDW 的循环淬灭，超快衍射的可采窗口由此拓展到高频累积模式[39]。"
- 参考文献表 [39]（Phys. Rev. B 110, 085155 (2024)，DOI 已附）
- 课题设想 00_research_idea.md「来源与可靠性」段

---

## arXiv:2506.01470 / Phys. Rev. X 15, 041028

**阅读日期**：2026-11-16
**标题**：Persistence of charge ordering instability to Coulomb engineering in the excitonic insulator candidate TiSe₂
**作者**：Sebastian Buchberger, Yann in 't Veld, Akhil Rajan, Philip A. E. Murgatroyd, Brendan Edwards, Bruno K. Saika, Naina Kushwaha, Maria H. Visscher, Jan Berges, Dina Carbone, Jacek Osiecki, Craig Polley, Tim Wehling, Phil D. C. King（伦敦大学学院/钻石光源等）
**来源**：arXiv:2506.01470 [cond-mat]，2025-06-02 提交；已刊出于 Physical Review X 15, 041028 (2025)，DOI: 10.1103/9trc-9865（CrossRef 内容协商核验：卷 15、文章号 041028、出版日 2025-11-12）。

### 核心结论
用机械剥离结合分子束外延制备单层 TiSe₂/graphite 与单层 TiSe₂/hBN 两类异质结，通过改变衬底介电屏蔽环境探测激子对电荷序转变的贡献。核心发现三条：
（1）屏蔽环境改变驱动准粒子能带的重整化——石墨衬底（强屏蔽）下导带底位于费米能级以下约 40 meV，hBN 衬底（弱屏蔽）下导带底抬至费米能级以上 (12±15) meV，能隙由 173±6 meV 增至 239±15 meV；
（2）**>60 meV 的能带重整化**表明石墨衬底的介电屏蔽与 TiSe₂ 层内自由载流子的内部屏蔽共同作用；
（3）温度依赖的电子结构演化在两类衬底上不受影响，说明**激子并非驱动 TiSe₂ 中 CDW 转变的必要因素**。

### 与课题的关联
研究内容 2.2「跨相变对比以同批次体相单晶固定屏蔽与衬底环境」这一控制措施的直接依据。此前该句的两项论断全部挂在同一条角标上，其中「介电屏蔽使单层 TiSe₂ 的准粒子带隙重整化超过 60 meV」实际出自本文，而从头算给出的「晶格涨落而非激子关联主导电子局域化」出自 Pashov 等的从头算工作（参考文献表 [26]）。本轮核实后拆分：>60 meV 的屏蔽重整化改挂本文（参考文献表 [40]），晶格涨落结论改挂 [26]。
对课题的作用有两层：（1）内容侧：本文确立了"屏蔽环境改变电子态但不改变化学序转变"的实验事实，因而本项目在体相块体单晶上做通道分解时，衬底与屏蔽不再是隐含变量；（2）机制侧：本文与 [26] 一实验一计算，两条独立证据同时指向激子非必要，这与立项依据中"电声耦合与激子关联两种机制对超晶格响应的贡献至今没有定量分解"的缺口直接对接，构成内容三分解比例测量的对照基线。

### 已引用位置
- 研究内容 2.2：「库仑工程实验中，介电屏蔽使单层 TiSe₂ 的准粒子带隙重整化超过 60 meV，温度依赖的电子结构演化却不受影响，激子并非 CDW 转变的必要驱动[40]」
- 参考文献表 [40]（Phys. Rev. X 15, 041028 (2025)，DOI 已附）
- 课题设想 00_research_idea.md「来源与可靠性」段

---

## 四条著录更正（本轮外部核验记录）

**阅读日期**：2026-11-16。以下四条在正文中的引述内容无误，问题出在参考文献表条目的著录字段，本轮按出版方真身更正。

**（一）Laulhé 等的 TaS₂ 超快 CDW 态形成工作**
真身：Phys. Rev. Lett. 118, 247401 (2017)，DOI 10.1103/PhysRevLett.118.247401，完整题名 "Ultrafast Formation of a Charge Density Wave State in 1T-TaS₂: Observation at Nanometer Scales Using Time-Resolved X-Ray Diffraction"。原条目把材料写作 1T-TaSe₂ 并删去副标题，属材料实体错写，正文引述的 1T-TaS₂ 光致粗化结论本身正确。本轮按刊出题名逐字回录（参考文献表 [28]）。

**（二）Pashov 等的 TiSe₂ 晶格涨落工作**
真身：npj Comput. Mater. 11, 152 (2025)，DOI 10.1038/s41524-025-01631-4，题名 "TiSe₂ is a band insulator created by lattice fluctuations, not an excitonic insulator"，第一作者为 Dimitar Pashov（原条目误以 Larsen 为首作、题名亦为预印本形）。本轮回录为 Pashov D, Larsen R E, Watson M D, et al.（参考文献表 [26]）。

**（三）Que 等的激子序综述**
真身：Nature Reviews Physics (2026)，DOI 10.1038/s42254-026-00986-x，题名 "Excitonic order in quantum materials"，原条目附有出版方未收录的副标题 "fingerprints, platforms and opportunities"，本轮删去（参考文献表 [21]）。

**（四）Ye 等的 TiSe₂ 晶格势刚度工作**
真身题名含材料限定语 "...in the charge-density-wave material 1T-TiSe₂"，原条目截短为 "in the charge density wave of TiSe₂"，本轮按刊出题名回录（参考文献表 [15]）。
