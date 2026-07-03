# Daily Job Deployment

## GitHub Actions Scheduled Job

The easiest no-cost deployment path is the GitHub Actions workflow in:

```text
.github/workflows/daily-sync.yml
```

It runs manually with `workflow_dispatch` and daily on this schedule:

```text
0 2 * * *
```

This runs once per day at 02:00 UTC.

## GitHub Actions Steps

1. Push the repo to GitHub.
2. Go to GitHub repo -> Settings -> Secrets and variables -> Actions.
3. Add repository secrets:

```env
GEMINI_API_KEY=your Gemini API key
GEMINI_FILE_SEARCH_STORE_NAME=fileSearchStores/kbsyncagentknowledgebase-fapa45j4vgza
```

4. Go to the Actions tab.
5. Select `Daily KB Sync`.
6. Click `Run workflow`.
7. Open the completed run and confirm the log contains:

```text
Job completed successfully.
Articles discovered: 30
Added: ...
Updated: ...
Skipped: ...
Uploaded to Gemini: ...
```

The workflow uploads `docs/last-run.log` as an artifact and commits updated
Markdown/manifest state back to the repo when content changes.

## Last Run Logs

```text
https://github.com/bac2908/kb-sync-agent/actions/runs/28638442875
```

Optional screenshot path:

```text
docs/screenshots/daily-job-log.png
```

## Render Cron Job Option

This repo also includes `render.yaml` if you prefer Render.

1. Push the repo to GitHub.
2. In Render, create a new Blueprint from the GitHub repo.
3. Render will detect `render.yaml` and create the cron job.
4. Add these environment variables in Render:

```env
GEMINI_API_KEY=your Gemini API key
GEMINI_FILE_SEARCH_STORE_NAME=fileSearchStores/kbsyncagentknowledgebase-fapa45j4vgza
```

5. Trigger a manual run once.
6. Open the Render cron job logs and confirm the output contains:

```text
Job completed successfully.
Articles discovered: 30
Added: ...
Updated: ...
Skipped: ...
Uploaded to Gemini: ...
```
