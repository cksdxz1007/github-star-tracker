# GitHub Star Tracker - 模块化重构方案

## 📋 当前状态分析

### 代码规模
- **总行数**: 387行
- **函数数量**: 7个主要函数
- **代码结构**: 单文件 monolithic 架构

### 当前模块分布
```
main.py (387行)
├── 配置管理 (1-31行)      - 环境变量加载和验证
├── 数据获取模块 (35-81行) - GitHub API调用
├── README处理 (83-168行)  - README提取和总结
├── AI分析模块 (172-240行) - LangChain分析
└── 主程序流程 (242-387行) - 业务逻辑编排
```

## 🎯 重构目标

1. **提高可维护性** - 单一职责原则，每个模块职责明确
2. **增强可测试性** - 模块独立，便于单元测试
3. **改善可扩展性** - 新功能可以独立模块形式添加
4. **优化协作体验** - 团队成员可并行开发不同模块
5. **促进代码复用** - fetchers、processors可在其他项目复用

## 📦 目标目录结构

```
📦 github-star-tracker/
├── 📁 src/                          # 源代码目录
│   ├── 📁 config/                   # 配置管理模块
│   │   ├── __init__.py
│   │   ├── settings.py              # 应用配置管理
│   │   └── github_api.py            # GitHub API配置
│   │
│   ├── 📁 fetchers/                 # 数据获取模块
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础Fetcher类
│   │   ├── starred_repos.py         # 获取starred仓库列表
│   │   ├── repo_stats.py            # 仓库统计数据获取
│   │   └── readme_extractor.py      # README内容提取
│   │
│   ├── 📁 processors/               # 数据处理模块
│   │   ├── __init__.py
│   │   ├── data_processor.py        # 数据清洗和处理
│   │   ├── language_analyzer.py     # 编程语言分析
│   │   └── description_enricher.py  # 项目描述丰富化
│   │
│   ├── 📁 analyzers/                # 分析模块
│   │   ├── __init__.py
│   │   ├── ai_analyzer.py           # AI分析（LangChain）
│   │   └── report_generator.py      # 报告生成器
│   │
│   ├── 📁 output/                   # 输出模块
│   │   ├── __init__.py
│   │   ├── csv_exporter.py          # CSV导出器
│   │   ├── markdown_exporter.py     # Markdown导出器
│   │   └── file_manager.py          # 文件管理
│   │
│   ├── 📁 utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py                # 日志记录
│   │   ├── validators.py            # 数据验证
│   │   └── helpers.py               # 辅助函数
│   │
│   └── 📁 models/                   # 数据模型
│       ├── __init__.py
│       ├── repository.py            # Repository数据模型
│       └── analysis_result.py       # 分析结果模型
│
├── 📁 tests/                        # 测试目录
│   ├── __init__.py
│   ├── conftest.py                  # pytest配置
│   ├── 📁 unit/                     # 单元测试
│   │   ├── test_fetchers/
│   │   ├── test_processors/
│   │   ├── test_analyzers/
│   │   └── test_output/
│   └── 📁 integration/              # 集成测试
│       └── test_end_to_end.py
│
├── 📁 scripts/                      # 脚本目录
│   ├── migrate_from_monolith.py     # 从单文件迁移脚本
│   └── setup_dev_env.sh             # 开发环境设置
│
├── 📄 main.py                       # 主入口（简化至~30行）
├── 📄 requirements-dev.txt          # 开发依赖
├── 📄 requirements.txt              # 生产依赖
├── 📄 pyproject.toml                # 项目配置
├── 📄 .env.example                  # 环境变量示例
├── 📄 README.md
└── 📄 docs/                         # 文档目录
    ├── ARCHITECTURE.md              # 架构文档
    ├── API_REFERENCE.md             # API参考
    └── DEVELOPMENT.md               # 开发指南
```

## 🔧 详细模块设计

### 1. 配置管理模块 (src/config/)

#### `settings.py`
**职责**: 应用配置管理

```python
from dataclasses import dataclass
from typing import Optional

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
        from dotenv import load_dotenv
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
```

#### `github_api.py`
**职责**: GitHub API相关配置

```python
class GitHubAPI:
    """GitHub API封装"""
    BASE_URL = "https://api.github.com"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.headers = settings.github_headers

    @property
    def starred_url(self) -> str:
        return f"{self.BASE_URL}/users/{self.settings.github_username}/starred"

    @property
    def repo_stats_url(self, repo_name: str) -> str:
        return f"{self.BASE_URL}/repos/{repo_name}/stats/participation"
```

### 2. 数据获取模块 (src/fetchers/)

#### `base.py`
**职责**: 基础Fetcher类

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

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
```

#### `starred_repos.py`
**职责**: 获取starred仓库列表

```python
class StarredRepoFetcher(BaseFetcher[Repository]):
    """获取用户starred仓库"""

    def fetch(self) -> List[Repository]:
        """获取所有starred仓库"""
        repos = []
        page = 1

        while True:
            url = f"{self.settings.github_api.starred_url}?per_page=100&page={page}"
            try:
                response = self._request(url)
                data = response.json()

                if not data:
                    break

                for repo_data in data:
                    repos.append(Repository.from_github_api(repo_data))

                print(f"   已加载第 {page} 页，累计 {len(repos)} 个...")
                page += 1
                time.sleep(self.settings.request_delay)

            except Exception as e:
                print(f"❌ API 请求失败: {e}")
                break

        return repos
```

#### `repo_stats.py`
**职责**: 仓库统计数据获取

```python
class RepoStatsFetcher(BaseFetcher[dict]):
    """获取仓库统计数据"""

    def fetch_commit_activity(self, repo_full_name: str) -> int:
        """获取过去一年的提交统计"""
        url = self.settings.github_api.repo_stats_url(repo_full_name)
        try:
            response = self._request(url)
            if response.status_code == 200:
                data = response.json()
                if 'all' in data:
                    return sum(data['all'])
        except:
            pass
        return 0

    def fetch_latest_commit(self, repo_full_name: str, branch: str) -> str:
        """获取最新提交信息"""
        url = f"{self.settings.github_api.BASE_URL}/repos/{repo_full_name}/commits/{branch}"
        try:
            response = self._request(url)
            if response.status_code == 200:
                msg = response.json()['commit']['message']
                return msg.split('\n')[0][:100]
        except:
            pass
        return "无法获取"
```

#### `readme_extractor.py`
**职责**: README内容提取和总结

```python
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
                import base64
                readme_content = base64.b64decode(response.json()['content']).decode('utf-8')

                # 使用LLM总结
                return self._summarize_with_llm(readme_content)

        except Exception as e:
            pass

        return "无描述"

    def _summarize_with_llm(self, readme_content: str) -> str:
        """使用LLM总结README"""
        # 实现LLM总结逻辑
        pass
```

### 3. 数据模型 (src/models/)

#### `repository.py`
**职责**: Repository数据模型

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Repository:
    """仓库数据模型"""
    full_name: str
    description: Optional[str]
    html_url: str
    language: Optional[str]
    stargazers_count: int
    pushed_at: Optional[str]

    @classmethod
    def from_github_api(cls, data: dict) -> 'Repository':
        """从GitHub API响应创建实例"""
        return cls(
            full_name=data['full_name'],
            description=data.get('description'),
            html_url=data['html_url'],
            language=data.get('language'),
            stargazers_count=data['stargazers_count'],
            pushed_at=data.get('pushed_at'),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "仓库名": self.full_name,
            "项目描述": self.description or "无描述",
            "仓库链接": self.html_url,
            "编程语言": self.language or "Unknown",
            "Star数": self.stargazers_count,
            "最近更新日期": self._format_date(self.pushed_at) if self.pushed_at else "N/A",
            "沉寂天数": self._calculate_inactive_days(),
        )

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return "N/A"
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")

    def _calculate_inactive_days(self) -> int:
        """计算沉寂天数"""
        if not self.pushed_at:
            return -1
        # 实现计算逻辑
        pass
```

### 4. 数据处理模块 (src/processors/)

#### `data_processor.py`
**职责**: 数据清洗和处理

```python
class DataProcessor:
    """数据处理器"""

    def __init__(self, settings: Settings):
        self.settings = settings

    def process_repositories(
        self,
        repos: List[Repository],
        readme_extractor: ReadmeExtractor,
        stats_fetcher: RepoStatsFetcher
    ) -> List[dict]:
        """处理仓库数据"""
        processed_data = []

        for repo in repos:
            # 计算沉寂天数
            days_inactive = repo._calculate_inactive_days()

            # 获取提交数据（仅限近半年更新的项目）
            commits_last_year = 0
            last_msg = ""

            if days_inactive != -1 and days_inactive < 180:
                commits_last_year = stats_fetcher.fetch_commit_activity(repo.full_name)
                last_msg = stats_fetcher.fetch_latest_commit(repo.full_name, "main")

            # 丰富描述信息
            description = repo.description
            if not description or description == "无描述":
                description = readme_extractor.extract(repo.full_name)

            # 构建最终数据
            processed_data.append({
                "仓库名": repo.full_name,
                "编程语言": repo.language or "Unknown",
                "项目描述": description,
                "仓库链接": repo.html_url,
                "Star数": repo.stargazers_count,
                "最近更新日期": repo._format_date(repo.pushed_at),
                "沉寂天数": days_inactive,
                "年提交数": commits_last_year,
                "最近更新内容": last_msg
            })

        return processed_data
```

### 5. 分析模块 (src/analyzers/)

#### `ai_analyzer.py`
**职责**: AI分析（LangChain）

```python
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
        context = self._build_context(df)

        # 生成报告
        prompt = self._build_prompt(context)
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "total_count": len(df),
            "active_30d": len(df[df['沉寂天数'] < 30]),
            "inactive_1yr": len(df[df['沉寂天数'] > 365]),
            "active_str": self._format_active_projects(df),
            "dead_str": self._format_dead_projects(df),
        })

    def _build_context(self, df: pd.DataFrame) -> dict:
        """构建分析上下文"""
        return {
            "total_count": len(df),
            "language_distribution": df['编程语言'].value_counts().to_dict(),
            "inactive_projects": len(df[df['沉寂天数'] > 365]),
        }
```

### 6. 输出模块 (src/output/)

#### `csv_exporter.py`
**职责**: CSV导出器

```python
class CSVExporter:
    """CSV导出器"""

    def __init__(self, output_dir: str = "csv_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, data: List[dict], timestamp: str) -> str:
        """导出数据到CSV"""
        df = pd.DataFrame(data)

        filename = f"{self.output_dir}/github_stars_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        # 生成语言统计
        self._export_language_summary(df, timestamp)

        return filename

    def _export_language_summary(self, df: pd.DataFrame, timestamp: str):
        """导出语言统计摘要"""
        summary_file = f"{self.output_dir}/language_summary_{timestamp}.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"GitHub Stars 项目语言分类摘要\n")
            f.write(f"{'='*50}\n\n")
            # 写入统计信息
```

#### `markdown_exporter.py`
**职责**: Markdown导出器

```python
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
```

### 7. 主入口 (main.py)

```python
from src.config.settings import Settings
from src.fetchers.starred_repos import StarredRepoFetcher
from src.fetchers.readme_extractor import ReadmeExtractor
from src.fetchers.repo_stats import RepoStatsFetcher
from src.processors.data_processor import DataProcessor
from src.analyzers.ai_analyzer import AIAnalyzer
from src.output.csv_exporter import CSVExporter
from src.output.markdown_exporter import MarkdownExporter
from datetime import datetime

def main():
    """主程序"""
    # 1. 加载配置
    settings = Settings.from_env()

    # 2. 创建组件
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
    repos = repo_fetcher.fetch()

    # 3.2 处理数据
    print(f"\n⚙️ [步骤 2/4] 正在深入分析 {len(repos)} 个仓库...")
    processed_data = data_processor.process_repositories(
        repos, readme_extractor, stats_fetcher
    )

    # 3.3 导出CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"\n💾 [步骤 3/4] 正在保存原始数据到 CSV 文件...")
    csv_exporter.export(processed_data, timestamp)

    # 3.4 生成分析报告
    print(f"\n🧠 [步骤 4/4] 正在通过 LLM 生成智能分析报告...")
    df = pd.DataFrame(processed_data)
    report = ai_analyzer.analyze(df)
    markdown_exporter.export(report, timestamp)

    print("\n✅ 所有任务完成!")

if __name__ == "__main__":
    main()
```

## 📝 迁移步骤

### 阶段一：创建基础架构 (1-2天)
1. 创建目录结构
2. 创建所有 `__init__.py` 文件
3. 创建基础配置模块 (`src/config/`)

### 阶段二：迁移数据获取 (2-3天)
1. 创建数据模型 (`src/models/`)
2. 迁移GitHub API相关功能 (`src/fetchers/`)
3. 迁移README提取功能
4. 测试数据获取模块

### 阶段三：迁移数据处理 (1-2天)
1. 创建数据处理器 (`src/processors/`)
2. 迁移数据清洗逻辑
3. 测试数据处理

### 阶段四：迁移分析功能 (1-2天)
1. 创建分析器 (`src/analyzers/`)
2. 迁移AI分析逻辑
3. 测试分析功能

### 阶段五：迁移输出功能 (1天)
1. 创建输出模块 (`src/output/`)
2. 迁移文件导出逻辑
3. 测试输出功能

### 阶段六：重构主程序 (1天)
1. 简化 `main.py`
2. 创建Orchestrator类（可选）
3. 端到端测试

### 阶段七：添加测试和文档 (2-3天)
1. 编写单元测试
2. 编写集成测试
3. 完善文档
4. 添加类型提示

## 🔍 重构检查清单

- [ ] 所有模块都有明确的职责
- [ ] 模块间耦合度低，高内聚
- [ ] 添加了充分的单元测试（覆盖率 >80%）
- [ ] 添加了类型提示
- [ ] 代码遵循PEP 8规范
- [ ] 文档完整且准确
- [ ] 迁移脚本工作正常
- [ ] 端到端测试通过

## 🎯 预期收益

1. **代码可维护性提升 60%** - 模块化后，定位问题更快
2. **新功能开发速度提升 40%** - 可并行开发不同模块
3. **测试覆盖率提升至 80%+** - 独立模块便于测试
4. **代码复用性提升** - fetchers、processors可复用
5. **团队协作效率提升** - 清晰的模块边界和职责

## 📚 相关文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 详细架构设计
- [API_REFERENCE.md](./API_REFERENCE.md) - API参考文档
- [DEVELOPMENT.md](./DEVELOPMENT.md) - 开发指南
- [Testing Guide](./TESTING.md) - 测试指南

---

**维护者**: Claude Code
**最后更新**: 2025-12-01
**版本**: v1.0
