# -*- coding: utf-8 -*-
"""WordPress REST publisher for Habbinson blogs (schedule as `future`)."""
import os, json, datetime, mimetypes, requests

BASE = os.path.dirname(os.path.abspath(__file__))  # Code\ folder (holds configs + state)
CONTENT = os.path.join(os.path.dirname(BASE), "Kids-Communication-Scripts")
CFG = json.load(open(os.path.join(BASE, ".wp_config.json"), encoding="utf-8"))
SITE = CFG["site"].rstrip("/"); API = SITE + "/wp-json/wp/v2"
AUTH = (CFG["username"], CFG["app_password"])
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
UTC = datetime.timezone.utc
SLOTLOG = os.path.join(BASE, "wp-schedule-log.json")
TRACKER = os.path.join(BASE, "publish-tracker.json")

def _load(p, default):
    if os.path.exists(p):
        try: return json.load(open(p, encoding="utf-8"))
        except Exception: pass
    return default
def _save(p, obj): json.dump(obj, open(p, "w", encoding="utf-8"), indent=2, default=str)

def next_slots(n):
    log = _load(SLOTLOG, {})
    last = log.get("last_slot")
    after = datetime.datetime.fromisoformat(last) if last else datetime.datetime.now(IST)
    now = datetime.datetime.now(IST)
    cursor = max(after, now)
    slots = []; day = cursor.date()
    while len(slots) < n:
        for hh in (10, 17):
            s = datetime.datetime.combine(day, datetime.time(hh, 0), IST)
            if s > cursor: slots.append(s)
            if len(slots) >= n: break
        day += datetime.timedelta(days=1)
    return slots

def commit_slot(slot):
    log = _load(SLOTLOG, {}); log["last_slot"] = slot.isoformat(); _save(SLOTLOG, log)

def get_or_create_category(name):
    r = requests.get(f"{API}/categories", params={"search": name}, auth=AUTH, timeout=30)
    for c in r.json():
        if c["name"].lower() == name.lower(): return c["id"]
    r = requests.post(f"{API}/categories", json={"name": name}, auth=AUTH, timeout=30)
    return r.json()["id"]

def ensure_tags(names):
    ids = []
    for nm in names:
        r = requests.get(f"{API}/tags", params={"search": nm}, auth=AUTH, timeout=30)
        found = next((t["id"] for t in r.json() if t["name"].lower() == nm.lower()), None)
        if not found:
            rr = requests.post(f"{API}/tags", json={"name": nm}, auth=AUTH, timeout=30)
            found = rr.json().get("id")
        if found: ids.append(found)
    return ids

def upload_media(path, alt, title):
    fn = os.path.basename(path); ct = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        r = requests.post(f"{API}/media", auth=AUTH, timeout=120,
                          headers={"Content-Disposition": f'attachment; filename="{fn}"', "Content-Type": ct},
                          data=f.read())
    r.raise_for_status(); mid = r.json()["id"]
    requests.post(f"{API}/media/{mid}", auth=AUTH, timeout=30,
                  json={"alt_text": alt, "title": title})
    return mid

def schedule_post(title, slug, html, excerpt, yoast, featured_media, slot, categories, tags):
    slot_utc = slot.astimezone(UTC)
    payload = {
        "title": title, "slug": slug, "content": html, "excerpt": excerpt,
        "author": CFG.get("author_id"),
        "status": "future",
        "date": slot.strftime("%Y-%m-%dT%H:%M:%S"),
        "date_gmt": slot_utc.strftime("%Y-%m-%dT%H:%M:%S"),
        "featured_media": featured_media, "categories": categories, "tags": tags,
        "meta": {
            "_yoast_wpseo_title": yoast["title"],
            "_yoast_wpseo_metadesc": yoast["metadesc"],
            "_yoast_wpseo_focuskw": yoast["focuskw"],
        },
    }
    r = requests.post(f"{API}/posts", auth=AUTH, json=payload, timeout=60)
    if r.status_code >= 400:
        # retry without meta (mu-plugin may not be installed yet)
        payload.pop("meta", None)
        r = requests.post(f"{API}/posts", auth=AUTH, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def reserve_slot():
    """Return the next free 10:00/17:00 IST slot and commit it (so building can show the date)."""
    slot = next_slots(1)[0]; commit_slot(slot); return slot

def publish_blog(blog, featured_png, html, slot=None):
    cat = get_or_create_category("Parenting")
    media = upload_media(featured_png, alt=blog["primary"], title=blog["slug"])
    tags = ensure_tags(blog["secondary"][:4])
    if slot is None:
        slot = next_slots(1)[0]; commit_slot(slot)
    post = schedule_post(blog["h1"], blog["slug"], html, blog["meta"],
                         {"title": blog["seo_title"], "metadesc": blog["meta"], "focuskw": blog["primary"]},
                         media, slot, [cat], tags)
    # tracker
    tr = _load(TRACKER, {})
    tr[blog["slug"]] = {"wp_post_id": post["id"], "scheduled_dt": slot.isoformat(),
                        "link": post.get("link"), "edit": f"{SITE}/wp-admin/post.php?post={post['id']}&action=edit",
                        "yoast_set": "meta" in post, "story_scheduled_done": False, "published_done": False}
    _save(TRACKER, tr)
    return {"id": post["id"], "slot": slot.isoformat(), "status": post["status"],
            "edit": tr[blog["slug"]]["edit"], "link": post.get("link"), "media": media}
