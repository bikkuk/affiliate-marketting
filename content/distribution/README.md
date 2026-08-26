# Distribution kit

Ready-to-paste posts for the communities where this log's content actually
belongs. **Nothing here is posted automatically** — posting from Nipoon's own
accounts has to be Nipoon's own click, both because the accounts are his and
because these communities ban accounts that look automated.

`WORKFLOW.md` says "nothing posts to any social platform in this phase." That
was right for launch. It has now cost 21 days at 10 visits. Treat this kit as
that gate opening.

## The one rule that matters

Every one of these communities will bury a link that reads as marketing. The
format that works is the same in all of them: **put the substance in the post
itself**, and let the link be a footnote for people who want the long version.
A post that can only be understood by clicking through gets removed. A post
that stands on its own and happens to link somewhere gets upvoted.

Corollary: don't post all of these in one day from one account, and reply to
comments for the first two hours or don't post at all. An unattended post that
gets three questions and no answers does more harm than not posting.

---

## 1. r/LocalLLaMA — the AI server build

Best fit on this list by a distance. Used-hardware builds for local inference
are core content there, and the "filming what goes wrong" angle is genuinely
rare — almost every build write-up is retrospective and tidy.

**Post as a text post, not a link post.** Wait until part 2 is live (29 Aug) so
there's a follow-up to point at, or post after the hardware actually arrives so
you can answer "did it work" in the comments.

**Title:**
> Building a 40GB pooled-VRAM node out of liquidated 2014 server parts (dual E5-2620 v3, X10DRi-T4+, 3090 + 5070 Ti) — and why the GPUs were the easy decision

**Body:**
```
Third machine on my LAN, built to take coding grind work off a metered API bill.
Parts are bought, nothing's arrived yet, so this is the reasoning rather than
benchmarks — I'm not posting numbers I haven't measured.

Platform: Supermicro X10DRi-T4+, 2x Xeon E5-2620 v3, 112GB DDR4.
GPUs: RTX 3090 (24GB) + RTX 5070 Ti (16GB) = 40GB pooled. A 3060 could make it 52
if I decide the slot is worth it.

Three things I got wrong or nearly got wrong:

1. I assumed VRAM was the hard part. It isn't — that arithmetic is knowable in
   advance. What I can't predict is the two E5-2620 v3s: lots of individually slow
   cores, which is fine for a normal server workload and possibly terrible for an
   MoE model spilling layers onto CPU. That's the class of model I actually want
   to run.

2. 40GB across two *different* cards isn't 40GB on one card. A 24+16 split has a
   seam, and where the seam falls depends on the model. I have opinions. I don't
   have measurements, so they stay opinions.

3. I nearly consolidated my existing small always-on box (3060) into this one.
   Talked myself out of it: the small box's entire value is being small and always
   on — transcription, embeddings, errand-sized models at 3am. Merge it and it's
   busy whenever the big rig is busy. Two machines, two roles.

The one measured number I have is unglamorous: that LAN runs ~12MB/s and drops
transfers over a gig. So model weights get downloaded *on* the server, never
copied *to* it. A networking limit ended up dictating the whole provisioning
approach.

Real cost nobody puts in a parts list: the 3090 isn't spare. It's in my desktop
doing work. My main machine gets weaker so the machine in the other room becomes
worth building.

I'm photographing and filming the assembly, including whatever goes wrong — used
enterprise gear fails in ways consumer builds don't and nobody documents it.
Write-up: <URL>
```

**Expect to be asked:** what MoE model specifically, why not just rent an A100,
what PSU, does the X10DRi-T4+ do above-4G decoding / bifurcation for two big
cards. Have real answers or say you don't know yet.

---

## 2. Hacker News — the two counterintuitive posts

HN wants a surprising, specific, technical claim. Submit **title + URL only**,
no editorialising, then answer questions in the thread.

These two have the right shape. The server build does not — HN is lukewarm on
build logs.

- `My illustration model rendered photographs, and turning the dial did nothing`
  → `/log/style-lora-rendered-photographs`
  The inverted rule (prose style words rescue scene prompts, fight character
  prompts) is the actual hook. Strongest submission on the site.

- `Why a tax advisor's Excel habit broke my RAG pipeline`
  → `/log/localki-excel-chunking-bug`
  Human-habit-breaks-software is a durable HN genre.

Submit Tue–Thu, roughly 08:00–10:00 US Eastern (14:00–16:00 CEST). One at a
time, at least a fortnight apart.

---

## 3. r/StableDiffusion and r/comfyui — the LoRA work

Same text-post rule. The photoreal-LoRA post is the one with a finding people
can use; lead with the finding, not the story:

**Title:**
> Trained style LoRA returned photoreal images on scene prompts at strength 1.0, 0.5 AND 0.0 — the fix was a prompt clause, not a weight

Post the before/after and the exact clause that fixed it in the body. This
subreddit rewards a reproducible recipe and punishes a teaser.

---

## 4. The German angle — unused, and it's the actual moat

Everything above chases an English-speaking global dev audience, which is where
the *reach* is. But the leads that pay for Klarverk and LocalKI are German small
businesses, and almost nobody writes about local/on-prem AI **in German, for
German SMEs, with DSGVO as the starting premise**.

That's a real gap and this site isn't in it — the log is entirely in English.

Recommendation: keep the log in English for reach, and put German-language
versions of the on-prem/DSGVO material on klarverk.de and localki.de where it
converts. Don't bilingual this site; a half-translated blog ranks for neither.

Low-effort German-language channels worth one post each once there's German
material to point at: r/de_EDV, the Selbstständigkeit/Steuerberater forums where
the Excel-chunking story lands, and LinkedIn in German rather than English.
