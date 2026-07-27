# Activity-Based Posting Automation + Behavioral Profiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every 2-3 days, automatically scan real activity across all active projects in the Main Brain vault, draft 0-2 humanized journal posts into `pending/` with a pc2-generated hero image, feed the same activity into the existing ADHD Data observation pipeline, and regenerate a corroboration-gated `PROFILE.md`. Nothing auto-publishes.

**Architecture:** Deterministic Python helper scripts (parsing, pc2 image calls, state cursor, profile synthesis) do the mechanical work and are unit-tested. A headless Claude Code invocation (triggered by a Windows Scheduled Task, since pc2 and local-disk projects aren't reachable from a cloud routine) does the one judgment step — picking which activity is post-worthy and writing the draft — then calls the helper scripts as tools.

**Tech Stack:** Python 3.11 (stdlib only — `urllib`, `json`, `pathlib`, `re`, `argparse`), pytest for tests, existing `System/tools/self_extract.py` reused as-is for observation extraction, PowerShell for Windows Scheduled Task registration.

## Global Constraints

- No invented numbers or fabricated data in any drafted post — real basis only, per `PROJECT_BRIEF.md`'s content rules. Use `[Placeholder: ...]` when a real figure isn't available yet.
- Nothing in `pending/` auto-publishes — approval stays exactly per `WORKFLOW.md` (approve / edit / drop, replied to in a live session).
- pc2 asset generation is abstract/mood images only — no generated diagrams, no fabricated screenshots or charts.
- `PROFILE.md` entries require at least 2 corroborating promoted observations per category; no clinical or diagnostic-sounding language, describe what was observed and when.
- Scanner reads all projects in `System/ACTIVE.md` (user-approved deviation from `PROJECT_BRIEF.md`'s narrower niche scope — do not "fix" this back without asking).
- Scheduled Task registration is a persistent system-config change — the registration script is provided but must be run by the user explicitly, not auto-executed.

---

### Task 1: Pipeline state cursor (`pipeline_state.py`)

**Files:**
- Create: `E:\CLAUDE\AFFILATE MARKETTING\scripts\pipeline_state.py`
- Create: `E:\CLAUDE\AFFILATE MARKETTING\tests\test_pipeline_state.py`
- Modify: `E:\CLAUDE\AFFILATE MARKETTING\.gitignore` — add `state/`

**Interfaces:**
- Produces: `read_last_run(path: pathlib.Path = DEFAULT_PATH) -> str | None`, `write_last_run(timestamp: str, path: pathlib.Path = DEFAULT_PATH) -> None`. Later tasks (the orchestrator prompt) call these to get/set the run cursor.

- [ ] **Step 1: Write the failing tests**

```python
# E:\CLAUDE\AFFILATE MARKETTING\tests\test_pipeline_state.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import pipeline_state as ps

def test_read_last_run_missing_file_returns_none(tmp_path):
    missing = tmp_path / "last_run.json"
    assert ps.read_last_run(missing) is None

def test_write_then_read_round_trips(tmp_path):
    target = tmp_path / "nested" / "last_run.json"
    ps.write_last_run("2026-07-27T08:00:00", target)
    assert ps.read_last_run(target) == "2026-07-27T08:00:00"

def test_write_creates_parent_directory(tmp_path):
    target = tmp_path / "does" / "not" / "exist" / "last_run.json"
    ps.write_last_run("2026-07-20", target)
    assert target.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_pipeline_state.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline_state'`

- [ ] **Step 3: Write the implementation**

```python
# E:\CLAUDE\AFFILATE MARKETTING\scripts\pipeline_state.py
#!/usr/bin/env python3
"""pipeline_state.py — read/write the posting-automation run cursor."""
import json
import pathlib

DEFAULT_PATH = pathlib.Path(__file__).resolve().parent.parent / "state" / "last_run.json"


def read_last_run(path: pathlib.Path = DEFAULT_PATH):
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("last_run")


def write_last_run(timestamp: str, path: pathlib.Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"last_run": timestamp}, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_pipeline_state.py -v`
Expected: 3 passed

- [ ] **Step 5: Add `state/` to `.gitignore`**

Open `E:\CLAUDE\AFFILATE MARKETTING\.gitignore` and append a line: `state/`

- [ ] **Step 6: Commit**

```bash
cd "E:\CLAUDE\AFFILATE MARKETTING"
git add scripts/pipeline_state.py tests/test_pipeline_state.py .gitignore
git commit -m "Add pipeline run-cursor helper (pipeline_state.py)"
```

---

### Task 2: Activity scanner (`scan_activity.py`)

**Files:**
- Create: `E:\CLAUDE\AFFILATE MARKETTING\scripts\scan_activity.py`
- Create: `E:\CLAUDE\AFFILATE MARKETTING\tests\test_scan_activity.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `find_active_projects(brain_main: pathlib.Path) -> list[tuple[str, pathlib.Path]]`, `extract_recent_log(state_md: pathlib.Path) -> list[dict]` (each dict: `{"date": str, "text": str}`), `scan(brain_main: pathlib.Path, cutoff: str) -> list[dict]` (each dict: `{"project": str, "date": str, "text": str, "state_md": str}`, sorted ascending by date). Later orchestration (Task 5) calls `scan(...)` and JSON-serializes the result.

- [ ] **Step 1: Write the failing tests**

```python
# E:\CLAUDE\AFFILATE MARKETTING\tests\test_scan_activity.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import scan_activity as sa

ACTIVE_MD = """# ACTIVE

## Projects
| Project | Type | Owner | Status | Next action |
|---|---|---|---|---|
| [Alpha](../Projects/Alpha/STATE.md) | software | claude | active | do the thing |
| [Beta](../Projects/Beta/STATE.md) | writing | claude | active | write the thing |
"""

STATE_MD = """---
project: Alpha
---

# Alpha — State

## Now — the single next action
- Do the thing.

## Recent log
- 2026-07-20 — Old entry, before cutoff.
- 2026-07-25 — Shipped the deploy pipeline rebuild, archived 30 legacy files.
  Continuation line that should be appended to the same entry.
- 2026-07-26 — Second recent entry.

## Open decisions / threads
- 2026-07-27 — This looks like a bullet but it's in the wrong section, must be ignored.
"""


def make_vault(tmp_path):
    (tmp_path / "System").mkdir()
    (tmp_path / "System" / "ACTIVE.md").write_text(ACTIVE_MD, encoding="utf-8")
    (tmp_path / "Projects" / "Alpha").mkdir(parents=True)
    (tmp_path / "Projects" / "Alpha" / "STATE.md").write_text(STATE_MD, encoding="utf-8")
    return tmp_path


def test_find_active_projects_parses_table_links(tmp_path):
    vault = make_vault(tmp_path)
    projects = sa.find_active_projects(vault)
    names = [name for name, _ in projects]
    assert names == ["Alpha", "Beta"]
    alpha_path = dict(projects)["Alpha"]
    assert alpha_path == (vault / "Projects" / "Alpha" / "STATE.md").resolve()


def test_extract_recent_log_only_reads_recent_log_section(tmp_path):
    vault = make_vault(tmp_path)
    entries = sa.extract_recent_log(vault / "Projects" / "Alpha" / "STATE.md")
    assert len(entries) == 3
    assert entries[0] == {"date": "2026-07-20", "text": "Old entry, before cutoff."}
    assert "Continuation line" in entries[1]["text"]
    assert all("wrong section" not in e["text"] for e in entries)


def test_extract_recent_log_missing_file_returns_empty(tmp_path):
    assert sa.extract_recent_log(tmp_path / "nope.md") == []


def test_scan_filters_by_cutoff_and_sorts(tmp_path):
    vault = make_vault(tmp_path)
    results = sa.scan(vault, cutoff="2026-07-20")
    dates = [r["date"] for r in results]
    assert dates == ["2026-07-25", "2026-07-26"]
    assert results[0]["project"] == "Alpha"
    assert results[0]["state_md"].endswith("STATE.md")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_scan_activity.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_activity'`

- [ ] **Step 3: Write the implementation**

```python
# E:\CLAUDE\AFFILATE MARKETTING\scripts\scan_activity.py
#!/usr/bin/env python3
"""
scan_activity.py — collect "Recent log" entries from every active project's
STATE.md, dated strictly after a cutoff. Pure parsing, no LLM calls.

Usage:
  python scripts/scan_activity.py <brain_main_path> <cutoff_date YYYY-MM-DD>
"""
import argparse
import json
import pathlib
import re

ROW_LINK = re.compile(r"^\|\s*\[([^\]]+)\]\(([^)]+)\)")
BULLET = re.compile(r"^- (\d{4}-\d{2}-\d{2})\s*(?:—|--)\s*(.*)$")


def find_active_projects(brain_main: pathlib.Path):
    active_md = brain_main / "System" / "ACTIVE.md"
    text = active_md.read_text(encoding="utf-8")
    projects = []
    for line in text.splitlines():
        m = ROW_LINK.match(line.strip())
        if not m:
            continue
        name, rel_link = m.group(1), m.group(2)
        state_path = (brain_main / "System" / rel_link).resolve()
        projects.append((name, state_path))
    return projects


def extract_recent_log(state_md: pathlib.Path):
    if not state_md.exists():
        return []
    lines = state_md.read_text(encoding="utf-8").splitlines()
    entries = []
    current = None
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if current:
                entries.append(current)
                current = None
            in_section = stripped == "## Recent log"
            continue
        if not in_section:
            continue
        m = BULLET.match(stripped)
        if m:
            if current:
                entries.append(current)
            current = {"date": m.group(1), "text": m.group(2).strip()}
        elif current is not None and stripped:
            current["text"] += " " + stripped
    if current:
        entries.append(current)
    return entries


def scan(brain_main: pathlib.Path, cutoff: str):
    results = []
    for name, state_path in find_active_projects(brain_main):
        for entry in extract_recent_log(state_path):
            if entry["date"] > cutoff:
                results.append({
                    "project": name,
                    "date": entry["date"],
                    "text": entry["text"],
                    "state_md": str(state_path),
                })
    results.sort(key=lambda e: e["date"])
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brain_main_path")
    ap.add_argument("cutoff_date", help="YYYY-MM-DD, entries strictly after this date are returned")
    args = ap.parse_args()
    out = scan(pathlib.Path(args.brain_main_path), args.cutoff_date)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_scan_activity.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd "E:\CLAUDE\AFFILATE MARKETTING"
git add scripts/scan_activity.py tests/test_scan_activity.py
git commit -m "Add activity scanner over Main Brain STATE.md recent logs"
```

---

### Task 3: pc2 hero image generation (`generate_hero_image.py`)

**Files:**
- Create: `E:\CLAUDE\AFFILATE MARKETTING\scripts\generate_hero_image.py`
- Create: `E:\CLAUDE\AFFILATE MARKETTING\tests\test_generate_hero_image.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `generate(slug: str, output_dir: pathlib.Path, comfy_url: str = DEFAULT_COMFY_URL) -> pathlib.Path`. Raises `(urllib.error.URLError, TimeoutError, RuntimeError)` on any pc2-unreachable/failure condition — callers (Task 5's orchestration) catch these to implement the spec's "skip image, note placeholder" edge case.

- [ ] **Step 1: Write the failing tests**

```python
# E:\CLAUDE\AFFILATE MARKETTING\tests\test_generate_hero_image.py
import json
import sys
import pathlib
import urllib.error
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import generate_hero_image as ghi


def _response(payload: bytes):
    cm = mock.MagicMock()
    cm.__enter__.return_value.read.return_value = payload
    return cm


def test_submit_returns_prompt_id():
    fake = _response(json.dumps({"prompt_id": "abc123"}).encode())
    with mock.patch("urllib.request.urlopen", return_value=fake):
        prompt_id = ghi.submit("http://localhost:8189", ghi.build_workflow("test prompt"))
    assert prompt_id == "abc123"


def test_wait_for_result_polls_until_present(monkeypatch):
    calls = {"n": 0}

    def fake_urlopen(req, timeout=30):
        calls["n"] += 1
        if calls["n"] < 2:
            return _response(json.dumps({}).encode())
        return _response(json.dumps({"abc123": {"outputs": {"9": {"images": []}}}}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr(ghi.time, "sleep", lambda _seconds: None)
    result = ghi.wait_for_result("http://localhost:8189", "abc123", timeout=10)
    assert calls["n"] == 2
    assert "outputs" in result


def test_generate_writes_image_file(tmp_path, monkeypatch):
    def fake_submit(comfy_url, workflow):
        return "abc123"

    def fake_wait(comfy_url, prompt_id, timeout=180):
        return {"outputs": {"9": {"images": [{"filename": "f.png", "subfolder": "", "type": "output"}]}}}

    def fake_fetch(comfy_url, image_info, dest):
        dest.write_bytes(b"PNGDATA")

    monkeypatch.setattr(ghi, "submit", fake_submit)
    monkeypatch.setattr(ghi, "wait_for_result", fake_wait)
    monkeypatch.setattr(ghi, "fetch_image", fake_fetch)

    dest = ghi.generate("my-slug", tmp_path / "images")
    assert dest.name == "my-slug_hero.png"
    assert dest.read_bytes() == b"PNGDATA"


def test_generate_raises_when_pc2_unreachable(tmp_path, monkeypatch):
    def fake_submit(comfy_url, workflow):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(ghi, "submit", fake_submit)
    try:
        ghi.generate("my-slug", tmp_path / "images")
        assert False, "expected URLError"
    except urllib.error.URLError:
        pass
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_generate_hero_image.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generate_hero_image'`

- [ ] **Step 3: Write the implementation**

```python
# E:\CLAUDE\AFFILATE MARKETTING\scripts\generate_hero_image.py
#!/usr/bin/env python3
"""
generate_hero_image.py — generate one abstract/mood hero image via the pc2
ComfyUI instance for a bench-log journal entry. Abstract mood only, per
PROJECT_BRIEF.md's content rules — never asked to depict specific unverified
data (no diagrams, no fake screenshots, no fake charts).

Usage:
  python scripts/generate_hero_image.py <slug> <output_dir> [--comfy-url http://localhost:8189]
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_COMFY_URL = "http://localhost:8189"
PROMPT_TEXT = (
    "abstract moody photo of a home AI workstation at night, GPU fan glow, "
    "tangled cables, terminal light reflecting off a desk, no text, no logos, "
    "no readable screen content, cinematic, dark teal and amber tones"
)
NEGATIVE_TEXT = "text, logo, watermark, readable screen, low quality"


def build_workflow(prompt_text: str) -> dict:
    return {
        "3": {"class_type": "KSampler", "inputs": {
            "seed": 0, "steps": 20, "cfg": 7.0, "sampler_name": "euler",
            "scheduler": "normal", "denoise": 1.0,
            "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": 1024, "height": 576, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt_text, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": NEGATIVE_TEXT, "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "bench_log_hero", "images": ["8", 0]}},
    }


def submit(comfy_url: str, workflow: dict) -> str:
    body = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(f"{comfy_url}/prompt", data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data["prompt_id"]


def wait_for_result(comfy_url: str, prompt_id: str, timeout: int = 180) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(f"{comfy_url}/history/{prompt_id}")
        with urllib.request.urlopen(req, timeout=30) as r:
            hist = json.loads(r.read())
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"pc2 ComfyUI did not finish prompt {prompt_id} within {timeout}s")


def fetch_image(comfy_url: str, image_info: dict, dest: pathlib.Path) -> None:
    params = urllib.parse.urlencode({
        "filename": image_info["filename"],
        "subfolder": image_info.get("subfolder", ""),
        "type": image_info.get("type", "output"),
    })
    req = urllib.request.Request(f"{comfy_url}/view?{params}")
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())


def generate(slug: str, output_dir: pathlib.Path, comfy_url: str = DEFAULT_COMFY_URL) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f"{slug}_hero.png"
    workflow = build_workflow(PROMPT_TEXT)
    prompt_id = submit(comfy_url, workflow)
    result = wait_for_result(comfy_url, prompt_id)
    images = result.get("outputs", {}).get("9", {}).get("images", [])
    if not images:
        raise RuntimeError(f"pc2 ComfyUI returned no images for prompt {prompt_id}")
    fetch_image(comfy_url, images[0], dest)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("output_dir")
    ap.add_argument("--comfy-url", default=DEFAULT_COMFY_URL)
    args = ap.parse_args()
    try:
        dest = generate(args.slug, pathlib.Path(args.output_dir), args.comfy_url)
    except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
        print(f"PC2_UNREACHABLE: {e}")
        sys.exit(2)
    print(str(dest))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python -m pytest tests/test_generate_hero_image.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd "E:\CLAUDE\AFFILATE MARKETTING"
git add scripts/generate_hero_image.py tests/test_generate_hero_image.py
git commit -m "Add pc2 ComfyUI abstract hero image generator"
```

---

### Task 4: Profile synthesis (`regenerate_profile.py`, lives in the vault, not the affiliate repo)

**Files:**
- Create: `E:\CLAUDE\BRAIN MAIN\System\tools\regenerate_profile.py`
- Create: `E:\CLAUDE\BRAIN MAIN\System\tools\tests\test_regenerate_profile.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (reads `Projects/ADHD Data/observations.md` at runtime).
- Produces: `parse_observations(text: str) -> dict[str, list[str]]`, `build_profile(observations_text: str) -> str`. Later orchestration (Task 5) calls this script directly (`python System/tools/regenerate_profile.py <observations.md> <PROFILE.md>`).

- [ ] **Step 1: Write the failing tests**

```python
# E:\CLAUDE\BRAIN MAIN\System\tools\tests\test_regenerate_profile.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import regenerate_profile as rp

OBSERVATIONS = """# Observations

## Working style
- 2026-07-19 — High-burst, project-hopping.
- 2026-07-20 — Opens sessions with one ambiguous word.

## Communication
- 2026-07-19 — Wants direct, lead-with-the-answer replies.

## Decisions / patterns
- 2026-07-19 — Runs many parallel ventures at once.
- 2026-07-19 — Credits the agentic setup with letting him finish projects.

## Some Unmapped Section
- 2026-07-21 — A one-off note that showed up somewhere new.
"""


def test_parse_observations_groups_by_heading():
    parsed = rp.parse_observations(OBSERVATIONS)
    assert len(parsed["Working style"]) == 2
    assert len(parsed["Communication"]) == 1
    assert len(parsed["Decisions / patterns"]) == 2


def test_build_profile_excludes_single_bullet_sections():
    profile = rp.build_profile(OBSERVATIONS)
    assert "Communication/collaboration style" not in profile
    assert "Working rhythm & cadence" in profile
    assert "Decision-making tendencies" in profile


def test_build_profile_maps_unknown_section_to_other_when_corroborated():
    text = OBSERVATIONS + "- 2026-07-22 — A second one-off note in the same unmapped section.\n"
    profile = rp.build_profile(text)
    assert "Other recurring behaviors" in profile
    assert "one-off note" in profile


def test_build_profile_empty_input_has_no_sections():
    profile = rp.build_profile("# Observations\n\n_(future entries append below)_\n")
    assert "No category has reached the corroboration threshold yet." in profile
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "E:\CLAUDE\BRAIN MAIN" && python -m pytest System/tools/tests/test_regenerate_profile.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'regenerate_profile'`

- [ ] **Step 3: Write the implementation**

```python
# E:\CLAUDE\BRAIN MAIN\System\tools\regenerate_profile.py
#!/usr/bin/env python3
"""
regenerate_profile.py — synthesize Projects/ADHD Data/PROFILE.md from the
verified, promoted observations in Projects/ADHD Data/observations.md.

Deterministic, no LLM call, no new inference. A category only appears if it
already has 2+ promoted observations backing it (corroboration guardrail) —
single-incident notes stay in observations.md only. Fully regenerates the
file each run so it never drifts from what's currently verified.

Usage:
  python System/tools/regenerate_profile.py <observations.md> <PROFILE.md>
"""
import argparse
import pathlib
import re

SECTION_MAP = {
    "Working style": "Working rhythm & cadence",
    "Communication": "Communication/collaboration style",
    "Decisions / patterns": "Decision-making tendencies",
}
PROFILE_SECTIONS = [
    "Working rhythm & cadence",
    "Focus/attention patterns",
    "Decision-making tendencies",
    "Project-engagement patterns",
    "Communication/collaboration style",
    "Other recurring behaviors",
]
MIN_CORROBORATION = 2

HEADING = re.compile(r"^## (.+)$")
BULLET = re.compile(r"^- \d{4}-\d{2}-\d{2} — .+$")


def parse_observations(text: str) -> dict:
    sections = {}
    current = None
    for line in text.splitlines():
        m = HEADING.match(line.strip())
        if m:
            current = m.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current and BULLET.match(line.strip()):
            sections[current].append(line.strip())
    return sections


def build_profile(observations_text: str) -> str:
    parsed = parse_observations(observations_text)
    profile_bullets = {name: [] for name in PROFILE_SECTIONS}
    for source_section, bullets in parsed.items():
        target = SECTION_MAP.get(source_section, "Other recurring behaviors")
        profile_bullets[target].extend(bullets)

    lines = [
        "# PROFILE — behavioral patterns (regenerated, do not hand-edit)",
        "",
        "Synthesized from `observations.md`. A category only appears here once at "
        f"least {MIN_CORROBORATION} promoted observations support it — this "
        "describes what's been observed and when, not a diagnosis or assessment. "
        "Regenerated in full on every posting-automation run; edits belong in "
        "`observations.md`, not here.",
        "",
    ]
    any_section = False
    for section in PROFILE_SECTIONS:
        bullets = profile_bullets[section]
        if len(bullets) < MIN_CORROBORATION:
            continue
        any_section = True
        lines.append(f"## {section}")
        lines.extend(bullets)
        lines.append("")
    if not any_section:
        lines.append("_No category has reached the corroboration threshold yet._")
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("observations_md")
    ap.add_argument("profile_md")
    args = ap.parse_args()
    obs_path = pathlib.Path(args.observations_md)
    profile_path = pathlib.Path(args.profile_md)
    profile_path.write_text(build_profile(obs_path.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote {profile_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "E:\CLAUDE\BRAIN MAIN" && python -m pytest System/tools/tests/test_regenerate_profile.py -v`
Expected: 4 passed

- [ ] **Step 5: Run it once for real against the live observations file, review the output by hand**

Run: `cd "E:\CLAUDE\BRAIN MAIN" && python System/tools/regenerate_profile.py "Projects/ADHD Data/observations.md" "Projects/ADHD Data/PROFILE.md"`

Read the generated `Projects/ADHD Data/PROFILE.md` and confirm every line traces back to an existing `observations.md` bullet — this is the "review before trusting a new pipeline's first output" checkpoint, not an automated test.

- [ ] **Step 6: Commit**

```bash
cd "E:\CLAUDE\BRAIN MAIN"
git add "System/tools/regenerate_profile.py" "System/tools/tests/test_regenerate_profile.py" "Projects/ADHD Data/PROFILE.md"
git commit -m "Add corroboration-gated PROFILE.md synthesis from ADHD Data observations"
```

---

### Task 5: Orchestrator prompt + reused observation extraction

**Files:**
- Create: `E:\CLAUDE\AFFILATE MARKETTING\scripts\run_pipeline_prompt.md`
- Modify: `E:\CLAUDE\BRAIN MAIN\Projects\Local AI Bench Log\STATE.md` (documents the new automation in "Map")

No new Python here — Task 5 is wiring, not a testable unit. It uses `System/tools/self_extract.py` (already exists, already tested by its own hallucination guard) as-is, and calls Tasks 1-4's scripts as subprocesses/tools.

**Interfaces:**
- Consumes: `pipeline_state.read_last_run` / `write_last_run` (Task 1), `scan_activity.scan` (Task 2), `generate_hero_image.generate` (Task 3), `System/tools/self_extract.py` (existing), `System/tools/regenerate_profile.py` (Task 4).
- Produces: nothing consumed by later tasks — this is the end of the chain.

- [ ] **Step 1: Write the orchestrator prompt**

```markdown
<!-- E:\CLAUDE\AFFILATE MARKETTING\scripts\run_pipeline_prompt.md -->
# Posting-automation run (headless)

Working directory: `E:\CLAUDE\AFFILATE MARKETTING`. Do these steps in order,
stop and report if any step fails rather than skipping ahead silently.

1. `cursor = python scripts/pipeline_state.py` is not a CLI — instead import
   it or call:
   `python -c "import sys; sys.path.insert(0,'scripts'); import pipeline_state as p; print(p.read_last_run() or '2026-07-01')"`
   Use the printed value as `<cutoff>`. If it printed nothing, use `2026-07-01`.
2. `git -C "E:\CLAUDE\BRAIN MAIN" pull` — if this fails, STOP, do not write
   anything, leave `state/last_run.json` untouched.
3. `python scripts/scan_activity.py "E:\CLAUDE\BRAIN MAIN" <cutoff>` — read
   the JSON output.
4. If the list is empty: skip to step 8 (no post, no image, but still worth
   checking whether any activity happened that's new for the profiler even if
   too thin for a post — if truly nothing at all, log a no-op and skip to step 9).
5. From the scanned entries, judge which (if any, 0-2) are genuinely
   content-worthy per `PROJECT_BRIEF.md`'s content rules (a real session, test,
   number, or decision — not routine noise). For each chosen entry, draft a
   journal entry into `pending/YYYY_MM_DD_slug.md`, first-person loose voice
   matching the four existing files already in `pending/` (not the earlier
   "TESTED" boilerplate format). Every numeric/measured claim must trace to the
   scanned `STATE.md` text; use `[Placeholder: ...]` otherwise.
6. For each drafted post, run:
   `python scripts/generate_hero_image.py <slug> design/hero_images`
   If it exits with code 2 (pc2 unreachable), do not fail the run — add
   `hero_image: null` and a `[Placeholder: hero image pending, pc2 unreachable
   at run time]` note to the post's frontmatter instead, and continue.
7. For every `state_md` path that appeared in step 3's output (whether or not
   it produced a post), run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\self_extract.py" "<state_md path>"`
   This appends candidate observations to `Projects/ADHD Data/observations.pending.md`
   via the existing hallucination-guarded pipeline. Do not promote anything to
   `observations.md` yourself — that stays a separate, existing manual step.
8. Run:
   `python "E:\CLAUDE\BRAIN MAIN\System\tools\regenerate_profile.py" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\observations.md" "E:\CLAUDE\BRAIN MAIN\Projects\ADHD Data\PROFILE.md"`
9. `git add pending/ design/hero_images/` and commit in the bench-log repo
   (only if something changed). `git -C "E:\CLAUDE\BRAIN MAIN" add "Projects/ADHD Data/observations.pending.md" "Projects/ADHD Data/PROFILE.md"` and commit there too (only if something changed).
10. Update this project's `Projects/Local AI Bench Log/STATE.md` "Now" line
    to say how many drafts are waiting review.
11. Call `pipeline_state.write_last_run(<current UTC ISO timestamp>)` to move
    the cursor forward — only after every prior step succeeded (or was a
    deliberate, logged skip like the pc2-unreachable case).
```

- [ ] **Step 2: Do a manual dry run**

With no live activity guarantee, run steps 1-3 by hand first to sanity-check the scanner output before trusting the full prompt:

Run: `cd "E:\CLAUDE\AFFILATE MARKETTING" && python scripts/scan_activity.py "E:\CLAUDE\BRAIN MAIN" 2026-07-01`
Expected: a JSON array of recent-log entries across active projects, newest last.

- [ ] **Step 3: Update `Local AI Bench Log`'s `STATE.md`**

Add a line under "Map" noting the new automation: `Posting automation: scripts/run_pipeline_prompt.md, run via a Windows Scheduled Task every 2-3 days — see docs/superpowers/specs/2026-07-27-activity-posting-automation-design.md for the full design.`

- [ ] **Step 4: Commit**

```bash
cd "E:\CLAUDE\AFFILATE MARKETTING"
git add scripts/run_pipeline_prompt.md
git commit -m "Add posting-automation orchestrator prompt"
cd "E:\CLAUDE\BRAIN MAIN"
git add "Projects/Local AI Bench Log/STATE.md"
git commit -m "Note new posting-automation pipeline in Local AI Bench Log STATE.md"
```

---

### Task 6: Windows Scheduled Task registration (user runs this explicitly)

**Files:**
- Create: `E:\CLAUDE\AFFILATE MARKETTING\scripts\register_scheduled_task.ps1`

This registers a persistent, standing system change (a recurring scheduled task). Per this session's safety rules, that requires the user's own explicit go-ahead to actually execute — this task produces the script; running it is the user's call, not something to run automatically as part of "finishing the plan."

- [ ] **Step 1: Write the registration script**

```powershell
# E:\CLAUDE\AFFILATE MARKETTING\scripts\register_scheduled_task.ps1
# Registers the "Bench Log - Activity Posting Automation" task.
# Run this manually, once, after reviewing what it does — it is NOT auto-run
# by anything else in this plan.

$Action = New-ScheduledTaskAction -Execute "claude.exe" `
    -Argument "--print --dangerously-skip-permissions `"$(Get-Content 'E:\CLAUDE\AFFILATE MARKETTING\scripts\run_pipeline_prompt.md' -Raw)`"" `
    -WorkingDirectory "E:\CLAUDE\AFFILATE MARKETTING"

$Trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 3 -At 8am

Register-ScheduledTask -TaskName "Bench Log - Activity Posting Automation" `
    -Action $Action -Trigger $Trigger `
    -Description "Every 3 days: scans Main Brain activity, drafts bench-log posts, generates pc2 hero images, feeds ADHD Data profiler. Never auto-publishes." `
    -RunLevel Limited
```

- [ ] **Step 2: Verify the task definition without registering it**

Run: `powershell -NoProfile -Command "Get-Content 'E:\CLAUDE\AFFILATE MARKETTING\scripts\register_scheduled_task.ps1'"` and read it back — confirm the working directory, interval, and that no credentials are embedded.

- [ ] **Step 3: Commit**

```bash
cd "E:\CLAUDE\AFFILATE MARKETTING"
git add scripts/register_scheduled_task.ps1
git commit -m "Add (unregistered) Windows Scheduled Task definition for posting automation"
```

- [ ] **Step 4: Tell the user the exact command to run when ready**

Report to the user: `powershell -NoProfile -File "E:\CLAUDE\AFFILATE MARKETTING\scripts\register_scheduled_task.ps1"` — running it is their decision, not part of this plan's automated execution.
