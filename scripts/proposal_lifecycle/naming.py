from __future__ import annotations

from typing import Any, Dict, Optional

from proposal_lifecycle.constants import PROJECT_TYPES, _log


class NamingMixin:
    # ------------------------------------------------------------------
    # 课题命名规则（v6.5.4）
    # ------------------------------------------------------------------

    # 命名规则：{项目类型}-{课题名称}-{启动日期}
    # 课题名称取自课题的具体科学问题或核心方法（而非大的研究领域）
    # 示例：general-quantum-geometry-inversion-20260726
    #       key-bsv-driven-hhg-20260726
    #       major-topological-photoresponse-mapping-20260726
    # 项目类型简称：general(面上) / key(重点) / major(重大)
    _NAMING_PATTERN = None  # 编译时初始化

    # 项目类型 → 简称映射
    PROJECT_TYPE_SHORT = {
        "general": "general",
        "key": "key",
        "major": "major",
    }

    @classmethod
    def _get_naming_pattern(cls):
        if cls._NAMING_PATTERN is None:
            import re
            # general-quantum-geometry-inversion-20260726
            # 项目类型-课题名称(基于科学问题/核心方法)-日期(YYYYMMDD)[-序号]
            cls._NAMING_PATTERN = re.compile(
                r"^(general|key|major)-([a-z][a-z0-9-]{1,40})-(\d{4})(\d{2})(\d{2})(?:-(\d{2}))?$"
            )
        return cls._NAMING_PATTERN

    def validate_proposal_id(self, proposal_id: str) -> Dict[str, Any]:
        """校验课题 ID 是否符合命名规则。

        规则：{项目类型}-{课题名称}-{启动日期}[-序号]
        - 项目类型：general(面上) / key(重点) / major(重大)
        - 课题名称：取自课题的具体科学问题或核心方法（非研究领域），
                    2-40位小写字母/数字/连字符
        - 启动日期：YYYYMMDD 格式
        - 序号：可选，同一天同名的第二个起加序号

        命名要点：
          ✓ quantum-geometry-inversion（量子几何反演——具体方法）
          ✓ bsv-driven-hhg（BSV驱动的高次谐波——具体问题）
          ✗ hhg（太泛，是研究领域不是课题内容）
          ✗ optics（太泛）

        Returns:
            {valid, reason, parsed: {project_type, name, date, seq}}
        """
        pattern = self._get_naming_pattern()
        match = pattern.match(proposal_id)
        if not match:
            return {
                "valid": False,
                "reason": (
                    f"命名不符合规则。正确格式：{{项目类型}}-{{课题名称}}-{{YYYYMMDD}}\n"
                    f"项目类型：general(面上) / key(重点) / major(重大)\n"
                    f"课题名称：取自具体科学问题/核心方法，非研究领域\n"
                    f"示例：general-quantum-geometry-inversion-20260726\n"
                    f"收到：{proposal_id}"
                ),
                "parsed": None,
            }
        return {
            "valid": True,
            "reason": "命名合规",
            "parsed": {
                "project_type": match.group(1),
                "name": match.group(2),
                "date": f"{match.group(3)}-{match.group(4)}-{match.group(5)}",
                "date_raw": match.group(3) + match.group(4) + match.group(5),
                "seq": match.group(6),
            },
        }

    def generate_proposal_id(
        self,
        name: str,
        project_type: str = "general",
        date_str: Optional[str] = None,
    ) -> str:
        """自动生成课题 ID。

        Args:
            name: 课题名称缩写（如 hhg, bsv, quantum-geometry）
            project_type: 项目类型（general/key/major）
            date_str: 启动日期 YYYYMMDD（默认今天）

        Returns:
            符合命名规则的课题 ID
        """
        if date_str is None:
            import datetime
            date_str = datetime.datetime.now().strftime("%Y%m%d")

        name = name.lower().strip()
        type_short = self.PROJECT_TYPE_SHORT.get(project_type, "general")
        base = f"{type_short}-{name}-{date_str}"

        # 如果已存在，加序号后缀（-02, -03...）
        state = self._load_state()
        existing_ids = set(state["proposals"].keys())

        if base not in existing_ids:
            for stage in LIFECYCLE_STAGES:
                if (self.root / stage / base).exists():
                    break
            else:
                return base

        # 同一天同名课题加序号
        for seq in range(2, 100):
            candidate = f"{base}-{seq:02d}"
            if candidate not in existing_ids:
                exists_in_dir = False
                for stage in LIFECYCLE_STAGES:
                    if (self.root / stage / candidate).exists():
                        exists_in_dir = True
                        break
                if not exists_in_dir:
                    return candidate

        return f"{base}-99"
