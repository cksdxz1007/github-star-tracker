"""数据处理模块"""
from typing import List, Dict, Any
from datetime import datetime, timezone
from models.repository import Repository
from fetchers.repo_stats import RepoStatsFetcher
from fetchers.readme_extractor import ReadmeExtractor
from config.settings import Settings


class DataProcessor:
    """数据处理器"""

    def __init__(self, settings: Settings):
        self.settings = settings

    def process_repositories(
        self,
        repos: List[Repository],
        readme_extractor: ReadmeExtractor,
        stats_fetcher: RepoStatsFetcher
    ) -> List[Dict[str, Any]]:
        """处理仓库数据"""
        processed_data = []
        now = datetime.now(timezone.utc)

        for repo in repos:
            # 计算沉寂天数
            days_inactive = repo._calculate_inactive_days()

            # 获取提交数据（仅限近半年更新的项目）
            commits_last_year = 0
            last_msg = ""

            if days_inactive != -1 and days_inactive < 180:
                commits_last_year = stats_fetcher.fetch_commit_activity(repo.full_name)
                last_msg = stats_fetcher.fetch_latest_commit(repo.full_name, repo.default_branch)

            # 丰富描述信息
            description = repo.description
            if not description or description == "无描述":
                description = readme_extractor.extract(repo.full_name)

            # 构建最终数据
            processed_data.append({
                "仓库名": repo.full_name,
                "编程语言": repo.language or "Unknown",
                "项目描述": description,
                "仓库链接": repo.html_url,
                "Star数": repo.stargazers_count,
                "最近更新日期": repo._format_date(repo.pushed_at),
                "沉寂天数": days_inactive,
                "年提交数": commits_last_year,
                "最近更新内容": last_msg,
                "仓库状态": repo._get_status(),
                "项目年龄": repo._calculate_project_age(),
                "关注者数": repo.watchers_count,
                "订阅者数": repo.subscribers_count,
                "Fork数": repo.forks_count,
                "开放Issues": repo.open_issues_count,
                "项目标签": ", ".join(repo.topics) if repo.topics else "无",
            })

        return processed_data
