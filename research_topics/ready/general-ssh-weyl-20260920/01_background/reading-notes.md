## 2301.08636

（Hajri & Ben Belgacem，"Convergent approaches for the Dirichlet Monge-Ampère problem"，math.NA，2023-01-20）

### 研究问题
为二维 Dirichlet Monge-Ampère 方程 det(D²u)=f（x∈Ω）、u=φ（∂Ω）、u 凸，构造三种数值方法并证明其收敛到黏性解。核心难点在于解可能奇异，要求数值格式保持单调（退化椭圆）。

### 研究背景
该方程联系 prescribed Gauss 曲率问题、仿射几何（仿射球/仿射极大曲面）、流体力学、几何光学与气象学（半地转方程），并应用于网格生成、图像配准、反射镜设计。既有方法——Alexandrov 几何离散 [24]、变分法（增广拉格朗日/最小二乘）[10,11]、vanishing moment [18]——对光滑解有效但对奇异解失效；Oberman 型宽模板格式 [22]（二维）/[19]（高维）收敛到黏性解，本文等效问题思路承自 [3]。

### 研究方法
由 AM-GM 变体不等式 2√det(AB)≤Tr(AB) 定义 g̃=Δu−2√f≥0，把 MAD 化为线性 Poisson 问题 Δu=2√f+g̃，再对 g 构造不动点迭代：g_{n+1}=Q(g_n)=√(u_xx²+u_yy²+2u_xy²+2f)−2√f 或 g_{n+1}=F(g_n)=√|det D²u^{g_n}−f|+g_n。用二维 17 点宽模板有限差分离散（λ₁、λ₂ 的单调格式，非降函数复合保持退化椭圆），以 Barles-Souganidis 理论证明收敛，离散系统用 Damped Newton 求解。

### 主要发现与核心结论
三种方法（A/B/C）均获收敛性证明并经数值算例验证：在 N×N 网格上取 N=31, 45, 63, 89, 127（步长 h=L/N），与 [19] 的 17 点宽模板法对照，报告各方法误差与总 CPU 时间随 N 的变化。结论：等效问题+宽模板单调离散可对奇异解情形构造收敛的 Dirichlet MA 求解器。

### 潜在研究方向
仅处理二维与最简 Dirichlet 边界条件，更一般的算子与边界条件（文中指向 [12]）未涉及。高维推广、收敛速率（Barles-Souganidis 框架本身不给出速率）为开放问题。


## 2310.07079

（Zhang*, Hua* & Qian，UC Santa Cruz，"Secure Decentralized Learning with Blockchain"，cs.CR/cs.LG，v1 2023-10-10、v2 2024-03-11）

### 研究问题
去中心化联邦学习（DFL）去除中心服务器后，如何防御恶意客户端投毒攻击并解决参与激励缺失。论文提出基于区块链的 BDFL（Blockchain-based Decentralized Federated Learning）框架。

### 研究背景
FL 依赖中心聚合器，存在单点故障与瓶颈；DFL 改用 P2P 邻居交换模型更新消除中心依赖，但无法假设客户端全诚实——恶意者可上传虚假模型更新发起投毒，低质量模型的误差还会随网络传播放大。同时直接把模型更新上链不可行（存储/计算开销、延迟、区块与交易大小限制）。

### 研究方法
BDFL 含四部件：模型验证的审计委员会、激励机制、声誉模型、动态网络更新协议套件（DFL 拓扑维护 + 模型交换协议）。关键设计：智能合约要求 ≥2/3 审计者签名确认；BFT 假设攻击者 <33% 共识参与者；验证用匿名公共验证集，阈值取最近 20 epoch 的平均精度 μ_{t−1} 与标准差 σ_{t−1}，A^ω<μ_{t−1}−2σ_{t−1} 判为恶意；恶意客户端声誉减半（rep_u→rep_u/2），诚实者按 (A−μ_{t−1})/σ_{t−1}·0.01 增益（例：A=μ+2σ 时声誉+0.02）；邻居数上限 2L。在真实数据集（MNIST/CIFAR 类）上以 10%/20%/30% 恶意客户端评估。

### 主要发现与核心结论
引入声誉机制后，即使存在 30% 恶意客户端，BDFL 仍在真实数据集上实现快速模型收敛与高精度；10%/20%/30% 三档攻击强度对比验证机制稳健。声誉与验证历史只定期上链（而非模型本身），规避了区块链存储瓶颈。

### 潜在研究方向
依赖较强假设：审计者算力相当、持有合理公共验证数据、恶意者不超过 1/3 审计者。声誉-区块链交互开销、高 churn 动态网络的扩展性、非 IID 数据分布场景仍待检验。


## 2312.05771

（Wang, Ren, Song, Zhang, Zheng & Qiang，中科院软件所，"Hacking Task Confounder in Meta-Learning"，cs.LG/stat.ML，v1 2023-12-10、v5 2024-05-29，IJCAI 2024）

### 研究问题
元学习中为何出现任务间负知识迁移（训练任务学到的知识反而损害未见任务泛化）？论文以因果分析定位根源——"任务混淆因子（Task Confounders）"，并提出即插即用的 MetaCRL 加以消除。

### 研究背景
元学习（N-way K-shot 采样、support/query 划分、双层优化）的通行假设是训练推进→知识更丰富→泛化更好；作者的反直觉实验显示负迁移真实存在。已有基线 MAML、MetaSGD、ANIL、T-NET 与因果类基线 IFSL、MR-MAML 均未针对任务间伪相关导致的负迁移建模。

### 研究方法
动机实验：从 miniImageNet 随机采样 400 个任务（300 训练/100 测试），以迁移指标 R_{i,j}=L(D_j^q, f_θ^{j,1})/L(D_j^q, f_θ^{j,2}) 量化（R<1 正迁移、R>1 负迁移）。用结构因果模型（SCM）分析，发现任务特定（非共享）因果因子与标签空间存在伪相关且随 batch 变化——Task Confounders。MetaCRL 双模块：解耦生成因子的 disentangling 模块 + 基于不变性的双层优化 causal 模块，可套用于任意元学习基线；实验覆盖 sinusoid 回归、位姿预测、药物活性预测、图像分类（miniImageNet、Omniglot，及 50 组共 300 个负迁移任务构成的 TC 数据集）。

### 主要发现与核心结论
多基准达 SOTA：相对即插即用类基线平均 MSE 降低 0.034 与 0.013，跨元学习基础模型 MSE 降低超 0.1；消融（5-way 1-shot miniImageNet、20-way 1-shot Omniglot 等）显示两模块结合时提升最大；使用 MetaCRL 后迁移直方图转向正迁移，因果因子提取精度随训练推进提升（f_θ3>f_θ2>f_θ1>原始模型的序关系被验证）。

### 潜在研究方向
混淆因子随 batch 变化，需训练全程持续消除而非一次性处理；引入 MetaCRL 带来额外训练时长，作者仅称 trade-off "acceptable" 未给系统开销分析；更大 backbone 与更广任务域的验证仍是开放问题。

---
备注：三篇笔记已同步存盘至 ~/notes/arxiv_2301.08636.md、~/notes/arxiv_2310.07079.md、~/notes/arxiv_2312.05771.md。另需提示：这三篇均属数值分析/区块链安全/元学习领域，与课题 general-ssh-weyl-20260920（SSH-Weyl 强场物理）主题无关，疑为检索环节的噪声结果。


## 2512.13140（Weeth & Madsen 2025）

- 阅读日期：2026-11-12
- 文献标题：Intense-Laser Nondipole-Induced Symmetry Breaking in Solids
- 来源：arXiv 预印本（researcher 定向检索 lit-gap-1793750870）
- 核心结论：强激光的非偶极效应本身即可在固体中诱导对称性破缺，给出偶极近似下不出现的响应分量。
- 与课题关联：为方向一假阳性来源补充驱动场侧的破缺通道——谐波谱破缺信号在归因于晶体拓扑前须先排除驱动场自身破缺；驱动场对称性由此作为受控扫描变量。
- 已引用位置：rationale §2.1（Trines 段后新段）、content §2.7 K1（假阳性来源其三）、references [42]。

## 2609.20085（van Essen, Ham, Nie & Kraus 2026）

- 阅读日期：2026-11-12
- 文献标题：Transient High-Harmonic Generation from Solids: From Spectroscopy and Control to Programmable Emission
- 来源：arXiv 预印本（researcher 定向检索 lit-gap-1793750870）
- 核心结论：把固体 HHG 的发射推进到瞬态调控与可编程输出，界定驱动场可调参数空间的外沿。
- 与课题关联：与 Weeth-Madsen 同向，共同说明驱动场调控维度会进入谐波谱，方向一的判定域须把该维度纳入受控扫描而非固定背景。
- 已引用位置：rationale §2.1（同段）、content §2.7 K1（假阳性来源其三）、references [43]。


## PhysRevLett.120.177401（Bauer & Hansen 2018）R4 补录

- 阅读日期：2026-11-12
- 文献标题：High-harmonic generation in solids with and without topological edge states
- 来源：Phys. Rev. Lett. 120, 177401 (2018)；DOI: 10.1103/PhysRevLett.120.177401（critic R4 CrossRef 核验通过；R3-04 承诺回录，本轮兑现）
- 核心结论：SSH 模型拓扑相在带隙下方的谐波产额比平庸相最高增强达 14 个数量级，带隙下方增强伴随谐波阶次向低阶压缩，边界态由此成为 HHG 的可观测增强源。
- 与课题关联：方向二 SSH 边界态谐波压缩判据的奠基文献，谐波压缩度阈值响应指标的机制来源。
- 已引用位置：rationale §2.2（Bauer 与 Hansen 段）、content §2.2，references [6]。
