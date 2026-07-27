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
