---
title: "I'm building a 40 GB AI server out of 2014 server parts, and the GPUs are the boring half"
date: 2026-08-25
project: Local AI infrastructure / third node
status: planned
stack: Ubuntu Server, Ollama, SSH tunnels (mirroring the existing pc2 setup)
hardware: RTX 3090 24 GB + RTX 5070 Ti 16 GB, dual Xeon E5-2620 v3, Supermicro X10DRi-T4+, 112 GB DDR4
---

**PLANNED** · nothing racked yet · no benchmark, no power figure, on purpose

I have a pile of used parts on the floor and a decision I made yesterday that I actually like: a third machine, built almost entirely from hardware nobody wants any more, whose only job is to run a coding model locally and take the grind work off a metered API bill.

The parts list reads like a 2014 datacenter that got liquidated. A Supermicro X10DRi-T4+ board, two Xeon E5-2620 v3s, 112 GB of DDR4. Into that go two graphics cards I already own — an RTX 3090 at 24 GB and an RTX 5070 Ti at 16 GB — for 40 GB of pooled VRAM. There's an RTX 3060 that could make it 52 GB if I decide the slot is worth it.

Here's the thing I keep having to say out loud: **the GPUs are the least interesting part of this build.** VRAM is the number everyone quotes because it's the number that gates whether a model loads at all, and I already know how that arithmetic comes out. What I don't know is everything downstream of it, and that's where used server hardware actually bites.

Two E5-2620 v3s give me a lot of cores that are each individually slow. That is completely fine for the thing a server is normally for, and potentially not fine at all for a mixture-of-experts model that spills layers onto the CPU — which is precisely the class of model I want to run. Forty gigabytes of pooled VRAM across two *different* cards is also not the same object as forty gigabytes on one card; a 24+16 split has a seam in it, and where that seam falls depends on the model. I have opinions about how both of those will go. I have no measurements, so they stay opinions, and they stay out of this post as numbers.

The one hard number I *do* have comes from the box that already exists. The second machine on this LAN — a small always-on Ubuntu box with a 3060 in it — talks to my main PC at about 12 MB/s and drops transfers over a gigabyte. That's measured, that's the network this new machine inherits, and it's the reason a decision that sounded technical turned out to be a logistics decision: big model weights get downloaded **on** the server, not copied **to** it.

The genuinely interesting choice was one I nearly got wrong. My first instinct was to merge everything — pull the 3060 out of the little box, consolidate into one large GPU host, stop maintaining two machines. I talked myself out of it in about ten minutes. The small box's entire value is that it's small and always on: transcription, embeddings, an errand-sized model, available at 3 a.m. without me thinking about it. The moment it becomes half of a big rig, it's busy whenever the big rig is busy, and I've traded two capabilities for one. So they stay separate. Two machines, two roles.

Everything else about the plan is deliberately unoriginal. Same Ubuntu Server, same driver and Ollama stack, same key-based SSH, same tunnel-it-to-localhost pattern the existing box already uses — new alias, new ports, nothing else new. One playbook for two machines. The temptation with a fresh build is to make it a laboratory for four things you've been meaning to try; the cost of that shows up six months later when neither box works the way the other one does and you can't remember which is which.

There's one honest caveat sitting in my own build notes. The plan names a specific model — a current MoE coding model — as the target, and I wrote a warning next to it telling myself to re-check that name at build time rather than trust it. A model name in a month-old plan is already stale. The *shape* of what I want (an MoE coder that fits in 40 GB) will outlive the name by a year.

There's also a cost I keep not writing down, which is the 3090. It isn't spare. It's in my desktop right now, doing real work. Moving it into the server means my main machine gets weaker so that a machine in the other room gets strong enough to be worth building. That trade is the actual bet here, and it's not one I can settle with a spec sheet.

Next entry on this: what it actually draws from the wall, and whether two slow Xeons ruin the thing the VRAM made possible.
