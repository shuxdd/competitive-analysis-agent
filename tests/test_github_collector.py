"""
GitHub 采集器测试
================
"""

import pytest
from collector.github_collector import GitHubCollector


class TestGitHubCollector:
    """GitHub 采集器测试"""

    def test_initialization(self):
        """测试初始化"""
        collector = GitHubCollector(token="test_token")
        assert collector.name == "github"
        assert collector.token == "test_token"

    def test_initialization_no_token(self):
        """测试无 token 初始化"""
        collector = GitHubCollector()
        assert collector.token is None

    def test_parse_repo_data(self):
        """测试解析仓库数据"""
        collector = GitHubCollector()

        raw_data = {
            "full_name": "notionhq/notion-sdk-js",
            "description": "Official Notion SDK for JavaScript",
            "stars": 12500,
            "forks": 800,
            "open_issues": 45,
            "language": "TypeScript",
            "license": "MIT",
            "created_at": "2020-05-01T00:00:00Z",
            "updated_at": "2026-06-10T00:00:00Z",
            "pushed_at": "2026-06-10T00:00:00Z",
            "default_branch": "main",
            "topics": ["notion", "sdk", "javascript"],
            "homepage": "https://notion.so",
        }

        result = collector.parse(raw_data)

        assert result["repo"] == "notionhq/notion-sdk-js"
        assert result["stars"] == 12500
        assert result["forks"] == 800
        assert result["language"] == "TypeScript"
        assert result["license"] == "MIT"
        assert result["topics"] == ["notion", "sdk", "javascript"]

    def test_parse_empty_data(self):
        """测试解析空数据"""
        collector = GitHubCollector()
        result = collector.parse({})
        assert result["repo"] == ""
        assert result["stars"] == 0

    def test_clean_removes_none(self):
        """测试清洗去除 None 值"""
        collector = GitHubCollector()
        data = {
            "repo": "test/repo",
            "stars": 100,
            "license": None,
            "topics": None,
            "homepage": "",
        }
        cleaned = collector.clean(data)
        assert cleaned["repo"] == "test/repo"
        assert cleaned["stars"] == 100
        assert "license" not in cleaned
        assert "topics" not in cleaned
        assert "homepage" not in cleaned

    def test_parse_error_data(self):
        """测试解析错误数据"""
        collector = GitHubCollector()
        raw_data = {"full_name": "test/repo", "error": "not found", "status": "error"}
        result = collector.parse(raw_data)
        assert result["status"] == "error"
