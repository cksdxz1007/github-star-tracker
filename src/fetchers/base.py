"""数据获取器基类"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Type
import time
import requests
from config.settings import Settings

T = TypeVar('T')


class BaseFetcher(ABC, Generic[T]):
    """数据获取器基类"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    @abstractmethod
    def fetch(self, *args, **kwargs) -> List[T]:
        """获取数据"""
        pass

    def _request(self, url: str, **kwargs) -> requests.Response:
        """发起HTTP请求"""
        response = self.session.get(url, headers=self.settings.github_headers, **kwargs)
        response.raise_for_status()
        return response

    def _request_with_retry(self, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
        """带重试的HTTP请求"""
        for attempt in range(max_retries):
            try:
                return self._request(url, **kwargs)
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"   ⚠️ 请求失败，{self.settings.request_delay}s后重试... (第{attempt+1}次)")
                time.sleep(self.settings.request_delay)
                continue
