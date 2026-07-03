import hashlib
import json
import re
from typing import Dict, List, Optional

import requests

from src.cleaner import clean_html, html_to_markdown
from src.config import (
    ARTICLE_API_URL_TEMPLATE,
    ARTICLES_MANIFEST_PATH,
    BASE_API_URL,
    MARKDOWN_DIR,
    PINNED_ARTICLE_IDS,
    STATE_DIR,
)


MANIFEST_PATH = ARTICLES_MANIFEST_PATH


def slugify(text: str) -> str:
    """
    Convert article title into safe filename.
    Example: 'How to Add a YouTube Video?' -> 'how-to-add-a-youtube-video'
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "article"


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
        "file_path": str(MARKDOWN_DIR / f"{slug}.md"),
    }


def save_markdown_file(item: Dict) -> None:
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    path = MARKDOWN_DIR / f"{item['slug']}.md"
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
    print(f"Markdown folder: {MARKDOWN_DIR}")
    print(f"Manifest file: {MANIFEST_PATH}")

    return processed_items


if __name__ == "__main__":
    scrape_to_markdown(limit=30)
