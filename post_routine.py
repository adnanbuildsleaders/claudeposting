# -*- coding: utf-8 -*-
"""v13 shared posting routine.

POLICY (locked 2026-06-05):
  1. Nothing posts for a SCHEDULED (not-yet-live) blog.
  2. No images ever go out (no teaser, no "now live" image story).
  3. On publish only, push VIDEO to Instagram + YouTube.
  4. Instagram gets BOTH a video Story AND a feed Reel (SEO caption); YouTube gets a Short.
     All three reuse the ONE video built per blog.

Used by both ig_post_due.py (2h task) and publish_backlog.py (spaced burst)."""
import os, json, datetime, requests
import wp_publish as WP
import video_scripts as VS
import ig_story as S
import yt_upload as YT
# video_engine is imported lazily inside ensure_video() so the cloud IG poster
# (which uses pre-built mp4s) doesn't need numpy/imageio/ffmpeg.

IST = WP.IST
TRK = WP.TRACKER
KINDS = ["ig-video", "ig-reel", "yt-short"]          # priority order


def _now(): return datetime.datetime.now(IST)
def load(): return json.load(open(TRK, encoding="utf-8"))
def save(tr): json.dump(tr, open(TRK, "w", encoding="utf-8"), indent=2, default=str)


def wp_live(pid):
    try:
        return requests.get(f"{WP.API}/posts/{pid}", auth=WP.AUTH,
                            params={"context": "edit"}, timeout=20).json().get("status") == "publish"
    except Exception:
        return False


def ensure_video(slug, e):
    """Build the blog's video once (seed derived from slug -> unique audio); cache the path."""
    vp = e.get("video_path")
    if vp and os.path.exists(vp):
        return vp
    import video_engine as VE                            # lazy: only needed when (re)building
    m = VS.SCRIPTS[slug]
    vdir = os.path.join(WP.BASE, "youtube", "videos"); os.makedirs(vdir, exist_ok=True)
    vp = os.path.join(vdir, slug + ".mp4")
    VE.build_video(m["script"], m["palette"], vp)        # seed auto-derived from filename
    e["video_path"] = vp
    return vp


def due_actions(tr, now=None):
    """(slug, kind) for every video output owed by a LIVE blog whose post_at time has arrived.
    post_at = when the outputs should publish: new blogs use their 10:00/17:00 slot (= scheduled_dt);
    backlog blogs are dripped at 13:00 IST, one per day (set explicitly in the tracker). Empty otherwise."""
    now = now or _now()
    out = []
    for slug, e in tr.items():
        if slug not in VS.SCRIPTS:
            continue
        when = e.get("post_at") or e.get("scheduled_dt")
        if not when:
            continue
        if now < datetime.datetime.fromisoformat(when):  # rules 1 + scheduling: not before post_at
            continue
        if not wp_live(e.get("wp_post_id")):             # rule 3: only once WP shows publish
            continue
        e["live_detected"] = True
        if not e.get("ig_video_done"):
            out.append((slug, "ig-video"))
        if not e.get("ig_reel_done"):
            out.append((slug, "ig-reel"))
        if YT.configured() and not e.get("yt_video_id"):
            out.append((slug, "yt-short"))
    out.sort(key=lambda a: KINDS.index(a[1]))
    return out


def run_action(slug, kind, tr):
    """Execute one action; mutates tr[slug]; returns (ok, info)."""
    e = tr[slug]; m = VS.SCRIPTS[slug]
    if kind == "ig-video":
        r = S.post_video_story(ensure_video(slug, e), publish=True)
        if r["ok"]: e["ig_video_done"] = True
        return r["ok"], r
    if kind == "ig-reel":
        r = S.post_reel(ensure_video(slug, e), VS.caption_for(slug), publish=True)
        if r["ok"]: e["ig_reel_done"] = True
        return r["ok"], r
    if kind == "yt-short":
        vp = ensure_video(slug, e)
        title = (m["title"] + " #Shorts")[:100]
        desc = (m["script"]["cta_line"] + "\n\nRead the full guide: https://habbinson.com/" + m["final_slug"] +
                "/\n\n#parenting #parentingtips #raisingleaders #confidentkids #Shorts\n"
                "Don't just raise a child - raise a leader.")
        r = YT.upload_short(vp, title, desc, tags=["parenting", "parenting tips", "raising leaders", "kids", "shorts"])
        if r.get("ok"): e["yt_video_id"] = r["video_id"]
        return bool(r.get("ok")), r
    return False, {"ok": False, "error": "unknown kind " + kind}
