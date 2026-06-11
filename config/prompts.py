"""
Prompt模板
==========

定义LLM调用的Prompt模板。
"""

# 信息抽取Prompt
EXTRACTION_PROMPT = """
你是一个专业的竞品信息提取专家。请从以下文本中提取结构化的竞品信息。

文本内容：
{content}

请提取以下信息并以JSON格式返回：
{
    "company_name": "公司名称",
    "products": [
        {
            "name": "产品名称",
            "description": "产品描述",
            "features": ["功能1", "功能2"],
            "pricing": {
                "model": "定价模式",
                "tiers": [...]
            }
        }
    ],
    "target_market": "目标市场",
    "key_differentiators": ["差异化点1", "差异化点2"]
}

只返回JSON，不要其他内容。
"""

# SWOT分析Prompt
SWOT_PROMPT = """
基于以下竞品信息，生成SWOT分析。

竞品信息：
{competitor_info}

请按照以下格式输出：

## 优势 (Strengths)
- ...

## 劣势 (Weaknesses)
- ...

## 机会 (Opportunities)
- ...

## 威胁 (Threats)
- ...
"""

# 报告生成Prompt
REPORT_PROMPT = """
你是一个专业的竞品分析师。请基于以下分析结果，生成一份专业的竞品分析报告。

分析数据：
{analysis_data}

报告要求：
1. 结构清晰，逻辑连贯
2. 数据准确，有来源引用
3. 观点明确，有洞察深度
4. 建议具体，可执行

请生成Markdown格式的报告。
"""

# 任务规划Prompt
PLANNING_PROMPT = """
分析任务规划：
- 竞品列表：{competitors}
- 分析类型：{analysis_type}
- 分析维度：{dimensions}

请规划数据采集策略，确定：
1. 每个竞品需要搜索的关键词
2. 需要爬取的URL列表
3. 需要提取的信息类型

返回JSON格式的采集计划。
"""

# 快速报告Prompt
QUICK_REPORT_PROMPT = """
你是一个竞品分析师。请基于以下分析结果，生成一份简洁的竞品快速概览报告。

分析数据：
{analysis_data}

报告要求：
1. 简洁明了，重点突出
2. 包含：公司概览、关键产品、主要差异化、定价摘要
3. 每个部分不超过3-5个要点
4. 适合快速阅读，总长度控制在500字以内

请生成Markdown格式的报告。
"""

# 深度报告Prompt
DEEP_REPORT_PROMPT = """
你是一个资深竞品分析师。请基于以下分析结果，生成一份深度竞品分析报告。

分析数据：
{analysis_data}

报告要求：
1. 结构清晰，逻辑严密
2. 包含：执行摘要、市场分析、竞品详细对比、SWOT分析、趋势分析、竞争格局、战略建议、风险评估
3. 每个部分要有深入分析和数据支撑
4. 观点明确，洞察深刻，建议具体可执行
5. 附上数据来源和参考链接

请生成Markdown格式的报告，总长度建议2000-3000字。
"""

# 问答Prompt
QA_PROMPT = """
基于以下竞品知识库信息，回答用户的问题。

知识库信息：
{context}

用户问题：
{question}

请提供准确、详细的回答，并引用数据来源。
"""
