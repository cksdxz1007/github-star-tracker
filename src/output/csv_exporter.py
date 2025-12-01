"""CSV导出器"""
import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


class CSVExporter:
    """CSV导出器"""

    def __init__(self, output_dir: str = "csv_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, data: List[Dict[str, Any]], timestamp: str) -> str:
        """导出数据到CSV"""
        df = pd.DataFrame(data)

        filename = f"{self.output_dir}/github_stars_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        # 生成语言统计
        self._export_language_summary(df, timestamp)

        return filename

    def _export_language_summary(self, df: pd.DataFrame, timestamp: str):
        """导出语言统计摘要"""
        language_counts = df['编程语言'].value_counts()

        summary_file = f"{self.output_dir}/language_summary_{timestamp}.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"GitHub Stars 项目语言分类摘要\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总项目数: {len(df)}\n\n")
            f.write(f"语言分布:\n")
            for lang, count in language_counts.items():
                f.write(f"  {lang}: {count} 个项目 ({count/len(df)*100:.1f}%)\n")
