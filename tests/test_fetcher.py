# tests/test_fetcher.py
import sys
import os
import unittest
from unittest.mock import patch
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tool.fetcher import fetch_html, FetchError


class TestFetchHtml(unittest.TestCase):

    @patch("tool.fetcher.requests.get")
    def test_returns_html_on_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body>test</body></html>"
        html = fetch_html("https://mp.weixin.qq.com/s/abc123")
        self.assertEqual(html, "<html><body>test</body></html>")

    @patch("tool.fetcher.requests.get")
    def test_raises_on_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("connection error")
        with self.assertRaises(FetchError):
            fetch_html("https://mp.weixin.qq.com/s/abc123")

    def test_raises_on_invalid_url(self):
        with self.assertRaises(FetchError):
            fetch_html("not-a-url")


if __name__ == "__main__":
    unittest.main()
