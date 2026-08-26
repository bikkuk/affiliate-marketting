#!/usr/bin/env python3
"""
scan_activity.py - collect real project activity from the Main Brain vault,
dated strictly after a cutoff. Pure parsing, no LLM calls.

WHY THIS WAS REWRITTEN (2026-08-26)
-----------------------------------
v1 read "## Recent log" bullet sections out of each project's STATE.md. The
2026-08-25 vault redesign split the per-project record and retired that section:
as of the rewrite, **0 of 38 STATE.md files contained "## Recent log"**. So the
scan returned [] on every run, the pipeline dutifully concluded "nothing
happened", wrote nothing, and reported success. It had been doing that silently
since the redesign.

v2 derives activity from the vault's **git history** instead. Git cannot silently
stop existing the way a hand-maintained prose section can, and the dates are real
rather than whatever an agent remembered to type.

Two kinds of noise get filtered, because both would otherwise drown the signal:

  * **Bulk sweeps.** One commit touching many projects is infrastructure (the
    vault split touched all 38). Real project work touches one or two.
  * **Housekeeping commits.** Session checkpoints, generated board/PULSE
    regeneration - motion without news.

Usage:
  python scripts/scan_activity.py <brain_main_path> <cutoff YYYY-MM-DD>
  python scripts/scan_activity.py <brain_main_path> --health

--health verifies the scanner's assumptions about the vault still hold, and
exits non-zero if they don't. Run it whenever the scan comes back empty: an
empty scan is either "a quiet fortnight" or "the format moved again", and those
two must never be indistinguishable again.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

# A commit touching more than this many distinct projects is a sweep, not news.
BULK_THRESHOLD = 4

# Commit subjects that represent motion rather than news.
NOISE_SUBJECT = re.compile(
    r"^(auto:|chore:|board:|pulse|regenerate|vault:|merge branch|"
    r"wip\b|typo\b|formatting\b)",
    re.I,
)

PROJECT_PATH = re.compile(r"^Projects/([^/]+)/")

# Vault prose carries emoji; Windows stdout defaults to cp1252 and would raise
# UnicodeEncodeError mid-write, leaving the caller with truncated JSON.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(repo, *args):
    out = subprocess.run(
        ["git", "-C", str(repo)] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if out.returncode != 0:
        raise RuntimeError(
            "git %s failed: %s"
            % (" ".join(args), out.stderr.decode("utf-8", "replace")[:300])
        )
    return out.stdout.decode("utf-8", "replace")


def read_commits(brain_main, cutoff):
    """Yield {subject, date, projects[]} for vault commits after cutoff."""
    raw = git(
        brain_main, "log", "--since=%s" % cutoff, "--name-only",
        "--format=%x00%ad%x01%s", "--date=short", "--", "Projects/",
    )
    commits = []
    for chunk in raw.split("\x00"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        head, _, files = chunk.partition("\n")
        date, _, subject = head.partition("\x01")
        projects = set()
        for line in files.splitlines():
            m = PROJECT_PATH.match(line.strip())
            if m:
                projects.add(m.group(1))
        if projects:
            commits.append({
                "date": date.strip(),
                "subject": subject.strip(),
                "projects": sorted(projects),
            })
    return commits


def now_excerpt(state_md, limit=700):
    """The project's current '## Now' text - context for judging the commit."""
    if not state_md.exists():
        return ""
    lines = state_md.read_text(encoding="utf-8", errors="replace").splitlines()
    out, capturing = [], False
    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            capturing = line.strip().lower().startswith("## now")
            continue
        if capturing:
            out.append(line)
    return "\n".join(out).strip()[:limit]


def scan(brain_main, cutoff, bulk_threshold=BULK_THRESHOLD):
    brain_main = pathlib.Path(brain_main)
    per_project = {}
    for c in read_commits(brain_main, cutoff):
        if len(c["projects"]) > bulk_threshold:
            continue                      # infrastructure sweep
        if NOISE_SUBJECT.match(c["subject"]):
            continue                      # motion, not news
        if c["date"] <= cutoff:
            continue
        for proj in c["projects"]:
            per_project.setdefault(proj, []).append(
                {"date": c["date"], "subject": c["subject"]}
            )

    results = []
    for proj, commits in per_project.items():
        state_md = brain_main / "Projects" / proj / "STATE.md"
        commits.sort(key=lambda x: x["date"])
        results.append({
            "project": proj,
            "date": commits[-1]["date"],
            # 'text' kept for compatibility with run_pipeline_prompt.md
            "text": " · ".join(c["subject"] for c in commits),
            "commits": commits,
            "state_md": str(state_md),
            "now": now_excerpt(state_md),
        })
    results.sort(key=lambda e: e["date"])
    return results


def health(brain_main):
    """Assert the vault still looks the way this scanner expects."""
    brain_main = pathlib.Path(brain_main)
    problems, notes = [], []

    if not (brain_main / ".git").exists():
        problems.append("no .git at %s - cannot read history" % brain_main)
    else:
        try:
            n = len(read_commits(brain_main, "1970-01-01"))
            notes.append("git readable, %d project-touching commits all-time" % n)
            if n == 0:
                problems.append("git has no commits touching Projects/ at all")
        except RuntimeError as e:
            problems.append(str(e))

    states = sorted((brain_main / "Projects").glob("*/STATE.md"))
    notes.append("%d STATE.md files found" % len(states))
    if not states:
        problems.append("no Projects/*/STATE.md - vault layout moved")
    else:
        with_now = sum(1 for s in states if now_excerpt(s))
        notes.append("%d of %d have a readable '## Now'" % (with_now, len(states)))
        if with_now == 0:
            problems.append(
                "NO STATE.md has a '## Now' section - the format moved again, "
                "exactly the failure that killed v1 of this scanner"
            )

    for line in notes:
        print("  ok   %s" % line)
    for line in problems:
        print("  FAIL %s" % line)
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brain_main_path")
    ap.add_argument("cutoff_date", nargs="?",
                    help="YYYY-MM-DD; entries strictly after this are returned")
    ap.add_argument("--health", action="store_true",
                    help="verify the scanner's assumptions, exit non-zero if broken")
    ap.add_argument("--bulk-threshold", type=int, default=BULK_THRESHOLD)
    args = ap.parse_args()

    if args.health:
        print("scan_activity health check:")
        return health(args.brain_main_path)

    if not args.cutoff_date:
        ap.error("cutoff_date is required unless --health is given")

    out = scan(args.brain_main_path, args.cutoff_date, args.bulk_threshold)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
