---
title: "I bought the whole server, and now I get to do nothing about it for a week"
date: 2026-08-26
project: Local AI infrastructure / third node
status: ordered
part: 2 of 2
stack: Ubuntu Server, Ollama, SSH tunnels (mirroring the existing pc2 setup)
hardware: RTX 3090 24 GB + RTX 5070 Ti 16 GB, dual Xeon E5-2620 v3, Supermicro X10DRi-T4+, 112 GB DDR4
---

**ORDERED** · parts bought, nothing delivered yet · no benchmarks, no power figures, nothing has been switched on

The plan I wrote up yesterday is now money that has left my account. Every part for the third machine is bought. None of it is here. For the next several days the entire project consists of refreshing tracking pages, which is a genuinely strange phase to be in after a month of arguing with myself about whether to build this at all.

Worth being precise about what "all the parts" means, because the buy list is smaller than the spec sheet. The platform is what I actually paid for: the Supermicro X10DRi-T4+ board, the two Xeon E5-2620 v3s, the 112 GB of DDR4, and the unglamorous supporting cast that never makes it into anyone's parts list — power, chassis, cooling, cables, the storage it boots from. The graphics cards weren't a purchase. The RTX 3090 and the RTX 5070 Ti are cards I already own, and moving them is the part of this build that costs something real: the 3090 is in my desktop today, doing work, and it comes out so that a machine in the other room becomes worth having. Forty gigabytes of pooled VRAM is the headline. A weaker main PC is the invoice.

The waiting is annoying and also the only clean thinking time this project will get. Once the boxes are open there's a strong pull toward *just get it posting*, and every decision made in that state is made under hardware pressure. So the decisions stay where I put them yesterday and I'm not reopening them: same Ubuntu Server as the existing box, same driver and Ollama stack, key-based SSH, tunnelled to localhost on its own port. New alias, new ports, nothing else new. One playbook for two machines. A fresh build is a magnet for trying four unfamiliar things at once, and the bill for that arrives six months later when neither box works like the other.

The one thing I *am* changing is that I'm going to film it.

Not a build montage. When the parts land I'm photographing and recording the assembly as it happens, including the parts that go wrong, because used enterprise hardware from 2014 fails in ways that consumer builds don't and almost nobody documents it. A modern consumer build is essentially solved — there are a thousand clean videos of a clean board going into a clean case. A liquidated dual-socket server board is a different genre: mounting hardware that may or may not be the mounting hardware it shipped with, cooling designed for a chassis I don't have, firmware from a decade ago, and a management interface that expects to be on a network I haven't built. I don't know which of those will actually bite. That's exactly why it's worth recording rather than reconstructing from memory afterwards.

There's an obvious trap in this and I'd rather name it now than discover it on camera. Filming a build makes you slower, and worse, it tempts you into performing a build instead of doing one — retaking a step so it looks tidy, skipping the part where you sit and stare at a manual for ten minutes because that's boring footage. The boring ten minutes is usually where the actual information is. So the rule I'm setting for myself before the first box arrives: the camera runs, the build does not wait for the camera, and nothing gets re-staged. If that produces bad footage of a good build, I'll take that trade.

What won't be in the next entry: any number. No tokens per second, no wattage, no thermal figures, no verdict on whether two slow Xeons strangle a model that spills off the GPUs. I have opinions about all four. None of them are measurements, and this log doesn't print opinions as numbers. The meter goes on the wall socket before I make a single claim about what this thing costs to run.

Next entry: what turned up in the boxes, and whether it POSTs.
