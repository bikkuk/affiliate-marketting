# Workflow

## Folder structure

```
site/
  content/
    posts/          one markdown file per journal entry
    newsletter/      one markdown file per newsletter issue
  pending/           drafts waiting on review, nothing here is public yet
  published/         approved entries, mirrors what is live on the site
  design/
  src/               the actual Astro site, built and owned by Claude Code
WORKFLOW.md
PROJECT_BRIEF.md
SETUP_CHECKLIST.md
```

Post filenames: `YYYY_MM_DD_short_slug.md`. Underscores, not hyphens, so the convention stays consistent everywhere in this kit.

## The pipeline

1. A real session happens somewhere, LocalKI, AI Clone, a ComfyUI test, a client build, anything with an actual result.
2. Claude Code reads what happened and drafts a journal entry into `pending/`. Same for a newsletter issue once there are two or three entries to digest.
3. Claude Code shows the draft to Nipoon directly in the Claude Code session. Nothing publishes yet.
4. Nipoon reviews. Three outcomes only, kept simple on purpose:
   - "approved" or "publish it" moves the file from `pending/` to `published/`, commits, and deploys
   - a note or edit sends it back for a revision pass
   - "drop it" deletes the draft
5. On approval, Claude Code commits to GitHub, Netlify deploys automatically from the repo, and the same approved content goes to Substack through its Publisher API.
6. Nothing posts to any social platform in this phase. That gets added only once phase 1 is running cleanly for a few weeks.

This is the entire review mechanism. No dashboard, no separate approval tool, just a reply in the same Claude Code session.

## Cadence

No fixed schedule at the start. An entry gets drafted when something real happened, not on a calendar. Once there's a rhythm, a newsletter digest goes out roughly every one to two weeks summarizing whatever published since the last one.

## What Claude Code owns

Drafting, formatting, metadata, commits, deploys, and pushing approved newsletter issues to Substack.

## What Nipoon owns

Reviewing and approving. That's the whole job in this phase.

## Setup order

1. Domain and GitHub repo
2. Netlify project connected to that repo
3. Astro site skeleton, deployed once, even with placeholder content, so the pipeline has somewhere to publish to
4. Substack publication created, Publisher API access confirmed
5. First real entry drafted, reviewed, published, to prove the loop works end to end
6. Only after step 5 works: start phase 2, the ADHD track, as a second instance of this same kit
