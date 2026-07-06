#!/usr/bin/env python3
"""Generate the dlorp profile README (dlorp/dlorp).

The profile README is CURATED here, not scraped live. dlorp's repos are
private, so shields.io — which renders badges from GitHub's *public* API with
no auth — cannot produce dynamic per-repo badges (they would render "invalid").
So every badge below is STATIC, and the banner is a PNG produced by the render
agents (SVG does not render reliably in GitHub profile READMEs — see the
banner history in git). This script owns the README's structure and prose;
the agents own the banner image and the badge values.

To update the profile: edit the CONFIG blocks below (or the banner PNG) and let
the daily-scan workflow redeploy. The repo scan (repo-data.json) is a separate
concern consumed by the vault's repo-cards cron — it does not drive this file.

repo-data.json is read only to refresh the "repos" count badge when a real
scan is present; it never injects unvalidated content and always has a static
fallback, so a missing/partial scan can never corrupt the profile.
"""

import json
from pathlib import Path

# ── Banner (agent-produced PNG; never SVG) ──────────────────────────
BANNER = "./hdls-banner.png"

# ── Intro ───────────────────────────────────────────────────────────
INTRO = [
    "A signal chain research collective. We preserve vanishing knowledge with",
    "dr3dg3-n3t, build local AI tools with synapse-engine and myc3lium, and keep",
    "smaller models viable in the field. Everything runs on hardware we own.",
]

# ── Flagship cards (curated; static badges) ─────────────────────────
# badges: list of (label, message, color, alt). label="" -> message-only badge.
FLAGSHIP = [
    {
        "name": "synapse-engine",
        "url": "https://github.com/dlorp/synapse-engine",
        "badges": [
            ("status", "active", "ff9500", "status"),
            ("stack", "Python | C++ | CUDA", "CC8800", "stack"),
            ("last commit", "recent", "ff9500", "last commit"),
            ("language", "C++", "CC8800", "language"),
        ],
        "desc": ("LLM workshop: load, benchmark, finetune, and abliterate local models. "
                 "Modular prototype system where each stage of the model lifecycle is a "
                 "separate, swappable component. Built to make smaller models viable in "
                 "the field."),
    },
    {
        "name": "myc3lium",
        "url": "https://github.com/dlorp/myc3lium",
        "badges": [
            ("status", "active", "ff9500", "status"),
            ("stack", "Python | C", "CC8800", "stack"),
            ("last commit", "recent", "ff9500", "last commit"),
            ("language", "C", "CC8800", "language"),
        ],
        "desc": ("FastAPI bridge between Reticulum mesh networking and Meshtastic LoRa. "
                 "Runs on ESP32 for low-power field deployment. Named after the "
                 "underground network of fungal mycelium."),
    },
    {
        "name": "dr3dg3-n3t",
        "url": "https://github.com/dlorp/dr3dg3-n3t",
        "badges": [
            ("status", "active", "ff9500", "status"),
            ("stack", "HTML | JSON | preservation", "CC8800", "stack"),
            ("last commit", "recent", "ff9500", "last commit"),
            ("type", "whole earth catalog", "CC8800", "type"),
        ],
        "desc": ('Offline internet — a "Web 3.0 Whole Earth Catalog" for preserving '
                 "knowledge that matters. Curated snapshots of vanishing sources, "
                 "structured for browsing without a connection."),
    },
]

# ── Other projects (curated; static status) ─────────────────────────
# stack: list of tokens joined with " | " (escaped for the markdown table).
OTHER = [
    {"name": "r3LAY", "url": "https://github.com/dlorp/r3LAY",
     "desc": "Local-first research terminal for hobbyists — maintenance logging, "
             "natural language input, RAG search across your docs",
     "stack": ["Python", "Shell"], "status": ("active", "ff9500")},
    {"name": "phase-engine", "url": "https://github.com/dlorp/phase-engine",
     "desc": "Circadian awareness tool for Sensor Watch — four natural phases, "
             "intelligent feedback. Bangle.js 2 for testing, f91W custom firmware "
             "is the target",
     "stack": ["C", "C++", "Python"], "status": ("active", "ff9500")},
    {"name": "t3rra1n", "url": "https://github.com/dlorp/t3rra1n",
     "desc": "Terminal UI that doubles as an immersive ARG — field reports from a "
             "stranded HDLS researcher documenting alien landscapes",
     "stack": ["Python"], "status": ("active", "ff9500")},
    {"name": "heedless.net", "url": "https://github.com/dlorp/heedless.net",
     "desc": "HDLS domain — public-facing site",
     "stack": ["HTML"], "status": ("active", "ff9500")},
    {"name": "knowledge-vault", "url": "https://github.com/dlorp/knowledge-vault",
     "desc": "3000+ entries across 62 domains — the collective memory",
     "stack": ["Markdown"], "status": ("active", "ff9500")},
    {"name": "vault-crawler", "url": "https://github.com/dlorp/vault-crawler",
     "desc": "Automated source intake for the knowledge vault",
     "stack": ["Python"], "status": ("active", "ff9500")},
]

# ── Metrics footer (agent-maintained static values) ─────────────────
REPOS_FALLBACK = "18"          # used when no real scan is present
LANGUAGES = "Python | C++ | C | JavaScript"
VAULT_ENTRIES = "3000+"
DOMAINS = "62"

# ── "What We Do" diagram (static) ───────────────────────────────────
WHAT_WE_DO = """preserve                 build                   research
   |                       |                       |
dr3dg3-n3t            synapse-engine          small LLMs
offline internet      model workshop          in the field
   |                       |                       |
   +-----------+-----------+-----------+-----------+
               |
            HDLS lab
     hardware we own
     no cloud, no keys"""

SKIP = {"hdls-metrics", "dlorp", "hello-world"}


# ── Helpers ─────────────────────────────────────────────────────────
def _seg(s):
    """URL-encode one shields.io path segment (label or message)."""
    return (s.replace("-", "--").replace("_", "__")
             .replace(" ", "%20").replace("|", "%7C").replace("+", "%2B"))


def badge_url(label, message, color):
    if label:
        return f"https://img.shields.io/badge/{_seg(label)}-{_seg(message)}-{color}"
    return f"https://img.shields.io/badge/{_seg(message)}-{color}"


def img(label, message, color, alt):
    return f'<img src="{badge_url(label, message, color)}" alt="{alt}" />'


def repo_count(default):
    """Live repo count from a real scan, else the static fallback.

    A real scan of dlorp/* returns many repos; the committed seed has only a
    few. Require a plausible count (>=5) before trusting it, so seed/partial
    data never shrinks the badge.
    """
    path = Path(__file__).parents[2] / "repo-data.json"
    try:
        with open(path) as f:
            repos = json.load(f).get("repos", [])
        shown = [r for r in repos if r.get("name") not in SKIP]
        if len(shown) >= 5:
            return str(len(shown))
    except (OSError, ValueError, AttributeError):
        pass
    return default


# ── Renderers ───────────────────────────────────────────────────────
def render_flagship(repo):
    badges = [f"        {img(*b)}<br/>" for b in repo["badges"][:-1]]
    badges.append(f"        {img(*repo['badges'][-1])}")
    return "\n".join([
        '    <td width="33%" valign="top">',
        f'      <h3 align="center"><a href="{repo["url"]}">{repo["name"]}</a></h3>',
        '      <p align="center">',
        *badges,
        '      </p>',
        '      <p align="center">',
        f'        {repo["desc"]}',
        '      </p>',
        '    </td>',
    ])


def render_row(repo):
    stack = " \\| ".join(repo["stack"])
    status = f"https://img.shields.io/badge/{_seg(repo['status'][0])}-{repo['status'][1]}"
    return f'| [{repo["name"]}]({repo["url"]}) | {repo["desc"]} | {stack} | ![]({status}) |'


# ── Main ────────────────────────────────────────────────────────────
def main():
    L = []

    # Banner
    L += ['<p align="center">',
          f'  <img src="{BANNER}" width="640" alt="HDLS" />',
          '</p>', '', '---', '']

    # Intro
    L += [f"> {line}" for line in INTRO]
    L += ['', '---', '']

    # Flagship
    L += ['## Flagship Projects', '', '<table>', '  <tr>']
    for repo in FLAGSHIP:
        L.append(render_flagship(repo))
    L += ['  </tr>', '</table>', '', '---', '']

    # Other projects
    L += ['## Other Projects', '',
          '| Project | Description | Stack | Status |',
          '|---------|-------------|-------|--------|']
    for repo in OTHER:
        L.append(render_row(repo))
    L += ['', '---', '']

    # What We Do
    L += ['## What We Do', '', '```', WHAT_WE_DO, '```', '', '---', '']

    # Metrics
    L += ['## Metrics', '', '<p>',
          f'  {img("repos", repo_count(REPOS_FALLBACK), "ff9500", "repos")}',
          f'  {img("languages", LANGUAGES, "CC8800", "languages")}',
          f'  {img("vault entries", VAULT_ENTRIES, "7A5200", "vault entries")}',
          f'  {img("domains", DOMAINS, "7A5200", "domains")}',
          '</p>', '', '---', '']

    # Footer
    L += ['<p align="center">',
          f'  {img("HDLS", "research collective", "ff9500", "HDLS")}',
          '</p>']

    out_path = Path(__file__).parents[2] / "PROFILE-README.md"
    with open(out_path, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"Profile README written to {out_path}")
    print(f"Flagship: {[r['name'] for r in FLAGSHIP]}")
    print(f"Other:    {[r['name'] for r in OTHER]}")


if __name__ == "__main__":
    main()
