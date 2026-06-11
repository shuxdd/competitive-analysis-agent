"""
信息提取节点
============

使用LLM从爬取的网页中提取结构化竞品信息。
"""

import json
import logging
from agent.graph_state import AgentState
from agent.llm import create_llm
from config.prompts import EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


async def extract_info(state: AgentState) -> dict:
    """
    信息提取节点

    对爬取的网页内容使用LLM提取结构化信息。
    """
    logger.info("开始信息提取...")

    raw_data = state.get("raw_data", [])
    extracted = []

    try:
        llm = create_llm(temperature=0.1)

        for entry in raw_data:
            if entry.get("source") != "web_scrape":
                continue

            text = entry.get("text", "")
            if not text or len(text) < 50:
                continue

            competitor = entry.get("competitor", "")
            url = entry.get("url", "")

            logger.info(f"  提取: {competitor} - {url}")

            try:
                # 截断文本以控制token量
                truncated_text = text[:4000]

                prompt = EXTRACTION_PROMPT.format(content=truncated_text)
                response = await llm.ainvoke(prompt)
                content = response.content

                # 解析JSON响应
                try:
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_str = content.split("```")[1].split("```")[0].strip()
                    else:
                        json_str = content.strip()

                    info = json.loads(json_str)
                except json.JSONDecodeError:
                    info = {"raw_response": content}

                extracted.append({
                    "competitor": competitor,
                    "source_url": url,
                    "extracted_info": info
                })

                logger.info(f"    提取成功: {info.get('company_name', '未知')}")

            except Exception as e:
                logger.warning(f"    提取失败: {e}")
                extracted.append({
                    "competitor": competitor,
                    "source_url": url,
                    "extracted_info": {},
                    "error": str(e)
                })

        logger.info(f"信息提取完成，共处理 {len(extracted)} 个页面")
        return {
            "extracted_info": extracted,
            "status": "extracting",
            "errors": state.get("errors", [])
        }

    except Exception as e:
        logger.error(f"信息提取节点失败: {e}")
        return {
            "extracted_info": extracted,
            "status": "extracting",
            "errors": state.get("errors", []) + [f"提取节点错误: {str(e)}"]
        }
