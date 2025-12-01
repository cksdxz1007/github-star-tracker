# GitHub Star Tracker

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/📦-Modular%20Architecture-orange.svg)](docs/ARCHITECTURE.md)

*GitHub starred 项目管理与AI分析工具 - 帮你分析和管理GitHub上star的项目，使用AI生成洞察报告*

## ✨ 特性亮点

- 🔍 **智能获取** - 自动获取你的所有GitHub starred项目
- 📊 **数据分析** - 分析项目活跃度、编程语言分布、沉寂天数
- 📝 **README提取** - 无描述项目自动从README提取并总结用途
- 🤖 **AI分析** - 基于LangChain + LLM生成智能分析报告
- 📤 **多格式导出** - CSV数据导出 + Markdown分析报告
- 🏗️ **模块化架构** - 清晰分离关注点，易于维护和扩展

## 🚀 核心功能

- **数据获取** - 通过GitHub API获取starred仓库列表
- **数据处理** - 清理、转换、丰富数据信息
- **AI分析** - 智能生成项目健康度评分和建议
- **报告输出** - 结构化输出CSV和Markdown报告

## 📊 输出示例

### CSV数据导出 (`csv_output/github_stars_YYYYMMDD.csv`)

```csv
仓库名,编程语言,项目描述,仓库链接,Star数,最近更新日期,沉寂天数,年提交数,最近更新内容
GibsonAI/Memori,Python,"Open-Source Memory Engine for LLMs...",https://github.com/GibsonAI/Memori,8518,2025-11-24,6,298,Clarify beta testing program details...
```

### AI分析报告 (`reports/analysis_report_YYYYMMDD.md`)

```markdown
# GitHub Star 项目资产健康度分析报告

## 1. 整体健康度评分与评价

**整体评分：7.0 / 10**

您的技术栈呈现出良好的多样性与活跃度...
```

## 🔧 环境要求

### 前置条件

- Python 3.12+
- uv 包管理器 (推荐) 或 pip
- GitHub Personal Access Token
- OpenAI或DeepSeek API Key

### 快速开始

1. **克隆仓库**

```bash
git clone https://github.com/cksdz1007/github-star-tracker.git
cd github-star-tracker
```

2. **安装依赖**

```bash
# 使用uv (推荐)
uv sync

# 或使用pip
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
```

4. **配置 .env 文件**

```bash
# ============== GitHub 配置 ==============
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# ============== LLM API 配置 ==============
OPENAI_API_KEY=your_openai_or_deepseek_api_key
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
```

### API密钥配置

**GitHub Token:**

1. 访问 <https://github.com/settings/tokens>
2. 点击 "Generate new token (classic)"
3. 选择权限: `public_repo`
4. 复制生成的token

**OpenAI/DeepSeek API Key:**

- OpenAI: <https://platform.openai.com/api-keys>
- DeepSeek: <https://platform.deepseek.com>

### 运行

```bash
# 方法1: 使用uv运行 (推荐)
uv run python main.py

# 方法2: 激活虚拟环境后运行
source .venv/bin/activate && python main.py
```

### 输出文件

运行完成后会在当前目录生成:

```
📁 csv_output/
  📊 github_stars_YYYYMMDD_HHMMSS.csv      # CSV数据
  📄 language_summary_YYYYMMDD_HHMMSS.txt  # 语言统计

📁 reports/
  📝 analysis_report_YYYYMMDD_HHMMSS.md    # AI分析报告
```

## 📁 项目结构

```
github-star-tracker/
├── 📂 src/                      # 核心代码
│   ├── 📂 config/               # 配置管理
│   │   └── settings.py          # 设置管理
│   ├── 📂 fetchers/             # 数据获取
│   │   ├── starred_repos.py     # 获取starred仓库
│   │   ├── repo_stats.py        # 获取仓库统计
│   │   └── readme_extractor.py  # README提取
│   ├── 📂 processors/           # 数据处理
│   │   └── data_processor.py    # 数据处理器
│   ├── 📂 analyzers/            # AI分析
│   │   └── ai_analyzer.py       # AI分析器
│   ├── 📂 output/               # 文件输出
│   │   ├── csv_exporter.py      # CSV导出
│   │   └── markdown_exporter.py # Markdown导出
│   ├── 📂 models/               # 数据模型
│   │   └── repository.py        # 仓库模型
│   └── 📂 utils/                # 工具函数
├── 📂 tests/                    # 测试文件
├── 📂 docs/                     # 文档
│   ├── REFACTORING_PLAN.md      # 重构计划
│   ├── ARCHITECTURE.md          # 架构文档
│   ├── REFACTORING_SUMMARY.md   # 重构总结
│   └── README.md                # 文档导航
├── 📂 scripts/                  # 脚本
│   └── migrate_from_monolith.py # 迁移脚本
├── 📂 csv_output/               # CSV输出目录
├── 📂 reports/                  # 报告输出目录
├── main.py                      # 主入口 (v2.0 - 模块化架构)
├── main_old.py                  # 原始单文件版本备份
├── CLAUDE.md                    # Claude Code指南
└── pyproject.toml               # 项目配置
```

## 🏗️ 架构设计

**模块化架构 (v2.0)** - 代码组织为6个核心模块:

### 核心模块

1. **Config** - 环境配置管理
2. **Fetchers** - 从GitHub API获取数据
3. **Processors** - 数据处理和转换
4. **Analyzers** - 基于AI的数据分析
5. **Output** - 文件输出和导出
6. **Models** - 数据模型定义

### 设计原则

- ✨ **单一职责** - 每个模块有明确单一目的
- 🔄 **依赖倒置** - 高层模块依赖抽象而非具体实现
- 🛡️ **类型安全** - 100%类型提示覆盖
- 🧪 **可测试性** - 模块可独立测试

## 🔍 功能详解

### 数据获取

- **Starred仓库** - 批量获取所有star的仓库（自动分页）
- **仓库统计** - 获取提交活动、最新提交信息
- **README提取** - 从README文件提取并总结项目描述

### 数据处理

- **描述丰富** - 从README补充无描述项目信息
- **活跃度分析** - 计算沉寂天数、活跃状态
- **数据清洗** - 标准化时间格式、数据验证

### AI分析

- **健康度评分** - 0-10分评分项目整体健康状况
- **活跃度分析** - 分析近期更新内容
- **技术建议** - 对长期未更项目提供处理建议
- **语言分布** - 统计编程语言分布情况

### 输出报告

- **CSV数据** - 完整项目数据，便于进一步分析
- **语言统计** - 编程语言分布和占比
- **Markdown报告** - AI生成的综合分析报告

## 📋 使用示例

### 快速上手

```bash
# 1. 运行程序
uv run python main.py

# 2. 查看AI报告
cat reports/analysis_report_$(date +%Y%m%d)*.md
```

### 高级分析

```bash
# 统计Python项目数量
grep "Python" csv_output/github_stars_*.csv | wc -l

# 查找1年以上未更新的项目
awk -F',' '$7 > 365' csv_output/github_stars_*.csv
```

## ⚡ 性能优化

- **API速率限制** - 0.2秒延迟避免触发GitHub API限制
- **智能跳过** - 超过180天未更新的仓库跳过提交统计（节省API配额）
- **惰性加载** - 仅对无描述项目获取README内容
- **优雅降级** - 单个API调用失败不影响整体流程
- **UTC时间** - 统一时区处理

## 📚 开发指南

### 环境设置

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码格式化
uv run black src/
uv run flake8 src/
uv run mypy src/
```

### 重构详情

本项目已从单文件架构重构为模块化架构:

- [REFACTORING_PLAN.md](docs/REFACTORING_PLAN.md) - 详细重构计划
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计文档
- [REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md) - 重构完成总结

### Claude Code 指南

完整的使用指南和开发说明请参考 [CLAUDE.md](CLAUDE.md):

- 项目架构详解
- 开发环境配置
- 模块职责说明
- 定制化配置点
- 最佳实践指南

## ❗ 常见问题

### API错误 (401 Unauthorized)

**问题**: 提示API认证失败
**解决**: 检查 `.env` 文件中的 `GITHUB_TOKEN` 是否正确，确保token有效且权限包含 `public_repo`

### 环境变量冲突

**问题**: 即使配置了.env文件仍然报错
**解决**: 检查系统环境变量是否与.env冲突:

```bash
unset GITHUB_TOKEN && unset OPENAI_API_KEY && uv run python main.py
```

### README提取失败

**问题**: 部分项目README内容获取失败
**解决**: 项目可能无README或README路径异常，已内置fallback机制，会使用简单的模式匹配

## 📈 更新日志

### v2.0 (2025-12-01) - 模块化重构

- ✨ 新增模块化架构
- ✨ 新增编程语言分析
- ✨ 新增README提取和总结
- ✨ 新增详细执行日志
- ✨ 新增CSV语言统计摘要
- ✨ 优化错误处理和API限制
- ✨ 提升代码可维护性和可测试性

### v1.0 (2025-12-01) - 初始版本

- ✨ 获取GitHub starred仓库
- ✨ AI分析报告生成
- ✨ CSV和Markdown导出

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - AI分析框架
- [GitHub API](https://docs.github.com/en/rest) - 数据获取
- [pandas](https://pandas.pydata.org/) - 数据处理

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

📧 联系方式: <your-email@example.com>
🐛 问题反馈: [GitHub Issues](https://github.com/cksdz1007/github-star-tracker/issues)
