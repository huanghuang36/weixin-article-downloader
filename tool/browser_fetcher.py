# -*- coding: utf-8 -*-
"""Fetch HTML using Playwright browser automation.

Two modes:
1. CDP mode (default): Connect to user's running Chrome via Chrome DevTools Protocol.
   User opens Chrome, completes any verification, then this tool connects and captures.
2. Standalone mode (fallback): Launch a new Chromium with --auto-detect.
"""

import time
from tool import config as cfg


class BrowserFetchError(Exception):
    """Raised when browser fetching fails."""


def _wait_for_article_content(page) -> bool:
    """Check if the article content element exists on the page."""
    try:
        el = page.query_selector("#js_content")
        return el is not None
    except Exception:
        return False


def _is_verification_page(page) -> bool:
    """Check if the page is a verification/CAPTCHA page."""
    title = page.title()
    if "验证" in title or "verify" in title.lower():
        return True
    try:
        body = page.inner_text("body", timeout=3000)
        if "secitptpage" in body or "验证" in body:
            return True
    except Exception:
        pass
    return False


def _wait_for_content(page, max_wait=cfg.BROWSER_MAX_WAIT, check_interval=cfg.BROWSER_CHECK_INTERVAL) -> bool:
    """Wait for article content to appear. Used for both CDP and standalone modes.

    Args:
        page: Playwright page object.
        max_wait: Maximum seconds to wait.
        check_interval: Seconds between each check.

    Returns:
        True if article content appeared, False if timed out.
    """
    # First check if already loaded
    if _wait_for_article_content(page):
        return True

    elapsed = 0
    while elapsed < max_wait:
        if _wait_for_article_content(page):
            return True
        time.sleep(check_interval)
        elapsed += check_interval
    return False


def _capture_from_cdp(url: str) -> str:
    """Connect to user's Chrome via CDP and capture article content.

    Args:
        url: Article URL to navigate to.

    Returns:
        Full page HTML.

    Raises:
        BrowserFetchError: If connection fails.
    """
    import subprocess
    import sys

    from playwright.sync_api import sync_playwright

    # Check if Chrome is running with remote debugging
    try:
        result = subprocess.run(
            ["lsof", "-i", ":9222", "-sTCP:LISTEN"],
            capture_output=True, text=True, timeout=5,
        )
        chrome_running = result.returncode == 0
    except Exception:
        chrome_running = False

    if not chrome_running:
        print("[BROWSER] Chrome not running with remote debugging on port 9222.")
        print("[BROWSER] Start Chrome with:")
        print(f'  open -a "Google Chrome" --args --remote-debugging-port=9222')
        print("[BROWSER] Then re-run this command.")
        raise BrowserFetchError("Chrome CDP not available")

    # Check if user already has the article page open
    print(f"[BROWSER] Connecting to Chrome on {cfg.BROWSER_CDP_URL}...")

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(cfg.BROWSER_CDP_URL)
            context = browser.contexts[0] if browser.contexts else browser.new_context()

            # Check if any existing tab already has the target page
            target_page = None
            for p in context.pages:
                try:
                    if p.url and url.split("?")[0] in p.url:
                        target_page = p
                        print("[BROWSER] Found article in existing tab.")
                        break
                except Exception:
                    pass

            if target_page is None:
                # Navigate in current tab
                pages = context.pages
                if pages:
                    target_page = pages[0]
                else:
                    target_page = context.new_page()

                print(f"[BROWSER] Navigating to: {url}")
                try:
                    target_page.goto(url, timeout=cfg.BROWSER_TIMEOUT * 1000, wait_until="load")
                except Exception as e:
                    raise BrowserFetchError(f"Failed to navigate to URL: {e}")

            # Wait for content
            if not _wait_for_content(target_page):
                title = target_page.title()
                if _is_verification_page(target_page):
                    print("[BROWSER] Verification page detected.")
                    print("[BROWSER] Please complete the verification in your Chrome browser.")
                    print("[BROWSER] Waiting...")
                    if not _wait_for_content(target_page):
                        raise BrowserFetchError("Timed out waiting for verification. Please try again.")
                else:
                    raise BrowserFetchError(
                        f"Article content did not load after {cfg.BROWSER_MAX_WAIT} seconds."
                    )

            html = target_page.content()
            browser.close()
            return html

    except BrowserFetchError:
        raise
    except Exception as e:
        raise BrowserFetchError(f"CDP connection failed: {e}")


def _launch_standalone(url: str) -> str:
    """Launch a new Chromium instance and capture article content.

    Args:
        url: Article URL.

    Returns:
        Full page HTML.

    Raises:
        BrowserFetchError: If launch or capture fails.
    """
    import tempfile
    import shutil

    from playwright.sync_api import sync_playwright

    user_data_dir = tempfile.mkdtemp(prefix="weixin-browser-")

    try:
        with sync_playwright() as pw:
            browser_ctx = pw.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=cfg.BROWSER_HEADLESS,
                user_agent=cfg.USER_AGENT,
                viewport={"width": 375, "height": 812},
                locale="zh-CN",
            )
            page = browser_ctx.pages[0]

            print(f"[BROWSER] Navigating to: {url}")
            try:
                page.goto(url, timeout=cfg.BROWSER_TIMEOUT * 1000, wait_until="load")
            except Exception as e:
                raise BrowserFetchError(f"Failed to navigate to URL: {e}")

            if not _wait_for_content(page):
                if _is_verification_page(page):
                    if cfg.BROWSER_HEADLESS:
                        raise BrowserFetchError(
                            "Verification page detected in headless mode. "
                            "Set BROWSER_HEADLESS=False to complete verification."
                        )
                    print("[BROWSER] Verification detected. Please complete in the browser window.")
                    if not _wait_for_content(page):
                        raise BrowserFetchError("Timed out waiting for verification.")
                else:
                    raise BrowserFetchError("Article content did not load.")

            html = page.content()
            browser_ctx.close()
            return html

    finally:
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception:
            pass


def fetch_html_browser(url: str) -> str:
    """Fetch article HTML using Playwright browser.

    Tries CDP mode first (connect to user's running Chrome), falls back to
    standalone Chromium if CDP is not available.

    Args:
        url: The article URL.

    Returns:
        The full page HTML content.

    Raises:
        BrowserFetchError: If all fetch methods fail.
    """
    try:
        return _capture_from_cdp(url)
    except BrowserFetchError as e:
        print(f"[BROWSER] CDP mode unavailable: {e}")
        print("[BROWSER] Falling back to standalone Chromium launch...")
        return _launch_standalone(url)
