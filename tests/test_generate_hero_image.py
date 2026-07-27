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
