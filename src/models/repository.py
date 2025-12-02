"""Repository 数据模型"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
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

    # 高价值指标
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    archived: bool = False
    disabled: bool = False
    watchers_count: int = 0
    subscribers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    has_issues: bool = True
    topics: List[str] = None

    def __post_init__(self):
        """后处理初始化"""
        if self.topics is None:
            self.topics = []

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

            # 高价值指标
            updated_at=data.get('updated_at'),
            created_at=data.get('created_at'),
            archived=data.get('archived', False),
            disabled=data.get('disabled', False),
            watchers_count=data.get('watchers_count', 0),
            subscribers_count=data.get('subscribers_count', 0),
            forks_count=data.get('forks_count', 0),
            open_issues_count=data.get('open_issues_count', 0),
            has_issues=data.get('has_issues', True),
            topics=data.get('topics', []),
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
            "仓库状态": self._get_status(),
            "项目年龄": self._calculate_project_age(),
            "关注者数": self.watchers_count,
            "订阅者数": self.subscribers_count,
            "Fork数": self.forks_count,
            "开放Issues": self.open_issues_count,
            "项目标签": ", ".join(self.topics) if self.topics else "无",
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

    def _get_status(self) -> str:
        """获取仓库状态"""
        if self.disabled:
            return "已禁用 🚫"
        elif self.archived:
            return "已归档 📦"
        elif self.has_issues:
            return "活跃维护中 ✅"
        else:
            return "未知状态 ❓"

    def _calculate_project_age(self) -> str:
        """计算项目年龄"""
        if not self.created_at:
            return "N/A"

        try:
            created = datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_days = (now - created).days

            if age_days < 30:
                return f"{age_days}天"
            elif age_days < 365:
                return f"{age_days // 30}个月"
            else:
                years = age_days // 365
                remaining_months = (age_days % 365) // 30
                if remaining_months > 0:
                    return f"{years}年{remaining_months}个月"
                else:
                    return f"{years}年"
        except:
            return "N/A"
