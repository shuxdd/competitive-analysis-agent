"""
搜索节点
========

使用搜索引擎、GitHub、应用商店、华为应用市场等多数据源并行采集竞品信息。
"""

import asyncio
import logging
from agent.graph_state import AgentState
from collector.web_search import WebSearchCollector
from collector.github_collector import GitHubCollector
from collector.app_store_collector import AppStoreCollector
from collector.huawei_collector import HuaweiCollector
from config.settings import settings
from utils.retry import retry_async
from agent.progress import report_progress

logger = logging.getLogger(__name__)

# 竞品名称到 GitHub 仓库的映射
GITHUB_REPOS = {
    "notion": "makenotion/notion-sdk-js",
    "obsidian": "obsidianmd/obsidian-releases",
}

# 竞品名称到 Google Play 应用 ID 的映射
GOOGLE_PLAY_APPS = {
    "notion": "notion.id",
    "obsidian": "md.obsidian",
    "钉钉": "com.alibaba.android.rimet",
    "企业微信": "com.tencent.wework",
    "飞书文档": "com.ss.android.lark",
}

# 竞品名称到华为应用市场包名的映射
HUAWEI_APPS = {
    "钉钉": "com.alibaba.android.rimet",
    "企业微信": "com.tencent.wework",
    "飞书文档": "com.ss.android.lark",
    "文心一言": "com.baidu.baiduapp",
    "通义千问": "com.aliyun.tongyi",
    "小红书": "com.xingin.xhs",
    "知乎": "com.zhihu.android",
    "B站": "tv.danmaku.bili",
    "有赞": "com.youzan.shop",
}

# 标签到数据源的映射
TAG_DATA_SOURCES = {
    "开源": ["github"],
    "开发者工具": ["github"],
    "GitHub": ["github"],
    "App": ["app_store"],
    "移动": ["app_store"],
    "C端": ["app_store"],
}


def _get_extra_sources(competitor_name: str, plan: dict) -> list:
    """根据竞品标签决定额外数据源"""
    sources = []
    competitors_meta = plan.get("competitors_meta", {})
    tags = competitors_meta.get(competitor_name, {}).get("tags", [])
    for tag in tags:
        if tag in TAG_DATA_SOURCES:
            sources.extend(TAG_DATA_SOURCES[tag])
    return list(set(sources))


async def _collect_one(
    name: str,
    keywords: list,
    plan: dict,
    search_collector: WebSearchCollector,
    github_collector: GitHubCollector,
    app_store_collector: AppStoreCollector,
    huawei_collector: HuaweiCollector,
) -> list:
    """
    采集单个竞品的所有数据源（并行执行）

    Returns:
        该竞品的所有采集结果列表
    """
    name_lower = name.lower()
    extra_sources = _get_extra_sources(name, plan)
    tasks = []

    # 1. 网页搜索（始终执行）
    async def _search():
        try:
            result = await retry_async(
                lambda: search_collector.search_competitor(
                    name, keywords=keywords or None, num_results=5
                )
            )
            logger.info(f"  [{name}] 搜索完成，{result.get('total_results', 0)} 条结果")
            return {"competitor": name, "source": "web_search", "data": result}
        except Exception as e:
            logger.warning(f"  [{name}] 搜索失败: {e}")
            return {"competitor": name, "source": "web_search", "data": {"results": [], "total_results": 0}, "error": str(e)}

    tasks.append(_search())

    # 2. GitHub（按需）
    if "github" in extra_sources or name_lower in GITHUB_REPOS:
        repo_name = GITHUB_REPOS.get(name_lower)
        if repo_name:
            async def _gh(rn=repo_name):
                try:
                    result = await github_collector.run(rn)
                    logger.info(f"  [{name}] GitHub 完成: ⭐{result.get('data', {}).get('stars', 0)}")
                    return {"competitor": name, "source": "github", "data": result.get("data", {})}
                except Exception as e:
                    logger.warning(f"  [{name}] GitHub 失败: {e}")
                    return None
            tasks.append(_gh())

    # 3. Google Play（按需）
    if "app_store" in extra_sources or name_lower in GOOGLE_PLAY_APPS:
        app_id = GOOGLE_PLAY_APPS.get(name_lower)
        if app_id:
            async def _gp(aid=app_id):
                try:
                    result = await app_store_collector.run(aid, store="google")
                    logger.info(f"  [{name}] 应用商店完成: ⭐{result.get('data', {}).get('rating', 0)}")
                    return {"competitor": name, "source": "app_store", "data": result.get("data", {})}
                except Exception as e:
                    logger.warning(f"  [{name}] 应用商店失败: {e}")
                    return None
            tasks.append(_gp())

    # 4. 华为应用市场（按需，有密钥文件时启用）
    if name_lower in HUAWEI_APPS and settings.huawei_key_file:
        pkg_name = HUAWEI_APPS[name_lower]
        async def _hw(pkg=pkg_name):
            try:
                result = await huawei_collector.run(pkg, max_size=30)
                logger.info(f"  [{name}] 华为完成: ⭐{result.get('data', {}).get('rating', 0)}")
                return {"competitor": name, "source": "huawei", "data": result.get("data", {})}
            except Exception as e:
                logger.warning(f"  [{name}] 华为失败: {e}")
                return None
        tasks.append(_hw())

    # 并行执行所有数据源采集
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤异常和 None
    collected = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"  [{name}] 采集异常: {r}")
        elif r is not None:
            collected.append(r)

    return collected


async def search_competitors(state: AgentState) -> dict:
    """
    搜索节点

    并行采集所有竞品的多个数据源：
    - 网页搜索（始终执行）
    - GitHub（按标签或映射表）
    - 应用商店（按标签或映射表）
    - 华为应用市场（按映射表 + 有密钥）
    """
    logger.info("开始搜索竞品信息...")

    plan = state.get("collection_plan", {})
    competitors = plan.get("competitors", state["competitors"])

    # 初始化采集器
    search_collector = WebSearchCollector(api_key=settings.serpapi_key)
    github_collector = GitHubCollector(token=settings.github_token)
    app_store_collector = AppStoreCollector()
    huawei_collector = HuaweiCollector()

    # 构建所有竞品的采集任务
    comp_tasks = []
    for comp in competitors:
        name = comp if isinstance(comp, str) else comp.get("name", "")
        keywords = [] if isinstance(comp, str) else comp.get("search_keywords", [])
        logger.info(f"搜索竞品: {name}")

        comp_tasks.append(_collect_one(
            name, keywords, plan,
            search_collector, github_collector, app_store_collector, huawei_collector,
        ))

    # 所有竞品并行采集
    comp_results = await asyncio.gather(*comp_tasks, return_exceptions=True)

    # 合并结果
    all_results = []
    for i, result in enumerate(comp_results):
        if isinstance(result, Exception):
            name = competitors[i] if isinstance(competitors[i], str) else competitors[i].get("name", "")
            logger.error(f"竞品 {name} 采集异常: {result}")
            all_results.append({
                "competitor": name,
                "source": "error",
                "data": {},
                "error": str(result),
            })
        else:
            all_results.extend(result)

    logger.info(f"搜索完成，共处理 {len(competitors)} 个竞品，{len(all_results)} 条结果")
    report_progress(state.get("progress_callback"), "searcher")
    return {
        "raw_data": all_results,
        "status": "collecting",
        "errors": state.get("errors", [])
    }
