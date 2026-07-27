---
title: "A client asked if I could train a custom model on their images. I didn't know yet."
date: 2026-07-21
project: LocalKI / Klarverk
status: researched, not built
stack: Stable Diffusion LoRA fine-tuning, on-prem
hardware: n/a — still in the "should we even do this" phase
---

Somebody asked, basically in passing, whether I could train something on their own images — their product photos, their style — instead of just running the RAG setup I'd already pitched them on. Same on-prem, same "your data never leaves the building" pitch, just a different kind of model underneath.

I didn't say yes on the spot. I didn't actually know if it made sense as a real offering yet, so I spent an evening figuring that out instead of just quoting a number that felt right.

The honest answer: it's not a bolt-on. LoRA fine-tuning is closer to a small project than a checkbox feature — you're not selling "AI image generation," you're selling a specific trained thing that works for one client's specific images, and that has a floor on how much attention it needs regardless of how good your tooling gets. So the pricing conclusion I landed on was project-priced, not per-image. Per-image pricing implies it scales like inference. It doesn't. The expensive part is getting the dataset and training right once, not generating afterward.

I haven't built this yet. It's sitting as a candidate service, logged, waiting for the next time the services list actually gets touched. What I did decide is not to undersell it just because "it's just a LoRA" sounds small from the outside. It isn't, once you've actually tried to scope what "done" looks like for a client who isn't a hobbyist fine-tuning their own Discord avatar.

If you're pricing something similar and you're tempted to go per-generation: don't, until you've actually run one end to end and timed where the hours went.
