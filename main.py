import os
from pathlib import Path

from dotenv import load_dotenv

from src.delta import calculate_delta, load_manifest, summarize_delta
from src.gemini_uploader import upload_markdown_files_to_gemini
from src.scraper import MANIFEST_PATH, save_manifest, scrape_to_markdown


def get_article_limit() -> int:
    article_limit = int(os.getenv("ARTICLE_LIMIT", "30"))
    if article_limit < 1:
        raise ValueError("ARTICLE_LIMIT must be greater than zero.")
    return article_limit


def main() -> None:
    load_dotenv()

    article_limit = get_article_limit()

    print("Starting KB sync job...")
    print(f"Article limit: {article_limit}")

    previous_manifest = load_manifest(MANIFEST_PATH)

    print("\nStep 1: Scraping articles and converting to Markdown...")
    # The manifest is committed only after upload succeeds. If Gemini is
    # unavailable, the next run will see the same delta and retry it.
    scraped_items = scrape_to_markdown(
        limit=article_limit,
        persist_manifest=False,
    )

    delta = calculate_delta(previous_manifest, scraped_items)
    delta_summary = summarize_delta(delta)
    changed_items = delta["added"] + delta["updated"]
    changed_paths = [Path(item["file_path"]) for item in changed_items]
    file_hashes = {str(Path(item["file_path"])): item["hash"] for item in changed_items}

    print("\nStep 2: Delta summary...")
    print(f"Articles discovered: {len(scraped_items)}")
    print(f"Added: {delta_summary['added']}")
    print(f"Updated: {delta_summary['updated']}")
    print(f"Removed from source: {delta_summary['removed']}")
    print(f"Skipped: {delta_summary['skipped']}")

    print("\nStep 3: Uploading delta Markdown files to Gemini File Search Store...")
    upload_result = upload_markdown_files_to_gemini(
        files_to_upload=changed_paths,
        file_hashes=file_hashes,
    )
    save_manifest(scraped_items)

    print("\nJob completed successfully.")
    print(f"Articles discovered: {len(scraped_items)}")
    print(f"Added: {delta_summary['added']}")
    print(f"Updated: {delta_summary['updated']}")
    print(f"Removed from source: {delta_summary['removed']}")
    print(f"Skipped: {delta_summary['skipped']}")
    print(f"Uploaded to Gemini: {upload_result['uploaded_files']}")
    print(f"Gemini skipped uploads: {upload_result['skipped_files']}")
    print(f"Estimated chunks embedded: {upload_result['estimated_chunks']}")


if __name__ == "__main__":
    main()
