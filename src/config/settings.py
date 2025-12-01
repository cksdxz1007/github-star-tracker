"""应用配置管理"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Settings:
    """应用配置管理类"""
    github_token: str
    github_username: str
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    llm_model_name: str = "gpt-3.5-turbo"
    request_delay: float = 0.2

    def __post_init__(self):
        """验证配置完整性"""
        if not all([self.github_token, self.github_username, self.openai_api_key]):
            raise ValueError("❌ 请在 .env 文件中配置所有必要的环境变量。")

    @classmethod
    def from_env(cls) -> 'Settings':
        """从环境变量创建配置"""
        load_dotenv()
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            github_username=os.getenv("GITHUB_USERNAME"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            llm_model_name=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
        )

    @property
    def github_headers(self) -> dict:
        """GitHub API请求头"""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
