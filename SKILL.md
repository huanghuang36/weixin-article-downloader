---
name: weixin-article-downloader
description: Download WeChat official account articles to Markdown with local images and video embeds. Supports browser mode to bypass anti-crawl verification.
trigger: 微信公众号文章|下载公众号文章|保存公众号文章|weixin article|wechat article|公众号文章下载
---

# WeChat Article to Markdown

Download a WeChat official account article and convert it to a Markdown document, including:
- Full text content
- All images downloaded to local `images/` directory
- Video links preserved (with optional local download)

## Usage

```bash
# Find the script directory (relative to this project root)
TOOL_DIR="$(cd "$(dirname "$0")" && pwd)/tool"

# HTTP mode (default, may trigger anti-crawl verification)
python "$TOOL_DIR/main.py" "<ARTICLE_URL>" [-o ./output]

# Browser mode (bypasses anti-crawl, recommended)
python "$TOOL_DIR/main.py" "<ARTICLE_URL>" --browser
```

## Arguments

- `<ARTICLE_URL>` — Required. The WeChat article URL (must start with `https://mp.weixin.qq.com/s/`)
- `-o` — Output directory (default: `./output`)
- `--download-video` — Attempt to download videos locally using yt-dlp
- `--browser` — Use Playwright browser mode to bypass WeChat anti-crawl verification

## Example

```bash
TOOL_DIR="$(cd "$(dirname "$0")" && pwd)/tool"

# Browser mode (recommended for reliability)
python "$TOOL_DIR/main.py" "https://mp.weixin.qq.com/s?__biz=..." --browser -o ./articles/
```

Output structure:
```
articles/article-title/
├── article.md
├── images/
│   ├── img_001.png
│   └── img_002.png
└── videos/          # only if --download-video succeeded
    └── video_001.mp4
```

## Prerequisites

Run once to install dependencies:
```bash
TOOL_DIR="$(cd "$(dirname "$0")" && pwd)/tool"
bash "$TOOL_DIR/../install.sh"
```

## Notes

- Browser mode (`--browser`) connects to your running Chrome via CDP (port 9222). First start Chrome with:
  ```bash
  open -a "Google Chrome" --args --remote-debugging-port=9222
  ```
  Then open the article URL in Chrome, complete any verification, and re-run the command. The tool will find the existing tab and capture the content.
- If CDP is unavailable, it falls back to launching a standalone Chromium instance.
- Images are downloaded with a random delay to avoid rate limiting.
- If image download fails, the original URL is kept in the Markdown.
- Video download requires `yt-dlp` (installed via `install.sh`).
