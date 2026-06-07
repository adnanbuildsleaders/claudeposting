# -*- coding: utf-8 -*-
"""Instagram Story / Reel publisher via the Instagram Graph API (Instagram Login).

Videos are served from raw.githubusercontent.com (public GitHub repo assets/) —
no WordPress upload or credentials required here.
Token is long-lived (60d) and auto-refreshable without the app secret."""
import os, json, time, requests

BASE  = os.path.dirname(os.path.abspath(__file__))
CFG   = os.path.join(BASE, ".ig_config.json")
IG    = json.load(open(CFG, encoding="utf-8"))
TOKEN = IG["access_token"]
IGID  = IG["ig_user_id"]
GRAPH = "https://graph.instagram.com"


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------

def refresh_token():
    """Extend the 60-day long-lived token (no app secret needed)."""
    import datetime
    r = requests.get(f"{GRAPH}/refresh_access_token",
                     params={"grant_type": "ig_refresh_token",
                             "access_token": IG["access_token"]}, timeout=30)
    if r.status_code == 200 and "access_token" in r.json():
        IG["access_token"] = r.json()["access_token"]
        IG["token_expires_in_sec"] = r.json().get("expires_in")
        IG["last_refresh"] = datetime.datetime.now().isoformat()
        json.dump(IG, open(CFG, "w", encoding="utf-8"), indent=2)
    return r.status_code, r.json()


def maybe_refresh(min_hours=24):
    """Refresh at most once/day so the long-lived token never lapses."""
    import datetime
    last = IG.get("last_refresh")
    if last:
        try:
            elapsed = (datetime.datetime.now() -
                       datetime.datetime.fromisoformat(last)).total_seconds()
            if elapsed < min_hours * 3600:
                return None
        except Exception:
            pass
    try:
        return refresh_token()[0]
    except Exception as ex:
        return ("refresh-error", str(ex))


# ---------------------------------------------------------------------------
# Container helpers
# ---------------------------------------------------------------------------

def publish_container(creation_id):
    r = requests.post(f"{GRAPH}/{IGID}/media_publish",
                      data={"creation_id": creation_id, "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()


def create_video_story_container(video_url):
    r = requests.post(f"{GRAPH}/{IGID}/media",
                      data={"media_type": "STORIES", "video_url": video_url,
                            "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()


def create_reel_container(video_url, caption):
    """Feed REEL (permanent post, shared to the main grid)."""
    r = requests.post(f"{GRAPH}/{IGID}/media",
                      data={"media_type": "REELS", "video_url": video_url,
                            "caption": caption[:2200], "share_to_feed": "true",
                            "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()


def poll_container(creation_id, tries=20, every=15):
    """Poll status_code until FINISHED/ERROR (video ingest is async; ~30-120 s)."""
    for _ in range(tries):
        r = requests.get(f"{GRAPH}/{creation_id}",
                         params={"fields": "status_code,status",
                                 "access_token": TOKEN}, timeout=30)
        st = r.json().get("status_code")
        if st in ("FINISHED", "ERROR", "EXPIRED"):
            return st, r.json()
        time.sleep(every)
    return "TIMEOUT", {}


# ---------------------------------------------------------------------------
# Public API — both accept a GitHub raw https:// URL directly
# ---------------------------------------------------------------------------

def post_video_story(video_url, publish=True):
    """STORIES video container → poll until FINISHED → publish.
    video_url: must be a publicly accessible https:// URL (GitHub raw or similar).
    publish=False = safe dry run (validates ingest, posts nothing)."""
    sc, cj = create_video_story_container(video_url)
    if sc != 200 or "id" not in cj:
        return {"ok": False, "stage": "container", "status": sc,
                "resp": cj, "video_url": video_url}
    st, sj = poll_container(cj["id"])
    if st != "FINISHED":
        return {"ok": False, "stage": "processing", "status_code": st,
                "resp": sj, "video_url": video_url, "creation_id": cj["id"]}
    if not publish:
        return {"ok": True, "stage": "ready_not_published",
                "creation_id": cj["id"], "video_url": video_url}
    sc2, pj = publish_container(cj["id"])
    return {"ok": sc2 == 200, "stage": "publish", "status": sc2,
            "resp": pj, "video_url": video_url}


def post_reel(video_url, caption, publish=True):
    """REELS container (SEO caption) → poll until FINISHED → publish.
    video_url: must be a publicly accessible https:// URL (GitHub raw or similar).
    publish=False = safe dry run (validates ingest, posts nothing)."""
    sc, cj = create_reel_container(video_url, caption)
    if sc != 200 or "id" not in cj:
        return {"ok": False, "stage": "container", "status": sc,
                "resp": cj, "video_url": video_url}
    st, sj = poll_container(cj["id"])
    if st != "FINISHED":
        return {"ok": False, "stage": "processing", "status_code": st,
                "resp": sj, "video_url": video_url, "creation_id": cj["id"]}
    if not publish:
        return {"ok": True, "stage": "ready_not_published",
                "creation_id": cj["id"], "video_url": video_url}
    cid = cj["id"]; sc2 = None; pj = None
    for _ in range(5):                         # eventual-consistency: wait + retry
        time.sleep(5)
        sc2, pj = publish_container(cid)
        if sc2 == 200 and isinstance(pj, dict) and "id" in pj:
            return {"ok": True, "stage": "publish", "status": sc2,
                    "resp": pj, "video_url": video_url}
    return {"ok": False, "stage": "publish", "status": sc2,
            "resp": pj, "video_url": video_url}
