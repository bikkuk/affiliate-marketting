# Posting-automation run (headless)

Working directory: `E:\CLAUDE\AFFILATE MARKETTING`. Do these steps in order,
stop and report if any step fails rather than skipping ahead silently.

1. Get the cutoff: run
   `python -c "import sys; sys.path.insert(0,'scripts'); import pipeline_state as p; print(p.read_last_run() or '2026-07-01')"`
   Use the printed value as `<cutoff>`.
2. `git -C "E:\CLAUDE\BRAIN MAIN" pull` — if this fails, STOP, do not write
   anything, leave `state/last_run.json` untouched.
3. `python scripts/scan_activity.py "E:\CLAUDE\BRAIN MAIN" <cutoff>` - read
   the JSON output. Each entry now carries `commits` (the real vault commits for
   that project in the window) and `now` (the project's current "## Now" text,
   for context when judging whether the commit is actually news).
4. **If the list is empty, do NOT assume it was a quiet week.** Run
   `python scripts/scan_activity.py "E:\CLAUDE\BRAIN MAIN" --health`.
   - Health **fails** (non-zero): STOP. Report loudly, write nothing, and leave
     `state/last_run.json` untouched. The vault format has moved and the scanner
     is blind. This exact failure ran undetected from the 2026-08-25 vault
     redesign until 2026-08-26: v1 of the scanner keyed on a "## Recent log"
     section that the redesign deleted, so it returned `[]` on every run while
     reporting success.
   - Health **passes**: the fortnight really was quiet. Log a no-op and skip to
     step 10.

   **The standing rule this encodes:** a producer that finds no input must say so
   loudly. An empty result and a broken reader must never look the same.
5. **WIP CAP CHECK, before drafting anything.** Count the `.md` files already in
   `pending/`. The blogs lane caps at **2** (`BRAIN MAIN/System/Exposure-Protocol.md`
   §5). If `pending/` already holds 2 or more, **draft nothing** - report that the
   queue is full and skip to step 10.

   This is the throttle rule: AI production is capped by measured review
   throughput. `pending/` once held three drafts for a month because production
   was uncapped and review was not. A full queue is a stop signal, not a backlog.

6. From the scanned entries, judge which (if any, 0-2) are genuinely
   content-worthy per `PROJECT_BRIEF.md`'s content rules (a real session, test,
   number, or decision — not routine noise). For each chosen entry, draft a
   journal entry into `pending/YYYY_MM_DD_slug.md`, first-person loose voice
   matching the four existing files already in `pending/` (not the earlier
   "TESTED" boilerplate format). Every numeric/measured claim must trace to the
   scanned `STATE.md` text; use `[Placeholder: ...]` otherwise.
7. For each drafted post, run:
   `python scripts/generate_hero_image.py <slug> design/hero_images`
   If it exits with code 2 (pc2 unreachable), do not fail the run — add
   `hero_image: null` and a `[Placeholder: hero image pending, pc2 unreachable
   at run time]` note to the post's frontmatter instead, and continue.
8. For every `state_md` path that appeared in step 3's output (whether or not
   it produced a post), run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\self_extract.py" "<state_md path>"`
   This appends candidate observations to `Projects/ADHD Data/observations.pending.md`
   via the existing hallucination-guarded pipeline. Do not promote anything to
   `observations.md` yourself — that stays a separate, existing manual step.
9. Run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\regenerate_profile.py" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\observations.md" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\PROFILE.md"`
10. `git add pending/ design/hero_images/` and commit in the bench-log repo
   (only if something changed). `git -C "E:\CLAUDE\BRAIN MAIN" add "Projects/ADHD Data/observations.pending.md" "Projects/ADHD Data/PROFILE.md"` and commit there too (only if something changed).
11. Update this project's `Projects/Local AI Bench Log/STATE.md` "Now" line
    to say how many drafts are waiting review.
12. Call `pipeline_state.write_last_run(<current UTC ISO timestamp>)` to move
    the cursor forward — only after every prior step succeeded (or was a
    deliberate, logged skip like the pc2-unreachable case).
