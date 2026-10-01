"""Generate a radical-theme GitHub stats SVG card from live API data."""
import json
import os
import urllib.request

USER = os.environ.get("GITHUB_USER", "Outsider163")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HDR = {"User-Agent": "profile-stats"}
if TOKEN:
    HDR["Authorization"] = f"token {TOKEN}"


def get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100")
own = [r for r in repos if not r["fork"]]

stars = sum(r["stargazers_count"] for r in own)

commits = 0
for r in own:
    page = 1
    while True:
        batch = get(
            f"https://api.github.com/repos/{USER}/{r['name']}/commits"
            f"?per_page=100&page={page}&author={USER}"
        )
        commits += len(batch)
        if len(batch) < 100:
            break
        page += 1

prs = issues = 0
for r in own:
    page = 1
    while True:
        batch = get(
            f"https://api.github.com/repos/{USER}/{r['name']}/issues"
            f"?state=all&per_page=100&page={page}&creator={USER}"
        )
        for it in batch:
            if "pull_request" in it:
                prs += 1
            else:
                issues += 1
        if len(batch) < 100:
            break
        page += 1

rows = [
    ("★", "Total Stars Earned:", stars),
    ("◷", "Total Commits (all-time):", commits),
    ("⇅", "Total PRs:", prs),
    ("◎", "Total Issues:", issues),
    ("☰", "Public Repos:", len(repos)),
]

W, H = 500, 195
svg = [
    f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'xmlns="http://www.w3.org/2000/svg" role="img">',
    '<style>text{font-family:Segoe UI,Ubuntu,Sans-Serif}</style>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="4.5" '
    'fill="#141321" stroke="#e1e4e8" stroke-opacity="0.15"/>',
    f'<text x="25" y="35" font-size="16" font-weight="600" fill="#fe428e">'
    f'{USER}&#8217;s GitHub Stats</text>',
]
y = 68
for icon, label, value in rows:
    svg.append(
        f'<text x="25" y="{y}" font-size="13" fill="#fe428e">{icon}</text>'
    )
    svg.append(
        f'<text x="50" y="{y}" font-size="13" fill="#a9fef7">{label}</text>'
    )
    svg.append(
        f'<text x="{W-25}" y="{y}" font-size="13" font-weight="600" '
        f'fill="#a9fef7" text-anchor="end">{value}</text>'
    )
    y += 26
svg.append("</svg>")

with open("profile-stats.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))

print(f"stars={stars} commits={commits} prs={prs} issues={issues} repos={len(repos)}")
