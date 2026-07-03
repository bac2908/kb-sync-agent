# Submission Checklist

## Must Submit

- GitHub repo with a cryptic name that does not include `optisigns`.
- `.env.sample`, no real keys committed.
- `Dockerfile` that runs `main.py` once and exits successfully.
- `README.md` with setup, local run, Docker run, daily job notes, and screenshot.
- `docs/screenshots/youtube-answer.png`.
- Daily job log link or artifact.

## Current Project Status

- Scrape and Markdown: done, `data/markdown` has 30+ files.
- API-based Gemini File Search upload: done.
- Assistant sanity check with cited URL: done.
- `main.py` daily sync with delta logs: done.
- Dockerfile: done.
- GitHub Actions daily workflow: ready in `.github/workflows/daily-sync.yml`.
- Hosted daily job run URL: done in `docs/deployment.md`.

## Before Pushing

The current parent Git root appears to be `D:/`, so create a clean repo from this folder only:

```bash
cd D:/kb-sync-agent
git init
git add .
git commit -m "init kb sync agent"
```

Then create a GitHub repo with a name like:

```text
kb-sync-agent
doc-sync-worker
support-kb-sync
```

Avoid names containing:

```text
optisigns
optibot
```

## GitHub Actions Secrets

After pushing, add these repository secrets:

```env
GEMINI_API_KEY=...
GEMINI_FILE_SEARCH_STORE_NAME=fileSearchStores/kbsyncagentknowledgebase-fapa45j4vgza
```

Run `Daily KB Sync` manually once and copy the run URL into `docs/deployment.md`.
