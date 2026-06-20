# -*- coding: utf-8 -*-
"""success_upload.py — upload curated B2C testimonial/marketing videos to YouTube as
UNLISTED (link-only) and register them in videos-manifest.json so the website's
Success Stories page (+ homepage) can embed them.

UNLISTED = not searchable, not on the channel page; only viewable via the embed/link
on the site — exactly what the founder asked for.

Prereq: `.yt_config.json` present with {client_id, client_secret, refresh_token}
(same OAuth used by the daily Shorts uploader). Then:

    py -3.11 success_upload.py            # upload the curated list, write manifest
    py -3.11 success_upload.py --push     # also commit+push the assets repo

If creds are missing it prints what to do and writes NOTHING.
"""
import os, json, subprocess, sys
import yt_upload as YT

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "videos-manifest.json")
B2C = r"D:\Claude\Habbinson Media\Habbinson Media\B2C"

# Curated, already-edited assets worth showing publicly (link-only).
CURATED = [
    {"slug": "habbinson-story", "title": "The Habbinson Story", "role": "Our story",
     "path": os.path.join(B2C, "For Marketing", "Habbinson - Story.mp4")},
    {"slug": "building-personalities", "title": "Building Personalities", "role": "Students, parents & teachers",
     "path": os.path.join(B2C, "For Marketing", "Habbinson - Building Personalities.mp4")},
    {"slug": "parent-nida-fallah", "title": "A Parent's Experience", "role": "Mrs. Nida Fallah, Parent",
     "path": os.path.join(B2C, "Testimonials", "Parents", "Interview with Nida Fallah_.mp4")},
    {"slug": "teacher-sachi", "title": "Why I Teach Here", "role": "Sachi Thawrani, Teacher",
     "path": os.path.join(B2C, "Testimonials", "Employees", "Sachi - Teacher.mp4")},
    {"slug": "student-experience", "title": "A Student's Experience", "role": "Habbinson student",
     "path": os.path.join(B2C, "Testimonials", "Students", "Experience(video).mp4")},
]

DESC = ("Habbinson - Personality & Entrepreneurship School. Live, small-batch classes that turn "
        "shy learners into confident communicators and young entrepreneurs. habbinson.com")


def _load():
    if os.path.exists(MANIFEST):
        try:
            return json.load(open(MANIFEST, encoding="utf-8"))
        except Exception:
            pass
    return {"videos": []}


def _save(data):
    seen, out = set(), []
    for v in data["videos"]:
        if v["slug"] in seen:
            continue
        seen.add(v["slug"]); out.append(v)
    data["videos"] = out
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run():
    if not YT.configured():
        print("YouTube is NOT configured (.yt_config.json missing client_id/secret/refresh_token).")
        print("Add it (same OAuth as the daily Shorts uploader), then re-run. Nothing uploaded.")
        return
    data = _load()
    have = {v["slug"] for v in data["videos"] if v.get("youtubeId")}
    for item in CURATED:
        if item["slug"] in have:
            print("skip (already uploaded):", item["slug"]); continue
        if not os.path.exists(item["path"]):
            print("skip (missing file):", item["path"]); continue
        size_mb = os.path.getsize(item["path"]) / 1e6
        print(f"uploading {item['slug']} ({size_mb:.0f} MB) as UNLISTED ...")
        res = YT.upload_short(item["path"], item["title"],
                              f"{item['title']} - {item['role']}\n\n{DESC}",
                              tags=["Habbinson", "communication", "entrepreneurship"],
                              privacy="unlisted")
        if res.get("ok"):
            entry = {"slug": item["slug"], "title": item["title"], "role": item["role"],
                     "youtubeId": res["video_id"]}
            data["videos"] = [v for v in data["videos"] if v["slug"] != item["slug"]] + [entry]
            _save(data)
            print("  ok ->", res["video_id"])
        else:
            print("  FAILED:", res)
    print("manifest:", MANIFEST)


def git_push(message="Add success-story videos manifest"):
    try:
        subprocess.run(["git", "-C", HERE, "add", "videos-manifest.json"], check=True)
        subprocess.run(["git", "-C", HERE, "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", HERE, "push"], check=True)
        print("pushed")
    except subprocess.CalledProcessError as e:
        print("git push skipped/failed:", e)


if __name__ == "__main__":
    run()
    if "--push" in sys.argv:
        git_push()
