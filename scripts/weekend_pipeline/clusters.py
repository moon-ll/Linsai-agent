#!/usr/bin/env python3
"""clusters.py — 输入端知识簇注册表（v6.9.12）。

设计目标（对应用户四点需求中的"聚类 + 防冗余"）：
    1. 持久化簇注册表：聚类结果跨周存活，不再每周无状态重猜。
    2. 增量归簇：新摘要优先匹配已有 open 簇（"沿已有类融入"），
       匹配失败才挂 orphans（单篇不成簇，凑齐 ≥2 篇才开新簇）。
    3. 簇生命周期：open（积累中）→ linked（已路由到课题）→ closed
       （陈旧关闭）。linked/closed 簇不再吸收新成员，但保留在注册
       表中供查重（防止同样的主题未来重复开簇）。
    4. 全部归簇逻辑零 LLM（确定性关键词 Jaccard），LLM 只用于簇内
       提炼（cluster_distill job），成本可控、可回归测试。

用法：
    from weekend_pipeline.clusters import (
        load_clusters, assign_summaries, form_new_clusters,
    )
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


CLUSTERS_PATH = PROJECT_ROOT / "memory" / "weekend-input" / "clusters.json"

# 簇状态
CLUSTER_OPEN = "open"        # 积累中，可吸收新成员
CLUSTER_LINKED = "linked"    # 已路由到课题（merge/new/expansion 均算）
CLUSTER_CLOSED = "closed"    # 陈旧关闭（长期无新成员且未链接课题）
CLUSTER_DEFERRED = "deferred"  # v6.9.18：路由暂缓（不满足 new 门槛，继续积累）

# 归簇参数（实测标定，见 _kw_similarity 注释）
# v7.2.56（输入端熔断根因修复）双阈值数据标定：对真实孤儿池 200 条样本
# 19900 对 item_similarity 全分布实测——均值 0.028 / 中位 0.011 / p99
# 0.140 / p99.9 0.202 / max 0.440。旧阈值 FORM 0.30 / ASSIGN 0.22 在
# 统计上不可达（≥0.30 对占比 0.005%，度数 ≥2 孤儿 0 条）——5 个周末
# assigned=0 / new_clusters=0 / ideas=0 即 input_pipeline_broken 的直接
# 根因。标定到 p99~p99.5 区间（0.15）：样本对通过率 0.68%、可成团种子
# 58 条；配合 FORM_CLUSTER_DEDUP 0.45 查重 + MIN_CLUSTER_MEMBERS=3 +
# topic_match 四重门槛（成员≥3 + LLM 知识卡 + 方向相关 + 相似度<0.50）
# 防乱聚。
ASSIGN_SIM_THRESHOLD = 0.15       # 新摘要 vs 已有簇：超过即归入
FORM_CLUSTER_SIM_THRESHOLD = 0.15  # orphans 互相之间：超过可聚团
# v6.10.28: 防换皮查重独立阈值——原与聚团共用过严：部分重叠但
# 研究问题不同的合法新方向（如"超快光谱孤儿团 vs 已有 HHG 簇"共享
# 泛词但核心词不同）被挡在簇外，09-19 实测 orphans 积压 567 条、
# assigned=0 即源于此。仅"与已有簇高度重合"（≥0.45）才拒开新簇；
# 聚团阈值本身已由 v7.2.56 按实测分布另行标定（见上）。
FORM_CLUSTER_DEDUP_THRESHOLD = 0.45
# v6.10.28: 相似度摘要正文通道截断（三通道之一，见 summary_similarity）
SUMMARY_TEXT_LIMIT = 500
MIN_CLUSTER_MEMBERS = 3           # 成新簇最少成员数（v6.9.18: 2→3，两篇
                                  # 凑数簇占 08-16 实测 143 簇的绝大多数）
# v7.3.21（用户裁决 决定 2）：成员计数改按"唯一论文"——同一论文经不同
# 来源入库会得到多个 source_id（arXiv 预印本/期刊版/不同检索源），按记录
# 计数会把 2 篇伪装成 3 成员。开关置 off 回到 v7.3.20 的记录计数口径。
PAPER_DEDUP_ENV = "LINSAI_CLUSTER_DEDUP_PAPERS"
# v7.3.23（用户裁决 5b-1）：孤儿池身份去重——同一论文经不同来源入库会在
# 孤儿池留下多条记录（arXiv 页 + 期刊页 + 简报转述），按 DOI/arXiv/归一
# 标题连通归并成 1 条，防止重复记录占用池容量与 42 天清理预算。
# 开关置 off 回到逐记录保留口径。
ORPHAN_DEDUP_ENV = "LINSAI_ORPHAN_DEDUP"
# v7.3.25（用户裁决 决定 8）：孤儿老化三段式（默认开，置 off 回滚）。
# 第一段：存活 >60 天 → 全池聚团时降权（权重 1.0 → 0.85 线性递减，不排除）；
# 第二段：存活 >180 天 → 移出全池聚团候选并归档到 registry.supplementary_pool
# （不删除，仍可 search_supplementary_pool 按需检索）；第三段（归档再激活）下轮议。
ORPHAN_AGING_ENV = "LINSAI_ORPHAN_AGING"
ORPHAN_SOFT_AGE_DAYS = 60
ORPHAN_ARCHIVE_AGE_DAYS = 180
ORPHAN_WEIGHT_FLOOR = 0.85
# v7.3.26（用户裁决）：人工确认的「同篇不同 arXiv 版本」白名单。去重时允许
# 归并，代表取较新版本（arXiv 年月大者），并打 needs_review 便于回溯。
CONFIRMED_SAME_PAPER_ARXIV = (
    frozenset({"2011.11079", "1906.12135"}),
)
# v7.3.21（决定 3）：超大连通分量（唯一论文 > 20）二级拆分。用"标题为主"
# 的更强特征重算子连通分量，每片须 ≥3 篇唯一论文；不足 3 篇的碎片并回
# 最相近的一片，避免孤儿回灌。开关置 off 回到不拆分口径。
LARGE_CLUSTER_SPLIT_ENV = "LINSAI_CLUSTER_SPLIT"
LARGE_CLUSTER_SPLIT_THRESHOLD = 20   # 触发二级拆分的唯一论文数
SPLIT_TITLE_WEIGHT = 0.7             # 拆分时标题权重（标题为主）
SPLIT_SIM_THRESHOLD = 0.30           # 拆分子分量的强相似阈值
# 跨领域簇标记（不删簇，交 topic_match LLM 仲裁判定）
# v7.3.25（用户裁决 决定 6）：判据放宽为「唯一论文 ≥3 且方向命中率 <0.5」——
# 旧口径（≥8 / <0.6）漏标 6 个明显跨领域小簇（金融、PSIS-LOO、计算成像、
# 机器学习力场、语义分割、无线能量传输）。
CROSS_DOMAIN_MIN_PAPERS = 3
CROSS_DOMAIN_DIRECTION_RATIO = 0.5   # 命中核心范式（强场操控/HHG 超快测量）比例下限
ORPHAN_MAX_AGE_DAYS = 42          # orphan 超龄丢弃（一直凑不成簇的散料）
CLUSTER_STALE_WEEKS = 4           # open 簇 N 周无新成员且未链接 → closed
# v6.10.7: 路由信号（topic_match defer 时回写，供 stale 清理判定）
ROUTE_SIGNAL_ACCUMULATE = "accumulate"  # 高相关但成员 <3 继续积累（抢救对象）
ROUTE_SIGNAL_OFF_TOPIC = "off_topic"    # 主题不对齐（积累无意义，可正常关闭）


# ---------------------------------------------------------------------------
# 注册表 I/O
# ---------------------------------------------------------------------------


def load_clusters(path: Optional[Path] = None) -> Dict[str, Any]:
    """加载簇注册表（不存在返回空骨架）。"""
    path = path or CLUSTERS_PATH
    data = load_json(path, default={})
    if "clusters" not in data:
        data["clusters"] = []
    if "orphans" not in data:
        data["orphans"] = []
    return data


def save_clusters(data: Dict[str, Any], path: Optional[Path] = None) -> None:
    """原子保存簇注册表。"""
    path = path or CLUSTERS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_utc()
    with file_lock("weekend-clusters"):
        save_json(path, data)


# ---------------------------------------------------------------------------
# 相似度（零 LLM，确定性）
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> set:
    """中英文混合分词：中文 2-gram 滑窗 + 英文单词（v6.9.18）。

    旧实现中文按 {2,8} 贪婪连续切分——中文无空格，整句被切成超长
    token，两个不同句子的 token 集几乎恒不相交，标题相似度对中文
    恒近 0（08-16 实测乱聚与好聚的标题分量无区分度）。2-gram 与
    kb_text 索引同口径（内联实现，避免跨包导入私有函数），长短语
    匹配由相邻 2-gram 组合覆盖。
    """
    if not text:
        return set()
    tokens = set()
    for m in re.finditer(r"[a-zA-Z]{3,}", text.lower()):
        tokens.add(m.group())
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", text):
        w = m.group()
        for i in range(len(w) - 1):
            tokens.add(w[i : i + 2])
    return tokens


def norm_keyword(kw: str) -> str:
    """关键词归一化（v6.9.14）。

    08-15 实测：GLM 摘要关键词存在同义不同形——"高次谐波产生" vs
    "高次谐波产生 (HHG)"，作为集合成员永不相等。统一去尾部括注、
    去首尾空白、转小写。
    """
    if not kw:
        return ""
    kw = re.sub(r"\s*[（(][^（）()]*[)）]\s*$", "", str(kw)).strip().lower()
    return kw


def kw_set(keywords) -> set:
    """关键词列表 → 归一化集合。"""
    return {norm_keyword(k) for k in (keywords or []) if norm_keyword(k)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _overlap(a: set, b: set) -> float:
    """overlap 系数：|A∩B| / min(|A|,|B|)。

    08-15 实测标定：摘要关键词仅 5-15 个，同子领域两篇论文通常共享
    2-4 个核心词。Jaccard 分母是并集（2 共享/9 并集 ≈ 0.22），对短
    集合系统性偏低——435 对真实摘要最高仅 0.161，阈值 0.22/0.30
    永远达不到，簇零形成、输入链空转。overlap 以较小集合为分母
    （2/5 = 0.40），语义是"这篇的核心词是否落在簇的核心词内"，与
    归簇意图一致。标题 token 分量保持 Jaccard（token 集较长，无此问题）。
    """
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


# ---------------------------------------------------------------------------
# 相似度通道 v2（v7.3.1，开关 LINSAI_CLUSTER_SIM=v1 可回滚）
# ---------------------------------------------------------------------------
# 背景：v7.2.56 的标定口径（关键词 overlap 0.5 + 标题 Jaccard 0.25 + 摘要
# Jaccard 0.25）在真实孤儿池上存在两个结构性问题——
#   ① 领域泛词（强场物理 / 非线性光学 / 固态高次谐波 等）在关键词集合里
#      占比极高，单条泛词命中即可让 overlap 过 0.15（1/6≈0.17），
#      832 条孤儿在 0.15 阈值下连成 581 条巨型连通分量，被
#      FORM_CLUSTER_DEDUP 0.45 整体拒绝 → 3 成员成团恒为 0；
#   ② 同义不同形（高次谐波产生 / 固态高次谐波 / HHG；MoS$_2$ / MoS₂）
#      未被归一，真实同主题对被系统性低估。
# v2 通道因此做三件事：文本归一（arXiv/年份/化学式/缩写与全称）+ 领域
# 泛词表抑制（三类通道各一份，离线按 1302 文档语料 df 统计生成，
# 方向特异性词已白名单保留）+ 字段加权（标题 0.35 > 摘要 0.20）。
# 阈值 0.15 与 3 成员门槛不变；开关置 v1 即恢复 v7.2.56 原口径。

SIM_CHANNEL_ENV = "LINSAI_CLUSTER_SIM"
SIM_CHANNEL_V1 = "v1"
SIM_CHANNEL_V2 = "v2"
SIM_FIELD_WEIGHTS = (0.45, 0.35, 0.20)  # 关键词 / 标题 / 摘要

_SUB_TRANS = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹", "01234567890123456789")
_RE_ARXIV = re.compile(r"(arxiv[:\s]*)?\b\d{4}\.\d{4,5}(v\d+)?\b", re.I)
_RE_DOI = re.compile(r"\b10\.\d{4,}/[^\s,;]+", re.I)
_RE_YEAR = re.compile(r"[（(](?:19|20)\d{2}[)）]")
_RE_DATE = re.compile(r"(20\d{2}[-年]\d{1,2}[-月]\d{1,2}日?|20\d{2}\d{4})")
_RE_LATEX_SUB = re.compile(r"_\{?(\d+)\}?")

_SIM_PHRASE_MAP = [
    # 英文全称 → 缩写（含高频同义写法）
    (re.compile(r"high[- ]order harmonic generation|high[- ]harmonic generation|harmonic generation", re.I), " hhg "),
    (re.compile(r"extreme[- ]ultraviolet|xuv", re.I), " xuv "),
    (re.compile(r"terahertz|thz", re.I), " thz "),
    (re.compile(r"time[- ]dependent density functional( theory)?|tddft", re.I), " tddft "),
    (re.compile(r"quantum geometric tensor|quantum geometry", re.I), " 量子几何 "),
    (re.compile(r"berry curvature", re.I), " 贝里曲率 "),
    (re.compile(r"moire|moiré|twisted bilayer", re.I), " moire "),
    # 中文同义族（长词优先，避免被短词截断）
    (re.compile(r"贝里曲率|berry曲率"), " 贝里曲率 "),
    (re.compile(r"量子几何张量|量子几何"), " 量子几何 "),
    (re.compile(r"高次谐波产生|高次谐波发射|固态高次谐波|固体高次谐波|高次谐波|谐波产生"), " 高次谐波 "),
    (re.compile(r"极紫外"), " xuv "),
    (re.compile(r"太赫兹"), " thz "),
    (re.compile(r"含时密度泛函(理论)?"), " tddft "),
    (re.compile(r"阿秒科学|阿秒物理|阿秒动力学|阿秒"), " 阿秒 "),
    (re.compile(r"摩尔纹|摩尔超晶格|莫尔超晶格|莫尔"), " moire "),
    (re.compile(r"外尔"), " weyl "),
    # 运维简报套话（不属于研究主题）
    (re.compile(r"林赛每日简报|每日简报|林赛简报|研究简报|文献简报|daily briefing", re.I), " "),
]

_STOP_EN = frozenset({
    "the", "and", "of", "in", "for", "with", "from", "by", "on", "to", "a", "an",
    "using", "based", "via", "study", "studies", "new", "effect", "effects", "role",
    "toward", "towards", "insight", "insights", "analysis", "approach", "investigation",
    "observation", "theory", "model", "models", "measurement", "measurements",
    "experiment", "experiments", "results", "review", "system", "systems", "method",
    "methods", "mechanism", "mechanisms", "application", "applications", "probe",
    "probing", "induced", "driven",
})

_STOP_ZH = frozenset({
    "研究", "方法", "我们", "以及", "可以", "通过", "基于", "进行", "系统", "不同",
    "影响", "作用", "本文", "该工", "工作", "提出", "实现", "体系", "问题", "结果",
    "表明", "具有", "一种", "主要", "重要", "方面", "过程", "条件", "情况", "其一",
    "其二", "两项", "共同", "发展", "提供", "利用", "导致", "使得", "采用", "获得",
    "显示", "揭示", "讨论", "对比", "结合", "这一", "其中", "此外", "因此", "从而",
    "需要", "能够", "来自", "相关", "证明", "观察到", "理论", "分析", "探讨", "阐释",
    "给出", "同时", "进一步", "方法学", "实验", "数值",
})

# 领域泛词表（离线按 1302 文档语料 df 生成：关键词 df≥5%、标题 df≥5%、
# 摘要 df≥10%；方向特异性词如 量子几何/贝里曲率/莫尔超晶格/moire/tddft
# 已从关键词表白名单剔除）。可按新语料增删，命中即视为"无区分度证据"。
_SimGenericKeywords = frozenset({
    "一性", "二维", "二维材料", "互作", "交变", "依赖", "信息", "偏振", "偶极", "光场",
    "光子", "光学", "光电", "光谱", "共振", "关联", "凝聚", "几何", "函数", "分子",
    "分辨", "劈裂", "力学", "动力", "动量", "半导", "压缩", "原子", "原理", "双层",
    "反常", "反演", "反铁", "变磁", "周期", "响应", "器学", "场物", "增强", "墨烯",
    "声子", "子体", "子光", "子几", "子动", "子学", "学习", "密度", "对称", "导体",
    "射线", "尔效", "层间", "工程", "带内", "带间", "干涉", "平衡", "强场", "强场物理",
    "快光", "快动", "性光", "性原", "性材", "性破", "扑材", "拓扑", "拓扑材料", "探测",
    "控制", "效应", "散射", "方程", "旋劈", "旋电", "时间", "晶体", "机器", "材料",
    "极化", "模型", "模拟", "次谐", "泵浦", "流子", "测量", "演对", "激光", "物理",
    "理计", "电子", "电流", "电离", "电荷", "相互", "相位", "相变", "相干", "瞬态",
    "石墨", "破缺", "磁体", "磁性", "称性", "空间", "第一", "第一性原理计算", "红外",
    "线性", "经典", "结构", "绝缘", "维材", "缘体", "耦合", "联电", "聚态", "能带",
    "能谷", "能量", "脉冲", "自旋", "自旋电子学", "计算", "调控", "谐波", "谱学",
    "谷电", "超快", "超快光学", "超快光谱学", "跃迁", "轨道", "载流", "输运", "过渡",
    "近似", "连续", "里曲", "重构", "量子", "量子光学", "金属", "铁磁", "间分", "阿秒",
    "隧穿", "霍尔", "非线", "非线性光学", "驱动", "高次", "高次谐波",
})
_SimGenericTitle = frozenset({
    "attosecond", "electron", "field", "hhg", "high", "light", "nonlinear", "optical",
    "phase", "quantum", "spectroscopy", "spin", "time", "ultrafast", "wave",
})
_SimGenericSummary = frozenset({
    "hhg", "中的", "了新", "产生", "体中", "作为", "供了", "依赖", "偏振", "光场",
    "光子", "光学", "光谱", "关联", "几何", "分辨", "力学", "动力", "动量", "原子",
    "参数", "发现", "周期", "响应", "对称", "平台", "强场", "强度", "拓扑", "探测",
    "效应", "文提", "方案", "时间", "显著", "机制", "材料", "极化", "核心", "框架",
    "模型", "模拟", "次谐", "测量", "激光", "物理", "电子", "直接", "相位", "相干",
    "磁体", "示了", "称性", "空间", "立了", "线性", "结构", "耦合", "能带", "能量",
    "脉冲", "自旋", "观测", "计算", "诱导", "调控", "谐波", "超快", "轨道", "通道",
    "量子", "铁磁", "阿秒", "非线", "驱动", "高次",
})


def sim_channel() -> str:
    """当前相似度通道（默认 v2；LINSAI_CLUSTER_SIM=v1 回滚旧口径）。"""
    return os.environ.get(SIM_CHANNEL_ENV, SIM_CHANNEL_V2).strip().lower()


def _normalize_text(text: str) -> str:
    """相似度通道 v2 文本归一：下标/LaTeX/arXiv/DOI/年份/同义词映射。"""
    s = str(text or "").translate(_SUB_TRANS)
    s = s.replace("$", "").replace("\\", " ")
    s = _RE_LATEX_SUB.sub(r"\1", s)
    s = s.replace("{", " ").replace("}", " ")
    s = _RE_ARXIV.sub(" ", s)
    s = _RE_DOI.sub(" ", s)
    s = _RE_YEAR.sub(" ", s)
    s = _RE_DATE.sub(" ", s)
    for rx, rep in _SIM_PHRASE_MAP:
        s = rx.sub(rep, s)
    return s


def _tokens_v2(text: str) -> set:
    """v2 分词：英文词（去停用）+ 化学式（MoS2/WS2）+ 中文 2-gram（去停用）。"""
    s = _normalize_text(text)
    tokens = set()
    for m in re.finditer(r"[a-zA-Z]{3,}", s.lower()):
        w = m.group()
        if w not in _STOP_EN:
            tokens.add(w)
    for m in re.finditer(r"\b[A-Z][a-z]?(?:[A-Z][a-z]?)?\d+\b", s):
        tokens.add(m.group().lower())
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", s):
        w = m.group()
        for i in range(len(w) - 1):
            gram = w[i:i + 2]
            if gram not in _STOP_ZH:
                tokens.add(gram)
    return tokens


def _kw_tokens_v2(keywords) -> set:
    """v2 关键词分词：归一化整词 + 中文 2-gram（同义族经归一后自然合并）。"""
    tokens = set()
    for kw in (keywords or []):
        nk = norm_keyword(kw)
        if not nk:
            continue
        nt = _normalize_text(nk).strip()
        if not nt:
            continue
        tokens.add(nt.replace(" ", "_"))
        if re.search(r"[\u4e00-\u9fff]", nt):
            for m in re.finditer(r"[\u4e00-\u9fff]{2,}", nt):
                w = m.group()
                for i in range(len(w) - 1):
                    gram = w[i:i + 2]
                    if gram not in _STOP_ZH:
                        tokens.add(gram)
    return tokens


def cluster_summary_text(cluster: Dict[str, Any], limit: int = 800) -> str:
    """簇侧文本：簇摘要 + 成员摘要拼接（相似度摘要通道用）。

    v6.10.28: 纯 keywords+title 对"关键词抽取不全但研究同源"的文献
    系统性失配（09-19 实测 10 条新料 assigned=0 全落 orphans）。簇的
    主题信号不只在其关键词，成员摘要正文是关键词缺失时的兜底。
    """
    parts = [cluster.get("summary", "") or ""]
    for m in (cluster.get("member_summaries") or [])[:6]:
        s = (m.get("summary") or "").strip()
        if s:
            parts.append(s)
    return " ".join(parts)[:limit]


def _features(item: Dict[str, Any], cluster_side: bool = False) -> Tuple[set, set, set]:
    """抽取三通道特征（关键词 / 标题 / 摘要正文），随通道开关切换口径。"""
    if sim_channel() == SIM_CHANNEL_V1:
        kw = kw_set(item.get("keywords"))
        ti = _tokenize(item.get("title", ""))
        su = _tokenize(
            cluster_summary_text(item) if cluster_side
            else (item.get("summary") or "")[:SUMMARY_TEXT_LIMIT]
        )
        return kw, ti, su
    kw = _kw_tokens_v2(item.get("keywords"))
    ti = _tokens_v2(item.get("title", ""))
    su = _tokens_v2(
        cluster_summary_text(item) if cluster_side
        else (item.get("summary") or "")[:SUMMARY_TEXT_LIMIT]
    )
    return kw, ti, su


def _overlap_specific(spec_a: set, spec_b: set, raw_a: set, raw_b: set) -> float:
    """v2 overlap：分子 = 具体词（抑制后）交集，分母 = 原始较小集合。

    分母若也用抑制后集合，某条目的关键词被泛词表剔到只剩 1-2 个词时，
    单点巧合即得 overlap=1.0（v7.3.18 实测使 5 条 borderline 夹具误判
    为直接归簇）。分母取原始集合，泛词抑制只减分子不缩分母。
    """
    if not spec_a or not spec_b or not raw_a or not raw_b:
        return 0.0
    return len(spec_a & spec_b) / min(len(raw_a), len(raw_b))


def _jaccard_specific(spec_a: set, spec_b: set, raw_a: set, raw_b: set) -> float:
    """v2 Jaccard：分子 = 具体词交集，分母 = 原始并集（同上防分母缩水）。"""
    if not spec_a or not spec_b:
        return 0.0
    den = len(raw_a | raw_b)
    return len(spec_a & spec_b) / den if den else 0.0


def _score_features(fa: Tuple[set, set, set], fb: Tuple[set, set, set],
                    channel: Optional[str] = None) -> float:
    """按通道口径组合三通道分（v1 旧口径 / v2 泛词抑制 + 字段加权）。"""
    channel = channel or sim_channel()
    if channel == SIM_CHANNEL_V1:
        return (
            0.5 * _overlap(fa[0], fb[0])
            + 0.25 * _jaccard(fa[1], fb[1])
            + 0.25 * _jaccard(fa[2], fb[2])
        )
    kw_a, kw_b = fa[0] - _SimGenericKeywords, fb[0] - _SimGenericKeywords
    ti_a, ti_b = fa[1] - _SimGenericTitle, fb[1] - _SimGenericTitle
    su_a, su_b = fa[2] - _SimGenericSummary, fb[2] - _SimGenericSummary
    w_kw, w_ti, w_su = SIM_FIELD_WEIGHTS
    return (
        w_kw * _overlap_specific(kw_a, kw_b, fa[0], fb[0])
        + w_ti * _jaccard_specific(ti_a, ti_b, fa[1], fb[1])
        + w_su * _overlap_specific(su_a, su_b, fa[2], fb[2])
    )


def summary_similarity(item: Dict[str, Any], cluster: Dict[str, Any]) -> float:
    """摘要条目 vs 簇的相似度（三通道：关键词 0.45 / 标题 0.35 / 摘要 0.20）。

    v7.3.1: v2 通道对领域泛词做抑制、对同义不同形做归一，标题权重高于
    摘要（标题是最具体的主题信号）；`LINSAI_CLUSTER_SIM=v1` 回滚旧口径
    （0.5/0.25/0.25）。
    """
    return _score_features(_features(item), _features(cluster, cluster_side=True))


def item_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """两条摘要之间的相似度（orphan 聚团用），三通道口径与归簇一致。"""
    return _score_features(_features(a), _features(b))


def cluster_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """两簇之间的相似度（v6.9.18 compose 同课题归并注入用）。

    口径与归簇一致：关键词 overlap 0.7 + 标题 Jaccard 0.3。同目标
    课题的多个簇若彼此相似，只注入成员最多簇的知识卡，其余只挂
    信息源——根治 08-16 实测 BSV 课题被 6 个变体簇重复注入。
    """
    return item_similarity(a, b)


# ---------------------------------------------------------------------------
# 增量归簇
# ---------------------------------------------------------------------------


# v7.2.4: orphan → 现有课题直连路由参数（不经簇的补充通道）
# v7.2.57: 0.35 → 0.25——按真实分布重标定（与 v7.2.56 聚类阈值同方法论）。
ORPHAN_ROUTE_SIM_THRESHOLD = 0.25
"""orphan vs 课题文本路由线。口径 = 0.6×关键词命中率 + 0.4×正文 overlap：

关键词命中率（主信号，可解释）＝ orphan 关键词中其全部 2-gram/整词
都出现在课题设想文本里的比例；正文 overlap ＝ orphan 摘要 token 落在
课题文本中的比例（min 集合分母）。

v7.2.57 标定依据：首版 0.35 落在真实分布远端统计不可达——917 孤儿 ×
11 课题实测每孤儿最高分分布 max=0.359 / p99=0.331 / p95=0.288 / p85
≈0.25 / 中位 0.183，≥0.35 仅 1 条（0.1%），通道连续多周零路由（10-29
健康检查 #9 残余项实测）。下调至 0.25（p85 区间）后过线 135 条，其中
86% 同时通过方向词表+核心范式双命中（input_jobs 侧 route_filter 前置
过滤，与 _new_gates 同口径），叠加每课题周上限 5 条防灌水。"""

ORPHAN_ROUTE_MAX_PER_PROPOSAL = 5
"""每课题每周挂载上限（防灌水：低分长尾大量涌入会稀释课题视野）。"""


def _kw_in_text(kw: str, text_tokens: set) -> bool:
    """关键词是否命中课题文本 token 集（v7.2.4）。

    中文词：其全部相邻 2-gram 均在文本 token 集中才算命中（整词级
    匹配，避免单 2-gram 巧合）；英文词：整词（≥3 字符 lower）在集合。
    """
    nk = norm_keyword(kw)
    if not nk:
        return False
    if re.fullmatch(r"[a-z0-9 \-]+", nk):
        words = [w for w in nk.split() if len(w) >= 3]
        if not words:
            return False
        return all(w in text_tokens for w in words)
    grams = {nk[i:i + 2] for i in range(len(nk) - 1)}
    if not grams:
        return nk in text_tokens
    return grams.issubset(text_tokens)


def orphan_proposal_similarity(orphan: Dict[str, Any], proposal_text: str) -> float:
    """orphan vs 课题设想文本相似度（v7.2.4，零 LLM 确定性）。

    口径：0.6×关键词命中率 + 0.4×正文 overlap。课题文本无现成
    keywords（设想文档非摘要产物），关键词通道反向实现——逐个检查
    orphan 关键词是否被课题文本覆盖；正文通道与 item_similarity 的
    overlap 口径一致（短集合分母，语义"该文献核心词是否落在课题内"）。
    """
    p_tokens = _tokenize(proposal_text)
    if not p_tokens:
        return 0.0
    kws = kw_set(orphan.get("keywords"))
    if kws:
        hits = sum(1 for kw in kws if _kw_in_text(kw, p_tokens))
        kw_hit = hits / len(kws)
    else:
        kw_hit = 0.0
    o_tokens = _tokenize((orphan.get("summary") or "")[:SUMMARY_TEXT_LIMIT])
    text_ov = _overlap(o_tokens, p_tokens)
    return 0.6 * kw_hit + 0.4 * text_ov


def route_orphans_to_proposals(
    registry: Dict[str, Any],
    proposal_texts: Dict[str, str],
    threshold: float = ORPHAN_ROUTE_SIM_THRESHOLD,
    max_per_proposal: int = ORPHAN_ROUTE_MAX_PER_PROPOSAL,
    route_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> Dict[str, Any]:
    """orphan 池直连现有课题（v7.2.4）——不经簇的补充路由。

    背景：簇池常态 linked 化后 open 簇清零（09-28 实测 62 簇 0 open），
    recycle_orphans 二次匹配无对象；单篇不成簇的新文献（每周 ~9 篇）
    只剩 42 天超龄清理＝知识流失。本通道以课题设想文本为靶，超阈值
    的 orphan 挂载为课题 supplementary 信息源并移出池子（挂载动作由
    调用方 input_jobs 执行——本函数只做匹配与池操作，保持纯函数可测）。

    v7.2.57: 新增 route_filter 前置过滤——阈值只保证"与某课题文本相
    似"，不保证"方向在射程内"（实测过线条目中 14% 双命中不过）。
    调用方传入方向闸（scope_hit + core_theme_hit，与 _new_gates 同
    口径）双重把关；filter 拒绝的 orphan 一律留池（不移出，继续等待
    聚簇或超龄清理），不产生路由记录。

    Args:
        registry: 簇注册表（orphans 原地更新：命中项移除，余者保留）
        proposal_texts: {proposal_id: 设想文本}
        threshold: 路由线（ORPHAN_ROUTE_SIM_THRESHOLD）
        max_per_proposal: 每课题本周挂载上限
        route_filter: 可选方向闸（入参 orphan 条目，True 才允许路由）

    Returns:
        {"routed": [{"source_id", "proposal_id", "score"}...],
         "candidates": N, "remaining": N}
    """
    routed: List[Dict[str, Any]] = []
    orphans = registry.setdefault("orphans", [])
    per_proposal: Dict[str, int] = {}
    keep: List[Dict[str, Any]] = []
    for o in orphans:
        sid = o.get("source_id", "")
        best_pid, best_score = None, 0.0
        if sid and proposal_texts and (route_filter is None or route_filter(o)):
            for pid, text in proposal_texts.items():
                if per_proposal.get(pid, 0) >= max_per_proposal:
                    continue
                score = orphan_proposal_similarity(o, text)
                if score > best_score:
                    best_score, best_pid = score, pid
        if best_pid is not None and best_score >= threshold:
            routed.append({
                "source_id": sid,
                "proposal_id": best_pid,
                "score": round(best_score, 3),
                # v7.2.4: 原始条目副本——调用方挂载失败时塞回池防丢
                "entry": dict(o),
            })
            per_proposal[best_pid] = per_proposal.get(best_pid, 0) + 1
        else:
            keep.append(o)
    registry["orphans"] = keep
    return {
        "routed": routed,
        "candidates": len(orphans),
        "remaining": len(keep),
    }


def _new_cluster_id(existing_ids: Optional[set] = None) -> str:
    """生成簇 id：cl_{日期}_{uuid6}，注册表内查重（v6.9.18）。

    旧实现用 id(object()) 做 hash seed——CPython 中临时对象立即回收，
    id 高频复用，同批创建大量碰撞（08-16 实测 143 簇中同一 ID 最多
    重复 10 次，mark_linked/cluster_index 按 ID 索引全部错绑）。
    """
    import uuid
    existing = existing_ids or set()
    while True:
        cid = f"cl_{now_utc()[:10].replace('-', '')}_{uuid.uuid4().hex[:6]}"
        if cid not in existing:
            return cid


def _top_group_keywords(group: List[Dict[str, Any]], top: int = 3) -> List[str]:
    """团内高频关键词（v6.9.18 簇标题来源）。

    按关键词在团内出现的成员数排序（被 ≥2 个成员共享的词更能代表
    共同主题），同频按首次出现顺序。取代旧实现直接拿种子论文标题
    当簇标题（单篇标题不是主题名）。
    """
    counts: Dict[str, int] = {}
    order: Dict[str, int] = {}
    for idx, g in enumerate(group):
        for kw in (g.get("keywords") or []):
            nk = norm_keyword(kw)
            if not nk:
                continue
            counts[nk] = counts.get(nk, 0) + 1
            order.setdefault(nk, idx)
    ranked = sorted(counts, key=lambda k: (-counts[k], order[k]))
    shared = [k for k in ranked if counts[k] >= 2]
    picked = (shared or ranked)[:top]
    return picked


def _merge_keywords(cluster: Dict[str, Any], item: Dict[str, Any], cap: int = 12) -> None:
    """簇关键词合并：归一化去重，保留新词，上限 cap。"""
    existing: list = []
    seen = set()
    for kw in list(cluster.get("keywords", []) or []):
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            existing.append(nk)
            seen.add(nk)
    for kw in item.get("keywords", []) or []:
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            existing.append(nk)
            seen.add(nk)
    cluster["keywords"] = existing[:cap]


# v6.10.38: 吸收上限——linked 簇影子吸收防无限膨胀
MAX_ABSORB_MEMBERS = 30


def absorbable_clusters(registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """可吸收簇：open 簇 + 未超上限的 linked 簇（closed 排除）。

    v6.10.38：linked 簇恢复吸收（"影子吸收"）——簇生命周期是"成簇→
    当周路由→linked→死"，open 簇常态清零（09 月连续 4 周 assigned=0
    实测），同主题新文献被开簇查重挡回孤儿池等 42 天清理=知识流失。
    linked 簇新成员不触发重新路由，只作增量信息源。
    """
    out: List[Dict[str, Any]] = []
    for c in registry.get("clusters", []):
        if c.get("status") == CLUSTER_OPEN:
            out.append(c)
        elif (
            c.get("status") == CLUSTER_LINKED
            and len(c.get("member_source_ids") or []) < MAX_ABSORB_MEMBERS
        ):
            out.append(c)
    return out


def assign_summaries(
    summaries: List[Dict[str, Any]],
    registry: Dict[str, Any],
    threshold: float = ASSIGN_SIM_THRESHOLD,
    llm_arbiter=None,
    borderline_low: float = 0.12,
) -> Dict[str, Any]:
    """把本周摘要增量归入可吸收簇（open + linked）；未匹配的挂 orphans。

    防冗余核心：closed 簇不吸收（已陈旧关闭）。v6.10.38 重大修正——
    linked 簇恢复吸收（"影子吸收"）：旧口径只与 open 簇匹配，而簇的
    生命周期是"成簇→当周路由→linked→死"，open 簇常态清零（09 月连续
    4 周 assigned=0 实测），同主题新文献被开簇查重（防换皮）挡回孤儿
    池等 42 天清理=系统性知识流失。linked 簇吸收的新成员不触发重新
    路由，只作增量信息源（cluster_assign 侧挂载 supplementary）。
    成员上限 MAX_ABSORB_MEMBERS 防无限膨胀。单条摘要可归多个簇时选最高分。

    v6.10.12: borderline LLM 仲裁层——纯 Jaccard 阈值 0.22 对跨术语语义
    相关的新文献系统性失配（实测 09-12/13 三天 assigned=0、50 条摘要全
    orphan、orphan 池膨胀至 471 且 42 天清理=知识流失）。对最佳候选分
    落在 [borderline_low, threshold) 的摘要，交 llm_arbiter(summary,
    cluster, score) 做语义判断：True 归入（method="llm"），False/不可用
    保持 orphan（零成本兜底）。保护簇（accumulate 等第 3 篇）直接受益。

    Args:
        llm_arbiter: 可选回调 (item, cluster, score) -> bool；None 保持
            纯 Jaccard 行为（回归兼容）。

    Returns:
        {"assigned": [{cluster_id, source_id, score, method?, cluster_status?}...],
         "orphaned": [source_id...]}
    """
    assigned: List[Dict[str, Any]] = []
    orphaned: List[str] = []
    candidates = absorbable_clusters(registry)

    for item in summaries:
        sid = item.get("source_id", "")
        if not sid:
            continue
        best_cluster, best_score = None, 0.0
        for c in candidates:
            score = summary_similarity(item, c)
            if score > best_score:
                best_score, best_cluster = score, c

        method = "jaccard"
        if best_cluster is None or best_score < threshold:
            # v6.10.12: borderline 区间交 LLM 语义仲裁
            if (
                llm_arbiter is not None
                and best_cluster is not None
                and best_score >= borderline_low
            ):
                try:
                    if llm_arbiter(item, best_cluster, best_score):
                        method = "llm"
                    else:
                        best_cluster = None
                except Exception:
                    best_cluster = None  # 仲裁异常保守 orphan
            else:
                best_cluster = None

        if best_cluster is not None:
            _absorb_member(best_cluster, item)
            entry = {"cluster_id": best_cluster["cluster_id"], "source_id": sid, "score": round(best_score, 3)}
            if method != "jaccard":
                entry["method"] = method
            if best_cluster.get("status") == CLUSTER_LINKED:
                entry["cluster_status"] = "linked"
            assigned.append(entry)
        else:
            # 挂 orphans 等凑簇（单篇不成簇）
            orphans = registry.setdefault("orphans", [])
            if not any(o.get("source_id") == sid for o in orphans):
                orphans.append({
                    "source_id": sid,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "keywords": item.get("keywords", []) or [],
                    "path": item.get("path", ""),
                    "first_seen": now_utc(),
                })
            orphaned.append(sid)

    return {"assigned": assigned, "orphaned": orphaned}


def _absorb_member(cluster: Dict[str, Any], item: Dict[str, Any]) -> None:
    """成员吸收（assign_summaries / recycle_orphans 共用）。

    沿已有类融入：追加成员、合并关键词、刷新时间戳。
    v6.9.18: member_summaries 补存 path——compose 的信息源挂载以
    簇内成员自述为准（跨周可用），不再依赖当天 summaries。
    """
    members = cluster.setdefault("member_source_ids", [])
    sid = item.get("source_id", "")
    if sid and sid not in members:
        members.append(sid)
        cluster.setdefault("member_summaries", []).append({
            "source_id": sid,
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "keywords": item.get("keywords", []) or [],
            "path": item.get("path", ""),
        })
        _merge_keywords(cluster, item)
        cluster["updated_at"] = now_utc()


# v6.10.29: 孤儿池规模防护上限（v7.2.56 起不再触发回退，保留常量供
# 历史引用与监控对账；邻接表一次预计算后度数选取为查表 O(n)）
MAX_LEADER_SEARCH = 800


# ---------------------------------------------------------------------------
# 论文身份去重 + 超大簇二级拆分（v7.3.21，用户裁决 决定 2 / 决定 3）
# ---------------------------------------------------------------------------


def _flag_on(env_name: str, default: str = "on") -> bool:
    """布尔开关读取：off/0/false/no/disabled/空 均视为关闭。"""
    raw = os.environ.get(env_name, default)
    return str(raw).strip().lower() not in {"off", "0", "false", "no", "disabled", ""}


def paper_dedup_enabled() -> bool:
    """论文级去重开关（LINSAI_CLUSTER_DEDUP_PAPERS，默认开）。"""
    return _flag_on(PAPER_DEDUP_ENV)


def large_split_enabled() -> bool:
    """超大簇二级拆分开关（LINSAI_CLUSTER_SPLIT，默认开）。"""
    return _flag_on(LARGE_CLUSTER_SPLIT_ENV)


def orphan_dedup_enabled() -> bool:
    """孤儿池身份去重开关（LINSAI_ORPHAN_DEDUP，默认开）。"""
    return _flag_on(ORPHAN_DEDUP_ENV)


def orphan_aging_enabled() -> bool:
    """孤儿老化三段式开关（LINSAI_ORPHAN_AGING，默认开）。"""
    return _flag_on(ORPHAN_AGING_ENV)


_RE_PAPER_DOI = re.compile(r"(?<![\d.])10\.\d{4,}/[^\s,;\"'）)]+", re.I)
# arXiv ID：兼容 2310.17007 / 2404_05830（文件名把点写成下划线）
_RE_PAPER_ARXIV = re.compile(r"(\d{4})[._](\d{4,5})(?:v\d+)?", re.I)
_RE_TITLE_KEY = re.compile(r"[^a-z0-9\u4e00-\u9fff]+")


def _norm_title_key(title: str) -> str:
    """标题归一化身份键：小写、去 arXiv/年份、去标点空白。"""
    s = _normalize_text(str(title or ""))
    return _RE_TITLE_KEY.sub("", s.lower())[:120]


def paper_keys(item: Dict[str, Any]) -> List[str]:
    """论文的全部可用身份标识（DOI / arXiv ID / 归一化标题）。

    同一论文经不同来源入库会得到多个 source_id（arXiv 预印本、期刊版、
    不同检索源），按记录计数会把 2 篇伪装成 3 成员。真实语料里 DOI 常被
    写成 slug（`10-1103-84vm-tvzm`）无法解析，所以不能只取单一主键——
    改为返回全部可识别标识，由 `_unique_papers` 按「任一标识相同即同篇」
    做连通归并，标题在 DOI/arXiv 缺失时兜底。
    """
    keys: List[str] = []
    doi_blob = " ".join(
        str(item.get(k, "") or "") for k in ("source_id", "path", "doi", "title")
    )
    for m in _RE_PAPER_DOI.finditer(doi_blob):
        keys.append("doi:" + m.group(0).rstrip(".").lower())
    ax_blob = " ".join(
        str(item.get(k, "") or "") for k in ("source_id", "path", "arxiv_id", "doi")
    )
    for m in _RE_PAPER_ARXIV.finditer(ax_blob):
        keys.append("arxiv:%s.%s" % (m.group(1), m.group(2)))
    tkey = _norm_title_key(item.get("title", ""))
    if len(tkey) >= 8:
        keys.append("title:" + tkey)
    if not keys:
        # v7.3.24: 无任何可识别标识时不生成公共兜底键——旧实现返回
        # "sid:unknown"，会把所有匿名记录误并成同一篇（连通归并的假阳性）。
        # 返回空列表让 _paper_identity_groups 视其为独立记录。
        sid = str(item.get("source_id", "") or "").strip().lower()
        if sid:
            keys.append("sid:" + sid)
    return keys


def paper_key(item: Dict[str, Any]) -> str:
    """论文主键（DOI > arXiv ID > 归一化标题，供展示/审计用，决定 2）。"""
    keys = paper_keys(item)
    if keys:
        return keys[0]
    return "sid:" + (str(item.get("source_id", "") or "").strip().lower() or "unknown")


def _paper_identity_groups(items: List[Dict[str, Any]]) -> List[List[int]]:
    """按 DOI/arXiv/归一标题「任一标识相同即同篇」做连通归并。

    返回每组的原始下标列表（组内下标升序，组间按首下标升序，确定性）。
    """
    n = len(items)
    if n == 0:
        return []
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner: Dict[str, int] = {}
    for i, item in enumerate(items):
        for k in paper_keys(item):
            if k in owner:
                ra, rb = _find(i), _find(owner[k])
                if ra != rb:
                    parent[rb] = ra
            else:
                owner[k] = i
    comps: Dict[int, List[int]] = {}
    for i in range(n):
        comps.setdefault(_find(i), []).append(i)
    return sorted((sorted(g) for g in comps.values()), key=lambda g: g[0])


def _unique_papers(group: List[Dict[str, Any]]) -> List[str]:
    """团内唯一论文数：按任一身份标识相同即同篇做连通归并（决定 2）。

    返回每个唯一论文的主键（排序保证确定性）。同一论文的 arXiv 记录
    （`arxiv:2310.17007`）与期刊记录（标题相同、DOI 为 slug 无法解析）
    会经标题键合并成 1 篇，不会把 2 篇算成 3 成员。
    """
    return sorted(paper_key(group[g[0]]) for g in _paper_identity_groups(group))


def _orphan_richness(item: Dict[str, Any]) -> Tuple[int, int, int]:
    """去重代表选择的信息丰度：有路径 > 摘要长 > 关键词多。"""
    return (
        1 if str(item.get("path", "") or "") else 0,
        len(str(item.get("summary", "") or "")),
        len(item.get("keywords") or []),
    )


def _paper_arxiv_ids(item: Dict[str, Any]) -> List[Tuple[str, str]]:
    """提取记录中的 arXiv ID 片段（年月, 编号），供「可否归并」判定。"""
    blob = " ".join(
        str(item.get(k, "") or "") for k in ("source_id", "path", "arxiv_id", "doi")
    )
    return [(m.group(1), m.group(2)) for m in _RE_PAPER_ARXIV.finditer(blob)]


def _paper_dois(item: Dict[str, Any]) -> List[str]:
    """提取记录中的 DOI 片段（小写），供「可否归并」判定。"""
    blob = " ".join(
        str(item.get(k, "") or "") for k in ("source_id", "path", "doi", "title")
    )
    return [m.group(0).rstrip(".").lower() for m in _RE_PAPER_DOI.finditer(blob)]


def dedup_orphans(registry: Dict[str, Any]) -> int:
    """孤儿池身份去重（v7.3.23，用户裁决 5b-1 / 7）。

    同一论文经不同来源入库会在孤儿池留下多条记录（arXiv 页 + 期刊页 +
    简报转述），按 DOI/arXiv/归一标题连通归并成 1 条：保留信息最丰的
    代表（有路径 > 摘要长 > 关键词多，同分取最早 first_seen，再按
    source_id 定序），代表缺失的 title/summary/path/keywords 从被并记录
    补齐。零 LLM、幂等；重复调用第二次返回 0。

    v7.3.25（决定 7）：标题相同但 arXiv 编号不同的组不自动合并——仅当
    差异可归因为「年份前缀笔误」（编号相同、年份不同，如 2508.16422 与
    2608.16422）时才并，且给代表记录打 `needs_review=True` +
    `merged_source_ids` 便于回溯；编号本身不同（非书写/年份差异）的组
    保持不动，留人工判断。

    Returns:
        被移除的冗余记录数。
    """
    if not orphan_dedup_enabled():
        return 0
    orphans = registry.get("orphans") or []
    if len(orphans) < 2:
        return 0
    groups = _paper_identity_groups(orphans)
    drop: set = set()
    for g in groups:
        if len(g) < 2:
            continue
        ids = [_paper_arxiv_ids(orphans[i]) for i in g]
        id_set = {f"{y}.{n}" for xs in ids for (y, n) in xs}
        numbers = {n for xs in ids for (_y, n) in xs}
        doils = [set(d) for d in (_paper_dois(orphans[i]) for i in g) if d]
        common_doi = any(a & b for k, a in enumerate(doils) for b in doils[k + 1:])
        confirmed = any(pair <= id_set for pair in CONFIRMED_SAME_PAPER_ARXIV)
        if len(numbers) > 1 and not common_doi and not confirmed:
            # 编号本身不同且无共同 DOI：不是年份/书写形态差异 → 不自动合并（决定 7）
            continue
        years = {y for xs in ids for (y, _n) in xs}
        rep = g[0]
        if confirmed:
            # 人工确认同篇多版本：代表固定为较新版本（arXiv 年月最大者）
            rep = max(g, key=lambda i: max(_paper_arxiv_ids(orphans[i]) or [("0000", "00000")]))
        else:
            for i in g[1:]:
                if _orphan_richness(orphans[i]) > _orphan_richness(orphans[rep]):
                    rep = i
                elif _orphan_richness(orphans[i]) == _orphan_richness(orphans[rep]):
                    fi, fr = str(orphans[i].get("first_seen", "")), str(orphans[rep].get("first_seen", ""))
                    if fi and (not fr or fi < fr):
                        rep = i
                    elif fi == fr and str(orphans[i].get("source_id", "")) < str(orphans[rep].get("source_id", "")):
                        rep = i
        target = orphans[rep]
        for i in g:
            if i == rep:
                continue
            other = orphans[i]
            for k in ("title", "summary", "path", "keywords"):
                if not target.get(k) and other.get(k):
                    target[k] = other[k]
            drop.add(i)
        if len(years) > 1 or confirmed:
            # 年份前缀笔误 / 人工确认多版本合并：打回溯标记，原始 source_id 一并留存
            target["needs_review"] = True
            target["merged_source_ids"] = sorted(
                str(orphans[i].get("source_id", "")) for i in g if i != rep
            )
    if not drop:
        return 0
    registry["orphans"] = [o for i, o in enumerate(orphans) if i not in drop]
    return len(drop)


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def orphan_age_days(item: Dict[str, Any], now: Optional[datetime] = None) -> int:
    """孤儿存活天数（first_seen 缺失/异常返回 0，按最年轻处理）。"""
    t = _parse_iso(item.get("first_seen", ""))
    if not t:
        return 0
    ref = now or datetime.now(timezone.utc)
    return max(0, (ref - t).days)


def orphan_weight(item: Dict[str, Any], now: Optional[datetime] = None) -> float:
    """老化降权系数（决定 8 第一段）：>60 天起线性递减，下限 0.85。

    只降低相似度乘子、不排除记录——高龄孤儿仍可凭强相似加入新簇。
    """
    if not orphan_aging_enabled():
        return 1.0
    age = orphan_age_days(item, now)
    if age <= ORPHAN_SOFT_AGE_DAYS:
        return 1.0
    if age >= ORPHAN_ARCHIVE_AGE_DAYS:
        return ORPHAN_WEIGHT_FLOOR
    span = ORPHAN_ARCHIVE_AGE_DAYS - ORPHAN_SOFT_AGE_DAYS
    drop = (1.0 - ORPHAN_WEIGHT_FLOOR) * (age - ORPHAN_SOFT_AGE_DAYS) / span
    return 1.0 - drop


def stamp_orphan_ages(registry: Dict[str, Any], now: Optional[datetime] = None) -> int:
    """回写每个孤儿的 `orphan_age_days`（决定 8 第一段的可观测字段）。

    Returns:
        存活超过降权线（60 天）的记录数。
    """
    if not orphan_aging_enabled():
        return 0
    ref = now or datetime.now(timezone.utc)
    aged = 0
    for o in registry.get("orphans") or []:
        age = orphan_age_days(o, ref)
        o["orphan_age_days"] = age
        if age > ORPHAN_SOFT_AGE_DAYS:
            aged += 1
    return aged


def archive_aged_orphans(registry: Dict[str, Any], now: Optional[datetime] = None) -> int:
    """存活 >180 天的孤儿移出聚团池、归档到补充池（决定 8 第二段）。

    归档不删除：记录整体移入 `registry["supplementary_pool"]`，追加
    `archived_at` / `archive_reason`，仍可由 `search_supplementary_pool()`
    按需检索。归档段不再参与每周全池聚团与 42 天清理。

    Returns:
        本次归档条数。
    """
    if not orphan_aging_enabled():
        return 0
    ref = now or datetime.now(timezone.utc)
    keep: List[Dict[str, Any]] = []
    archived: List[Dict[str, Any]] = []
    for o in registry.get("orphans") or []:
        if orphan_age_days(o, ref) > ORPHAN_ARCHIVE_AGE_DAYS:
            o["archived_at"] = ref.strftime("%Y-%m-%dT%H:%M:%SZ")
            o["archive_reason"] = f"age>{ORPHAN_ARCHIVE_AGE_DAYS}d"
            archived.append(o)
        else:
            keep.append(o)
    if not archived:
        return 0
    registry["orphans"] = keep
    pool = registry.setdefault("supplementary_pool", [])
    pool.extend(archived)
    return len(archived)


def search_supplementary_pool(registry: Dict[str, Any], query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """归档补充池按需检索（决定 8 第二段：归档后仍可用）。

    零 LLM：查询词元与条目标题/关键词/摘要的重合度排序，返回前 limit 条。
    """
    q = _tokenize(query or "")
    if not q:
        return []
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for item in registry.get("supplementary_pool") or []:
        text = " ".join([
            str(item.get("title", "") or ""),
            " ".join(item.get("keywords") or []),
            str(item.get("summary", "") or "")[:SUMMARY_TEXT_LIMIT],
        ])
        hit = len(q & _tokenize(text))
        if hit:
            scored.append((hit / len(q), item))
    scored.sort(key=lambda x: -x[0])
    return [it for _s, it in scored[:limit]]


def core_theme_members(cluster: Dict[str, Any]) -> List[Dict[str, Any]]:
    """立题取料：仅保留命中核心范式（强场操控 / HHG 超快测量）的成员。

    v7.3.22（用户裁决 1）：跨领域簇保留不删（不合并、不删簇），但金融/
    保险/量子计算算法/通用 ML 等跨领域成员不得进入设想证据链。核心范式
    探测不可用或单条异常时 fail-open（保留该成员），避免链路因探测故障
    整体丢料。
    """
    try:
        from .sources import core_theme_hit
    except Exception:
        return list(cluster.get("member_summaries") or [])
    kept: List[Dict[str, Any]] = []
    for m in cluster.get("member_summaries") or []:
        text = " ".join([
            str(m.get("title", "") or ""),
            " ".join(m.get("keywords") or []),
            str(m.get("summary", "") or "")[:SUMMARY_TEXT_LIMIT],
        ])
        try:
            hit = core_theme_hit(text) is not None
        except Exception:
            hit = True
        if hit:
            kept.append(m)
    return kept


def idea_evidence_members(cluster: Dict[str, Any]) -> List[Dict[str, Any]]:
    """立题证据链成员：cross_domain 簇按核心范式过滤，正常簇原样返回。"""
    members = list(cluster.get("member_summaries") or [])
    if not cluster.get("cross_domain"):
        return members
    return core_theme_members(cluster)


def evidence_paper_count(cluster: Dict[str, Any]) -> int:
    """立题证据链的唯一论文数（cross_domain 簇为过滤后口径）。"""
    return len(_unique_papers(idea_evidence_members(cluster)))


def _direction_ratio(group: List[Dict[str, Any]]) -> float:
    """团内命中核心范式（强场操控 / HHG 超快测量）的唯一论文比例。

    只用于 cross_domain 标记（决定 3）：跨领域大簇保留不删，交
    topic_match 的 LLM 仲裁判定。sources 不可用或探测失败返回 -1.0
    （调用方据此不打标记，fail-open）。
    """
    try:
        from .sources import core_theme_hit
    except Exception:
        return -1.0
    seen: set = set()
    hits = 0
    total = 0
    try:
        for g in group:
            k = paper_key(g)
            if k in seen:
                continue
            seen.add(k)
            text = " ".join([
                str(g.get("title", "") or ""),
                " ".join(g.get("keywords") or []),
                str(g.get("summary", "") or "")[:300],
            ])
            total += 1
            if core_theme_hit(text) is not None:
                hits += 1
    except Exception:
        return -1.0
    return (hits / total) if total else -1.0


def _split_similarity(fa: Tuple[set, set], fb: Tuple[set, set]) -> float:
    """拆分类的强相似度：标题为主（0.7）+ 关键词（0.3），泛词抑制。

    与归簇通道口径独立（拆分只在超大类内部使用，不再依赖 SIM 通道
    开关）；分母同样取原始集合，防泛词抑制把分母剔小后虚高。
    """
    kw_a, kw_b = fa[0] - _SimGenericKeywords, fb[0] - _SimGenericKeywords
    ti_a, ti_b = fa[1] - _SimGenericTitle, fb[1] - _SimGenericTitle
    return (
        SPLIT_TITLE_WEIGHT * _jaccard_specific(ti_a, ti_b, fa[1], fb[1])
        + (1.0 - SPLIT_TITLE_WEIGHT) * _overlap_specific(kw_a, kw_b, fa[0], fb[0])
    )


def _split_large_group(group: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """超大连通分量二级拆分（决定 3）。

    触发条件：唯一论文数 > LARGE_CLUSTER_SPLIT_THRESHOLD（20）。用
    "标题为主（0.7）+ 关键词（0.3）"的更强特征在 SPLIT_SIM_THRESHOLD
    （0.30）重算子连通分量；唯一论文 <3 的碎片并回平均相似最高的
    大片（避免孤儿回灌）。若拆完只剩 1 片（强特征也没能分开），原样
    返回 [group]，不做无意义拆分。
    """
    if len(group) < MIN_CLUSTER_MEMBERS + 1:
        return [group]
    if len(_unique_papers(group)) <= LARGE_CLUSTER_SPLIT_THRESHOLD:
        return [group]

    feats = [
        (_kw_tokens_v2(g.get("keywords")), _tokens_v2(g.get("title", "")))
        for g in group
    ]
    n = len(group)
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def _union(a: int, b: int) -> None:
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if _split_similarity(feats[i], feats[j]) >= SPLIT_SIM_THRESHOLD:
                _union(i, j)

    comps: Dict[int, List[int]] = {}
    for i in range(n):
        comps.setdefault(_find(i), []).append(i)
    parts_idx = list(comps.values())

    def _part_papers(idx: List[int]) -> List[str]:
        return _unique_papers([group[i] for i in idx])

    big = [p for p in parts_idx if len(_part_papers(p)) >= MIN_CLUSTER_MEMBERS]
    small = [p for p in parts_idx if len(_part_papers(p)) < MIN_CLUSTER_MEMBERS]
    if len(big) <= 1:
        # 拆不出第二个合格片：要么本就一体，要么全部碎片（原样返回）
        return [group]

    for sp in small:
        best, best_sim = None, -1.0
        for bp in big:
            vals = [_split_similarity(feats[i], feats[j]) for i in sp for j in bp]
            sim = (sum(vals) / len(vals)) if vals else 0.0
            if sim > best_sim:
                best, best_sim = bp, sim
        if best is not None:
            best.extend(sp)

    return [[group[i] for i in sorted(p)] for p in big]


def form_new_clusters(
    registry: Dict[str, Any],
    threshold: float = FORM_CLUSTER_SIM_THRESHOLD,
    min_members: int = MIN_CLUSTER_MEMBERS,
) -> List[Dict[str, Any]]:
    """从 orphans 中聚团成新簇（领袖优先 + 组内生长）。

    v6.10.29: 原"首种子贪心"对弥散簇失配——团内成员两两相似但首条
    orphan 只与部分成员相似时，首种子吸不满 3 篇就退场，链式簇
    （A~B~C 而 A≁C）永远聚不起来（实测 567 孤儿仅聚 2 簇，386 条
    强场相关散料滞留 42 天清理线前）。改进：
    ① 领袖优先：每轮取度数（与其余 orphan 相似 ≥threshold 的数量）
       最高者当种子，顺序无关；② 组内生长：吸收与组内**任一**成员
       相似 ≥threshold 的 orphan 直至收敛，链式簇也能成团；
    ③ 规模防护：孤儿池 > MAX_LEADER_SEARCH 时退回首种子模式防失控。
    其余规则不变：团规模 ≥min_members 才开新簇；新簇需与全部已有
    簇（含 linked/closed）查重，过近不开（防换皮重开，成员退回）。
    v6.9.18: 簇标题用团内高频关键词拼接；簇 ID uuid 防碰撞。
    """
    orphans: List[Dict[str, Any]] = registry.get("orphans", [])
    all_clusters = registry.get("clusters", [])
    formed: List[Dict[str, Any]] = []
    deferred: List[Dict[str, Any]] = []  # 已当过种子或查重退回的，本轮不再当种子
    existing_ids = {c.get("cluster_id") for c in all_clusters}
    if len(orphans) < min_members:
        registry["orphans"] = list(orphans)
        return formed

    # ── 邻接表一次预计算（v7.2.56）──
    # v7.3.1: 特征（分词结果）逐条预计算一次，避免 O(n²) 内重复归一化
    n = len(orphans)
    channel = sim_channel()
    feats = [_features(o) for o in orphans]
    # v7.3.25（用户裁决 决定 8 第一段）：老化降权——相似度乘 wi*wj，
    # 只降低高龄孤儿的成团优先级、不排除（开关 off 时全为 1.0）。
    weights = [orphan_weight(o) for o in orphans]
    neighbors: List[set] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if (_score_features(feats[i], feats[j], channel) * weights[i] * weights[j]
                    >= threshold):
                neighbors[i].add(j)
                neighbors[j].add(i)

    remaining = set(range(n))  # 仍可当种子/被吸收的下标

    def _degree(i: int) -> int:
        return len(neighbors[i] & remaining)

    while len(remaining) >= min_members:
        # 领袖优先：度数最高者当种子（并列取先出现，确定性）
        best_i, best_d = -1, -1
        for i in sorted(remaining):
            d = _degree(i)
            if d > best_d:
                best_i, best_d = i, d
        if best_d < min_members - 1:
            # 最连通领袖都凑不满 3 篇 → 池内不存在可聚团，收尾
            deferred.extend(orphans[i] for i in remaining)
            remaining = set()
            break
        seed = best_i
        remaining.discard(seed)
        # 组内生长：BFS 吸收与组内任一成员相邻的 orphan 直至收敛
        group_idx = [seed]
        frontier = [seed]
        while frontier:
            nxt = []
            for g in frontier:
                for cand in sorted(neighbors[g] & remaining):
                    remaining.discard(cand)
                    group_idx.append(cand)
                    nxt.append(cand)
            frontier = nxt
        group = [orphans[i] for i in group_idx]

        # v7.3.21（决定 3）：超大类（唯一论文 > 20）先二级拆分成若干候选片，
        # 每片独立过"唯一论文 ≥3 + 换皮查重"两道关。
        parts = _split_large_group(group) if large_split_enabled() else [group]
        dedup_on = paper_dedup_enabled()
        for part in parts:
            if dedup_on:
                puniq = _unique_papers(part)
                pcount = len(puniq) if puniq else len(part)
            else:
                puniq, pcount = [], len(part)
            if pcount < min_members:
                # 唯一论文不足（含"3 条记录 2 篇唯一"）/ 单篇不成簇：
                # 本轮已试过 → deferred（不静默丢失）
                deferred.extend(part)
                continue

            # 与全部已有簇查重（防换皮重开；关键词 overlap 口径与归簇一致）。
            # v6.10.28: 阈值独立为 FORM_CLUSTER_DEDUP_THRESHOLD（0.45）——原与
            # 聚团共用 0.30，部分重叠但研究问题不同的团被误杀（超快光谱孤儿
            # 团与 HHG 簇共享泛词即被挡），阈值提高后仅"主题高度重合"拒开。
            candidate_title = "、".join(_top_group_keywords(part))
            candidate_kw = kw_set([k for g in part for k in (g.get("keywords") or [])])
            too_close = False
            for c in all_clusters + formed:
                kw_sim = _overlap(candidate_kw, kw_set(c.get("keywords")))
                ti_sim = _jaccard(_tokenize(candidate_title), _tokenize(c.get("title", "")))
                if 0.7 * kw_sim + 0.3 * ti_sim >= FORM_CLUSTER_DEDUP_THRESHOLD:
                    too_close = True
                    break
            if too_close:
                # 团员全部退回 deferred（防止同轮反复聚同一个不合格团）
                deferred.extend(part)
                continue

            # 跨领域簇只打标记、不删簇——交 topic_match 的 LLM 仲裁判定
            ratio = _direction_ratio(part)
            cross_domain = bool(ratio >= 0 and pcount >= CROSS_DOMAIN_MIN_PAPERS
                                and ratio < CROSS_DOMAIN_DIRECTION_RATIO)
            cluster = {
                "cluster_id": _new_cluster_id(existing_ids),
                "title": candidate_title,
                "keywords": sorted(candidate_kw)[:12],
                "summary": "",  # 待 cluster_distill 提炼
                "member_source_ids": [g.get("source_id", "") for g in part],
                "member_summaries": [
                    {
                        "source_id": g.get("source_id", ""),
                        "title": g.get("title", ""),
                        "summary": g.get("summary", ""),
                        "keywords": g.get("keywords", []) or [],
                        "path": g.get("path", ""),
                    }
                    for g in part
                ],
                "unique_paper_count": pcount,
                "paper_keys": puniq,
                "duplicate_record_count": (len(part) - len(puniq)) if puniq else 0,
                "cross_domain": cross_domain,
                "direction_hit_ratio": round(ratio, 3) if ratio >= 0 else None,
                # v7.3.62: 新簇持久标记"从未尝试提炼"，不受 7 天新鲜度窗口限制
                "pending_first_distill": True,
                "status": CLUSTER_OPEN,
                "linked_proposal_id": None,
                "created_at": now_utc(),
                "updated_at": now_utc(),
            }
            existing_ids.add(cluster["cluster_id"])
            all_clusters.append(cluster)
            formed.append(cluster)

    # orphans 收敛为：剩余可聚项 + 本轮已试过种子的散料
    registry["orphans"] = [orphans[i] for i in sorted(remaining)] + deferred
    return formed


# ---------------------------------------------------------------------------
# 生命周期维护
# ---------------------------------------------------------------------------


def prune_orphans(
    registry: Dict[str, Any],
    max_age_days: int = ORPHAN_MAX_AGE_DAYS,
    keep_fn=None,
) -> int:
    """丢弃超龄 orphan（一直凑不成簇的散料，避免无限堆积）。

    v6.10.29: 强场相关孤儿豁免——keep_fn(o) 为真的超龄 orphan 保留
    并标记 theme_protected。背景：孤儿池 348 条处于 28-42 天濒临清理
    窗口，其中 267 条命中强场/超快核心范式（HHG 光源、阿秒计量、
    Berry 相光学）——纯聚类失配的散料不是垃圾，是未来成簇/课题的
    候选素材（form_new_clusters 与 recycle_orphans 每周末对整个池
    重跑，超龄保留不阻断继续参与聚类）。仅核心范式豁免，其余超龄
    照常清理（防无限堆积的初衷不变）。
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    before = len(registry.get("orphans", []))
    kept: List[Dict[str, Any]] = []
    for o in registry.get("orphans", []):
        if o.get("first_seen", "") >= cutoff:
            kept.append(o)
            continue
        if keep_fn is not None and keep_fn(o):
            o["theme_protected"] = True
            kept.append(o)
    registry["orphans"] = kept
    return before - len(kept)


def recycle_orphans(registry: Dict[str, Any], threshold: float = ASSIGN_SIM_THRESHOLD) -> int:
    """孤儿回收（v6.10.29）：聚团后剩余孤儿与可吸收簇二次匹配。

    背景：旧孤儿从未参与增量归簇——assign_summaries 只处理当轮摘要，
    form_new_clusters 只在孤儿互相之间配对，跨轮孤儿与已有簇（含本轮
    新簇）之间没有匹配通道。09-19 实测 R27 十条新料归簇失败全落
    orphans、orphans 膨胀至 567 且 320 条逼近 42 天清理线，其中 386 条
    命中强场/超快核心范式（HHG 光源、阿秒计量、Berry 相光学）——纯
    聚类算法失配导致的散料，不是知识本身无价值。

    本 pass 在 form_new_clusters 之后执行：新簇已入注册表，剩余孤儿
    与可吸收簇（v6.10.38 扩展为 open + linked，与 assign_summaries
    同口径）按 ASSIGN_SIM_THRESHOLD（0.22）取最高分回收，零 LLM、
    确定性。被回收孤儿从池中移除（免于本轮 42 天清理），吸收沿用
    _absorb_member（成员/关键词/时间戳同步），簇的提炼闭环会随蒸馏
    轮补知识卡。

    Args:
        registry: 簇注册表（form_new_clusters 已更新 orphans 与 clusters）
        threshold: 回收相似度门槛（默认与归簇一致 0.22）

    Returns:
        回收的孤儿数量
    """
    candidates = absorbable_clusters(registry)
    if not candidates:
        return 0
    remaining: List[Dict[str, Any]] = registry.get("orphans", [])
    kept: List[Dict[str, Any]] = []
    recycled = 0
    for o in remaining:
        best_c, best_s = None, 0.0
        for c in candidates:
            s = summary_similarity(o, c)
            if s > best_s:
                best_s, best_c = s, c
        if best_c is not None and best_s >= threshold:
            _absorb_member(best_c, o)
            recycled += 1
        else:
            kept.append(o)
    registry["orphans"] = kept
    return recycled


def close_stale_clusters(registry: Dict[str, Any], stale_weeks: int = CLUSTER_STALE_WEEKS) -> Dict[str, Any]:
    """open 簇 N 周无新成员且未链接课题 → closed（不再吸收，防僵尸簇）。

    v6.10.7 保护分支：route_signal == accumulate 的超期簇不自动关闭——
    这类簇被 topic_match 判为"高相关但成员 <3 继续积累"（差 1 篇过
    new 门槛），自动 closed 会把跨周积累作废（实测 09-12：4 个高相关
    簇卡 2/3 成员 26 天，距 4 周 stale 线仅 2 天）。改为标记
    pending_human_review 进人工队列裁决（补检索凑第 3 篇 / 手工关闭），
    簇保持 open 可继续吸收新成员。

    Returns:
        {"closed": 关闭数, "protected": 保护数, "protected_ids": [...]}
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(weeks=stale_weeks)).strftime("%Y-%m-%dT%H:%M:%SZ")
    closed = 0
    protected: List[str] = []
    for c in registry.get("clusters", []):
        if c.get("status") != CLUSTER_OPEN or c.get("updated_at", "") >= cutoff:
            continue
        if c.get("route_signal") == ROUTE_SIGNAL_ACCUMULATE:
            # 高相关待积累：保护 + 人工裁决标记（幂等：已有标记不重复记时）
            if not c.get("pending_human_review"):
                c["pending_human_review"] = True
                c["stale_notified_at"] = now_utc()
            protected.append(c.get("cluster_id", ""))
            continue
        c["status"] = CLUSTER_CLOSED
        closed += 1
    return {"closed": closed, "protected": len(protected), "protected_ids": protected}


def mark_linked(registry: Dict[str, Any], cluster_id: str, proposal_id: str) -> bool:
    """簇路由到课题后标记 linked。"""
    for c in registry.get("clusters", []):
        if c.get("cluster_id") == cluster_id:
            c["status"] = CLUSTER_LINKED
            c["linked_proposal_id"] = proposal_id
            c["updated_at"] = now_utc()
            return True
    return False


def open_clusters_with_fresh_members(registry: Dict[str, Any], week_start_iso: str) -> List[Dict[str, Any]]:
    """列出本周有新成员的 open 簇（cluster_distill 的处理对象）。"""
    return [
        c for c in registry.get("clusters", [])
        if c.get("status") == CLUSTER_OPEN and c.get("updated_at", "") >= week_start_iso
    ]


def mark_pending_first_distill(registry: Dict[str, Any]) -> int:
    """给"从未尝试提炼且仍 open"的簇打 pending_first_distill 持久标记。

    v7.3.62（用户裁决 修 1）：CLUSTER_DISTILL_ROUND_CAP=3 + 每周末只跑一次
    + 队列只认 updated_at ≥ now-7d，导致排在第 4 位以后的新簇既没提炼到、
    也没 pending_redistill（从未尝试过），下一周直接掉出 7 天窗口永久饥饿。
    本标记与 pending_redistill 同机制、语义为"从未尝试"：不受新鲜度窗口
    限制，且排位优先于重提炼，避免老簇反复挤占。只对 open 且无
    distilled_at/distilled_by/pending_redistill 的簇打标。
    """
    marked = 0
    for c in registry.get("clusters", []):
        if c.get("status") != CLUSTER_OPEN:
            continue
        if c.get("pending_first_distill") or c.get("pending_redistill"):
            continue
        if c.get("distilled_at") or c.get("distilled_by"):
            continue
        c["pending_first_distill"] = True
        marked += 1
    return marked


def open_clusters_needing_distill(registry: Dict[str, Any], week_start_iso: str) -> List[Dict[str, Any]]:
    """待提炼 open 簇：从未尝试（pending_first_distill）> 重试（pending_redistill）
    > 本周有新成员（fresh）。

    v6.10.28: 提炼闭环——原 fallback 降级（distilled_by != llm）后知识卡
    永久定格，new 门槛（要求 LLM 知识卡）永不通过，簇只能等新成员
    才再进提炼队列。pending_redistill 标记让"LLM 提炼失败/质量不合格"
    的簇不受周窗口限制、下轮自动重试，直至提炼成功或簇被路由/关闭。

    v7.3.62: 新增 pending_first_distill 通道并对队列排序——从未尝试的簇
    优先于重试簇，后者优先于本周新成员簇；同组内保持注册表顺序。
    """
    fresh = {c.get("cluster_id") for c in open_clusters_with_fresh_members(registry, week_start_iso)}
    first, retry, rest = [], [], []
    for c in registry.get("clusters", []):
        if c.get("status") != CLUSTER_OPEN:
            continue
        if c.get("pending_first_distill"):
            first.append(c)
        elif c.get("pending_redistill"):
            retry.append(c)
        elif c.get("cluster_id") in fresh:
            rest.append(c)
    return first + retry + rest
