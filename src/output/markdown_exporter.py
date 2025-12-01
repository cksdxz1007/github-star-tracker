"""Markdown导出器"""
import os
from typing import Optional


class MarkdownExporter:
    """Markdown导出器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, report_content: str, timestamp: str) -> str:
        """导出报告到Markdown"""
        filename = f"{self.output_dir}/analysis_report_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        return filename
