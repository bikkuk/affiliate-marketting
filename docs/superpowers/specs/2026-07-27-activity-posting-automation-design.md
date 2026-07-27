# Activity-Based Posting Automation + Behavioral Profiler — Design

Status: approved by user 2026-07-27, ready for implementation plan.

## Problem

`published/` has had exactly one post since launch (2026-07-24), three days ago, against the intended
2-3 day cadence. Nothing feeds `pending/` automatically — every draft so far has been hand-triggered in
a live session. Separately, the user wants a standing, meticulous behavioral-pattern profile of himself,
built as a byproduct of this same activity data, without forking a second observation system alongside
the one that already exists in [[ADHD Data]].

## Decisions made during brainstorming

1. **Extend ADHD Data, don't fork.** The profiler lives in `Projects/ADHD Data/`, not inside the
   affiliate project. It reuses the existing `observations.md` / `observations.pending.md` quarantine +
   verbatim-quote-verification pipeline already defined in `Projects/ADHD Data/pipeline.md`.
2. **Standing profile document, not just a log.** In addition to the existing dated observations log, a
   new `Projects/ADHD Data/PROFILE.md` synthesizes accumulated *promoted* observations into a structured,
   living behavioral-pattern document. Regenerated on the same cadence as the content pipeline.
3. **Scanner scope: all active projects in `System/ACTIVE.md`**, not just the LocalKI/Klarverk niche
   `PROJECT_BRIEF.md` originally scoped the site to. This is an explicit, user-approved deviation from
   that brief — noted here so a future session doesn't "fix" it back without asking. The niche scope
   still governs which scanned items are worth turning into a *public post*; the scanner itself casts
   wider because the profiler benefits from seeing everything, not just AI-consulting work.
4. **pc2 asset type: abstract/mood hero image only.** No generated diagrams, no fabricated screenshots
   or charts — those would risk presenting invented data as real, which `PROJECT_BRIEF.md`'s content
   rules explicitly forbid.
5. **Runs locally, not as a cloud routine.** The existing "Bench Log - Substack Morning Packet" cloud
   routine only clones one GitHub repo and can't reach pc2 (home LAN only) or local-disk-only project
   folders. This pipeline needs both, so it runs as a **Windows Scheduled Task** invoking a headless
   Claude Code session on PC1 every 2-3 days, not a `claude.ai` cloud routine.

## Architecture

```
Windows Scheduled Task (every 2-3 days)
        |
        v
headless Claude Code run, working dir = E:\CLAUDE\AFFILATE MARKETTING
        |
        1. read state/last_run.json (timestamp of previous run)
        2. git pull E:\CLAUDE\BRAIN MAIN (brain-main.git)
        3. for each project row in System/ACTIVE.md:
             read Projects/<name>/STATE.md "Recent log" section
             collect entries dated after last_run
        4. from collected entries:
             a. select 0-2 real, concrete, content-worthy items -> draft journal
                entries into pending/ (humanized voice, per WORKFLOW.md format,
                content rules: real basis only, no invented numbers)
             b. append candidate dated behavioral observations for ALL collected
                entries (not just the ones chosen for posts) into
                Projects/ADHD Data/observations.pending.md, each with its
                verbatim source quote for the existing verification step
        5. for each drafted post: call pc2 ComfyUI -> one abstract/mood hero
           image, saved under design/ or public/ in the bench-log repo,
           referenced from the post's frontmatter
        6. regenerate Projects/ADHD Data/PROFILE.md from current
           observations.md (promoted only)
        7. commit pending/ + PROFILE.md changes (two separate repos: bench-log
           repo for pending/+images, brain-main repo for observations/PROFILE.md)
        8. update this project's STATE.md "Now" line: "N drafts waiting review"
        9. write state/last_run.json with this run's timestamp
```

Nothing in `pending/` auto-publishes. Approval still happens exactly per `WORKFLOW.md`: the user reviews
next time they're in a live session, replies approve/edit/drop.

## Components

### 1. `scripts/scan_activity.py` (bench-log repo)
- Input: path to a local clone/checkout of `brain-main`, last-run timestamp.
- Reads `System/ACTIVE.md` project table, opens each linked `STATE.md`, extracts "Recent log" bullets
  with a date after the cutoff.
- Output: a list of `{project, date, text}` structured entries. No LLM call in this step — pure parsing.

### 2. Draft step (Claude Code, in-session — not a separate script)
- Given the structured entries from step 1, judge which (if any) are genuinely content-worthy (a real
  session, test, number, or decision — matches `PROJECT_BRIEF.md`'s content rules) versus routine noise.
- Draft 0-2 entries in the loose, first-person voice established by the four existing `pending/` drafts
  (see those as the style reference, not the earlier "TESTED" boilerplate format).
- Every numeric or measured claim must trace to something actually in the source `STATE.md` entry; use
  `[Placeholder: ...]` per existing convention when a real figure isn't available yet.

### 3. `scripts/generate_hero_image.py` (bench-log repo)
- Calls the pc2 ComfyUI MCP/HTTP endpoint (same access pattern already used elsewhere in this vault) with
  a fixed abstract/mood prompt template (hardware, terminal glow, cable/workstation motifs — no attempt
  to depict specific unverified content).
- Saves output image into the repo, filename matched to the post slug.

### 4. `scripts/append_observations.py` (writes into brain-main's ADHD Data folder)
- For every structured entry from step 1 (whether or not it became a post), append a candidate dated
  observation to `Projects/ADHD Data/observations.pending.md`, each carrying its exact source quote —
  reuses the existing hallucination-guard rule from `Projects/ADHD Data/pipeline.md` verbatim.
- Does not touch `observations.md` directly; promotion out of `.pending.md` stays a separate, existing
  step per current ADHD Data pipeline rules.

### 5. `Projects/ADHD Data/PROFILE.md` (new, regenerated each run)
- Sections: Working rhythm & cadence, Focus/attention patterns, Decision-making tendencies,
  Project-engagement patterns, Communication/collaboration style, Other recurring behaviors.
- **Guardrail: a pattern only gets a line in PROFILE.md once at least 2-3 corroborating promoted
  observations support it.** Single-incident observations stay in `observations.md` only, not
  synthesized up.
- No clinical or diagnostic-sounding language — this is an observed-behavior document, not an assessment.
  Describe what was seen and when, not what it means about the person.
- Fully regenerated (not appended) each run, from the current state of `observations.md`, so it never
  drifts from what's actually been verified.

### 6. `state/last_run.json` (bench-log repo, gitignored is fine — it's just a cursor)
- `{ "last_run": "<ISO timestamp>" }`. Written at the end of a successful run only.

## Error handling / edge cases
- No new "Recent log" entries since last run: skip drafting and image generation, still safe to touch
  observations/profile if anything new happened between entries, log a no-op line, don't force a post.
- pc2 unreachable (SSH tunnel down): draft the post text anyway, skip the image, note
  `[Placeholder: hero image pending, pc2 unreachable at run time]` in frontmatter so it's visibly
  incomplete rather than silently missing.
- brain-main pull fails / conflicts: abort the run, do not attempt any writes, leave `last_run.json`
  untouched so the next scheduled run retries the same window.

## Out of scope (explicitly not building now)
- Any auto-publish path — WORKFLOW.md's manual approval gate is unchanged.
- Social-platform posting (already deferred by `PROJECT_BRIEF.md`).
- Diagram/chart-style pc2 assets (mood image only, per decision 4 above).
- Promotion automation from `observations.pending.md` to `observations.md` (stays whatever the existing
  ADHD Data process already is).
