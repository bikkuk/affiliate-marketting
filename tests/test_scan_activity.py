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
