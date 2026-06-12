# -*- coding: utf-8 -*-
"""Cloud IG poster entry (runs in GitHub Actions at 10:00 / 13:00 / 17:00 IST).

Posts due Instagram outputs (video Story + feed Reel) for any blog whose post_at time has
arrived and whose WordPress post is live (trusted via post_id existence — no WP API call).
YouTube Shorts are pre-scheduled separately via publishAt, so this does IG only.
State (publish-tracker.json) is committed back by the workflow after each run.

Videos are served from raw.githubusercontent.com (assets/<slug>.mp4 committed to this repo).
The repo must be PUBLIC so Instagram's servers can fetch the raw video URL."""
import os, time
import post_routine as R
import ig_story as S

tr = R.load()
S.maybe_refresh()

acts = R.due_actions(tr)

# Anti-flood cap: post at most ONE blog per run (its Story + Reel), oldest slot first.
# The */30 cron then drips one blog every ~30 min instead of dumping a whole backlog at
# once. Idempotent + self-correcting: even if cron clusters, each run clears just one blog.
if acts:
    def _when(slug):
        e = tr.get(slug, {})
        return e.get("post_at") or e.get("scheduled_dt") or "9999"
    oldest = min({s for s, _ in acts}, key=_when)
    acts = [(s, k) for (s, k) in acts if s == oldest]

print("due IG actions (capped to 1 blog/run): %d" % len(acts), flush=True)

for i, (slug, kind) in enumerate(acts):
    ok, info = R.run_action(slug, kind, tr)
    R.save(tr)
    line = "[%d/%d] %-9s %-36s -> %s" % (
        i + 1, len(acts), kind, slug, "OK" if ok else "FAIL " + str(info)[:300])
    print(line.encode("ascii", "replace").decode(), flush=True)
    if i < len(acts) - 1:
        time.sleep(8)

R.save(tr)
print("cloud IG pass done", flush=True)
