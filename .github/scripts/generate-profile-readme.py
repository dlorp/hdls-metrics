#!/usr/bin/env python3
"""Generate dlorp profile README from repo-data.json.

Reads the metrics JSON and outputs a visual GitHub profile README.
Design can be swapped by modifying the render functions below.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
# Flagship projects get larger cards. Others get compact rows.
FLAGSHIP = {"r3LAY", "synapse-engine", "myc3lium"}
# Skip these from the dashboard
SKIP = {"hdls-metrics", "dlorp", "hello-world"}
# Repo order (flagship first, then alphabetical)
ORDER = ["r3LAY", "synapse-engine", "myc3lium", "phase-engine",
         "t3rra1n", "vault-crawler", "heedless.net", "knowledge-vault",
         "knowledge-vault-site", "second-movement", "myc3lium",
         "openclaw-conn", "openclaw-dash", "basiliskii-vita",
         "psx2blend", "uhh", "Bento"]

# ── Badge helpers ───────────────────────────────────────────────────
def badge(label, value, color="ff9500"):
    """Shields.io static badge."""
    return f"https://img.shields.io/badge/{label}-{value}-{color}"

def lang_badge(lang):
    """Language badge with color."""
    colors = {
        "Python": "3776AB", "TypeScript": "3178C6", "JavaScript": "F7DF1E",
        "C": "555555", "Rust": "CE422B", "Go": "00ADD8",
        "HTML": "E34F26", "CSS": "1572B6", "Shell": "89E051",
        "Lua": "000080", "Java": "ED8B00", "Ruby": "CC342D",
    }
    c = colors.get(lang, "555555")
    return badge(lang, "", c).rstrip("-")  # remove trailing dash for empty value

def time_ago(iso_str):
    """Human-readable time ago from ISO timestamp."""
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

# ── Card renderers ──────────────────────────────────────────────────
def render_flagship(repo):
    """Large card for flagship projects."""
    name = repo["name"]
    desc = repo.get("description", "No description")
    lang = repo.get("language", "")
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    pushed = time_ago(repo.get("pushed_at", ""))
    topics = repo.get("topics", [])
    release = repo.get("latest_release", {})
    rel_tag = release.get("tag", "")
    commits_7d = repo.get("commits_7d", 0)
    size_kb = repo.get("size_kb", 0)

    # Size display
    if size_kb > 1024 * 1024:
        size_str = f"{size_kb // (1024 * 1024)}GB"
    elif size_kb > 1024:
        size_str = f"{size_kb // 1024}MB"
    else:
        size_str = f"{size_kb}KB"

    # Build topic pills
    topic_str = " ".join(f"`{t}`" for t in topics[:5]) if topics else ""

    lines = [
        f"### 🔷 [{name}](https://github.com/dlorp/{name})",
        f"",
        f"> {desc}",
        f"",
    ]

    # Badges row
    badges = []
    if lang:
        badges.append(f"![{lang}](https://img.shields.io/badge/language-{lang.replace(' ', '%20')}-{lang_color(lang)})")
    badges.append(f"![stars](https://img.shields.io/github/stars/dlorp/{name}?style=flat&color=ff9500)")
    badges.append(f"![forks](https://img.shields.io/github/forks/dlorp/{name}?style=flat)")
    if rel_tag:
        badges.append(f"![release](https://img.shields.io/badge/release-{rel_tag}-brightgreen)")
    badges.append(f"![size](https://img.shields.io/badge/size-{size_str}-blue)")

    lines.append(" ".join(badges))
    lines.append("")

    # Stats line
    stats = []
    if commits_7d > 0:
        stats.append(f"📈 **{commits_7d}** commits this week")
    stats.append(f"🔄 Last active **{pushed}**")
    if stars > 0:
        stats.append(f"⭐ **{stars}** stars")
    lines.append(" · ".join(stats))

    if topic_str:
        lines.append("")
        lines.append(topic_str)

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def lang_color(lang):
    colors = {
        "Python": "3776AB", "TypeScript": "3178C6", "JavaScript": "F7DF1E",
        "C": "555555", "Rust": "CE422B", "Go": "00ADD8",
    }
    return colors.get(lang, "555555")


def render_compact(repo):
    """Compact row for non-flagship projects."""
    name = repo["name"]
    desc = repo.get("description", "No description")[:60]
    lang = repo.get("language", "")
    stars = repo.get("stars", 0)
    pushed = time_ago(repo.get("pushed_at", ""))
    commits_7d = repo.get("commits_7d", 0)

    activity = f"📈 {commits_7d}/wk" if commits_7d > 0 else "—"
    star_str = f"⭐{stars}" if stars > 0 else "—"

    return f"| [{name}](https://github.com/dlorp/{name}) | {desc} | {lang} | {star_str} | {activity} | {pushed} |"


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

    # Sort: flagship first, then by ORDER list, then alphabetical
    def sort_key(name):
        if name in FLAGSHIP:
            return (0, 0, name)
        try:
            idx = ORDER.index(name)
            return (1, idx, name)
        except ValueError:
            return (2, 0, name)

    sorted_names = sorted(repos.keys(), key=sort_key)
    # Filter out skipped repos
    sorted_names = [n for n in sorted_names if n not in SKIP]

    # ── Build README ──
    lines = []

    # Header
    lines.append('<div align="center">')
    lines.append("")
    lines.append("# HDLS — Heedless")
    lines.append("")
    lines.append("**Knowledge-as-topology.** Self-hosted AI pipelines, local-first tools,")
    lines.append("and the research infrastructure that connects them.")
    lines.append("")
    lines.append(f"![repos](https://img.shields.io/badge/{len(sorted_names)}_projects-ff9500?style=for-the-badge)")
    lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Flagship section
    flagship_repos = [repos[n] for n in sorted_names if n in FLAGSHIP]
    other_repos = [repos[n] for n in sorted_names if n not in FLAGSHIP]

    if flagship_repos:
        lines.append("## 🔷 Flagship Projects")
        lines.append("")
        for repo in flagship_repos:
            lines.append(render_flagship(repo))

    # Compact table for the rest
    if other_repos:
        lines.append("## 📦 More Projects")
        lines.append("")
        lines.append("| Project | Description | Lang | Stars | Activity | Last Active |")
        lines.append("|---------|-------------|------|-------|----------|-------------|")
        for repo in other_repos:
            lines.append(render_compact(repo))
        lines.append("")

    # Footer
    if not other_repos:
        lines.pop()  # remove last --- if no compact section followed
    lines.append("---")
    lines.append("")
    lines.append('<div align="center">')
    lines.append("")
    lines.append(f"*Last updated: {generated[:10]} by [hdls-metrics](https://github.com/dlorp/hdls-metrics)*")
    lines.append("")
    lines.append("[hdls.net](https://hdls.net) · [knowledge vault](https://github.com/dlorp/knowledge-vault)")
    lines.append("")
    lines.append("</div>")

    # Write
    out_path = Path(__file__).parents[2] / "README.md"
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Profile README written to {out_path}")
    print(f"Flagship: {[r['name'] for r in flagship_repos]}")
    print(f"Compact: {[r['name'] for r in other_repos]}")


if __name__ == "__main__":
    main()
