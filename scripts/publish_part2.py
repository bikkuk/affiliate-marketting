#!/usr/bin/env python
"""One-shot publisher for the AI-server series, part 2 of 2.

Approved for unattended publication by Nipoon on 2026-08-26 ("post one today
and the other in 3 days, dont wait for any more aprovals for both").
Part 1 went live 2026-08-26; this publishes part 2 on 2026-08-29.

Registered as the one-time scheduled task "Bench Log - Publish AI Server Part 2"
(see register_publish_part2.ps1). Idempotent: exits 0 without doing anything if
the staged files are gone, so a re-run or a retry can't double-publish.
"""
import io
import os
import shutil
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, 'scheduled', '2026_08_29')
SLUG = 'bought-the-server-filming-the-build'
ASTRO = SLUG + '.astro'
MD = '2026_08_26_parts_ordered_filming_the_build.md'

INDEX_MARKER = '  <!-- ENTRIES:TOP -->\n'
INDEX_ENTRY = '''
  <article class="entry">
    <span class="stamp">ordered \u00b7 infrastructure \u00b7 part 2 of 2</span>
    <h2>I bought the whole server, and now I get to do nothing about it for a week</h2>
    <div class="meta">26 Aug 2026 \u00b7 RTX 3090 24 GB + RTX 5070 Ti 16 GB \u00b7 112 GB DDR4 \u00b7 Ubuntu Server</div>
    <p>Every part for the third node is bought and none of it has arrived. What "all the parts" actually covers, why the 3090 leaving my desktop is the real price, and the rules I'm setting before I put a camera on the assembly.</p>
    <a class="read-more" href="/log/%s">Read the full entry \u2192</a>
  </article>
''' % SLUG

SITEMAP_MARKER = '  <!-- SITEMAP:TOP -->\n'
SITEMAP_ENTRY = '''  <url>
    <loc>https://hoppingproject.netlify.app/log/%s</loc>
    <lastmod>2026-08-26</lastmod>
    <priority>0.8</priority>
  </url>
''' % SLUG


def log(msg):
    line = '[%s] %s' % (date.today().isoformat(), msg)
    print(line)
    with io.open(os.path.join(ROOT, 'scheduled', 'publish_part2.log'), 'a',
                 encoding='utf-8') as fh:
        fh.write(line + '\n')


def insert_after(path, marker, payload):
    with io.open(path, encoding='utf-8') as fh:
        src = fh.read()
    if payload.strip() in src:
        log('SKIP %s: entry already present' % os.path.basename(path))
        return
    if src.count(marker) != 1:
        raise SystemExit('ABORT: marker not found exactly once in %s' % path)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(src.replace(marker, marker + payload))
    log('inserted entry into %s' % os.path.basename(path))


def run(cmd):
    proc = subprocess.run(cmd, cwd=ROOT, shell=False,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode('utf-8', 'replace').strip()
    if proc.returncode != 0:
        log('FAILED (%d): %s\n%s' % (proc.returncode, ' '.join(cmd), out))
        raise SystemExit(proc.returncode)
    return out


def main():
    staged_astro = os.path.join(STAGE, ASTRO)
    staged_md = os.path.join(STAGE, MD)
    if not (os.path.exists(staged_astro) and os.path.exists(staged_md)):
        log('nothing staged at %s - already published, exiting clean' % STAGE)
        return 0

    log('publishing part 2: %s' % SLUG)
    shutil.move(staged_astro, os.path.join(ROOT, 'src', 'pages', 'log', ASTRO))
    shutil.move(staged_md, os.path.join(ROOT, 'published', MD))
    log('moved page into src/pages/log/ and markdown into published/')

    insert_after(os.path.join(ROOT, 'src', 'pages', 'index.astro'),
                 INDEX_MARKER, INDEX_ENTRY)
    insert_after(os.path.join(ROOT, 'public', 'sitemap.xml'),
                 SITEMAP_MARKER, SITEMAP_ENTRY)

    shutil.rmtree(STAGE, ignore_errors=True)

    npm = shutil.which('npm') or shutil.which('npm.cmd')
    if npm:
        run([npm, 'run', 'build'])
        log('astro build OK')
    else:
        log('WARNING: npm not on PATH, skipped local build check')

    run(['git', 'add', '-A'])
    run(['git', 'commit', '-m',
         'Publish: I bought the whole server, and now I get to do nothing '
         'about it for a week (part 2 of 2)\n\n'
         'Second half of the AI-server series. Scheduled publication, '
         'pre-approved 2026-08-26 alongside part 1.\n\n'
         'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>'])
    run(['git', 'push', 'origin', 'main'])
    log('committed and pushed - Netlify will deploy')
    return 0


if __name__ == '__main__':
    sys.exit(main())
