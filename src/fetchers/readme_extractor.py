"""README提取和总结"""
import base64
import time
import requests
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import Settings


class ReadmeExtractor:
    """README提取器"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    def extract(self, repo_full_name: str) -> str:
        """提取README内容并总结"""
        url = f"https://api.github.com/repos/{repo_full_name}/readme"

        try:
            response = self.session.get(
                url,
                headers=self.settings.github_headers
            )

            if response.status_code == 200:
                readme_content = base64.b64decode(response.json()['content']).decode('utf-8')

                # 使用LLM总结
                return self._summarize_with_llm(readme_content)

        except Exception as e:
            pass

        return "无描述"

    def _summarize_with_llm(self, readme_content: str) -> str:
        """使用LLM总结README"""
        # 提取前1500个字符作为参考文本
        summary_text = readme_content[:1500]

        # 构建总结提示模板
        summary_prompt_template = """
        请阅读以下GitHub项目的README内容，用1-2句话总结这个项目的主要用途和功能。
        要求：
        1. 语言简洁明了，突出项目核心功能
        2. 字数控制在50字以内
        3. 直接说明项目是什么/做什么，不需要说明如何使用

        README内容：
        {summary_text}

        总结：
        """

        try:
            # 配置简化的LLM用于总结
            summary_llm = ChatOpenAI(
                model_name=self.settings.llm_model_name,
                temperature=0.3,
                openai_api_key=self.settings.openai_api_key,
                openai_api_base=self.settings.openai_api_base
            )

            prompt = PromptTemplate.from_template(summary_prompt_template)
            chain = prompt | summary_llm | StrOutputParser()
            result = chain.invoke({"summary_text": summary_text})

            if result and len(result.strip()) > 5:
                return result.strip()
            return "无描述"

        except Exception as llm_error:
            print(f"   ⚠️ LLM总结失败: {str(llm_error)[:50]}")
            # 如果LLM失败，回退到简单提取
            return self._simple_extract(summary_text)

    def _simple_extract(self, readme_content: str) -> str:
        """简单的README提取（作为LLM的备用方案）"""
        lines = readme_content.split('\n')[:30]
        title_lines = []
        description_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                title_lines.append(line.lstrip('#').strip())
            elif len(line) > 30 and not line.startswith('!['):
                description_lines.append(line)

        result_parts = []

        if title_lines:
            main_title = title_lines[0]
            if len(main_title) < 100:
                result_parts.append(main_title)

        for desc in description_lines[:3]:
            if 20 < len(desc) < 150:
                result_parts.append(desc)
                break

        if result_parts:
            result = ' | '.join(result_parts)
            if len(result) > 200:
                result = result[:200] + "..."
            return result

        return "无描述"
