# -*- coding: utf-8 -*-
"""Cloud IG Reel poster for EDITED reels (runs in GitHub Actions next to cloud_post.py).
Reads reels.json; for each reel whose post_at slot has arrived and isn't posted yet, publishes it
as an Instagram feed Reel from its public raw URL, then marks ig_done. Idempotent (never double-posts).
YouTube is handled separately by reel_publish.py via native publishAt — not here."""
import json, os, datetime, time
import ig_story as S

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
TR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reels.json")


def load():
    try: return json.load(open(TR, encoding="utf-8"))
    except Exception: return {}
def save(t): json.dump(t, open(TR, "w", encoding="utf-8"), indent=2, default=str)


tr = load()
S.maybe_refresh()
now = datetime.datetime.now(IST)
# An edited reel is due if its slot has passed and EITHER output (Story or Reel) is still pending.
due = [(rid, e) for rid, e in tr.items()
       if now >= datetime.datetime.fromisoformat(e["post_at"])
       and not (e.get("ig_story_done") and e.get("ig_reel_done"))]
print("due IG reels:", len(due), flush=True)
posted = 0
for i, (rid, e) in enumerate(due):
    cap = e.get("caption", "")
    # (a) video Story
    if not e.get("ig_story_done"):
        r = S.post_video_story(e["raw_url"], publish=True)
        if r.get("ok"):
            e["ig_story_done"] = True; e["ig_story_id"] = r.get("id"); posted += 1; save(tr)
            print("posted story", rid, flush=True)
        else:
            print("FAIL story", rid, str(r)[:240], flush=True)
        time.sleep(8)
    # (b) feed Reel
    if not e.get("ig_reel_done"):
        r = S.post_reel(e["raw_url"], cap, publish=True)
        if r.get("ok"):
            e["ig_reel_done"] = True; e["ig_reel_id"] = r.get("id"); posted += 1; save(tr)
            print("posted reel", rid, flush=True)
        else:
            print("FAIL reel", rid, str(r)[:240], flush=True)
    if i < len(due) - 1:
        time.sleep(8)
save(tr)
print("cloud reels pass done; posted", posted, flush=True)
