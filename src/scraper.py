import hashlib
import json
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


def create_http_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


HTTP_SESSION = create_http_session()


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


def fetch_article_by_id(article_id: str) -> dict:
    url = ARTICLE_API_URL_TEMPLATE.format(article_id=article_id)
    print(f"Fetching pinned article: {url}")
    response = HTTP_SESSION.get(url, timeout=30)
    response.raise_for_status()
    return response.json()["article"]


def fetch_articles(limit: int = 30) -> list[dict]:
    """
    Fetch articles from Zendesk Help Center API.
    Handles pagination until enough articles are collected.
    """
    articles = []
    seen_article_ids = set()
    url: str | None = f"{BASE_API_URL}?per_page=100"

    for article_id in PINNED_ARTICLE_IDS:
        article = fetch_article_by_id(article_id)
        articles.append(article)
        seen_article_ids.add(article.get("id"))

    while url and len(articles) < limit:
        print(f"Fetching: {url}")
        response = HTTP_SESSION.get(url, timeout=30)
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


def article_to_markdown(article: dict) -> dict:
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
        "article_id": str(article.get("id", "")),
        "title": title,
        "url": url,
        "slug": slug,
        "updated_at": updated_at,
        "markdown": markdown,
        "hash": content_hash,
        "file_path": str(MARKDOWN_DIR / f"{slug}.md"),
    }


def save_markdown_file(item: dict) -> None:
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    path = MARKDOWN_DIR / f"{item['slug']}.md"
    path.write_text(item["markdown"], encoding="utf-8")


def ensure_unique_slug(item: dict, used_slugs: set[str]) -> dict:
    """Keep same-title articles from overwriting each other on disk."""
    if item["slug"] not in used_slugs:
        used_slugs.add(item["slug"])
        return item

    suffix = item.get("article_id") or calculate_hash(item["url"])[:8]
    unique_item = dict(item)
    unique_item["slug"] = f"{item['slug']}-{suffix}"
    unique_item["file_path"] = str(MARKDOWN_DIR / f"{unique_item['slug']}.md")
    used_slugs.add(unique_item["slug"])
    return unique_item


def save_manifest(items: list[dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}
    for item in items:
        manifest[item["url"]] = {
            "article_id": item.get("article_id", ""),
            "title": item["title"],
            "slug": item["slug"],
            "updated_at": item["updated_at"],
            "hash": item["hash"],
            "file_path": item["file_path"],
        }

    temporary_path = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_path.replace(MANIFEST_PATH)


def scrape_to_markdown(
    limit: int = 30,
    persist_manifest: bool = True,
) -> list[dict]:
    """
    Main function for Step 3:
    - fetch articles
    - convert to Markdown
    - save .md files
    - save manifest
    """
    raw_articles = fetch_articles(limit=limit)
    processed_items = []
    used_slugs: set[str] = set()

    for article in raw_articles:
        item = article_to_markdown(article)
        item = ensure_unique_slug(item, used_slugs)
        save_markdown_file(item)
        processed_items.append(item)

        print(f"Saved: {item['file_path']}")

    if persist_manifest:
        save_manifest(processed_items)

    print()
    print("Scrape completed.")
    print(f"Articles saved: {len(processed_items)}")
    print(f"Markdown folder: {MARKDOWN_DIR}")
    if persist_manifest:
        print(f"Manifest file: {MANIFEST_PATH}")
    else:
        print("Manifest commit deferred until upload succeeds.")

    return processed_items


if __name__ == "__main__":
    scrape_to_markdown(limit=30)
