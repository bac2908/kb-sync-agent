import os
from pathlib import Path

from dotenv import load_dotenv

from src.delta import calculate_delta, load_manifest, summarize_delta
from src.gemini_uploader import upload_markdown_files_to_gemini
from src.scraper import MANIFEST_PATH, scrape_to_markdown


def get_article_limit() -> int:
    return int(os.getenv("ARTICLE_LIMIT", "30"))


def main() -> None:
    load_dotenv()

    article_limit = get_article_limit()

    print("Starting KB sync job...")
    print(f"Article limit: {article_limit}")

    previous_manifest = load_manifest(MANIFEST_PATH)

    print("\nStep 1: Scraping articles and converting to Markdown...")
    scraped_items = scrape_to_markdown(limit=article_limit)

    delta = calculate_delta(previous_manifest, scraped_items)
    delta_summary = summarize_delta(delta)
    changed_items = delta["added"] + delta["updated"]
    changed_paths = [Path(item["file_path"]) for item in changed_items]
    file_hashes = {
        str(Path(item["file_path"])): item["hash"]
        for item in changed_items
    }

    print("\nStep 2: Delta summary...")
    print(f"Articles discovered: {len(scraped_items)}")
    print(f"Added: {delta_summary['added']}")
    print(f"Updated: {delta_summary['updated']}")
    print(f"Skipped: {delta_summary['skipped']}")

    print("\nStep 3: Uploading delta Markdown files to Gemini File Search Store...")
    upload_result = upload_markdown_files_to_gemini(
        files_to_upload=changed_paths,
        file_hashes=file_hashes,
    )

    print("\nJob completed successfully.")
    print(f"Articles discovered: {len(scraped_items)}")
    print(f"Added: {delta_summary['added']}")
    print(f"Updated: {delta_summary['updated']}")
    print(f"Skipped: {delta_summary['skipped']}")
    print(f"Uploaded to Gemini: {upload_result['uploaded_files']}")
    print(f"Gemini skipped uploads: {upload_result['skipped_files']}")
    print(f"Estimated chunks embedded: {upload_result['estimated_chunks']}")


if __name__ == "__main__":
    main()
