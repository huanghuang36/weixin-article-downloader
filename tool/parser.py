# -*- coding: utf-8 -*-
"""Parse WeChat article HTML and extract text, images, videos."""

import re
from bs4 import BeautifulSoup, Tag
from tool import config as cfg


class ParseError(Exception):
    """Raised when parsing fails."""


def sanitize_title(title: str) -> str:
    """Sanitize article title for use as directory name.

    - Keep only Chinese, English, digits, spaces, hyphens
    - Truncate to MAX_TITLE_LENGTH
    """
    cleaned = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9 \-]", "", title).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if len(cleaned) > cfg.MAX_TITLE_LENGTH:
        cleaned = cleaned[:cfg.MAX_TITLE_LENGTH]
    return cleaned or "untitled"


class ArticleParser:
    """Parse WeChat article HTML and extract structured content."""

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "lxml")
        self.title = self._extract_title()
        self.author = self._extract_author()
        self.publish_time = self._extract_publish_time()
        self.cover_image = self._extract_cover_image()
        self.image_urls = []
        self.video_urls = []
        self.content_md = self.parse()

    def _extract_title(self) -> str:
        el = self.soup.find(id="activity-name")
        if el:
            return el.get_text(strip=True)
        return "untitled"

    def _extract_author(self) -> str:
        el = self.soup.find(id="js_name")
        if el:
            return el.get_text(strip=True)
        for cls in ["rich_media_meta_primary", "profile_nickname"]:
            el = self.soup.find(class_=cls)
            if el:
                return el.get_text(strip=True)
        return ""

    def _extract_publish_time(self) -> str:
        el = self.soup.find(id="publish_time")
        if el:
            return el.get_text(strip=True)
        return ""

    def _extract_cover_image(self) -> str:
        el = self.soup.find(id="js_cover")
        if el:
            img = el.find("img")
            if img:
                return img.get("data-src") or img.get("src") or ""
        content = self.soup.find(id="js_content")
        if content:
            img = content.find("img")
            if img:
                return img.get("data-src") or img.get("src") or ""
        return ""

    def _should_skip_image(self, img_tag: Tag) -> bool:
        src = img_tag.get("data-src") or img_tag.get("src") or ""
        for keyword in cfg.BLOCKED_IMG_KEYWORDS:
            if keyword in src.lower():
                return True
        width = img_tag.get("width") or img_tag.get("data-width")
        height = img_tag.get("height") or img_tag.get("data-height")
        if width is not None and height is not None:
            try:
                if int(width) <= 1 and int(height) <= 1:
                    return True
            except (ValueError, TypeError):
                pass
        return False

    def _process_node(self, node) -> str:
        if isinstance(node, str):
            return node
        if not isinstance(node, Tag):
            return ""
        tag_name = node.name or ""
        if tag_name in ("script", "style", "link", "meta"):
            return ""

        if tag_name == "img":
            if self._should_skip_image(node):
                return ""
            src = node.get("data-src") or node.get("src") or ""
            if not src:
                return ""
            alt = node.get("alt") or ""
            idx = len(self.image_urls) + 1
            self.image_urls.append(src)
            return f"\n![{alt}](images/img_{idx:03d}.png)\n"

        if tag_name == "iframe" and "video_iframe" in (node.get("class") or []):
            src = node.get("src") or ""
            if src:
                idx = len(self.video_urls) + 1
                self.video_urls.append(src)
                return f"\n[Video {idx}]({src})\n"

        if tag_name == "mp-common-video":
            src = node.get("src") or ""
            if src:
                idx = len(self.video_urls) + 1
                self.video_urls.append(src)
                return f"\n[Video {idx}]({src})\n"

        if tag_name == "a":
            href = node.get("href") or ""
            inner = "".join(self._process_node(c) for c in node.children)
            if href and not href.startswith("javascript:"):
                return f"[{inner.strip()}]({href})"
            return inner.strip()

        if tag_name in ("strong", "b"):
            inner = "".join(self._process_node(c) for c in node.children)
            return f"**{inner.strip()}**" if inner.strip() else ""

        if tag_name in ("em", "i"):
            inner = "".join(self._process_node(c) for c in node.children)
            return f"*{inner.strip()}*" if inner.strip() else ""

        if tag_name == "code":
            return f"`{node.get_text()}`"

        if tag_name == "br":
            return "\n"

        if tag_name in ("p", "section", "div"):
            inner = "".join(self._process_node(c) for c in node.children)
            text = inner.strip()
            if not text:
                return ""
            if node.get("class") and "blockquote" in " ".join(node.get("class")):
                lines = text.split("\n")
                return "\n" + "\n".join(f"> {l}" for l in lines) + "\n"
            return "\n\n" + text + "\n\n"

        return "".join(self._process_node(c) for c in node.children)

    def parse(self) -> str:
        content_div = self.soup.find(id="js_content")
        if not content_div:
            raise ParseError("Cannot find article content (js_content not found)")

        self.image_urls = []
        self.video_urls = []
        parts = []
        for child in content_div.children:
            md = self._process_node(child)
            if md.strip():
                parts.append(md)

        self.content_md = "\n".join(parts)
        self.content_md = re.sub(r"\n{3,}", "\n\n", self.content_md)
        return self.content_md
