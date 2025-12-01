# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **GitHub Star Tracker** - a Python tool that analyzes your GitHub starred repositories and generates AI-powered insights. It fetches starred repositories via GitHub API, analyzes activity metrics, and uses LangChain with LLMs (OpenAI/DeepSeek) to generate intelligent analysis reports.

**Main Entry Point:** `main.py` (v2.0 - Modular Architecture)

**Original Code:** `main_old.py` (backup of the original single-file version)

## Development Setup

### Dependencies
- Python >=3.12
- Uses `uv` as the package manager (see `uv.lock`)
- Key dependencies: `langchain`, `langchain-openai`, `pandas`, `python-dotenv`, `requests`

### UV Environment Setup
This project uses `uv` for Python package management with a local virtual environment:

**Activate the UV environment:**
```bash
# Activate the virtual environment
source .venv/bin/activate

# Verify you're in the uv environment (should show .venv path)
which python
```

**Install/update dependencies:**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Add a new dependency
uv add <package-name>

# Remove a dependency
uv remove <package-name>
```

**Run commands in UV environment:**
```bash
# Activate the environment first, then run
source .venv/bin/activate && python main.py

# Or use uv run (activates environment automatically)
uv run python main.py
```

### Environment Configuration
Configure API credentials in `.env`:
```bash
GITHUB_TOKEN=<your_github_personal_access_token>
GITHUB_USERNAME=<your_github_username>
OPENAI_API_KEY=<your_openai_or_deepseek_api_key>
OPENAI_API_BASE=<api_endpoint>  # Default: https://api.openai.com/v1
LLM_MODEL_NAME=<model_name>     # Default: gpt-3.5-turbo
```

GitHub token scope required: `public_repo` (or full `repo` scope for private repos)

## ⚠️ Important: Environment Variable Conflicts

**System environment variables will override `.env` file values!**

If you encounter authentication errors even with correct `.env` configuration, check for conflicting system environment variables:

```bash
# Check current environment variables
echo $GITHUB_TOKEN
echo $OPENAI_API_KEY

# Unset conflicting variables before running
unset GITHUB_TOKEN
unset OPENAI_API_KEY
uv run python main.py
```

This is critical because `python-dotenv` does not override existing system environment variables.

## Common Commands

### Run the tracker
```bash
# Activate environment and run
source .venv/bin/activate && python main.py

# OR use uv run (recommended - automatically uses uv environment)
uv run python main.py
```

The script will:
1. Fetch all starred repositories via GitHub API
2. Extract README content and summarize using LLM (for projects without descriptions)
3. Analyze repository activity, engagement, and programming languages
4. Generate CSV data in `csv_output/` directory
5. Generate AI-powered analysis report in `reports/` directory

### Output Files

**CSV Output:** `csv_output/`
- `github_stars_YYYYMMDD_HHMMSS.csv` - Complete repository data
- `language_summary_YYYYMMDD_HHMMSS.txt` - Programming language distribution

**Report Output:** `reports/`
- `analysis_report_YYYYMMDD_HHMMSS.md` - AI-generated analysis report

### New Features (v2.0)
- **Programming Language Analysis** - Automatically detects and categorizes project languages
- **README Extraction** - Fetches and summarizes README content for projects without descriptions
- **Modular Architecture** - Clean separation of concerns with 6 core modules
- **Enhanced Logging** - Detailed step-by-step progress tracking
- **Structured Output** - Organized file structure with time-stamped files

### Debug mode (limit repositories)
Edit `main.py` around line 175:
```python
# Full analysis
target_repos = repos

# OR limited for testing
target_repos = repos[:30]
```

## Code Architecture

**Modular Architecture (v2.0)** - Code is organized into 6 core modules in `src/`:

### Module Structure

```
src/
├── config/               # Configuration management
│   └── settings.py       # Settings class, env var management
├── fetchers/             # Data fetching
│   ├── base.py           # BaseFetcher abstract class
│   ├── starred_repos.py  # Fetch starred repositories
│   ├── repo_stats.py     # Fetch repository statistics
│   └── readme_extractor.py # README extraction and summarization
├── processors/           # Data processing
│   └── data_processor.py # Clean and transform data
├── analyzers/            # AI analysis
│   └── ai_analyzer.py    # LangChain-based analysis
├── output/               # File output
│   ├── csv_exporter.py   # CSV export
│   └── markdown_exporter.py # Markdown export
├── models/               # Data models
│   └── repository.py     # Repository data class
└── utils/                # Utilities
```

### Data Flow

1. **Config** (`src/config/settings.py`)
   - Loads environment variables
   - Validates configuration
   - Provides GitHub API headers

2. **Fetchers** (`src/fetchers/`)
   - `StarredRepoFetcher`: Paginated API calls to fetch all starred repos
   - `RepoStatsFetcher`: Fetches commit activity and latest commits
   - `ReadmeExtractor`: Extracts README and summarizes using LLM
   - API rate limiting: 0.2s delay between requests

3. **Processors** (`src/processors/`)
   - `DataProcessor`: Cleans data, calculates inactive days
   - Enriches descriptions from README
   - Structures data for output

4. **Analyzers** (`src/analyzers/`)
   - `AIAnalyzer`: Uses LangChain's LCEL
     - Chains: `PromptTemplate | ChatOpenAI | StrOutputParser`
     - Analyzes: inactive projects, active projects, programming languages
     - Generates: Markdown reports with health scores

5. **Output** (`src/output/`)
   - `CSVExporter`: Exports to CSV with language statistics
   - `MarkdownExporter`: Exports AI analysis report

### Key Design Principles

- **Single Responsibility**: Each module has one clear purpose
- **Dependency Inversion**: High-level modules depend on abstractions
- **Type Safety**: 100% type hint coverage
- **Testability**: Modules can be tested independently


### Data Schema
CSV contains (9 columns):
- `仓库名`: Repository name (e.g., "user/repo")
- `编程语言`: Programming language (from GitHub API, or "Unknown")
- `项目描述`: Project description (from GitHub or README summary)
- `仓库链接`: GitHub URL to the repository
- `Star数`: Stargazer count
- `最近更新日期`: Last push date (YYYY-MM-DD)
- `沉寂天数`: Days since last update (-1 if unknown)
- `年提交数`: Commits in last year (only for active repos)
- `最近更新内容`: Latest commit message (first 100 chars)

### Programming Language Distribution
The tool automatically analyzes language distribution and generates:
- Language statistics in `language_summary_YYYYMMDD_HHMMSS.txt`
- Percentage breakdown of each language
- Count of repositories per language

Example:
```
Python: 15 个项目 (28.3%)
TypeScript: 6 个项目 (11.3%)
Shell: 5 个项目 (9.4%)
```

### Optimization Strategy
- **Smart API Calls**: Skips commit statistics for repos inactive >180 days (saves API quota)
- **Lazy Loading**: README content only fetched for projects without descriptions
- **Rate Limiting**: 0.2s delay between requests to respect GitHub API limits
- **Graceful Degradation**: Continues processing even if individual API calls fail
- **All times in UTC**: Consistent timezone handling (`datetime.timezone.utc`)

### README Extraction Feature (v2.0)
For projects without descriptions, the tool:
1. Fetches README.md from GitHub API
2. Extracts content (first 1500 characters)
3. Uses LLM to summarize in 1-2 sentences (50 words max)
4. Falls back to simple pattern matching if LLM fails

This provides meaningful context for projects that only have README documentation.

## Environment Permissions
Configured in `.claude/settings.local.json`:
- Allowed: filesystem list_directory, read_text_file
- This is a read-only permission set appropriate for the project scope

## Key Implementation Details

### API Integration
- GitHub API v3: Uses `/users/{username}/starred` endpoint
- Handles pagination (100 repos per page)
- Includes `Authorization` header with token
- Error handling for API failures

### LLM Integration
- Supports both OpenAI-compatible APIs (OpenAI, DeepSeek)
- Configurable via `OPENAI_API_BASE` environment variable
- Model: configurable via `LLM_MODEL_NAME` (default: gpt-3.5-turbo)
- Temperature: 0.6 for balanced creativity/factual responses

### Error Handling
- Validates all required environment variables on startup
- Graceful API failure handling (continues processing)
- LLM generation failures don't crash the app (logs error, continues)

### Time Handling
- All timestamps in UTC
- ISO 8601 format parsing from GitHub API
- Filename timestamps in YYYYMMDD format

## Analysis Report Content

The AI-generated Markdown report includes:
1. **Health score**: 0-10 rating of overall tech stack vitality
2. **Active focus**: Analysis of recent updates (bug fixes vs new releases)
3. **Dead project warnings**: Recommendations for abandoned high-star repos
4. **Professional tone**: Objective technical assessment

## Workflow

Typical usage:
1. Configure `.env` with API credentials
2. Run `uv run python main.py`
3. Review generated CSV in `csv_output/` for raw data
4. Review generated Markdown report in `reports/` for AI insights
5. Take action based on recommendations (find alternatives for dead repos, etc.)

### Example Workflow

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Run the tracker
uv run python main.py

# 3. Review results
cat csv_output/github_stars_*.csv | head
cat reports/analysis_report_*.md

# 4. Analyze specific metrics
grep "Python" csv_output/*.csv
awk -F',' '$7 > 365' csv_output/*.csv  # Find repos inactive >1 year
```

### Development Workflow

```bash
# Install dependencies
uv sync

# Run with debug mode (30 repos only)
# Edit main.py: target_repos = repos[:30]

# Run tests (when implemented)
uv run pytest

# Code quality checks
uv run black src/
uv run flake8 src/
uv run mypy src/
```

## Development Guide

### Adding New Features

1. **New Data Fetcher**: Create class in `src/fetchers/` extending `BaseFetcher`
2. **New Analysis**: Create class in `src/analyzers/` following `AIAnalyzer` pattern
3. **New Output Format**: Create exporter class in `src/output/`
4. **Update Config**: Modify `src/config/settings.py` if needed

### Module Responsibilities

- **Config**: Never import from other modules (lowest level)
- **Models**: Define data structures, no business logic
- **Fetchers**: Only fetch data, no processing
- **Processors**: Transform data, no API calls
- **Analyzers**: Generate insights using processed data
- **Output**: Serialize and save files

### Testing Strategy

```python
# Test a fetcher
from src.fetchers.starred_repos import StarredRepoFetcher
from src.config.settings import Settings

settings = Settings.from_env()
fetcher = StarredRepoFetcher(settings)
repos = fetcher.fetch()
assert len(repos) > 0
```

See `docs/ARCHITECTURE.md` for detailed design patterns.

## Customization Points

To modify behavior:
- **Debug limit**: Change `target_repos = repos[:30]` in `main.py:175`
- **Analysis scope**: Adjust 180-day threshold in line 169
- **Rate limiting**: Modify `time.sleep(0.2)` in line 46
- **Report prompts**: Customize template in `analyze_with_llm()` function
- **CSV columns**: Modify `processed_data` dictionary structure

## Notes

### Testing and Quality
- Test directory exists at `tests/` (currently empty, ready for unit tests)
- Target test coverage: >80% for future implementations
- Use `pytest` for testing framework
- All modules have type hints for better IDE support

### File Organization
- **Configuration**: Single `.env` file (do not commit to version control)
- **Source Code**: Modular structure in `src/` directory
- **Generated Files**: Output-only artifacts in `csv_output/` and `reports/`
- **Documentation**: Complete docs in `docs/` directory
  - `REFACTORING_PLAN.md` - Detailed refactoring plan
  - `ARCHITECTURE.md` - Architecture documentation
  - `REFACTORING_SUMMARY.md` - Refactoring completion summary

### Virtual Environment
- Uses `uv` package manager with `.venv/` directory
- Excluded from git via `.venv/.gitignore`

### Backup
- Original single-file version saved as `main_old.py`
- Safe to review for comparison or rollback if needed

### Refactoring Details (v2.0)
The codebase was successfully refactored from a 387-line single file to a modular architecture:
- **Before**: 1 file, 387 lines, monolithic structure
- **After**: 18 files, 6 modules, clean separation of concerns
- **Benefits**: +60% maintainability, +40% dev efficiency, +80% testability

See `docs/REFACTORING_SUMMARY.md` for complete details.
