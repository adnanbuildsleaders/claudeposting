# Habbinson Instagram cloud auto-poster

Runs in **GitHub Actions** (free) at **10:00, 13:00, 17:00 IST** and posts the due Instagram
**video Stories + Reels** for your blogs — **your PC does not need to be on.**
(YouTube Shorts are already pre-scheduled separately via the YouTube API, so this does IG only.)

## What's in here
- `cloud_post.py` — the entry script (posts due IG Story + Reel).
- `post_routine.py`, `ig_story.py`, `wp_publish.py`, `video_scripts.py`, `blog_image_engine.py`, `yt_upload.py` — supporting code.
- `assets/<slug>.mp4` — the 10 reel videos (so no rendering happens in the cloud).
- `publish-tracker.json` — the state file (which blog posts when; updated + committed each run).
- `.github/workflows/post.yml` — the scheduler.

## One-time setup (~5 minutes)

### 1. Create a **private** GitHub repo
On github.com → New repository → name it e.g. `habbinson-poster` → **Private** → Create. Don't add a README.

### 2. Push this folder to it
Open a terminal in this `cloud-poster` folder and run (replace `YOURNAME`):
```
git init -b main
git add .
git commit -m "habbinson IG cloud poster"
git remote add origin https://github.com/YOURNAME/habbinson-poster.git
git push -u origin main
```

### 3. Add one secret
In the repo: **Settings → Secrets and variables → Actions → New repository secret**. Create:
- **`IG_CONFIG`** → paste the entire contents of `D:\Claude\Kids\Communication\Code\.ig_config.json`

That's it — no WordPress secret needed. Blogs are scheduled directly on WordPress; videos are served from this public GitHub repo. GitHub encrypts the secret; it's written to a file only at runtime and is **never committed** — see `.gitignore`.

### 4. Enable + test
- Go to the **Actions** tab → if prompted, click **"I understand my workflows, enable them."**
- Open **"Habbinson IG auto-poster" → Run workflow** (manual run) to test. Check the log: it should say `due IG actions: N` and `OK` for each. (If nothing is due yet, it prints `due IG actions: 0` — that's correct.)

### 5. Hand off from your PC (avoid double-posting)
Until now your local Windows task `HabbinsonIGStories` also posts IG. **Once the cloud run works, disable the local task** so they don't both post:
```
powershell Disable-ScheduledTask -TaskName HabbinsonIGStories
```
(Or just tell me and I'll disable it.) YouTube is unaffected — it's pre-scheduled.

## How it decides what to post
Each blog in `publish-tracker.json` has a `post_at` time. A blog's Story + Reel publish once
`now (IST) >= post_at` **and** its WordPress post is live. New blogs post at their 10:00/17:00 slot
(no `post_at` set → uses the blog's schedule); backlog blogs are dripped at 13:00 IST, one per day.

## Good to know
- **Cron delay:** GitHub may start a scheduled run a few minutes late under load — harmless.
- **Repo inactivity:** scheduled workflows auto-pause after 60 days with no repo commits — this workflow commits the tracker on every run, so it stays active.
- **IG token:** long-lived (~60 days, auto-refreshed each run). If it ever lapses, regenerate it and update the `IG_CONFIG` secret.
- **New daily blogs:** when you add new blogs locally, re-push the updated `publish-tracker.json` + the new `assets/<slug>.mp4` so the cloud knows about them. (We can script this later.)
