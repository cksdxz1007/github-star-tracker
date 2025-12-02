#!/usr/bin/env python3
"""GitHub Star Tracker - 主入口 (模块化版本)"""

import sys
import os
from pathlib import Path
import time

# 添加 src 到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import Settings
from fetchers.starred_repos import StarredRepoFetcher
from fetchers.readme_extractor import ReadmeExtractor
from fetchers.repo_stats import RepoStatsFetcher
from processors.data_processor import DataProcessor
from analyzers.ai_analyzer import AIAnalyzer
from output.csv_exporter import CSVExporter
from output.markdown_exporter import MarkdownExporter
from datetime import datetime


def main():
    """主程序"""
    try:
        # 1. 加载配置
        print("🚀 正在加载配置...")
        settings = Settings.from_env()
        print("   ✓ 配置加载完成")

        # 2. 创建组件
        print("\n🚀 初始化组件...")
        repo_fetcher = StarredRepoFetcher(settings)
        readme_extractor = ReadmeExtractor(settings)
        stats_fetcher = RepoStatsFetcher(settings)
        data_processor = DataProcessor(settings)
        ai_analyzer = AIAnalyzer(settings)
        csv_exporter = CSVExporter()
        markdown_exporter = MarkdownExporter()

        # 3. 执行数据流
        print("\n" + "="*50)
        print("🚀 GitHub Star Tracker 开始运行")
        print("="*50)

        # 3.1 获取数据
        print("\n📡 [步骤 1/4] 正在获取 GitHub Starred 仓库列表...")
        start_time = time.time()
        repos = repo_fetcher.fetch()
        if not repos:
            print("❌ 未获取到任何仓库，程序退出")
            return

        # 3.2 处理数据
        print(f"\n⚙️ [步骤 2/4] 正在深入分析 {len(repos)} 个仓库...")
        print("   - 收集仓库基本信息（描述、链接、星标数）")
        print("   - 计算沉寂天数和活动状态")
        print("   - 获取近期活跃仓库的提交数据")

        processed_data = data_processor.process_repositories(
            repos, readme_extractor, stats_fetcher
        )

        elapsed_total = time.time() - start_time
        print(f"   ✓ 仓库分析完成! 总用时 {elapsed_total:.1f}s")

        # 3.3 导出CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"\n💾 [步骤 3/4] 正在保存原始数据到 CSV 文件...")
        csv_filename = csv_exporter.export(processed_data, timestamp)

        # 3.4 生成分析报告
        print(f"\n🧠 [步骤 4/4] 正在通过 LLM 生成智能分析报告...")
        print("   - 分析活跃项目 (近6个月内更新)")
        print("   - 分析沉寂项目 (6个月-1年未更新)")
        print("   - 分析长期沉寂项目 (超过1年未更新)")
        print("   - 生成健康度评分、风险评估和行动计划")

        import pandas as pd
        df = pd.DataFrame(processed_data)
        report = ai_analyzer.analyze(df)
        md_filename = markdown_exporter.export(report, timestamp)

        print(f"   ✓ AI 分析报告已生成: {md_filename}")
        print("\n" + "="*50)
        print("📊 分析报告内容:")
        print("="*50)
        print(report)
        print("\n" + "="*50)
        print("✅ 所有任务完成!")
        print("="*50)
        print(f"\n📁 输出文件位置:")
        print(f"   📊 CSV文件: csv_output/")
        print(f"   📝 报告文件: reports/")
        print("="*50)

    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
