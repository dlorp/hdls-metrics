#!/usr/bin/env python3
"""Render the dlorp/dlorp profile README from profile-config.json.

Ownership split (deliberate):
- This script owns LAYOUT and PROSE assembly only.
- profile-config.json owns every BADGE value and the banner reference — it is
  manual / agent-owned. The renderer never invents, scrapes, or defaults a
  badge; it only places the values the config supplies. (dlorp's repos are
  private, so shields.io dynamic badges can't work anyway — badges must be
  curated static values.)
- The banner IMAGE (hdls-banner.png) is pinned in dlorp/dlorp and is NOT
  deployed by the workflow, so automation can never overwrite it.

To change the profile: edit profile-config.json (or the banner PNG in
dlorp/dlorp). repo-data.json (the scan output) feeds the vault's repo-cards
cron and is intentionally NOT read here.
"""

import json
import sys
from pathlib import Path

CONFIG = Path(__file__).parents[2] / "profile-config.json"


def _seg(s):
    """URL-encode one shields.io path segment (label or message)."""
    return (s.replace("-", "--").replace("_", "__")
             .replace(" ", "%20").replace("|", "%7C").replace("+", "%2B"))


def badge_url(label, message, color):
    if label:
        return f"https://img.shields.io/badge/{_seg(label)}-{_seg(message)}-{color}"
    return f"https://img.shields.io/badge/{_seg(message)}-{color}"


def img(spec):
    """spec = [label, message, color, alt]."""
    label, message, color, alt = spec
    return f'<img src="{badge_url(label, message, color)}" alt="{alt}" />'


def render_flagship(repo):
    badges = [f"        {img(b)}<br/>" for b in repo["badges"][:-1]]
    badges.append(f"        {img(repo['badges'][-1])}")
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


def main():
    try:
        with open(CONFIG) as f:
            cfg = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot read {CONFIG}: {exc}", file=sys.stderr)
        return 1

    L = []

    # Banner (reference only; the image is pinned in dlorp/dlorp)
    L += ['<p align="center">',
          f'  <img src="{cfg["banner"]}" width="640" alt="HDLS" />',
          '</p>', '', '---', '']

    # Intro
    L += [f"> {line}" for line in cfg["intro"]]
    L += ['', '---', '']

    # Flagship
    L += ['## Flagship Projects', '', '<table>', '  <tr>']
    for repo in cfg["flagship"]:
        L.append(render_flagship(repo))
    L += ['  </tr>', '</table>', '', '---', '']

    # Other projects
    L += ['## Other Projects', '',
          '| Project | Description | Stack | Status |',
          '|---------|-------------|-------|--------|']
    for repo in cfg["other_projects"]:
        L.append(render_row(repo))
    L += ['', '---', '']

    # What We Do
    L += ['## What We Do', '', '```', cfg["what_we_do"], '```', '', '---', '']

    # Metrics
    L += ['## Metrics', '', '<p>']
    L += [f'  {img(b)}' for b in cfg["metrics"]]
    L += ['</p>', '', '---', '']

    # Footer
    L += ['<p align="center">', f'  {img(cfg["footer"])}', '</p>']

    out_path = Path(__file__).parents[2] / "PROFILE-README.md"
    with open(out_path, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"Profile README written to {out_path}")
    print(f"Flagship: {[r['name'] for r in cfg['flagship']]}")
    print(f"Other:    {[r['name'] for r in cfg['other_projects']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
