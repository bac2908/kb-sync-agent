# Project Review Notes

## Concept

The pipeline converts OptiSigns support articles into a searchable knowledge base:

```text
Zendesk API -> clean Markdown -> Gemini File Search -> OptiBot answer with Article URL citations
```

## Approach

- Zendesk API is used instead of scraping rendered pages because article JSON includes title, URL, body HTML, and update metadata.
- HTML is cleaned with BeautifulSoup and converted to Markdown with `html2text`.
- Every Markdown file includes `Article URL:` so answers can cite source articles.
- Gemini File Search is used because the take-home allows Google Gemini and it avoids OpenAI API prepaid billing.
- Chunking uses 512 max tokens with 100 overlap tokens because Gemini rejected larger chunks.
- Delta detection compares SHA-256 hashes of generated Markdown.

## Daily Job

`main.py` runs the whole sync once:

```text
re-scrape -> calculate added/updated/skipped -> upload only changed files -> log counts
```

GitHub Actions runs it daily and stores `docs/last-run.log` as an artifact.

## Tradeoffs

- Updated articles are uploaded as fresh Gemini File Search documents. A production version should delete or replace the older document if the provider exposes stable document IDs.
- The repo stores Markdown and manifest state so scheduled jobs can detect deltas across runs.
- The YouTube support article is pinned so the required sample question always has the correct source document.

## Possible Improvements

- Store Gemini document IDs for clean replacement on updated articles.
- Add retry/backoff around upload operations.
- Add automated tests for slug generation, Markdown conversion, and delta detection.
- Add multilingual response behavior if OptiBot needs Vietnamese or French support.
