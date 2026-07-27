# Posting-automation run (headless)

Working directory: `E:\CLAUDE\AFFILATE MARKETTING`. Do these steps in order,
stop and report if any step fails rather than skipping ahead silently.

1. Get the cutoff: run
   `python -c "import sys; sys.path.insert(0,'scripts'); import pipeline_state as p; print(p.read_last_run() or '2026-07-01')"`
   Use the printed value as `<cutoff>`.
2. `git -C "E:\CLAUDE\BRAIN MAIN" pull` — if this fails, STOP, do not write
   anything, leave `state/last_run.json` untouched.
3. `python scripts/scan_activity.py "E:\CLAUDE\BRAIN MAIN" <cutoff>` — read
   the JSON output.
4. If the list is empty: skip to step 8 (no post, no image). If truly
   nothing at all happened, log a no-op and skip straight to step 9.
5. From the scanned entries, judge which (if any, 0-2) are genuinely
   content-worthy per `PROJECT_BRIEF.md`'s content rules (a real session, test,
   number, or decision — not routine noise). For each chosen entry, draft a
   journal entry into `pending/YYYY_MM_DD_slug.md`, first-person loose voice
   matching the four existing files already in `pending/` (not the earlier
   "TESTED" boilerplate format). Every numeric/measured claim must trace to the
   scanned `STATE.md` text; use `[Placeholder: ...]` otherwise.
6. For each drafted post, run:
   `python scripts/generate_hero_image.py <slug> design/hero_images`
   If it exits with code 2 (pc2 unreachable), do not fail the run — add
   `hero_image: null` and a `[Placeholder: hero image pending, pc2 unreachable
   at run time]` note to the post's frontmatter instead, and continue.
7. For every `state_md` path that appeared in step 3's output (whether or not
   it produced a post), run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\self_extract.py" "<state_md path>"`
   This appends candidate observations to `Projects/ADHD Data/observations.pending.md`
   via the existing hallucination-guarded pipeline. Do not promote anything to
   `observations.md` yourself — that stays a separate, existing manual step.
8. Run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\regenerate_profile.py" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\observations.md" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\PROFILE.md"`
9. `git add pending/ design/hero_images/` and commit in the bench-log repo
   (only if something changed). `git -C "E:\CLAUDE\BRAIN MAIN" add "Projects/ADHD Data/observations.pending.md" "Projects/ADHD Data/PROFILE.md"` and commit there too (only if something changed).
10. Update this project's `Projects/Local AI Bench Log/STATE.md` "Now" line
    to say how many drafts are waiting review.
11. Call `pipeline_state.write_last_run(<current UTC ISO timestamp>)` to move
    the cursor forward — only after every prior step succeeded (or was a
    deliberate, logged skip like the pc2-unreachable case).
