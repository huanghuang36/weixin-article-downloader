# tests/test_e2e.py
"""End-to-end test using mocked HTTP responses."""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tool.parser import ArticleParser, sanitize_title


SAMPLE_HTML = """
<html>
<head><title>Test</title></head>
<body>
<h1 id="activity-name">测试文章标题</h1>
<span id="js_name">测试作者</span>
<span id="publish_time">2024-01-15</span>
<div id="js_content">
<p>这是第一段文字。</p>
<p><strong>加粗文本</strong>和<em>斜体文本</em></p>
<p><img data-src="https://example.com/test.png" alt="test image" /></p>
<p>带<a href="https://example.com">链接</a>的段落</p>
</div>
</body>
</html>
"""


class TestE2E(unittest.TestCase):

    def test_full_pipeline_mock(self):
        """Test full parse + write pipeline with sample HTML."""
        parser = ArticleParser(SAMPLE_HTML)
        content = parser.parse()

        self.assertEqual(parser.title, "测试文章标题")
        self.assertEqual(parser.author, "测试作者")
        self.assertEqual(parser.publish_time, "2024-01-15")
        self.assertEqual(len(parser.image_urls), 1)
        self.assertIn("这是第一段文字", content)
        self.assertIn("**加粗文本**", content)
        self.assertIn("*斜体文本*", content)
        self.assertIn("[链接](https://example.com)", content)

    def test_sanitize_title_edge_cases(self):
        self.assertEqual(sanitize_title("Hello!@#$%^&*World"), "HelloWorld")
        self.assertEqual(sanitize_title("   spaces   "), "spaces")
        self.assertEqual(sanitize_title("a" * 200), "a" * 50)
        self.assertEqual(sanitize_title(""), "untitled")


if __name__ == "__main__":
    unittest.main()
