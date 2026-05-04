# -*- coding: utf-8 -*-
"""Fetch HTML content from WeChat article URLs."""

import re
import time
import requests
from tool import config as cfg


class FetchError(Exception):
    """Raised when fetching HTML fails."""


URL_PATTERN = re.compile(r"^https://mp\.weixin\.qq\.com/s[/\?]")


def fetch_html(url: str) -> str:
    """Fetch HTML from a WeChat article URL.

    Args:
        url: The article URL (must start with https://mp.weixin.qq.com/s/)

    Returns:
        The HTML content as a string.

    Raises:
        FetchError: If URL is invalid or request fails after retries.
    """
    if not URL_PATTERN.match(url):
        raise FetchError(f"Invalid WeChat article URL: {url}")

    headers = {
        "User-Agent": cfg.USER_AGENT,
        "Referer": cfg.REFERER,
    }

    last_error = None
    for attempt in range(cfg.MAX_RETRIES):
        try:
            resp = requests.get(url, headers=headers, timeout=cfg.TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < cfg.MAX_RETRIES - 1:
                time.sleep(cfg.RETRY_DELAY)

    raise FetchError(f"Failed to fetch after {cfg.MAX_RETRIES} retries: {last_error}")
