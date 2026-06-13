"""
搜索节点
========

使用搜索引擎、GitHub 等多数据源并行采集竞品信息。
数据源配置优先从 `competitors_meta` 中读取（由 API 层从数据库传递），
兼容无数据库场景（通过 tags 关键字触发）。
"""

import asyncio
import logging
from agent.graph_state import AgentState
from collector.web_search import WebSearchCollector
from collector.github_collector import GitHubCollector
from collector.apify_collector import ApifyCollector
from config.settings import settings
from utils.retry import retry_async
from agent.progress import report_progress

logger = logging.getLogger(__name__)

# 标签到数据源的映射（作为降级方案）
TAG_DATA_SOURCES = {
    "开源": ["github"],
    "开发者工具": ["github"],
    "GitHub": ["github"],
    "移动端": ["google_play", "app_store"],
    "移动应用": ["google_play", "app_store"],
    "iOS": ["app_store"],
    "Android": ["google_play"],
}


def _get_extra_sources(competitor_name: str, plan: dict) -> list:
    """根据竞品标签决定额外数据源"""
    sources = []
    competitors_meta = plan.get("competitors_meta", {})
    meta = competitors_meta.get(competitor_name, {})
    # 1. 从 competitors_meta 中读取显式配置
    if meta.get("google_play_id"):
        sources.append("google_play")
    if meta.get("app_store_id"):
        sources.append("app_store")
    if meta.get("github_repo"):
        sources.append("github")
    # 2. 从标签推断（降级）
    if not sources:
        tags = meta.get("tags", [])
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
    apify_collector: ApifyCollector,
) -> list:
    """
    采集单个竞品的所有数据源（并行执行）

    Returns:
        该竞品的所有采集结果列表
    """
    name_lower = name.lower()
    extra_sources = _get_extra_sources(name, plan)
    # 从 competitors_meta 读取显式配置
    competitors_meta = plan.get("competitors_meta", {})
    meta = competitors_meta.get(name, {})
    google_play_id = meta.get("google_play_id") or None
    app_store_id = meta.get("app_store_id") or None
    github_repo = meta.get("github_repo") or None
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
    if "github" in extra_sources and github_repo:
        async def _gh(rn=github_repo):
            try:
                result = await github_collector.run(rn)
                logger.info(f"  [{name}] GitHub 完成: ⭐{result.get('data', {}).get('stars', 0)}")
                return {"competitor": name, "source": "github", "data": result.get("data", {})}
            except Exception as e:
                logger.warning(f"  [{name}] GitHub 失败: {e}")
                return None
        tasks.append(_gh())

    # 3. Google Play（按需）
    if "google_play" in extra_sources and google_play_id:
        async def _gp(aid=google_play_id):
            try:
                result = await apify_collector.run(aid, store="google")
                logger.info(f"  [{name}] Google Play 完成: ⭐{result.get('data', {}).get('rating', 0)}")
                return {"competitor": name, "source": "google_play", "data": result.get("data", {})}
            except Exception as e:
                logger.warning(f"  [{name}] Google Play 失败: {e}")
                return None
        tasks.append(_gp())

    # 4. App Store（按需）
    if "app_store" in extra_sources and app_store_id:
        async def _as(aid=app_store_id):
            try:
                result = await apify_collector.run(aid, store="apple")
                logger.info(f"  [{name}] App Store 完成: ⭐{result.get('data', {}).get('rating', 0)}")
                return {"competitor": name, "source": "app_store", "data": result.get("data", {})}
            except Exception as e:
                logger.warning(f"  [{name}] App Store 失败: {e}")
                return None
        tasks.append(_as())

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
    """
    logger.info("开始搜索竞品信息...")

    # 检查 SerpAPI 配置
    if not settings.serpapi_key:
        msg = "未配置 SerpAPI 密钥，搜索功能不可用。请在 .env 中设置 SERPAPI_KEY。"
        logger.warning(msg)
        return {
            "raw_data": [],
            "status": "collecting",
            "errors": state.get("errors", []) + [msg],
        }

    plan = state.get("collection_plan", {})
    competitors = plan.get("competitors", state["competitors"])

    # 初始化采集器
    search_collector = WebSearchCollector(api_key=settings.serpapi_key)
    github_collector = GitHubCollector(token=settings.github_token)
    apify_collector = ApifyCollector()

    # 构建所有竞品的采集任务
    comp_tasks = []
    for comp in competitors:
        name = comp if isinstance(comp, str) else comp.get("name", "")
        keywords = [] if isinstance(comp, str) else comp.get("search_keywords", [])
        logger.info(f"搜索竞品: {name}")

        comp_tasks.append(_collect_one(
            name, keywords, plan,
            search_collector, github_collector, apify_collector,
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
