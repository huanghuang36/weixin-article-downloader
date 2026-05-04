#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WeChat Article to Markdown -- CLI entry point.

Usage:
    python main.py <URL> [-o output_dir] [--download-video] [--browser]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool.fetcher import fetch_html, FetchError
from tool.browser_fetcher import fetch_html_browser, BrowserFetchError
from tool.parser import ArticleParser, ParseError, sanitize_title
from tool.assets import AssetDownloader
from tool.markdown_writer import MarkdownWriter


def make_output_dir(base_dir: str, title: str) -> str:
    """Create a unique output directory for the article."""
    safe_name = sanitize_title(title)
    dir_path = os.path.join(base_dir, safe_name)

    counter = 1
    while os.path.exists(dir_path):
        dir_path = os.path.join(base_dir, f"{safe_name}_{counter}")
        counter += 1

    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def main():
    parser = argparse.ArgumentParser(
        description="Download a WeChat official account article to Markdown."
    )
    parser.add_argument("url", help="WeChat article URL (https://mp.weixin.qq.com/s/...)")
    parser.add_argument("-o", "--output", default="./output", help="Output directory (default: ./output)")
    parser.add_argument("--download-video", action="store_true", help="Try to download videos locally")
    parser.add_argument("--browser", action="store_true", help="Use browser mode (Playwright) to bypass anti-crawl")
    args = parser.parse_args()

    # Fetch article HTML
    print(f"[INFO] Fetching article: {args.url}")
    if args.browser:
        print("[INFO] Mode: browser (Playwright)")
        try:
            html = fetch_html_browser(args.url)
        except BrowserFetchError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[INFO] Mode: HTTP (requests)")
        try:
            html = fetch_html(args.url)
        except FetchError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    print("[INFO] Parsing content...")
    try:
        article = ArticleParser(html)
        article.parse()
    except ParseError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Title: {article.title}")
    print(f"[INFO] Author: {article.author or '(unknown)'}")
    print(f"[INFO] Images found: {len(article.image_urls)}")
    print(f"[INFO] Videos found: {len(article.video_urls)}")

    # Create output directory
    output_dir = make_output_dir(args.output, article.title)
    print(f"[INFO] Output directory: {output_dir}")

    # Download images
    asset_downloader = AssetDownloader(output_dir)
    image_map = {}
    for i, url in enumerate(article.image_urls, 1):
        print(f"[INFO] Downloading image {i}/{len(article.image_urls)}")
        local_path = asset_downloader.download_image(url, i)
        filename = f"img_{i:03d}.png"
        image_map[filename] = local_path

    # Replace image URLs in content with local paths
    content = article.content_md
    for i, (url, local_path) in enumerate(zip(article.image_urls, image_map.values()), 1):
        if local_path != url:
            content = content.replace(url, local_path)

    # Download videos (optional)
    video_embeds = []
    if args.download_video and article.video_urls:
        for i, url in enumerate(article.video_urls, 1):
            print(f"[INFO] Downloading video {i}/{len(article.video_urls)}")
            result = asset_downloader.download_video(url, i)
            video_embeds.append(result)
    else:
        video_embeds = [f"[Video {i}]({url})" for i, url in enumerate(article.video_urls, 1)]

    # Generate Markdown
    writer = MarkdownWriter(
        title=article.title,
        author=article.author,
        publish_time=article.publish_time,
        cover_image=article.cover_image,
        content_md=content,
        image_map=image_map,
        video_embeds=video_embeds,
        output_dir=output_dir,
    )
    filepath = writer.generate()

    print(f"[DONE] Article saved to: {filepath}")


if __name__ == "__main__":
    main()
