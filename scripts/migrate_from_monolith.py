#!/usr/bin/env python3
"""
GitHub Star Tracker - 单文件到模块化迁移脚本

此脚本将帮助您从 monolithic main.py 迁移到模块化架构。

使用方法:
    python scripts/migrate_from_monolith.py

注意事项:
- 请确保已备份原始 main.py
- 运行前请检查所有依赖是否已安装
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """创建目录结构"""
    directories = [
        "src",
        "src/config",
        "src/fetchers",
        "src/processors",
        "src/analyzers",
        "src/output",
        "src/utils",
        "src/models",
        "tests",
        "tests/unit",
        "tests/unit/test_fetchers",
        "tests/unit/test_processors",
        "tests/unit/test_analyzers",
        "tests/unit/test_output",
        "tests/integration",
    ]

    print("📁 创建目录结构...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")

    # 创建 __init__.py 文件
    init_dirs = [
        "src",
        "src/config",
        "src/fetchers",
        "src/processors",
        "src/analyzers",
        "src/output",
        "src/utils",
        "src/models",
        "tests",
        "tests/unit",
        "tests/unit/test_fetchers",
        "tests/unit/test_processors",
        "tests/unit/test_analyzers",
        "tests/unit/test_output",
        "tests/integration",
    ]

    print("\n📄 创建 __init__.py 文件...")
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        init_file.touch()
        print(f"  ✓ {init_file}")


def create_sample_files():
    """创建示例文件"""
    print("\n📝 创建示例配置文件...")

    # .env.example
    env_example = """# GitHub 配置
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# LLM 模型配置
OPENAI_API_KEY=your_openai_or_deepseek_api_key
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
"""

    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    print("  ✓ .env.example")

    # src/config/settings.py (示例)
    settings_code = '''"""应用配置管理"""
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
'''

    with open("src/config/settings.py", "w", encoding="utf-8") as f:
        f.write(settings_code)
    print("  ✓ src/config/settings.py")


def create_gitkeep_files():
    """创建 .gitkeep 文件"""
    print("\n🔒 创建 .gitkeep 文件...")

    gitkeep_dirs = [
        "src/fetchers",
        "src/processors",
        "src/analyzers",
        "src/output",
        "src/utils",
        "src/models",
        "tests/unit/test_fetchers",
        "tests/unit/test_processors",
        "tests/unit/test_analyzers",
        "tests/unit/test_output",
        "tests/integration",
    ]

    for directory in gitkeep_dirs:
        gitkeep = Path(directory) / ".gitkeep"
        gitkeep.touch()
        print(f"  ✓ {gitkeep}")


def create_migration_notes():
    """创建迁移说明"""
    notes = """# 迁移注意事项

## 已完成
✅ 目录结构已创建
✅ 基础配置模块已创建
✅ 示例文件已生成

## 需要手动迁移的内容

### 1. 迁移 src/fetchers/ 模块
从原 main.py (35-81行) 迁移以下函数:
- fetch_starred_repos()
- get_commit_activity()
- get_latest_commit_msg()

### 2. 迁移 src/fetchers/readme_extractor.py
从原 main.py (83-168行) 迁移:
- get_readme_summary()
- get_readme_simple()

### 3. 迁移 src/analyzers/ai_analyzer.py
从原 main.py (172-240行) 迁移:
- analyze_with_llm()

### 4. 迁移 src/processors/data_processor.py
从原 main.py (225-285行) 迁移数据处理逻辑

### 5. 迁移 src/output/ 模块
迁移 CSV 和 Markdown 导出功能

## 下一步操作
1. 根据 docs/REFACTORING_PLAN.md 的详细设计，实现各个模块
2. 运行测试确保功能正常
3. 提交代码并删除原 main.py 备份

## 提示
- 每个模块应该有明确的职责
- 添加类型提示和文档字符串
- 编写单元测试
"""

    with open("MIGRATION_NOTES.md", "w", encoding="utf-8") as f:
        f.write(notes)
    print("  ✓ MIGRATION_NOTES.md")


def main():
    """主函数"""
    print("="*60)
    print("  GitHub Star Tracker - 模块化迁移脚本")
    print("="*60)

    # 检查是否在项目根目录
    if not os.path.exists("main.py"):
        print("❌ 错误: 未找到 main.py，请在项目根目录运行此脚本")
        sys.exit(1)

    # 询问是否继续
    response = input("\n此脚本将创建模块化目录结构，是否继续? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ 迁移已取消")
        sys.exit(0)

    # 创建目录结构
    create_directory_structure()

    # 创建示例文件
    create_sample_files()

    # 创建 .gitkeep 文件
    create_gitkeep_files()

    # 创建迁移说明
    create_migration_notes()

    print("\n" + "="*60)
    print("✅ 迁移准备完成!")
    print("="*60)
    print("\n📋 下一步操作:")
    print("1. 查看 MIGRATION_NOTES.md 了解需要迁移的内容")
    print("2. 参考 docs/REFACTORING_PLAN.md 的详细设计")
    print("3. 逐个实现各个模块")
    print("4. 运行测试确保功能正常")
    print("\n💡 提示:")
    print("- 保持模块间低耦合、高内聚")
    print("- 添加充分的单元测试")
    print("- 遵循 PEP 8 编码规范")
    print("="*60)


if __name__ == "__main__":
    main()
