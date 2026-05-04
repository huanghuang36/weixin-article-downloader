# tests/test_parser.py
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tool.parser import ArticleParser, ParseError, sanitize_title


class TestArticleParser(unittest.TestCase):

    def test_extract_title(self):
        html = '<html><h1 id="activity-name">Test Article</h1>' \
               '<div id="js_content"><p>Hello <strong>world</strong></p></div></html>'
        parser = ArticleParser(html)
        self.assertEqual(parser.title, "Test Article")

    def test_extract_content(self):
        html = '<div id="js_content"><p>Hello <strong>world</strong></p></div>'
        parser = ArticleParser(html)
        content = parser.parse()
        self.assertIn("Hello **world**", content)

    def test_extract_images(self):
        html = '<div id="js_content">' \
               '<img data-src="https://example.com/img1.png" />' \
               '<img data-src="https://example.com/img2.png" />' \
               '</div>'
        parser = ArticleParser(html)
        parser.parse()
        self.assertEqual(len(parser.image_urls), 2)
        self.assertEqual(parser.image_urls[0], "https://example.com/img1.png")

    def test_extract_video_iframe(self):
        html = '<div id="js_content">' \
               '<iframe class="video_iframe" src="https://v.qq.com/xxx"></iframe>' \
               '</div>'
        parser = ArticleParser(html)
        parser.parse()
        self.assertEqual(len(parser.video_urls), 1)

    def test_parse_error_no_content(self):
        html = "<html><body>no article content</body></html>"
        with self.assertRaises(ParseError):
            ArticleParser(html)

    def test_sanitize_title(self):
        self.assertEqual(sanitize_title("Hello!@# World"), "Hello World")
        self.assertEqual(sanitize_title("测试文章"), "测试文章")
        long_title = "A" * 100
        self.assertEqual(len(sanitize_title(long_title)), 50)


if __name__ == "__main__":
    unittest.main()
