---
title: "I found the same pipeline designed three times in my own notes"
date: 2026-07-29
project: Main Brain / Local AI Bench Log
status: caught before it became a fourth
stack: local LLM (qwen2.5:14b on a 3060), Python collectors, markdown notes
hardware: RTX 3060 12GB, headless Ubuntu box on the LAN
---

I sat down this morning to brainstorm a blog generator. Sources in, local model drafts, I pick what's worth publishing. Reasonable idea. I asked my notes whether anything like it already existed, mostly as a formality.

It existed three times.

There's one that's actually built — an activity scanner that reads my project logs every three days and drafts posts into a review folder. Registered as a scheduled task two days ago. It has never completed a single run; the cursor file it writes at the end of a successful run doesn't exist on disk, and neither does the folder it puts images in. So: built, wired, scheduled, and silently doing nothing.

There's a second one, a full written design for the same thing with commit hooks and approval over a chat bot. Never built.

And there's a third — the idea I had this morning, which a session had already logged for me at 08:05 today with a note attached: *don't start a fourth parallel pipeline.*

The uncomfortable part isn't that I duplicated work. It's that this is the third time this month I've caught the same shape. Four days ago it was a bug diagnosed and written down in one project, then rediscovered from scratch in a different project the next day — same machine, one day apart. Three days ago it was an entire ComfyUI controller I'd built in a folder I'd forgotten about, blocked on the exact same missing file as another project, neither aware of the other.

Two things I actually take from this.

The first is that a built-and-scheduled thing is not a working thing. I'd have told you that pipeline was live. It's in my notes as live. It has produced nothing, and the only reason I know is that I went looking for a file that should have been there. If an automation has no cursor, no log, and no output you'd notice missing, you don't have automation — you have a scheduled task that fails politely.

The second is that memory isn't the fix. I have a good memory for my own projects and it didn't help once. What helped was a boring index file that gets read before starting anything, and one line in it from a session earlier the same day telling me not to do this. That's it. That's the whole mechanism.

If you run more than about three projects, the thing worth building first isn't the pipeline. It's the file that stops you building the pipeline twice.
