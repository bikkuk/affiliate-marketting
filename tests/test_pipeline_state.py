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
