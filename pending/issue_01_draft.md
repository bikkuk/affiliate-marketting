---
issue: 1
date: 2026-07-24
---

**Subject line:** The bug wasn't in the chunker

This is the first issue of what's going to be a running log, not a curated highlight reel. Real work on local AI systems, written up close to when it actually happened.

This week: LocalKI, the offline RAG workstation I'm building for German tax advisors, hit a wall in pilot testing. Six bugs surfaced, one of them traced back to something nobody would have guessed from the code alone, my pilot user's habit of converting every Excel file to PDF before uploading it. That single habit was quietly destroying the document structure the whole retrieval pipeline depends on.

Full writeup: [link to the post once the site is live]

Next issue covers how the fix is being tested against real client files, and whatever breaks next.

If you're working on local AI deployments in Germany and want a second pair of eyes, reply to this email.
