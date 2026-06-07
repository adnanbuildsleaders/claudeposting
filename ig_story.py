# -*- coding: utf-8 -*-
"""Instagram Story publisher via the Instagram Graph API (Instagram Login).
Pipeline: render PNG -> JPEG -> host on WP media (public URL) -> create STORIES container -> publish.
Token is long-lived (60d) and auto-refreshable without the app secret."""
import os, json, time, mimetypes, tempfile, requests
from PIL import Image
import wp_publish as WP
import blog_image_engine as IMG

BASE = os.path.dirname(os.path.abspath(__file__))
CFG  = os.path.join(BASE, ".ig_config.json")
IG   = json.load(open(CFG, encoding="utf-8"))
TOKEN = IG["access_token"]; IGID = IG["ig_user_id"]
GRAPH = "https://graph.instagram.com"

def refresh_token():
    """Extend the 60-day long-lived token (no app secret needed)."""
    import datetime
    r = requests.get(f"{GRAPH}/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": IG["access_token"]}, timeout=30)
    if r.status_code == 200 and "access_token" in r.json():
        IG["access_token"] = r.json()["access_token"]; IG["token_expires_in_sec"] = r.json().get("expires_in")
        IG["last_refresh"] = datetime.datetime.now().isoformat()
        json.dump(IG, open(CFG, "w", encoding="utf-8"), indent=2)
    return r.status_code, r.json()

def maybe_refresh(min_hours=24):
    """Refresh at most once/day so the long-lived token never lapses."""
    import datetime
    last = IG.get("last_refresh")
    if last:
        try:
            if (datetime.datetime.now() - datetime.datetime.fromisoformat(last)).total_seconds() < min_hours*3600:
                return None
        except Exception: pass
    try: return refresh_token()[0]
    except Exception as ex: return ("refresh-error", str(ex))

def _to_jpeg(png_path):
    im = Image.open(png_path).convert("RGB")
    jpg = png_path.rsplit(".", 1)[0] + ".jpg"; im.save(jpg, "JPEG", quality=92)
    return jpg

def host_on_wp(image_path, alt="adnanbuildsleaders new blog", title="habbinson blog story"):
    fn = os.path.basename(image_path); ct = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    with open(image_path, "rb") as f:
        r = requests.post(f"{WP.API}/media", auth=WP.AUTH, timeout=120,
                          headers={"Content-Disposition": f'attachment; filename="{fn}"', "Content-Type": ct},
                          data=f.read())
    r.raise_for_status(); j = r.json()
    requests.post(f"{WP.API}/media/{j['id']}", auth=WP.AUTH, timeout=30, json={"alt_text": alt, "title": title})
    return j["id"], j["source_url"]

def create_story_container(image_url):
    r = requests.post(f"{GRAPH}/{IGID}/media",
                      data={"media_type": "STORIES", "image_url": image_url, "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()

def publish_container(creation_id):
    r = requests.post(f"{GRAPH}/{IGID}/media_publish",
                      data={"creation_id": creation_id, "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()

def create_video_story_container(video_url):
    r = requests.post(f"{GRAPH}/{IGID}/media",
                      data={"media_type": "STORIES", "video_url": video_url, "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()

def create_reel_container(video_url, caption):
    """Feed REEL (permanent post, shared to the main grid). caption = SEO text + hashtags."""
    r = requests.post(f"{GRAPH}/{IGID}/media",
                      data={"media_type": "REELS", "video_url": video_url, "caption": caption[:2200],
                            "share_to_feed": "true", "access_token": TOKEN}, timeout=60)
    return r.status_code, r.json()

def poll_container(creation_id, tries=20, every=15):
    """Poll status_code until FINISHED/ERROR (video ingest is async; ~30-120s)."""
    for _ in range(tries):
        r = requests.get(f"{GRAPH}/{creation_id}", params={"fields": "status_code,status", "access_token": TOKEN}, timeout=30)
        st = r.json().get("status_code")
        if st in ("FINISHED", "ERROR", "EXPIRED"): return st, r.json()
        time.sleep(every)
    return "TIMEOUT", {}

def post_reel(video_path, caption, publish=True):
    """Host mp4 on WP -> REELS container (with SEO caption) -> poll until FINISHED -> publish.
    publish=False = safe dry run (validates ingest, posts nothing)."""
    mid, url = host_on_wp(video_path, alt="adnanbuildsleaders parenting reel", title="habbinson parenting reel")
    sc, cj = create_reel_container(url, caption)
    if sc != 200 or "id" not in cj:
        return {"ok": False, "stage": "container", "status": sc, "resp": cj, "video_url": url}
    st, sj = poll_container(cj["id"])
    if st != "FINISHED":
        return {"ok": False, "stage": "processing", "status_code": st, "resp": sj, "video_url": url, "creation_id": cj["id"]}
    if not publish:
        return {"ok": True, "stage": "ready_not_published", "creation_id": cj["id"], "video_url": url}
    cid = cj["id"]; sc2 = None; pj = None
    for _ in range(5):                       # eventual-consistency: wait + retry publish
        time.sleep(5)
        sc2, pj = publish_container(cid)
        if sc2 == 200 and isinstance(pj, dict) and "id" in pj:
            return {"ok": True, "stage": "publish", "status": sc2, "resp": pj, "video_url": url}
    return {"ok": False, "stage": "publish", "status": sc2, "resp": pj, "video_url": url}

def post_video_story(video_path, publish=True):
    """Host mp4 on WP -> STORIES video container -> poll until FINISHED -> publish. publish=False = safe dry run."""
    mid, url = host_on_wp(video_path, alt="adnanbuildsleaders blog short", title="habbinson blog video story")
    sc, cj = create_video_story_container(url)
    if sc != 200 or "id" not in cj:
        return {"ok": False, "stage": "container", "status": sc, "resp": cj, "video_url": url}
    st, sj = poll_container(cj["id"])
    if st != "FINISHED":
        return {"ok": False, "stage": "processing", "status_code": st, "resp": sj, "video_url": url, "creation_id": cj["id"]}
    if not publish:
        return {"ok": True, "stage": "ready_not_published", "creation_id": cj["id"], "video_url": url}
    sc2, pj = publish_container(cj["id"])
    return {"ok": sc2 == 200, "stage": "publish", "status": sc2, "resp": pj, "video_url": url}

def post_story(image_path, publish=True):
    """Full flow. publish=False stops after container creation (nothing goes public — safe test)."""
    jpg = _to_jpeg(image_path); mid, url = host_on_wp(jpg)
    sc, cj = create_story_container(url)
    if sc != 200 or "id" not in cj:
        return {"ok": False, "stage": "container", "status": sc, "resp": cj, "image_url": url}
    if not publish:
        return {"ok": True, "stage": "container_only", "creation_id": cj["id"], "image_url": url}
    cid = cj["id"]; sc2 = None; pj = None
    for _ in range(5):                       # eventual-consistency: wait + retry publish
        time.sleep(5)
        sc2, pj = publish_container(cid)
        if sc2 == 200 and isinstance(pj, dict) and "id" in pj:
            return {"ok": True, "stage": "publish", "status": sc2, "resp": pj, "image_url": url}
    return {"ok": False, "stage": "publish", "status": sc2, "resp": pj, "image_url": url}

if __name__ == "__main__":
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, "s.png")
    IMG.render_story("Stop Calling Your Child SMART", "SMART", "growth", "sunny", "scheduled", "JUN 4 · 10 AM IST", p)
    res = post_story(p, publish=False)   # SAFE: builds container only, does NOT post to the profile
    print(json.dumps(res, indent=2))
