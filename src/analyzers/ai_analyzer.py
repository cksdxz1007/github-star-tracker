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
        active_recent = len(df[(df['沉寂天数'] >= 0) & (df['沉寂天数'] < 180)])
        inactive_half_yr = len(df[(df['沉寂天数'] >= 180) & (df['沉寂天数'] <= 365)])
        inactive_1yr = len(df[df['沉寂天数'] > 365])

        # 选取近期活跃项目（<180天）Top 5
        top_active = df[df['沉寂天数'] < 180].sort_values("沉寂天数").head(5)
        active_str = "\n".join(
            [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  更新于{row['最近更新日期']}，更新内容: {row['最近更新内容']}"
             for _, row in top_active.iterrows()]
        )

        # 选取沉寂半年到一年的项目 Top 5
        half_yr_projects = df[(df['沉寂天数'] >= 180) & (df['沉寂天数'] <= 365)].sort_values("Star数", ascending=False).head(5)
        half_yr_str = "\n".join(
            [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  已停更{row['沉寂天数']}天 (Star: {row['Star数']})"
             for _, row in half_yr_projects.iterrows()]
        )

        # 选取超过一年的项目 Top 5
        dead_giants = df[df['沉寂天数'] > 365].sort_values("Star数", ascending=False).head(5)
        dead_str = "\n".join(
            [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  已停更{row['沉寂天数']}天 (Star: {row['Star数']})"
             for _, row in dead_giants.iterrows()]
        )

        # 构建分析提示
        template = """
        你是一名技术资产管理专家。请根据用户的 GitHub Star 数据生成一份详细的分析报告。

        【数据概览】
        - 关注项目总数: {total_count}
        - 活跃项目(近6个月内有更新): {active_recent}
        - 沉寂项目(6个月-1年未更新): {inactive_half_yr}
        - 长期沉寂项目(超过1年未更新): {inactive_1yr}

        【近期活跃项目 (近6个月内有更新)】
        {active_str}

        【沉寂项目 (6个月-1年未更新) - 需关注】
        {half_yr_str}

        【长期沉寂项目 (超过1年未更新) - 高风险】
        {dead_str}

        【任务】
        请生成一份 Markdown 格式的详细分析报告，包含以下部分：

        1. 【整体健康度评估】
           - 给出关于用户关注技术栈的整体健康度评分（0-10分）和简短评价
           - 分析活跃项目占比和风险项目占比

        2. 【活跃项目分析】
           - 对每个"近期活跃项目"，根据其编程语言和项目描述，说明这是什么类型的项目
           - 对其更新内容进行技术解读（推测是在修Bug、发新版、功能迭代等）
           - 评估这些项目在你工作流中的潜在价值

        3. 【沉寂项目分析 (6个月-1年未更新)】
           - 分析这些项目为何长时间未更新可能的原因
           - 评估项目是否仍有使用价值
           - 提供具体建议：是否需要寻找替代品、是否可以继续使用、或需要迁移
           - 特别关注高Star数的项目，因为这些可能是你工作流中的重要依赖

        4. 【长期沉寂项目分析 (超过1年未更新) - 高风险评估】
           - 对这些项目给出明确的行动建议
           - 强烈建议寻找替代品或制定迁移计划
           - 说明如果这些项目对你的工作很重要，应该采取什么措施（Fork项目、寻找替代、联系维护者等）
           - 评估安全风险和技术债务

        5. 【行动计划建议】
           - 整理一份优先级清单，按风险从高到低排序
           - 为每个类别提供具体的下一步行动建议

        要求：
        - 保持语气专业、客观
        - 每个建议都要具体可行
        - 在报告中适当提及编程语言信息
        - 重点关注安全和长期维护性问题
        """

        prompt = PromptTemplate.from_template(template)

        # 执行分析
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "total_count": total_count,
            "active_recent": active_recent,
            "inactive_half_yr": inactive_half_yr,
            "inactive_1yr": inactive_1yr,
            "active_str": active_str,
            "half_yr_str": half_yr_str,
            "dead_str": dead_str
        })
