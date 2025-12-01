"""获取仓库统计数据"""
import requests
from config.settings import Settings


class RepoStatsFetcher:
    """获取仓库统计数据"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    def _request(self, url: str) -> requests.Response:
        """发起HTTP请求"""
        response = self.session.get(url, headers=self.settings.github_headers)
        response.raise_for_status()
        return response

    def fetch_commit_activity(self, repo_full_name: str) -> int:
        """获取过去一年的提交统计"""
        url = f"https://api.github.com/repos/{repo_full_name}/stats/participation"
        try:
            response = self._request(url)
            if response.status_code == 200:
                data = response.json()
                if 'all' in data:
                    return sum(data['all'])
        except:
            pass
        return 0

    def fetch_latest_commit(self, repo_full_name: str, branch: str = "main") -> str:
        """获取最新提交信息"""
        url = f"https://api.github.com/repos/{repo_full_name}/commits/{branch}"
        try:
            response = self._request(url)
            if response.status_code == 200:
                msg = response.json()['commit']['message']
                return msg.split('\n')[0][:100]
        except:
            pass
        return "无法获取"
