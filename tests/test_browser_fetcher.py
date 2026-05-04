# -*- coding: utf-8 -*-
"""Test browser_fetcher module."""
import unittest
from unittest.mock import MagicMock, patch


class TestVerificationDetection(unittest.TestCase):

    def test_is_verification_page_by_title(self):
        """Test that pages with '验证' in title are detected."""
        from tool.browser_fetcher import _is_verification_page
        page = MagicMock()
        page.title.return_value = "微信安全验证"
        page.inner_text.side_effect = Exception("no body")
        self.assertTrue(_is_verification_page(page))

    def test_is_not_verification_page(self):
        """Test that normal article pages are not flagged."""
        from tool.browser_fetcher import _is_verification_page
        page = MagicMock()
        page.title.return_value = "来自微软资深工程师Koshy John的建议"
        page.inner_text.return_value = "这是一篇正常的文章内容"
        self.assertFalse(_is_verification_page(page))


class TestWaitForArticleContent(unittest.TestCase):

    def test_content_exists(self):
        """Test detection when #js_content is present."""
        from tool.browser_fetcher import _wait_for_article_content
        page = MagicMock()
        page.query_selector.return_value = MagicMock()  # element found
        self.assertTrue(_wait_for_article_content(page))

    def test_content_missing(self):
        """Test detection when #js_content is not present."""
        from tool.browser_fetcher import _wait_for_article_content
        page = MagicMock()
        page.query_selector.return_value = None  # element not found
        self.assertFalse(_wait_for_article_content(page))


if __name__ == "__main__":
    unittest.main()
