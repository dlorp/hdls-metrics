#!/usr/bin/env python3
"""Generate dlorp profile README from repo-data.json.

Design by 0r4cl3 — CRT/demoscene aesthetic, amber phosphor badges,
3-column flagship cards, compact table for other projects, signal chain diagram.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
FLAGSHIP = {"r3LAY", "synapse-engine", "myc3lium"}
SKIP = {"hdls-metrics", "dlorp", "hello-world"}
ORDER = ["r3LAY", "synapse-engine", "myc3lium", "phase-engine",
         "t3rra1n", "vault-crawler", "heedless.net", "knowledge-vault",
         "knowledge-vault-site", "second-movement", "openclaw-conn",
         "openclaw-dash", "basiliskii-vita", "psx2blend", "uhh", "Bento"]

# Descriptions for flagship cards (can be overridden by repo data)
FLAGSHIP_DESC = {
    "r3LAY": "Local AI project management with a TUI interface. Privacy-first: runs entirely on-device with Hermes agent orchestration and local LLM inference. The operational hub for the entire HDLS signal chain.",
    "synapse-engine": "LLM workshop: load, benchmark, finetune, and abliterate local models. Modular prototype system built on FastAPI. Each stage of the model lifecycle is a separate, swappable component.",
    "myc3lium": "FastAPI bridge between Reticulum mesh networking and Meshtastic LoRa. Runs on ESP32 for low-power field deployment. Named after the underground network of fungal mycelium.",
}

# Agent roster
AGENTS = [
    ("dr3dg3", "Source hunter, crawler"),
    ("pr0b3", "Deep-work researcher"),
    ("g0blin", "Vault gatekeeper, triage"),
    ("0r4cl3", "Design keeper, brand steward"),
    ("hyph4", "Coordinator, Discord presence"),
    ("s3ntry", "Security auditor"),
    ("3tch", "Code implementation"),
    ("r3nd3r", "Visual production"),
    ("spl1c3", "Content assembly"),
]

# ── Helpers ─────────────────────────────────────────────────────────
def url_encode(s):
    return s.replace(" ", "%20").replace("|", "%7C")

def time_ago(iso_str):
    if not iso_str:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt
        days = delta.days
        if days == 0:
            hours = delta.seconds // 3600
            return f"{hours}h ago" if hours > 0 else "today"
        elif days == 1:
            return "yesterday"
        elif days < 7:
            return f"{days}d ago"
        elif days < 30:
            return f"{days // 7}w ago"
        elif days < 365:
            return f"{days // 30}mo ago"
        else:
            return f"{days // 365}y ago"
    except Exception:
        return "unknown"

# ── Renderers ───────────────────────────────────────────────────────
def render_flagship_card(repo):
    """3-column HTML table cell for a flagship project."""
    name = repo["name"]
    desc = FLAGSHIP_DESC.get(name, repo.get("description", "No description"))
    lang = repo.get("language", "")
    stack = f"{lang}" if lang else "mixed"
    homepage = repo.get("homepage", "")
    repo_url = homepage if homepage else f"https://github.com/dlorp/{name}"

    # Build stack detail from top languages
    langs = repo.get("languages_top5", [])
    if len(langs) > 1:
        stack_detail = " | ".join(langs[:3])
    else:
        stack_detail = stack

    lines = [
        f'    <td width="33%" valign="top">',
        f'      <h3 align="center"><a href="{repo_url}">{name}</a></h3>',
        f'      <p align="center">',
        f'        <img src="https://img.shields.io/badge/status-active-ff9500" alt="status" /><br/>',
        f'        <img src="https://img.shields.io/badge/stack-{url_encode(stack_detail)}-CC8800" alt="stack" /><br/>',
        f'        <img src="https://img.shields.io/github/last-commit/dlorp/{name}?color=ff9500&label=last%20commit" alt="last commit" /><br/>',
        f'        <img src="https://img.shields.io/github/languages/top/dlorp/{name}?color=CC8800" alt="language" />',
        f'      </p>',
        f'      <p align="center">',
        f'        {desc}',
        f'      </p>',
        f'    </td>',
    ]
    return "\n".join(lines)


def render_compact_row(repo):
    """Table row for non-flagship projects."""
    name = repo["name"]
    desc = repo.get("description", "No description")
    lang = repo.get("language", "")
    stack = f"{lang}" if lang else "mixed"
    homepage = repo.get("homepage", "")
    repo_url = homepage if homepage else f"https://github.com/dlorp/{name}"
    commits_7d = repo.get("commits_7d", 0)

    # Status badge
    if commits_7d > 0:
        status = "active-ff9500"
    elif repo.get("archived"):
        status = "archived-555555"
    else:
        status = "dormant-7A5200"

    return f'| [{name}]({repo_url}) | {desc[:80]} | {stack} | ![status](https://img.shields.io/badge/{status}) |'


# ── Main ────────────────────────────────────────────────────────────
def main():
    data_path = Path(__file__).parents[2] / "repo-data.json"
    if not data_path.exists():
        print(f"ERROR: {data_path} not found")
        return

    with open(data_path) as f:
        data = json.load(f)

    repos = {r["name"]: r for r in data.get("repos", [])}
    generated = data.get("generated_at", "unknown")

    # Sort
    def sort_key(name):
        if name in FLAGSHIP:
            return (0, 0, name)
        try:
            idx = ORDER.index(name)
            return (1, idx, name)
        except ValueError:
            return (2, 0, name)

    sorted_names = sorted(repos.keys(), key=sort_key)
    sorted_names = [n for n in sorted_names if n not in SKIP]

    flagship_repos = [repos[n] for n in sorted_names if n in FLAGSHIP]
    other_repos = [repos[n] for n in sorted_names if n not in FLAGSHIP]

    # ── Build README ──
    lines = []

    # Banner
    lines.append('<p align="center">')
    lines.append('  <img src="./hdls-banner.svg" width="640" alt="HDLS — signal chain research collective" />')
    lines.append('</p>')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Intro
    lines.append('> HDLS is a personal research collective studying local AI, mesh networking,')
    lines.append('> knowledge systems, and embedded firmware. Everything runs on hardware I own.')
    lines.append('> No cloud dependencies, no API keys, no telemetry. The work is organized')
    lines.append('> through a signal chain of agents that hunt, read, ingest, and design.')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Flagship cards
    if flagship_repos:
        lines.append('## Flagship Projects')
        lines.append('')
        lines.append('<table>')
        lines.append('  <tr>')
        for repo in flagship_repos:
            lines.append(render_flagship_card(repo))
        lines.append('  </tr>')
        lines.append('</table>')
        lines.append('')
        lines.append('---')
        lines.append('')

    # Compact table
    if other_repos:
        lines.append('## Other Projects')
        lines.append('')
        lines.append('| Project | Description | Stack | Status |')
        lines.append('|---------|-------------|-------|--------|')
        for repo in other_repos:
            lines.append(render_compact_row(repo))
        lines.append('')
        lines.append('---')
        lines.append('')

    # Signal chain
    lines.append('## Signal Chain')
    lines.append('')
    lines.append('The HDLS pipeline runs as a signal chain of specialized agents. Each stage')
    lines.append('shapes the signal before passing it to the next:')
    lines.append('')
    lines.append('```')
    lines.append('  dr3dg3        pr0b3        g0blin')
    lines.append('    |             |             |')
    lines.append('    v             v             v')
    lines.append('  hunt  ------>  read  ------>  ingest  ------>  vault')
    lines.append('    |             |             |                |')
    lines.append('    |             |             |                |')
    lines.append('    +-------------+-------------+----------------+')
    lines.append('                          |')
    lines.append('                          v')
    lines.append('                       0r4cl3')
    lines.append('                    (design keeper)')
    lines.append('```')
    lines.append('')
    lines.append('| Agent | Role |')
    lines.append('|-------|------|')
    for agent, role in AGENTS:
        lines.append(f'| {agent} | {role} |')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Metrics footer
    lines.append('## Metrics')
    lines.append('')
    lines.append('<p>')

    # Creation dates for flagship
    for repo in flagship_repos:
        name = repo["name"]
        lines.append(f'  <img src="https://img.shields.io/github/created-at/dlorp/{name}?color=ff9500&label=" alt="" />')
    lines.append('</p>')
    lines.append('')
    lines.append('<p>')

    # Summary badges
    total_repos = len(sorted_names)
    lines.append(f'  <img src="https://img.shields.io/badge/repos-{total_repos}-ff9500" alt="repos" />')

    # Collect all languages
    all_langs = set()
    for repo in repos.values():
        if repo.get("language"):
            all_langs.add(repo["language"])
    lang_str = url_encode(" | ".join(sorted(all_langs)[:4]))
    lines.append(f'  <img src="https://img.shields.io/badge/languages-{lang_str}-CC8800" alt="languages" />')

    lines.append(f'  <img src="https://img.shields.io/badge/vault%20entries-3100%2B-7A5200" alt="vault entries" />')
    lines.append(f'  <img src="https://img.shields.io/badge/domains-62-7A5200" alt="domains" />')
    lines.append('</p>')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Footer
    lines.append('<p align="center">')
    lines.append(f'  <img src="https://img.shields.io/badge/HDLS-signal%20chain%20research%20collective-ff9500" alt="HDLS" />')
    lines.append('</p>')

    # Write
    out_path = Path(__file__).parents[2] / "PROFILE-README.md"
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Profile README written to {out_path}")
    print(f"Flagship: {[r['name'] for r in flagship_repos]}")
    print(f"Compact: {[r['name'] for r in other_repos]}")
    print(f"Total: {len(sorted_names)} repos")


if __name__ == "__main__":
    main()
