import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import html2text
import requests
from bs4 import BeautifulSoup


BASE_API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
ARTICLE_API_URL_TEMPLATE = (
    "https://support.optisigns.com/api/v2/help_center/en-us/articles/{article_id}.json"
)
PINNED_ARTICLE_IDS = [
    "360051014713",  # How to use YouTube with OptiSigns
]
OUTPUT_DIR = Path("data/markdown")
STATE_DIR = Path("data/state")
MANIFEST_PATH = STATE_DIR / "articles_manifest.json"


def slugify(text: str) -> str:
    """
    Convert article title into safe filename.
    Example: 'How to Add a YouTube Video?' -> 'how-to-add-a-youtube-video'
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "article"


def clean_html(html: str) -> str:
    """
    Remove unnecessary elements from article HTML.
    Keep main content, headings, links, lists, images, code blocks.
    """
    soup = BeautifulSoup(html or "", "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    for tag in soup.find_all(["span", "div"]):
        if not tag.get_text(strip=True) and not tag.find(["img", "a", "code", "pre"]):
            tag.decompose()

    return str(soup)


def html_to_markdown(html: str) -> str:
    """
    Convert cleaned HTML to Markdown.
    """
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    converter.unicode_snob = True
    converter.protect_links = True
    markdown = converter.handle(html)

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def fetch_article_by_id(article_id: str) -> Dict:
    url = ARTICLE_API_URL_TEMPLATE.format(article_id=article_id)
    print(f"Fetching pinned article: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()["article"]


def fetch_articles(limit: int = 30) -> List[Dict]:
    """
    Fetch articles from Zendesk Help Center API.
    Handles pagination until enough articles are collected.
    """
    articles = []
    seen_article_ids = set()
    url: Optional[str] = f"{BASE_API_URL}?per_page=100"

    for article_id in PINNED_ARTICLE_IDS:
        article = fetch_article_by_id(article_id)
        articles.append(article)
        seen_article_ids.add(article.get("id"))

    while url and len(articles) < limit:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        batch = data.get("articles", [])
        for article in batch:
            article_id = article.get("id")
            if article_id in seen_article_ids:
                continue

            articles.append(article)
            seen_article_ids.add(article_id)

            if len(articles) >= limit:
                break

        url = data.get("next_page")

    return articles[:limit]


def article_to_markdown(article: Dict) -> Dict:
    """
    Convert one Zendesk article dict to Markdown content and metadata.
    """
    title = article.get("title", "Untitled Article").strip()
    url = article.get("html_url", "").strip()
    body_html = article.get("body", "")
    updated_at = article.get("updated_at", "")

    cleaned_html = clean_html(body_html)
    body_md = html_to_markdown(cleaned_html)

    markdown = f"""# {title}

Article URL: {url}

{body_md}
"""

    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"

    slug = slugify(title)
    content_hash = calculate_hash(markdown)

    return {
        "title": title,
        "url": url,
        "slug": slug,
        "updated_at": updated_at,
        "markdown": markdown,
        "hash": content_hash,
        "file_path": str(OUTPUT_DIR / f"{slug}.md"),
    }


def save_markdown_file(item: Dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{item['slug']}.md"
    path.write_text(item["markdown"], encoding="utf-8")


def save_manifest(items: List[Dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}
    for item in items:
        manifest[item["url"]] = {
            "title": item["title"],
            "slug": item["slug"],
            "updated_at": item["updated_at"],
            "hash": item["hash"],
            "file_path": item["file_path"],
        }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def scrape_to_markdown(limit: int = 30) -> List[Dict]:
    """
    Main function for Step 3:
    - fetch articles
    - convert to Markdown
    - save .md files
    - save manifest
    """
    raw_articles = fetch_articles(limit=limit)
    processed_items = []

    for article in raw_articles:
        item = article_to_markdown(article)
        save_markdown_file(item)
        processed_items.append(item)

        print(f"Saved: {item['file_path']}")

    save_manifest(processed_items)

    print()
    print("Scrape completed.")
    print(f"Articles saved: {len(processed_items)}")
    print(f"Markdown folder: {OUTPUT_DIR}")
    print(f"Manifest file: {MANIFEST_PATH}")

    return processed_items


if __name__ == "__main__":
    scrape_to_markdown(limit=30)
