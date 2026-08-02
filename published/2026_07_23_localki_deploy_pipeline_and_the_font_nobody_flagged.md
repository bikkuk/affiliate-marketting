---
title: "Cleaning up 30 dead HTML files taught me more about deploys than the deploy did"
date: 2026-07-23
project: LocalKI
status: tested
stack: static HTML/CSS/JS, GitHub, Netlify continuous deployment
hardware: n/a, deploy infra not a benchmark entry
---

**TESTED** · LocalKI.de rebuild session · deploy pipeline + font swap

LocalKI.de had been running on manual drag-and-drop into Netlify. Every update meant opening the dashboard, dragging a folder, and hoping the right files were in it. That's fine for a site nobody's iterating on. It stops being fine the moment you're touching copy weekly.

So the actual fix was boring: point Netlify at a GitHub repo (`localki-de`, private) and let continuous deployment handle it. Push to `main`, site updates. No more manual step, no more "did I drag the current folder or last week's."

The more interesting part was what turned up while consolidating the source of truth. The working directory had over 30 legacy HTML variants sitting alongside an abandoned Electron scaffold and a half-finished redesign package — old attempts nobody had cleaned out. All of it got archived, not deleted, into a dated folder, so the live repo only contains what's actually deployed. Nothing regenerable (like `node_modules`) survived the move; everything else did, just out of the way.

The font swap is the part worth flagging on its own. The old logo used UnifrakturMaguntia — a Fraktur/blackletter typeface. In Germany that font family carries real right-wing associations for a lot of people, independent of anyone's intent in picking it. It's out now, replaced with Space Grotesk, Inter, and JetBrains Mono across the site, same layout and sizing otherwise. Small technical change, but the kind of thing that's cheap to fix once you know to look for it and expensive to explain later if you don't.

Why this matters past LocalKI specifically: a site's front-end code and its deploy plumbing rot the same way — quietly, until you need to touch either one and discover ten decisions nobody wrote down. Manual deploys and unarchived dead files are the same problem: no source of truth. Fixing both at once is cheaper than fixing them separately later.

[Placeholder: deploy time before/after switching off manual drag-and-drop, once it's actually timed]

Next entry: scoping the fuller LocalKI.de overhaul now that the deploy plumbing isn't in the way.
