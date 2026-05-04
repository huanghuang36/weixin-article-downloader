# -*- coding: utf-8 -*-
"""Download assets (images, videos) from URLs."""

import os
import time
import random
import requests
from tool import config as cfg


class AssetDownloader:
    """Download and save assets to local directories."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        self.videos_dir = os.path.join(output_dir, "videos")
        os.makedirs(self.images_dir, exist_ok=True)

    def download_image(self, url: str, index: int) -> str:
        filename = f"img_{index:03d}.png"
        filepath = os.path.join(self.images_dir, filename)
        relative_path = f"images/{filename}"

        try:
            resp = requests.get(url, timeout=cfg.TIMEOUT)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            time.sleep(random.uniform(cfg.IMAGE_DOWNLOAD_DELAY_MIN, cfg.IMAGE_DOWNLOAD_DELAY_MAX))
            return relative_path
        except Exception as e:
            print(f"[WARN] Failed to download image: {url} ({e})")
            return url

    def ensure_video_dir(self) -> str:
        os.makedirs(self.videos_dir, exist_ok=True)
        return self.videos_dir

    def download_video(self, url: str, index: int) -> str:
        try:
            import yt_dlp
        except ImportError:
            print("[WARN] yt-dlp not installed. Skipping video download.")
            return url

        self.ensure_video_dir()
        ydl_opts = {
            "outtmpl": os.path.join(self.videos_dir, "video_%(index)03d.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return f"videos/video_{index:03d}.mp4"
        except Exception as e:
            print(f"[WARN] Failed to download video: {url} ({e})")
            return url
