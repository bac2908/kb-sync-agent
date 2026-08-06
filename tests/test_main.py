import unittest
from unittest.mock import patch

import main

SCRAPED_ITEM = {
    "title": "Synthetic article",
    "url": "https://example.org/article",
    "slug": "synthetic-article",
    "updated_at": "2026-01-01T00:00:00Z",
    "hash": "new-hash",
    "file_path": "data/markdown/synthetic-article.md",
}


class MainSyncTests(unittest.TestCase):
    @patch("main.get_article_limit", return_value=1)
    @patch("main.load_manifest", return_value={})
    @patch("main.scrape_to_markdown", return_value=[SCRAPED_ITEM])
    @patch("main.upload_markdown_files_to_gemini", side_effect=RuntimeError("down"))
    @patch("main.save_manifest")
    def test_manifest_is_not_committed_when_upload_fails(
        self,
        save_manifest,
        upload_files,
        scrape,
        load_manifest,
        article_limit,
    ):
        with self.assertRaisesRegex(RuntimeError, "down"):
            main.main()

        save_manifest.assert_not_called()
        scrape.assert_called_once_with(limit=1, persist_manifest=False)

    @patch("main.get_article_limit", return_value=1)
    @patch("main.load_manifest", return_value={})
    @patch("main.scrape_to_markdown", return_value=[SCRAPED_ITEM])
    @patch(
        "main.upload_markdown_files_to_gemini",
        return_value={
            "uploaded_files": 1,
            "skipped_files": 0,
            "estimated_chunks": 1,
        },
    )
    @patch("main.save_manifest")
    def test_manifest_is_committed_after_upload_succeeds(
        self,
        save_manifest,
        upload_files,
        scrape,
        load_manifest,
        article_limit,
    ):
        main.main()

        upload_files.assert_called_once()
        save_manifest.assert_called_once_with([SCRAPED_ITEM])


if __name__ == "__main__":
    unittest.main()
