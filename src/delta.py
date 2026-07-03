import json
from pathlib import Path
from typing import Dict, List


def load_manifest(path: Path) -> Dict:
    if not path.exists():
        return {}

    return json.loads(path.read_text(encoding="utf-8"))


def calculate_delta(previous_manifest: Dict, current_items: List[Dict]) -> Dict:
    added = []
    updated = []
    skipped = []

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

    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
    }


def summarize_delta(delta: Dict) -> Dict:
    return {
        "added": len(delta["added"]),
        "updated": len(delta["updated"]),
        "skipped": len(delta["skipped"]),
    }
