---
title: "My illustration model rendered photographs, and turning the dial did nothing"
date: 2026-08-05
project: Children Storybook / Immerblatt Kinder
status: tested
stack: Flux.1-dev fp8, two stacked LoRAs (character + house style), ComfyUI, ai-toolkit
hardware: RTX 5070 Ti 16 GB, local
---

**TESTED** · 16-page picture book rendered end to end · 33 renders, ~30 s each

I finally shipped the thing this pipeline was built for: a 16-page illustrated children's book, one recurring character, all 16 pages on disk and assembled into a viewer. Two trained LoRAs doing the work — one for the character, one for the house style — stacked at full strength, which is the recipe I'd measured a day earlier and written down as settled.

The recipe was wrong. Not wrong for the pages I'd measured it on. Wrong for the ten pages I hadn't.

Six of sixteen pages have the character in frame. The other ten are scenes — a smoggy town, a canal street, a rooftop bus stop. With the style trigger alone in front of an architectural scene, page 1 came back as a **photograph**. Not a stylized render, not a near-miss: a photoreal image of grey smokestack buildings. My first instinct was that the character LoRA was fighting the style one, so I ran the page at character strength 1.0, 0.5, and 0.0. Photoreal at all three. That killed the strength theory outright — it wasn't a weight problem, it was a prompt problem. Adding one clause, *"children's picture book illustration, coloured pencil drawing on paper,"* fixed both bad pages on a single roll.

That's the part worth keeping, because it inverts the rule I'd written for myself. My own runbook said prose style words can only *fight* a trained style LoRA — that once you've trained the style, describing it in words just adds noise. On character-led prompts that holds. On scene-led prompts the opposite holds: the trained style has nothing to anchor to, Flux falls back to its photographic prior, and the prose words are what rescue it. Same model, same LoRA, opposite advice depending on what's in frame.

The other thing this run settled is cheaper to state and more expensive to ignore. I reviewed all sixteen pages individually against their own text rather than spot-checking a sample. Eight passed, eight failed, and the failures were not the kind a sample catches: one page had a **second copy of the main character** standing in the background, another had no people in it at all under text reading *"the grumps all grinned."* Both are instantly obvious when you look at the page, and both are invisible in a grid of thumbnails.

The economics make that easy. Each render is about 30 seconds — a full 16-page pass is 8 minutes. Re-rolling the eight bad pages cost less than the time it took to write down why they were bad. **Generating is cheap; reviewing is the expensive step, and it's the one people try to sample their way out of.** I've now been burned by a 2-of-N spot check twice on this project, once on a training dataset and once on finished pages.

One decision I expected to be hard turned out to be a deletion. I'd trained a third LoRA for locations and assumed I'd stack all three. An A/B on three pages, same seed, only that loader differing, showed it added a painted border artifact, paled the composition, and put modern cars in a canal street — while contributing no location fidelity the scene text wasn't already producing. It's out. Three-LoRA stacking stays unmeasured because it turned out to be unnecessary.

Next entry: the one thing this book genuinely cannot do — and why it's a dataset problem no prompt will solve.
