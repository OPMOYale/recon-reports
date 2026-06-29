#!/usr/bin/env python3
"""
Recon Reports — publish helper.

Encrypts a Recon HTML report with a password (via StatiCrypt) and drops the
ENCRYPTED file into this repository, then rebuilds index.html.

The unencrypted source report is NEVER copied here — only the encrypted output.

Usage
-----
Add or update a report:
    python publish_report.py add "C:\\Claude\\Recon\\reports\\2026-06-29_streamlining-....html" "MyPassword123!" --title "Streamlining the Workday Expense Process at Yale" --out expense-report.html

Rotate a password (re-encrypt the same source with a new password):
    python publish_report.py add "<same source>" "NewPassword!" --out expense-report.html

Rebuild the landing page only (after manually editing reports.json):
    python publish_report.py reindex

Then: commit + push in GitHub Desktop. GitHub Pages serves the result.

Requirements: Node.js + npx on PATH (StatiCrypt runs via `npx staticrypt`).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent
MANIFEST = REPO / "reports.json"
INDEX = REPO / "index.html"
TMP = REPO / ".tmp"


def load_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("  warning: reports.json was unreadable; starting fresh", file=sys.stderr)
    return []


def save_manifest(items):
    MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def find_npx():
    for cand in ("npx", "npx.cmd"):
        p = shutil.which(cand)
        if p:
            return p
    return None


def encrypt(source: Path, password: str, out_name: str):
    """Encrypt `source` with StatiCrypt, writing REPO/<out_name> (encrypted)."""
    npx = find_npx()
    if not npx:
        sys.exit("ERROR: could not find `npx` on PATH. Install Node.js, then retry.")
    if not source.exists():
        sys.exit(f"ERROR: source report not found: {source}")

    TMP.mkdir(exist_ok=True)
    staged = TMP / out_name            # encrypt a copy named exactly as we want the output
    shutil.copy(source, staged)
    try:
        # StatiCrypt writes <outdir>/<basename of input>. We point outdir at the repo root.
        cmd = [npx, "-y", "staticrypt", str(staged), "-p", password, "-d", str(REPO)]
        print(f"  encrypting -> {out_name} ...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            sys.stderr.write(res.stdout + "\n" + res.stderr + "\n")
            sys.exit("ERROR: StatiCrypt failed (see output above).")
    finally:
        # never leave the unencrypted staged copy lying around
        try:
            staged.unlink(missing_ok=True)
        except OSError:
            pass

    produced = REPO / out_name
    if not produced.exists():
        sys.exit(f"ERROR: expected encrypted file was not produced: {produced}")
    return produced


def upsert(items, out_name, title):
    for it in items:
        if it.get("file") == out_name:
            it["title"] = title
            it["updated"] = date.today().isoformat()
            return items
    items.append({
        "file": out_name,
        "title": title,
        "added": date.today().isoformat(),
        "updated": date.today().isoformat(),
    })
    return items


def build_index(items):
    items = sorted(items, key=lambda x: x.get("updated", ""), reverse=True)
    cards = []
    for it in items:
        cards.append(f"""      <a class="card" href="{it['file']}" target="_blank" rel="noopener">
        <div class="kicker">DIAGNOSTIC BRIEF · RECON</div>
        <div class="title">{it['title']}</div>
        <div class="meta">Updated {it.get('updated','')} · password required</div>
        <div class="cta">Open report &rarr;</div>
      </a>""")
    if not cards:
        cards.append('      <p class="empty">No reports published yet.</p>')
    cards_html = "\n".join(cards)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Recon Reports</title>
<style>
  :root {{ --ink:#0a1f44; --gold:#b58a2e; --paper:#f7f6f2; --muted:#5b6472; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  header {{ background:var(--ink); color:#fff; padding:48px 24px 40px; }}
  .wrap {{ max-width:880px; margin:0 auto; padding:0 24px; }}
  header .wrap {{ padding:0; }}
  .brand {{ font-size:13px; letter-spacing:.22em; color:var(--gold); font-weight:600; }}
  header h1 {{ font-size:30px; margin:10px 0 6px; font-weight:650; }}
  header p {{ color:#c9d2e3; margin:0; max-width:60ch; line-height:1.5; }}
  main {{ padding:36px 0 64px; }}
  .grid {{ display:grid; gap:16px; }}
  .card {{ display:block; text-decoration:none; color:inherit; background:#fff;
    border:1px solid #e6e3da; border-radius:14px; padding:22px 24px;
    transition:box-shadow .15s ease, transform .15s ease; }}
  .card:hover {{ box-shadow:0 8px 28px rgba(10,31,68,.12); transform:translateY(-1px); }}
  .kicker {{ font-size:11px; letter-spacing:.18em; color:var(--gold); font-weight:600; }}
  .title {{ font-size:19px; font-weight:600; margin:6px 0 4px; line-height:1.3; }}
  .meta {{ font-size:13px; color:var(--muted); }}
  .cta {{ margin-top:12px; font-size:14px; color:var(--ink); font-weight:600; }}
  .empty {{ color:var(--muted); }}
  footer {{ color:var(--muted); font-size:12px; padding:0 0 48px; line-height:1.6; }}
  footer .wrap {{ border-top:1px solid #e6e3da; padding-top:18px; }}
</style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="brand">RECON &middot; YALE</div>
      <h1>Analysis briefs</h1>
      <p>Each report opens in your browser and prompts for a password. Content is encrypted at rest; without the password the page cannot be read.</p>
    </div>
  </header>
  <main>
    <div class="wrap">
      <div class="grid">
{cards_html}
      </div>
    </div>
  </main>
  <footer>
    <div class="wrap">
      Confidential &mdash; for intended recipients only. Do not redistribute the link and password together.
    </div>
  </footer>
</body>
</html>
"""
    INDEX.write_text(html, encoding="utf-8")
    print(f"  rebuilt index.html ({len(items)} report(s))")


def cmd_add(args):
    out = args.out or Path(args.source).name
    if not out.endswith(".html"):
        out += ".html"
    encrypt(Path(args.source), args.password, out)
    items = load_manifest()
    title = args.title or out.replace("-", " ").replace(".html", "").title()
    items = upsert(items, out, title)
    save_manifest(items)
    build_index(items)
    print(f"OK  published '{title}' -> {out}")
    print("    Next: commit + push in GitHub Desktop.")


def cmd_reindex(_args):
    build_index(load_manifest())


def main():
    ap = argparse.ArgumentParser(description="Publish an encrypted Recon report.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="encrypt a report and add/update it in the repo")
    a.add_argument("source", help="path to the unencrypted Recon HTML report")
    a.add_argument("password", help="password viewers will need")
    a.add_argument("--title", help="display title on the landing page")
    a.add_argument("--out", help="output filename in the repo (e.g. expense-report.html)")
    a.set_defaults(func=cmd_add)

    r = sub.add_parser("reindex", help="rebuild index.html from reports.json")
    r.set_defaults(func=cmd_reindex)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
