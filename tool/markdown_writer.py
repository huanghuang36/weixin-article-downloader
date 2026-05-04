# -*- coding: utf-8 -*-
"""Generate Markdown document from parsed content."""

import os
from datetime import datetime


class MarkdownWriter:
    """Generate Markdown file from parsed article data."""

    def __init__(
        self,
        title: str,
        author: str,
        publish_time: str,
        cover_image: str,
        content_md: str,
        image_map: dict,
        video_embeds: list,
        output_dir: str,
    ):
        self.title = title
        self.author = author
        self.publish_time = publish_time
        self.cover_image = cover_image
        self.content_md = content_md
        self.image_map = image_map
        self.video_embeds = video_embeds
        self.output_dir = output_dir

    def _build_header(self) -> str:
        parts = [f"# {self.title}\n"]

        meta_parts = []
        if self.author:
            meta_parts.append(f"作者：{self.author}")
        if self.publish_time:
            meta_parts.append(f"发布时间：{self.publish_time}")
        if meta_parts:
            parts.append("> " + " | ".join(meta_parts) + "\n")

        if self.cover_image:
            parts.append(f"![封面]({self.cover_image})\n")

        return "\n".join(parts)

    def _build_footer(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"\n\n---\n*由 weixin-article-downloader 生成于 {now}*\n"

    def generate(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, "article.md")

        parts = [self._build_header()]

        if self.video_embeds:
            parts.append("\n## 视频\n")
            for embed in self.video_embeds:
                parts.append(embed + "\n")

        parts.append("\n## 正文\n")
        parts.append(self.content_md)
        parts.append(self._build_footer())

        full_content = "\n".join(parts)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return filepath
