---
title: "SERIES BRIEF — Building the Avatar (5 posts)"
date: 2026-08-02
project: Avatar / Local AI Bench Log
status: brief only — not drafted, needs user answers before writing
stack: Rainmeter → pywebview + WebView2, Python 3.11, Pillow, pytest, Codex, Claude Code
hardware: Windows 11, RTX 3060 box on the LAN (pc2)
---

# What this is

Raw material and a proposed structure for a 5-post series, taken from one long
session on 2026-08-02 that migrated the Avatar desktop widget off Rainmeter onto a
standalone Python app. **Nothing here is drafted yet** — the open questions at the
bottom need answering first, because two of them change what the posts are.

This is a good series because the arc is real and unflattering in the right way: a
bug got "fixed" five separate times, by two different AI agents, and the symptom
survived every fix. The resolution wasn't a better fix. It was deleting the feature
that was failing.

---

# The material, in order it actually happened

## 1. The widget vanished — and it was never running

Reported as "where's my avatar, how does it disappear?" Rainmeter itself wasn't in
the process list. Started it: still no avatar. `Rainmeter.ini` had `Active=0` on all
three configs — the engine had restarted and silently declined to restore what it
was showing. A startup shortcut existed and had fired. Nothing logged a problem.

## 2. Three silent bugs, one root cause each, all invisible

The to-do list "wasn't fully functional." It turned out to be three unrelated defects
that all present identically — as *nothing happening*:

- **A backslash eaten by its own language.** `"#AvatarPath#\todo.py"` in an ordinary
  Python f-string makes `\t` a TAB character. Every generated click action pointed at
  `#AvatarPath#<TAB>odo.py`, a path that cannot exist. Rainmeter logs nothing at all
  for an action it can't resolve. Same defect had shipped in two other files as a
  literal `0x08` (`\b` in `\book.py`) and `0x0D` (`\r` in `\refresh.py`).
- **A variable that means the wrong folder.** Clicks wrote their regenerated UI into
  `#@#` — Rainmeter's "this config's own resources folder." The config in question
  doesn't have one; it reads a sibling's. So the underlying markdown file toggled
  correctly every single time, and the thing on screen never changed. Looks exactly
  like a dead button.
- **A missing refresh.** The "add item" box wrote the file and regenerated the UI
  correctly, then never told the skin to reload it. Correct data, invisible.

Every one of these produces the same user-facing symptom: you click, nothing happens,
and no log anywhere records that anything went wrong.

## 3. The platform was the common factor

Not a Rainmeter hit piece — but the pattern is structural, not incidental:
`.ini`-based layout with relative pixel chaining, no live preview, no hot reload, and
silence on unresolvable actions. Every layout change had to be deployed to the real
desktop and looked at to find out if it worked. Three bugs in one session all shared
that shape. Also: right-clicking any skin surfaces Rainmeter's own menu (Manage,
Settings, About) which has nothing to do with your app and can't be removed.

## 4. Handing the rewrite to an agent

The business logic was already pure Python — extraction, mood selection, the Pillow
face drawing, the to-do read/write. Only the *shell* was Rainmeter. Codex got one
written brief and rebuilt the whole shell as a pywebview app (Windows' built-in
WebView2) in a single autonomous run: three views, all clicks wired directly to the
existing Python functions in-process, `--dev` hot reload in ~350ms, 138 tests passing.
It explicitly did not touch the working Rainmeter files, so both versions ran side by
side for comparison.

Worth being honest in the post: this went well *because* the logic was already
separated from the rendering. The migration was cheap because of a boundary that
existed before anyone planned to migrate.

## 5. Then three more bugs, and only the last one mattered

- **Crash on launch.** pywebview recursively inspects every public attribute of the
  object you hand it as `js_api` — it walked into the live WebView2 COM handle from
  the wrong thread and blew the recursion limit. Fix: expose two methods explicitly
  instead of the whole object.
- **Every click opened a terminal.** Diagnosed first as a CSS overflow bug — the
  project list wasn't height-constrained, so invisible rows overlapped the toolbar and
  ate clicks meant for buttons underneath. Real bug. Fixed it. Symptom persisted.
- **The actual cause.** Every action called a "refresh the view" helper that rebuilt
  the data payload — which shells out to `git status`. Correctly-routed clicks on
  *theme* and *pin* were spawning console windows, because the thing spawning them
  wasn't the click handler at all. The earlier test only trapped `Popen`, so it sailed
  past a `subprocess.run` in a completely different layer.

## 6. The fix that worked was deleting the feature

Clicking a project was *supposed* to open a Claude CLI session in a terminal. After
five rounds of fixing why the wrong things also opened terminals, the resolution was
to stop launching anything at all: clicking a project now appends one timestamped
line to a markdown file in that project's folder. The next session reads it.

That removes the failure mode rather than correcting it. Even if a hitbox is still
wrong somewhere, there's no launch left to fire. Strongest single takeaway in the
series.

---

# Proposed structure

| # | Working title | Core claim |
|---|---|---|
| 1 | The button that did nothing, and logged nothing | Three unrelated bugs, one identical symptom. Silent failure is worse than a crash. |
| 2 | A backslash ate my desktop widget | `\t`, `\b`, `\r` — escapes swallowed by the language that generated them, invisible in every editor. |
| 3 | I let an agent rebuild the whole front end | The migration was cheap because of a boundary drawn long before anyone planned to migrate. |
| 4 | I fixed it three times and it stayed broken | Each fix found a real bug. None of them was *the* bug. Debugging blind through someone else's eyes. |
| 5 | The fix was deleting the feature | Removing the capability beat correcting it. |

Post 4 is the strongest and most honest. Consider leading with it if the series
doesn't have to run chronologically.

---

# Questions before drafting — need answers

1. **What's the affiliate hook?** This is the one I can't answer for you. The series
   is genuinely good dev writing, but there are no products in it — it's Rainmeter
   (free), Python (free), WebView2 (bundled), and two AI coding tools. If the site
   monetizes through tool referrals, the only candidates are the AI subscriptions
   themselves. Is that the intended angle, or is this series meant as
   traffic/credibility content with monetization elsewhere?
2. **Chronological or lead with the strongest?** Post 4 is the best one and it's
   fourth.
3. **How pointed about Rainmeter?** It's a free tool by people who owe nobody
   anything. There's a version of post 1–2 that's a fair structural critique and a
   version that reads as trashing it. Which?
4. **Name the AI tools explicitly?** The story involves Claude Code and Codex by
   name, including both getting it wrong repeatedly. That's more interesting than
   hiding it, and it's more honest — but it's your call.
5. **Publish now or after the app is finished?** As of this brief the standalone app
   still has unfinished pieces (dashboard, themes, time module). The series can end at
   "the fix was deleting the feature" and stand alone, or wait and gain an ending.
6. **Any of this too revealing?** The posts would reference real project names from
   the vault board. Worth a pass for anything you'd rather not have public.

---

# Note for whoever drafts these

House style from `pending/2026_07_29_same_pipeline_three_times.md`: first person, plain
sentences, technical without jargon-flexing, admits the embarrassing part directly, ends
on one takeaway that generalizes past the specific tool. No listicles, no "in today's
fast-paced world." Frontmatter carries `title`, `date`, `project`, `status`, `stack`,
`hardware`.
