# tests/test_markdown_writer.py
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tool.markdown_writer import MarkdownWriter


class TestMarkdownWriter(unittest.TestCase):

    def setUp(self):
        self.output_dir = "/tmp/test_md_writer"

    def tearDown(self):
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_generate_basic(self):
        writer = MarkdownWriter(
            title="Test Article",
            author="Author Name",
            publish_time="2024-01-01",
            cover_image="images/cover.png",
            content_md="Hello **world**\n\n![img](images/img_001.png)",
            image_map={"img_001.png": "images/img_001.png"},
            video_embeds=[],
            output_dir=self.output_dir,
        )
        filepath = writer.generate()

        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            content = f.read()
        self.assertIn("# Test Article", content)
        self.assertIn("Author Name", content)
        self.assertIn("2024-01-01", content)
        self.assertIn("Hello **world**", content)

    def test_generate_with_video_embed(self):
        writer = MarkdownWriter(
            title="Video Test",
            author="",
            publish_time="",
            cover_image="",
            content_md="Some text",
            image_map={},
            video_embeds=["[Video 1](https://v.qq.com/xxx)"],
            output_dir=self.output_dir,
        )
        filepath = writer.generate()

        with open(filepath) as f:
            content = f.read()
        self.assertIn("[Video 1](https://v.qq.com/xxx)", content)


if __name__ == "__main__":
    unittest.main()
