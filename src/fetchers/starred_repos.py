"""获取用户starred仓库列表"""
from typing import List
from fetchers.base import BaseFetcher
from models.repository import Repository
from config.settings import Settings
import time


class StarredRepoFetcher(BaseFetcher[Repository]):
    """获取用户starred仓库"""

    def __init__(self, settings: Settings):
        super().__init__(settings)

    def fetch(self) -> List[Repository]:
        """获取所有starred仓库"""
        repos = []
        page = 1
        print(f"📡 开始获取用户 {self.settings.github_username} 的 Star 列表...")

        while True:
            url = f"https://api.github.com/users/{self.settings.github_username}/starred?per_page=100&page={page}"
            try:
                response = self._request(url)
                data = response.json()

                if not data:
                    break

                for repo_data in data:
                    repos.append(Repository.from_github_api(repo_data))

                print(f"   已加载第 {page} 页，累计 {len(repos)} 个...")
                page += 1
                time.sleep(self.settings.request_delay)

            except Exception as e:
                print(f"❌ API 请求失败: {e}")
                break

        return repos
