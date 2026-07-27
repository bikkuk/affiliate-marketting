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
