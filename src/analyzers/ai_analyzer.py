"""AI分析模块"""
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import Settings


class AIAnalyzer:
    """AI分析器"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model_name=settings.llm_model_name,
            temperature=0.6,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base
        )

    def analyze(self, df: pd.DataFrame) -> str:
        """分析仓库数据并生成报告"""
        # 构建分析上下文
        total_count = len(df)
        inactive_1yr = len(df[df['沉寂天数'] > 365])
        active_30d = len(df[df['沉寂天数'] < 30])

        # 选取近期最活跃的 Top 5
        top_active = df.sort_values("沉寂天数").head(5)
        active_str = "\n".join(
            [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  更新于{row['最近更新日期']}，更新内容: {row['最近更新内容']}"
             for _, row in top_active.iterrows()]
        )

        # 选取已经"死掉"但还有名气的 Top 5
        dead_giants = df[df['沉寂天数'] > 365].sort_values("Star数", ascending=False).head(5)
        dead_str = "\n".join(
            [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  已停更{row['沉寂天数']}天 (Star: {row['Star数']})"
             for _, row in dead_giants.iterrows()]
        )

        # 构建分析提示
        template = """
        你是一名技术资产管理专家。请根据用户的 GitHub Star 数据生成一份简报。

        【数据概览】
        - 关注项目总数: {total_count}
        - 极度活跃项目(近30天): {active_30d}
        - 疑似废弃项目(超1年): {inactive_1yr}

        【近期活跃焦点】
        {active_str}

        【如果是重依赖，需警惕的长期未更项目】
        {dead_str}

        【任务】
        请生成一份 Markdown 格式的分析报告。
        1. 给出一个关于用户关注技术栈的整体健康度评分（0-10分）和简短评价。
        2. 对"近期活跃焦点"中的每个项目，根据其编程语言和项目描述，说明这是什么类型的项目，然后对其更新内容进行技术解读（推测它是在修Bug还是发新版）。
        3. 对"长期未更项目"给出行动建议（如：建议寻找替代品），并说明如果这些项目对你的工作很重要应该怎么办。
        4. 保持语气专业、客观。每个建议都要具体可行。
        5. 在报告中适当提及编程语言信息，以便更好地理解技术栈分布。
        """

        prompt = PromptTemplate.from_template(template)

        # 执行分析
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "total_count": total_count,
            "active_30d": active_30d,
            "inactive_1yr": inactive_1yr,
            "active_str": active_str,
            "dead_str": dead_str
        })
