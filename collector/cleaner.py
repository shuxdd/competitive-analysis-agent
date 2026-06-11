"""
数据清洗工具
============

清洗和预处理采集的数据。
"""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # 移除特殊字符
        text = re.sub(r'[^\S\n]+', ' ', text)

        return text.strip()

    @staticmethod
    def extract_price(text: str) -> List[Dict[str, Any]]:
        """
        提取价格信息

        Args:
            text: 文本

        Returns:
            价格信息列表
        """
        prices = []

        # 匹配各种价格格式
        patterns = [
            (r'[¥￥]\s*(\d+(?:\.\d{2})?)', 'CNY'),  # ¥99, ￥99
            (r'\$\s*(\d+(?:\.\d{2})?)', 'USD'),       # $99
            (r'€\s*(\d+(?:\.\d{2})?)', 'EUR'),        # €99
            (r'£\s*(\d+(?:\.\d{2})?)', 'GBP'),        # £99
            (r'(\d+(?:\.\d{2})?)\s*元', 'CNY'),       # 99元
            (r'(\d+(?:\.\d{2})?)\s*円', 'JPY'),       # 99円
            (r'(\d+(?:\.\d{2})?)\s*美元', 'USD'),     # 99美元
            (r'(\d+(?:\.\d{2})?)\s*人民币', 'CNY'),   # 99人民币
        ]

        seen_prices = set()
        for pattern, currency in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                price = float(match.group(1))
                if price not in seen_prices:
                    seen_prices.add(price)
                    context = text[max(0, match.start() - 50):match.end() + 50]
                    prices.append({
                        "price": price,
                        "currency": currency,
                        "context": context.strip()
                    })

        return prices

    @staticmethod
    def _detect_currency(text: str) -> str:
        """检测货币类型"""
        if '¥' in text or '元' in text or '人民币' in text:
            return 'CNY'
        elif '$' in text or '美元' in text:
            return 'USD'
        elif '€' in text:
            return 'EUR'
        elif '£' in text:
            return 'GBP'
        elif '円' in text:
            return 'JPY'
        return 'UNKNOWN'

    @staticmethod
    def extract_features(text: str) -> List[str]:
        """
        提取功能特性

        Args:
            text: 文本

        Returns:
            功能列表
        """
        features = []

        # 功能关键词模式
        feature_patterns = [
            r'支持([^，。,.\n]+)',
            r'提供([^，。,.\n]+)',
            r'具备([^，。,.\n]+)',
            r'拥有([^，。,.\n]+)',
            r'功能[：:]([^，。,.\n]+)',
            r'特性[：:]([^，。,.\n]+)',
        ]

        for pattern in feature_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                feature = match.group(1).strip()
                if len(feature) > 2 and len(feature) < 50:
                    features.append(feature)

        # 去重
        return list(set(features))[:20]

    @staticmethod
    def extract_company_info(text: str) -> Dict[str, Any]:
        """
        提取公司信息

        Args:
            text: 文本

        Returns:
            公司信息
        """
        info = {}

        # 成立时间
        founded_patterns = [
            r'成立于\s*(\d{4})\s*年',
            r'创立于\s*(\d{4})\s*年',
            r'(\d{4})\s*年\s*成立',
            r'founded\s*in\s*(\d{4})',
        ]
        for pattern in founded_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['founded'] = match.group(1)
                break

        # 公司地点
        location_patterns = [
            r'总部[位于设在]*([^，。,.\n]+)',
            r'位于([^，。,.\n]+)',
            r'坐落在([^，。,.\n]+)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['location'] = match.group(1).strip()
                break

        # 融资信息
        funding_patterns = [
            r'融资([^，。,.\n]+)',
            r'获得([^，。,.\n]*投资[^，。,.\n]*)',
            r'估值([^，。,.\n]+)',
        ]
        for pattern in funding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['funding'] = match.group(0).strip()
                break

        # 员工规模
        employee_patterns = [
            r'员工[^，。,.\n]*(\d+[^，。,.\n]*人)',
            r'团队[^，。,.\n]*(\d+[^，。,.\n]*人)',
            r'(\d+\s*[-–]\s*\d+\s*人)',
        ]
        for pattern in employee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['employees'] = match.group(1).strip()
                break

        return info

    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Any]:
        """
        提取联系信息

        Args:
            text: 文本

        Returns:
            联系信息
        """
        info = {}

        # 邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            info['emails'] = list(set(emails))[:5]

        # 电话
        phone_patterns = [
            r'(\+?86)?1[3-9]\d{9}',  # 中国手机号
            r'(\d{3,4}[-\s]?\d{7,8})',  # 座机
            r'(\+\d{1,3}[-\s]?\d{4,14})',  # 国际电话
        ]
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        if phones:
            info['phones'] = list(set(phones))[:5]

        # 网站
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        if urls:
            info['websites'] = list(set(urls))[:5]

        return info

    @staticmethod
    def merge_data(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并多个数据源

        Args:
            data_list: 数据列表

        Returns:
            合并后的数据
        """
        merged = {
            "texts": [],
            "prices": [],
            "features": [],
            "company_info": {},
            "contact_info": {},
            "sources": []
        }

        for data in data_list:
            if not data:
                continue

            # 合并文本
            if "text" in data:
                merged["texts"].append(data["text"])

            # 合并价格
            if "prices" in data:
                merged["prices"].extend(data["prices"])

            # 合并功能
            if "features" in data:
                merged["features"].extend(data["features"])

            # 合并公司信息
            if "company_info" in data:
                for key, value in data["company_info"].items():
                    if key not in merged["company_info"] or not merged["company_info"][key]:
                        merged["company_info"][key] = value

            # 合并联系信息
            if "contact_info" in data:
                for key, value in data["contact_info"].items():
                    if key not in merged["contact_info"]:
                        merged["contact_info"][key] = []
                    merged["contact_info"][key].extend(value)

            # 记录来源
            if "url" in data:
                merged["sources"].append(data["url"])

        # 去重
        merged["features"] = list(set(merged["features"]))
        merged["sources"] = list(set(merged["sources"]))

        # 合并文本
        merged["combined_text"] = "\n\n".join(merged["texts"][:10])

        return merged
