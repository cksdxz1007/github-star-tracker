"""Repository 数据模型"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import time


@dataclass
class Repository:
    """仓库数据模型"""
    full_name: str
    description: Optional[str]
    html_url: str
    language: Optional[str]
    stargazers_count: int
    pushed_at: Optional[str]
    default_branch: str = "main"

    @classmethod
    def from_github_api(cls, data: Dict[str, Any]) -> 'Repository':
        """从GitHub API响应创建实例"""
        return cls(
            full_name=data['full_name'],
            description=data.get('description'),
            html_url=data['html_url'],
            language=data.get('language'),
            stargazers_count=data['stargazers_count'],
            pushed_at=data.get('pushed_at'),
            default_branch=data.get('default_branch', 'main'),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "仓库名": self.full_name,
            "项目描述": self.description or "无描述",
            "仓库链接": self.html_url,
            "编程语言": self.language or "Unknown",
            "Star数": self.stargazers_count,
            "最近更新日期": self._format_date(self.pushed_at) if self.pushed_at else "N/A",
            "沉寂天数": self._calculate_inactive_days(),
        }

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return "N/A"
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")

    def _calculate_inactive_days(self) -> int:
        """计算沉寂天数"""
        if not self.pushed_at:
            return -1

        dt = datetime.strptime(self.pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - dt).days
