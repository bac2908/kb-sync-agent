import json
from pathlib import Path


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}

    return json.loads(path.read_text(encoding="utf-8"))


def calculate_delta(previous_manifest: dict, current_items: list[dict]) -> dict:
    added = []
    updated = []
    skipped = []
    current_urls = {item["url"] for item in current_items}

    for item in current_items:
        article_url = item["url"]
        previous_item = previous_manifest.get(article_url)

        if not previous_item:
            added.append(item)
            continue

        if previous_item.get("hash") != item["hash"]:
            updated.append(item)
            continue

        skipped.append(item)

    removed = [
        {**previous_item, "url": article_url}
        for article_url, previous_item in previous_manifest.items()
        if article_url not in current_urls
    ]

    return {
        "added": added,
        "updated": updated,
        "removed": removed,
        "skipped": skipped,
    }


def summarize_delta(delta: dict) -> dict:
    return {
        "added": len(delta["added"]),
        "updated": len(delta["updated"]),
        "removed": len(delta.get("removed", [])),
        "skipped": len(delta["skipped"]),
    }
