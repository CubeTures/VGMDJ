# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

VGMDJ is a self-hosted tool for managing a video game music library: downloading albums from KHInsider, tagging files, hiding disliked tracks (with auto-hide by duration), and syncing with a Jellyfin media server. It's a FastAPI backend + SvelteKit frontend, deployed as a single Docker image (the backend serves the built frontend as static files).

## Commands

Backend (from repo root, uses `uv`):
```
uv sync                                    # install deps
uv run uvicorn src.main:app --reload       # run dev server (port 8000)
uv run ruff check .                        # lint (only import-sort rule "I" is enabled)
```

Frontend (from `frontend/`, uses `pnpm`):
```
pnpm install
pnpm run dev        # dev server, expects backend on localhost:8000
pnpm run build      # static build output to frontend/build (served by FastAPI)
pnpm run check      # svelte-kit sync + svelte-check (type checking)
```

There is no test suite in this repo currently.

Deploy: `./deploy.sh` builds the frontend, builds the Docker image, and pushes it to a private registry. It temporarily blanks `frontend/.env` for the build (the `.env` just contains overrides for dev) and restores it afterward.

## Configuration

Backend config comes from environment variables loaded via `.env` (see `.env.example`): `CONFIG_DIR`, `TMP_DIR`, `MUSIC_DIR`, `JELLYFIN_URL`, `JELLYFIN_USER_ID`, `JELLYFIN_TOKEN`, `FLARESOLVERR_URL`. These are read once at import time in `src/__init__.py` and required (no defaults in code) — the process fails fast if any are missing. The Docker image sets `CONFIG_DIR=/config`, `TMP_DIR=/tmp`, `MUSIC_DIR=/music` to match the Kubernetes volume mounts.

`CONFIG_DIR` holds persistent app state (`prefs.json`, lock files). `TMP_DIR` is scratch space where downloads are staged (`TMP_DIR/<franchise>/<album>`) before being moved into `MUSIC_DIR`, the root of the actual music library on disk.

## Architecture

**`pykhinsider/`** is a separate, independently-versioned local package (installed via `uv` path dependency, editable) that does the actual scraping/downloading from KHInsider (using FlareSolverr to get past Cloudflare). `src/khinsider.py` in the main app wraps it with app-specific logic (staging to `TMP_DIR`, tagging, moving into `MUSIC_DIR`, notifying Jellyfin).

**Library layout on disk**: `MUSIC_DIR/<album_artist>/<album>/<tracks...>`. Most backend endpoints take a `dirs: list[str]` that is joined onto `MUSIC_DIR` (see `utils.dirs_to_path`) rather than an opaque path, so the frontend always addresses folders by their path segments relative to the music root.

**Hiding tracks** (`src/ignore.py`): each folder can have a `.ignore` file, a custom flat-file format of alternating `#!meta {json}` / escaped-filename line pairs (not JSON as a whole — written this way so it's diff-friendly and greppable). Entries carry a `meta` dict; the only current key is `auto: true`, set by the auto-hide feature so it can tell auto-hidden tracks apart from manually hidden ones and un-hide them if the auto-hide threshold changes. Read/write always goes through `read_ignore`/`write_ignore`; don't hand-roll the format elsewhere.

**Auto-hide** (`src/auto_hide.py`): a duration threshold (seconds) stored in prefs. `refresh_auto_hidden_single` reconciles one leaf folder against the threshold (adds `auto` ignore entries for short tracks, removes ones that no longer qualify); `refresh_auto_hidden` walks every leaf folder under `MUSIC_DIR` (dirs with no subdirectories) and applies it. Runs on prefs change and after each download.

**Download status streaming** (`src/status.py`, `/download-status`): downloads run in FastAPI `BackgroundTasks` on worker threads, not the event loop. Progress is pushed via `_notify`, which is called from the worker thread but wakes the asyncio loop with `call_soon_threadsafe` (the loop reference is captured once at startup in `set_loop`). Each in-flight/recent download has a stable id (`uuid7`) and its lifecycle moves through the `Status` enum (`STARTED` → ... → `COMPLETED`); the last 10 statuses are cached in `_latest_messages` so a client connecting to the SSE stream mid-download immediately gets caught up before live updates. Do not update this to hold results in memory unbounded — the 10-item eviction is deliberate.

**Jellyfin integration** (`src/jellyfin.py`): thin REST wrapper. After any change to files on disk (hide/unhide, download complete), call `utils.refresh_dir_or_fallback` to tell Jellyfin to rescan — it tries to resolve the specific album folder via search and falls back to a full library refresh if it can't be found (e.g. brand new album not yet indexed).

**Concurrency/locking**: `prefs.json` and any writer needing cross-request safety uses `utils.lock_file` (a `filelock.FileLock` wrapper) around read-modify-write sections — see `prefs.py` and the `/auto-hide` endpoint for the pattern.

**Frontend**: SvelteKit with `adapter-static` (fully prerendered/static, `trailingSlash = "always"`), Svelte 5, Tailwind 4. Talks to the backend via `PUBLIC_API_URL` (frontend `.env`). Components live flat in `src/lib/components/`; no nested feature folders.

**`src/retag.py`** is a standalone one-off script (imports `utils` unqualified, not `src.utils` — it's not wired into the FastAPI app) for bulk-retagging an existing `Music/` folder tree. Not part of the request/response flow.
