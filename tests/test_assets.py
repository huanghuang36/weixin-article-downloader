import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tool.assets import AssetDownloader


class TestAssetDownloader(unittest.TestCase):

    def setUp(self):
        self.output_dir = "/tmp/test_assets"

    @patch("tool.assets.requests.get")
    @patch("tool.assets.time.sleep")
    def test_download_image(self, mock_sleep, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"fake image data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        downloader = AssetDownloader(self.output_dir)
        result = downloader.download_image("https://example.com/photo.png", 1)
        self.assertEqual(result, "images/img_001.png")
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "images/img_001.png")))

    @patch("tool.assets.requests.get")
    def test_download_image_skips_on_failure(self, mock_get):
        mock_get.side_effect = Exception("download failed")

        downloader = AssetDownloader(self.output_dir)
        result = downloader.download_image("https://example.com/photo.png", 1)
        self.assertEqual(result, "https://example.com/photo.png")

    def tearDown(self):
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)


if __name__ == "__main__":
    unittest.main()
