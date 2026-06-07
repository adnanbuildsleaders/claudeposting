# -*- coding: utf-8 -*-
"""YouTube Short uploader via Data API v3 (resumable, pure requests).
Reads .yt_config.json {client_id, client_secret, refresh_token}. upload_short(...) -> {ok, video_id}."""
import os, json, requests

BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(BASE, ".yt_config.json")

def _cfg(): return json.load(open(CFG, encoding="utf-8"))
def configured():
    if not os.path.exists(CFG): return False
    c = _cfg(); return all(c.get(k) for k in ("client_id", "client_secret", "refresh_token"))

def access_token():
    c = _cfg()
    r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"], "grant_type": "refresh_token"})
    r.raise_for_status(); return r.json()["access_token"]

def upload_short(video_path, title, description, tags=None, privacy="public", category="27", publish_at=None):
    """Upload a vertical <3min video as a Short. If publish_at (RFC3339 UTC, e.g. '2026-06-08T04:30:00Z')
    is given, the video uploads as PRIVATE and YouTube auto-publishes it PUBLIC at that time (PC can be off)."""
    tok = access_token()
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status["privacyStatus"] = "private"        # required for scheduled publishing
        status["publishAt"] = publish_at
    meta = {"snippet": {"title": title[:100], "description": description[:4900],
                        "tags": tags or [], "categoryId": category},
            "status": status}
    sz = os.path.getsize(video_path)
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/*", "X-Upload-Content-Length": str(sz)},
        data=json.dumps(meta), timeout=60)
    if r.status_code not in (200, 201) or "Location" not in r.headers:
        return {"ok": False, "stage": "init", "status": r.status_code, "resp": r.text[:400]}
    up = r.headers["Location"]
    with open(video_path, "rb") as f: body = f.read()
    r2 = requests.put(up, headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/*",
                                   "Content-Length": str(sz)}, data=body, timeout=600)
    if r2.status_code in (200, 201):
        return {"ok": True, "video_id": r2.json().get("id"), "resp": r2.json()}
    return {"ok": False, "stage": "upload", "status": r2.status_code, "resp": r2.text[:400]}

if __name__ == "__main__":
    print("configured:", configured())
