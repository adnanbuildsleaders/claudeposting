# -*- coding: utf-8 -*-
"""Cloud IG posting routine (no WP credentials required).

POLICY (locked 2026-06-05):
  1. Nothing posts for a SCHEDULED (not-yet-live) blog.
  2. No images ever go out.
  3. On publish only, push VIDEO to Instagram (Story + Reel).
  4. YouTube Shorts are pre-scheduled via publishAt — this routine skips them.

Videos are stored in GitHub (assets/<slug>.mp4) and served from raw.githubusercontent.com.
WP credentials are NOT needed here: we trust WP's own scheduler — if a wp_post_id exists
and now >= post_at, the blog will be live. The post_at gate already enforces timing."""
import os, json, datetime
import video_scripts as VS
import ig_story as S

BASE  = os.path.dirname(os.path.abspath(__file__))
TRK   = os.path.join(BASE, "publish-tracker.json")
IST   = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
KINDS = ["ig-video", "ig-reel"]   # cloud does IG only; YT = pre-scheduled

# GitHub raw base URL — assets/<slug>.mp4 are committed here and served publicly
GITHUB_RAW = "https://raw.githubusercontent.com/adnanbuildsleaders/claudeposting/main/assets"


def _now(): return datetime.datetime.now(IST)
def load(): return json.load(open(TRK, encoding="utf-8"))
def save(tr): json.dump(tr, open(TRK, "w", encoding="utf-8"), indent=2, default=str)


def wp_live(pid):
    """Trust WP's own scheduler: if a post_id exists the blog was scheduled and will auto-publish.
    No WP API call needed — avoids requiring WP credentials in GitHub secrets."""
    return bool(pid)


def ensure_video(slug, e):
    """Return the public GitHub raw URL for this slug's mp4.
    Falls back to e['video_path'] if it's already a hosted URL."""
    vp = e.get("video_path")
    if vp and vp.startswith("https://"):
        return vp                              # already a hosted URL
    # construct canonical GitHub raw URL
    return f"{GITHUB_RAW}/{slug}.mp4"


def due_actions(tr, now=None):
    """Return (slug, kind) for every IG output owed by a live blog whose post_at has arrived."""
    now = now or _now()
    out = []
    for slug, e in tr.items():
        if slug not in VS.SCRIPTS:
            continue
        when = e.get("post_at") or e.get("scheduled_dt")
        if not when:
            continue
        if now < datetime.datetime.fromisoformat(when):
            continue
        if not wp_live(e.get("wp_post_id")):
            continue
        e["live_detected"] = True
        if not e.get("ig_video_done"):
            out.append((slug, "ig-video"))
        if not e.get("ig_reel_done"):
            out.append((slug, "ig-reel"))
    out.sort(key=lambda a: KINDS.index(a[1]))
    return out


def run_action(slug, kind, tr):
    """Execute one IG action; mutates tr[slug]; returns (ok, info)."""
    e  = tr[slug]
    vp = ensure_video(slug, e)
    if kind == "ig-video":
        r = S.post_video_story(vp, publish=True)
        if r["ok"]: e["ig_video_done"] = True
        return r["ok"], r
    if kind == "ig-reel":
        r = S.post_reel(vp, VS.caption_for(slug), publish=True)
        if r["ok"]: e["ig_reel_done"] = True
        return r["ok"], r
    return False, {"ok": False, "error": "unknown kind " + kind}
