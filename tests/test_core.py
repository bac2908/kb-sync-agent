import unittest

from src.cleaner import clean_html, html_to_markdown
from src.delta import calculate_delta, summarize_delta
from src.gemini_uploader import estimate_chunks
from src.scraper import article_to_markdown, ensure_unique_slug, slugify


class CorePipelineTests(unittest.TestCase):
    def test_slugify_keeps_filename_safe(self):
        self.assertEqual(
            slugify("How to Add a YouTube Video?"),
            "how-to-add-a-youtube-video",
        )

    def test_duplicate_slug_gets_stable_article_id_suffix(self):
        item = {
            "article_id": "42",
            "url": "https://example.com/articles/42",
            "slug": "same-title",
            "file_path": "data/markdown/same-title.md",
        }

        unique_item = ensure_unique_slug(item, {"same-title"})

        self.assertEqual(unique_item["slug"], "same-title-42")
        self.assertTrue(unique_item["file_path"].endswith("same-title-42.md"))

    def test_cleaner_removes_scripts_and_preserves_links(self):
        html = (
            '<div><script>alert("x")</script><h2>Steps</h2>'
            '<a href="/help">Help</a></div>'
        )
        markdown = html_to_markdown(clean_html(html))

        self.assertIn("## Steps", markdown)
        self.assertIn("[Help]", markdown)
        self.assertNotIn("alert", markdown)

    def test_article_to_markdown_includes_article_url(self):
        item = article_to_markdown(
            {
                "title": "Sample Article",
                "html_url": "https://support.optisigns.com/hc/en-us/articles/1",
                "body": "<p>Hello</p>",
                "updated_at": "2026-07-03T00:00:00Z",
            }
        )

        self.assertTrue(item["markdown"].startswith("# Sample Article"))
        self.assertIn("Article URL: https://support.optisigns.com", item["markdown"])
        self.assertIn("Hello", item["markdown"])

    def test_delta_counts_added_updated_and_skipped(self):
        previous = {
            "https://example.com/a": {"hash": "same"},
            "https://example.com/b": {"hash": "old"},
        }
        current = [
            {"url": "https://example.com/a", "hash": "same"},
            {"url": "https://example.com/b", "hash": "new"},
            {"url": "https://example.com/c", "hash": "new"},
        ]

        self.assertEqual(
            summarize_delta(calculate_delta(previous, current)),
            {"added": 1, "updated": 1, "removed": 0, "skipped": 1},
        )

    def test_delta_detects_removed_article(self):
        previous = {
            "https://example.com/removed": {
                "hash": "old",
                "file_path": "data/markdown/removed.md",
            }
        }

        delta = calculate_delta(previous, [])

        self.assertEqual(delta["removed"][0]["url"], "https://example.com/removed")
        self.assertEqual(summarize_delta(delta)["removed"], 1)

    def test_chunk_estimate_has_overlap(self):
        text = "word " * 700
        self.assertGreaterEqual(estimate_chunks(text), 2)


if __name__ == "__main__":
    unittest.main()
