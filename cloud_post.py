# -*- coding: utf-8 -*-
"""Cloud IG poster entry (runs in GitHub Actions at 10:00 / 13:00 / 17:00 IST).

Posts due Instagram outputs (video Story + feed Reel) for any blog whose post_at time has
arrived and whose WordPress post is live (trusted via post_id existence — no WP API call).
YouTube Shorts are pre-scheduled separately via publishAt, so this does IG only.
State (publish-tracker.json) is committed back by the workflow after each run.

Videos are served from raw.githubusercontent.com (assets/<slug>.mp4 committed to this repo).
The repo must be PUBLIC so Instagram's servers can fetch the raw video URL."""
import os, time, datetime
import post_routine as R
import ig_story as S

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
TODAY = datetime.datetime.now(IST).strftime("%Y-%m-%d")

tr = R.load()
S.maybe_refresh()

acts = R.due_actions(tr)

# CHANGE 3 — ONE POST PER CALENDAR DAY. A second same-day IG post cannibalises the first's reach
# (~40% less, per the analytics audit). If we've already posted today, hold the rest for tomorrow.
meta = tr.get("_meta", {})
if acts and meta.get("last_ig_post_date") == TODAY:
    print("1/day cap: already posted on %s -> skipping until tomorrow." % TODAY, flush=True)
    acts = []

# Anti-flood: of whatever is still due, post only the OLDEST single blog this run; the next day's
# run takes the next one. Idempotent + self-correcting even if the cron clusters.
if acts:
    def _when(slug):
        e = tr.get(slug, {})
        return e.get("post_at") or e.get("scheduled_dt") or "9999"
    oldest = min({s for s, _ in acts}, key=_when)
    acts = [(s, k) for (s, k) in acts if s == oldest]

print("due IG actions (<=1 blog, <=1/day): %d" % len(acts), flush=True)

posted = False
for i, (slug, kind) in enumerate(acts):
    ok, info = R.run_action(slug, kind, tr)
    if ok:
        posted = True
    R.save(tr)
    line = "[%d/%d] %-9s %-36s -> %s" % (
        i + 1, len(acts), kind, slug, "OK" if ok else "FAIL " + str(info)[:300])
    print(line.encode("ascii", "replace").decode(), flush=True)
    if i < len(acts) - 1:
        time.sleep(8)

if posted:                                  # record the day so no 2nd post fires before tomorrow
    meta["last_ig_post_date"] = TODAY
    tr["_meta"] = meta

R.save(tr)
print("cloud IG pass done", flush=True)
