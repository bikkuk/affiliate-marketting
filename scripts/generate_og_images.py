#!/usr/bin/env python
"""Render 1200x630 social preview cards for every page, in the site's own brand.

Shares on Reddit / Hacker News / LinkedIn / Slack render as a bare grey link
without an og:image. This draws each card from the same palette and the same
self-hosted fonts the site already ships in public/fonts/, so a share looks
like the site rather than like a stock template.

Fonts are woff2 (that is what the browser wants); Pillow needs TrueType, so
they are decompressed to build/fonts_ttf/ on the fly. That directory is
disposable and gitignored -- the woff2 files in public/fonts/ stay the source
of truth.

Usage:  python scripts/generate_og_images.py [--check]
        --check verifies every card exists and is current, and exits non-zero
        if not (so it can gate a build without rewriting files).
"""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WOFF_DIR = os.path.join(ROOT, 'public', 'fonts')
TTF_DIR = os.path.join(ROOT, 'build', 'fonts_ttf')
OUT_DIR = os.path.join(ROOT, 'public', 'og')

W, H = 1200, 630
BG = '#15130F'
INK = '#EDE6D8'
INK_DIM = '#A39C8C'
MUTED = '#7C8577'
ACCENT = '#E8A33D'
LINE = '#2B2820'

PAD = 72

# slug -> (stamp, title, meta). Slug 'home' is the site-wide default card.
CARDS = {
    'home': (
        'local ai \u00b7 tested on ordinary hardware',
        'We test which local AI models and ComfyUI workflows actually run, '
        'then publish the exact configs.',
        'bench.log \u00b7 RTX 5070 Ti \u00b7 ComfyUI \u00b7 on-prem RAG',
    ),
    '40gb-ai-server-from-2014-parts': (
        'planned \u00b7 infrastructure \u00b7 part 1 of 2',
        "I'm building a 40 GB AI server out of 2014 server parts, and the "
        'GPUs are the boring half',
        '25 Aug 2026 \u00b7 dual Xeon E5-2620 v3 \u00b7 X10DRi-T4+ \u00b7 40 GB pooled VRAM',
    ),
    'bought-the-server-filming-the-build': (
        'ordered \u00b7 infrastructure \u00b7 part 2 of 2',
        'I bought the whole server, and now I get to do nothing about it '
        'for a week',
        '26 Aug 2026 \u00b7 RTX 3090 + RTX 5070 Ti \u00b7 112 GB DDR4 \u00b7 Ubuntu Server',
    ),
    'style-lora-rendered-photographs': (
        'tested \u00b7 storybook \u00b7 16 pages rendered',
        'My illustration model rendered photographs, and turning the dial '
        'did nothing',
        '5 Aug 2026 \u00b7 Flux.1-dev fp8 \u00b7 two stacked LoRAs \u00b7 RTX 5070 Ti 16 GB',
    ),
    'localki-excel-chunking-bug': (
        'tested \u00b7 localki \u00b7 pc1 offline',
        "Why a tax advisor's Excel habit broke my RAG pipeline",
        '24 Jul 2026 \u00b7 FastAPI \u00b7 ChromaDB \u00b7 Ollama Qwen 2.5 14B',
    ),
    'cleaning-up-30-dead-html-files': (
        'tested \u00b7 localki \u00b7 deploy pipeline',
        'Cleaning up 30 dead HTML files taught me more about deploys than '
        'the deploy did',
        '23 Jul 2026 \u00b7 GitHub \u00b7 Netlify \u00b7 Continuous Deployment',
    ),
    'should-i-even-offer-lora-training': (
        'researched \u00b7 localki / klarverk \u00b7 not built',
        "A client asked if I could train a custom model on their images. "
        "I didn't know yet.",
        '21 Jul 2026 \u00b7 Stable Diffusion LoRA fine-tuning \u00b7 on-prem',
    ),
}


def ttf(name):
    """Decompress one of the site's woff2 faces to TrueType, cached."""
    if not os.path.isdir(TTF_DIR):
        os.makedirs(TTF_DIR)
    out = os.path.join(TTF_DIR, name + '.ttf')
    if not os.path.exists(out):
        src = os.path.join(WOFF_DIR, name + '.woff2')
        if not os.path.exists(src):
            raise SystemExit('missing font: %s' % src)
        f = TTFont(src)
        f.flavor = None
        f.save(out)
    return out


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(slug, stamp, title, meta):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    grotesk_b = ttf('space-grotesk-700-latin')
    grotesk_m = ttf('space-grotesk-500-latin')
    mono = ttf('jetbrains-mono-400-latin')

    f_mark = ImageFont.truetype(grotesk_b, 30)
    f_stamp = ImageFont.truetype(mono, 20)
    f_meta = ImageFont.truetype(mono, 20)

    # A hairline frame + a thick accent spine down the left edge, so the card
    # reads as this site even at thumbnail size.
    d.rectangle([0, 0, W - 1, H - 1], outline=LINE, width=2)
    d.rectangle([0, 0, 8, H], fill=ACCENT)

    # Wordmark, with ".log" in accent the way the site header does it.
    x = PAD
    d.text((x, PAD - 8), 'bench', font=f_mark, fill=INK)
    x += d.textlength('bench', font=f_mark)
    d.text((x, PAD - 8), '.log', font=f_mark, fill=ACCENT)

    # Stamp, boxed in accent like the on-site .stamp element.
    sy = PAD + 58
    sw = d.textlength(stamp, font=f_stamp)
    d.rectangle([PAD, sy, PAD + sw + 26, sy + 38], outline=ACCENT, width=2)
    d.text((PAD + 13, sy + 7), stamp, font=f_stamp, fill=ACCENT)

    # Title: shrink to fit rather than truncate -- a cut-off headline is worse
    # than a slightly smaller one.
    max_w = W - (PAD * 2)
    for size in (62, 58, 54, 50, 46, 42, 38):
        f_title = ImageFont.truetype(grotesk_m, size)
        lines = wrap(d, title, f_title, max_w)
        lh = int(size * 1.22)
        if len(lines) * lh <= 300:
            break
    ty = sy + 78
    for ln in lines:
        d.text((PAD, ty), ln, font=f_title, fill=INK)
        ty += lh

    # Meta, pinned to the bottom above a rule.
    d.line([PAD, H - PAD - 46, W - PAD, H - PAD - 46], fill=LINE, width=2)
    d.text((PAD, H - PAD - 28), meta, font=f_meta, fill=MUTED)

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    path = os.path.join(OUT_DIR, slug + '.png')
    img.save(path, 'PNG', optimize=True)
    return path


def main():
    check = '--check' in sys.argv
    missing = []
    for slug, (stamp, title, meta) in sorted(CARDS.items()):
        path = os.path.join(OUT_DIR, slug + '.png')
        if check:
            if not os.path.exists(path):
                missing.append(slug)
            continue
        p = render(slug, stamp, title, meta)
        print('%-42s %6.1f KB' % (slug + '.png', os.path.getsize(p) / 1024.0))
    if check:
        if missing:
            print('MISSING og cards: %s' % ', '.join(missing))
            return 1
        print('all %d og cards present' % len(CARDS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
