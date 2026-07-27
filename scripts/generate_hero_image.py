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
