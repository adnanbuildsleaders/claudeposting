# -*- coding: utf-8 -*-
"""Cloud IG poster entry (runs in GitHub Actions at 10:00 / 13:00 / 17:00 IST).

Posts due Instagram outputs (video Story + feed Reel) for any blog whose post_at time has
arrived and whose WordPress post is live. YouTube Shorts are pre-scheduled separately via the
API (publishAt), so this only does IG. State (publish-tracker.json) is committed back by the workflow.
The reel mp4s ship in ./assets/<slug>.mp4 so no video rendering happens here."""
import os, time
import post_routine as R
import ig_story as S

BASE = os.path.dirname(os.path.abspath(__file__))

tr = R.load()
# point every blog's video_path at the committed asset (local Windows paths won't exist here)
for slug, e in tr.items():
    a = os.path.join(BASE, "assets", slug + ".mp4")
    if os.path.exists(a):
        e["video_path"] = a

S.maybe_refresh()
acts = [a for a in R.due_actions(tr) if a[1] in ("ig-video", "ig-reel")]   # IG only
print("due IG actions: %d" % len(acts), flush=True)
for i, (slug, kind) in enumerate(acts):
    ok, info = R.run_action(slug, kind, tr); R.save(tr)
    line = "[%d/%d] %-9s %-36s -> %s" % (i + 1, len(acts), kind, slug, "OK" if ok else "FAIL " + str(info)[:300])
    print(line.encode("ascii", "replace").decode(), flush=True)
    if i < len(acts) - 1:
        time.sleep(8)
R.save(tr)
print("cloud IG pass done", flush=True)
