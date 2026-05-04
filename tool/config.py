# -*- coding: utf-8 -*-
"""Configuration constants for WeChat article downloader."""

# HTTP settings
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1"
)
REFERER = "https://mp.weixin.qq.com/"
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Download settings
IMAGE_DOWNLOAD_DELAY_MIN = 0.5  # seconds
IMAGE_DOWNLOAD_DELAY_MAX = 1.0

# Output settings
MAX_TITLE_LENGTH = 50
DEFAULT_OUTPUT_DIR = "./output"

# Filter out decorative gifs/spacers
BLOCKED_IMG_KEYWORDS = ["wx_ani", "mmbiz_gif", "spacer", "loading"]

# Browser settings (--browser mode)
BROWSER_TIMEOUT = 60  # seconds for page load
BROWSER_CHECK_INTERVAL = 2  # seconds between content checks
BROWSER_MAX_WAIT = 300  # max seconds to wait for user verification
BROWSER_HEADLESS = False  # default to visible browser for verification
BROWSER_CDP_URL = "http://127.0.0.1:9222"  # Chrome DevTools Protocol endpoint
