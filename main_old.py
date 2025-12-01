# main.py
import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

# LangChain 导入
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 加载环境变量
load_dotenv()

# 2. 检查配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

if not all([GITHUB_TOKEN, GITHUB_USERNAME, OPENAI_API_KEY]):
    print("❌ 错误: 请在 .env 文件中配置所有必要的环境变量。")
    exit(1)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ==================== 功能模块：数据获取 ====================

def fetch_starred_repos():
    """获取所有 Star 的仓库列表"""
    repos = []
    page = 1
    print(f"📡 开始获取用户 {GITHUB_USERNAME} 的 Star 列表...")
    
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/starred?per_page=100&page={page}"
        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()
            if not data: break
            
            repos.extend(data)
            print(f"   已加载第 {page} 页，累计 {len(repos)} 个...")
            page += 1
            time.sleep(0.2) # 稍微限制速率
        except Exception as e:
            print(f"❌ API 请求失败: {e}")
            break
    return repos

def get_commit_activity(repo_full_name):
    """获取过去一年的提交统计 (Commit Frequency)"""
    url = f"https://api.github.com/repos/{repo_full_name}/stats/participation"
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if 'all' in data:
                return sum(data['all']) # 返回过去52周的总提交数
    except:
        pass
    return 0

def get_latest_commit_msg(repo_full_name, branch):
    """获取最后一次提交的 Message"""
    url = f"https://api.github.com/repos/{repo_full_name}/commits/{branch}"
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            msg = resp.json()['commit']['message']
            return msg.split('\n')[0][:100] # 只取第一行前100字
    except:
        pass
    return "无法获取"

def get_readme_summary(repo_full_name):
    """从README文件中使用LLM总结项目用途"""
    try:
        # 首先尝试获取README.md
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        resp = requests.get(url, headers=HEADERS)

        if resp.status_code == 200:
            import base64
            readme_content = base64.b64decode(resp.json()['content']).decode('utf-8')

            # 提取前1500个字符作为参考文本（给LLM更多内容）
            summary_text = readme_content[:1500]

            # 使用LLM总结
            summary_prompt = f"""
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
                    model_name=LLM_MODEL_NAME,
                    temperature=0.3,
                    openai_api_key=OPENAI_API_KEY,
                    openai_api_base=OPENAI_API_BASE
                )

                chain = summary_prompt | summary_llm | StrOutputParser()
                result = chain.invoke({})

                if result and len(result.strip()) > 5:
                    return result.strip()
                return "无描述"

            except Exception as llm_error:
                print(f"   ⚠️ LLM总结失败: {str(llm_error)[:50]}")
                # 如果LLM失败，回退到简单提取
                return get_readme_simple(summary_text)

        return "无描述"

    except Exception as e:
        return "无描述"

def get_readme_simple(readme_content):
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

# ==================== 功能模块：智能分析 ====================

def analyze_with_llm(df):
    """使用 LangChain 分析数据并生成报告"""
    print("\n🧠 数据处理完毕，正在通过 LLM 生成洞察报告...")
    
    # 1. 准备上下文 (Context Extraction)
    total_count = len(df)
    inactive_1yr = len(df[df['沉寂天数'] > 365])
    active_30d = len(df[df['沉寂天数'] < 30])
    
    # 选取近期最活跃的 Top 5
    top_active = df.sort_values("沉寂天数").head(5)
    active_str = "\n".join(
        [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  更新于{row['最近更新日期']}，更新内容: {row['最近更新内容']}"
         for _, row in top_active.iterrows()]
    )

    # 选取已经"死掉"但还有名气的 Top 5 (Star数高但很久没更)
    dead_giants = df[df['沉寂天数'] > 365].sort_values("Star数", ascending=False).head(5)
    dead_str = "\n".join(
        [f"- [{row['仓库名']}]({row['仓库链接']}) - [{row['编程语言']}] - {row['项目描述']}\n  已停更{row['沉寂天数']}天 (Star: {row['Star数']})"
         for _, row in dead_giants.iterrows()]
    )

    # 2. 构建 Prompt
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
    
    # 3. 配置模型
    llm = ChatOpenAI(
        model_name=LLM_MODEL_NAME,
        temperature=0.6, 
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE
    )
    
    # 4. 执行 (LCEL 语法)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "total_count": total_count,
        "active_30d": active_30d,
        "inactive_1yr": inactive_1yr,
        "active_str": active_str,
        "dead_str": dead_str
    })

# ==================== 主程序 ====================

def main():
    print("\n" + "="*50)
    print("🚀 GitHub Star Tracker 开始运行")
    print("="*50)

    # 步骤1: 获取基础列表
    print("\n📡 [步骤 1/4] 正在获取 GitHub Starred 仓库列表...")
    repos = fetch_starred_repos()
    if not repos:
        print("❌ 未获取到任何仓库，程序退出")
        return

    processed_data = []
    now = datetime.now(timezone.utc)

    print(f"\n⚙️ [步骤 2/4] 正在深入分析 {len(repos)} 个仓库...")
    print("   - 收集仓库基本信息（描述、链接、星标数）")
    print("   - 计算沉寂天数和活动状态")
    print("   - 获取近期活跃仓库的提交数据")

    # ⚠️ 调试模式：只取前 30 个仓库以节省时间。正式使用请去掉 [:30]
    target_repos = repos # acts on all repos
    # target_repos = repos[:30]

    start_time = time.time()

    for i, repo in enumerate(target_repos):
        pushed_at = repo['pushed_at']
        repo_name = repo['full_name']
        
        days_inactive = -1
        date_str = "N/A"
        
        if pushed_at:
            dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            days_inactive = (now - dt).days
            date_str = dt.strftime("%Y-%m-%d")
            
        # 优化策略：只有最近半年有更新的项目，才去查 commit frequency，节省 API
        commits_last_year = 0
        last_msg = ""

        if days_inactive != -1 and days_inactive < 180:
            commits_last_year = get_commit_activity(repo_name)
            last_msg = get_latest_commit_msg(repo_name, repo['default_branch'])

        # 获取项目描述和链接
        description = repo.get('description', '无描述') or '无描述'

        # 如果没有描述，尝试从README获取
        if not description or description == '无描述':
            print(f"   📄 正在获取 {repo_name} 的README内容...")
            description = get_readme_summary(repo_name)
            time.sleep(0.1)  # 稍微限制速率

        html_url = repo.get('html_url', '')
        language = repo.get('language', 'Unknown') or 'Unknown'

        processed_data.append({
            "仓库名": repo_name,
            "编程语言": language,
            "项目描述": description,
            "仓库链接": html_url,
            "Star数": repo['stargazers_count'],
            "最近更新日期": date_str,
            "沉寂天数": days_inactive,
            "年提交数": commits_last_year,
            "最近更新内容": last_msg
        })
        
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"   ✓ 已处理 {i+1}/{len(target_repos)} 个仓库 (用时 {elapsed:.1f}s)")

    elapsed_total = time.time() - start_time
    print(f"   ✓ 仓库分析完成! 总用时 {elapsed_total:.1f}s")

    # 步骤3: 保存 CSV
    print(f"\n💾 [步骤 3/4] 正在保存原始数据到 CSV 文件...")

    # 创建 DataFrame
    df = pd.DataFrame(processed_data)

    # 统计各语言的仓库数量
    language_counts = df['编程语言'].value_counts()
    print(f"   📊 项目语言分布: {dict(language_counts)}")

    # 创建输出目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_dir = "csv_output"
    os.makedirs(csv_dir, exist_ok=True)

    # 保存完整的CSV
    csv_filename = f"{csv_dir}/github_stars_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"   ✓ 完整数据已保存: {csv_filename}")

    # 生成语言统计摘要
    summary_file = f"{csv_dir}/language_summary_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"GitHub Stars 项目语言分类摘要\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总项目数: {len(df)}\n\n")
        f.write(f"语言分布:\n")
        for lang, count in language_counts.items():
            f.write(f"  {lang}: {count} 个项目 ({count/len(df)*100:.1f}%)\n")

    print(f"   ✓ 语言统计摘要: {summary_file}")
    print(f"   ✓ CSV文件保存在目录: {csv_dir}/")

    # 步骤4: 生成 AI 报告
    print(f"\n🧠 [步骤 4/4] 正在通过 LLM 生成智能分析报告...")
    print("   - 分析活跃项目和停滞项目")
    print("   - 生成健康度评分和技术建议")

    # 创建报告目录
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    try:
        report = analyze_with_llm(df)
        md_filename = f"{reports_dir}/analysis_report_{timestamp}.md"
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"   ✓ AI 分析报告已生成: {md_filename}")
        print("\n" + "="*50)
        print("📊 分析报告内容:")
        print("="*50)
        print(report)
        print("\n" + "="*50)
        print("✅ 所有任务完成!")
        print("="*50)
        print(f"\n📁 输出文件位置:")
        print(f"   📊 CSV文件: {csv_dir}/")
        print(f"   📝 报告文件: {reports_dir}/")
        print("="*50)
    except Exception as e:
        print(f"❌ AI 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

