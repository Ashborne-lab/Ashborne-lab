"""Draws the profile artwork (hero + animated year) as SVG, dark and light.

Usage: python scripts/generate.py [saved-contributions.html]
Reads the public contribution calendar, so it needs no token.
"""
import random
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path
from string import Template

USER = "Ashborne-lab"
NAME = "Shivam Kumar"
INITIALS = "SK"
TAGLINES = [
    "building agents that remember",
    "knowledge graphs and retrieval (RAG)",
    "learning in public, one PR at a time",
]
OUT = Path(__file__).resolve().parent.parent / "assets"

W, PAD = 850, 40
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(
        bg0="#0b1020", bg1="#111a30", border="#232c44", text="#e8edf7", muted="#7f8aa3",
        accent="#2dd4bf", hot="#fbbf24", beam="#ffffff", star="#9fb0d0",
        levels=["#182036", "#1a6b85", "#1a9aa3", "#2dd4bf", "#fbbf24"],
    ),
    "light": dict(
        bg0="#fbfcff", bg1="#eef2fa", border="#d5dcea", text="#141a2a", muted="#5f6b85",
        accent="#0d9488", hot="#d97706", beam="#0d9488", star="#9aa6c0",
        levels=["#e1e6f1", "#a9ded6", "#55bfb2", "#0d9488", "#d97706"],
    ),
}


def load_days(html):
    """-> sorted [(date, count, level)] from the contribution calendar markup."""
    tips = {
        m[1]: 0 if m[2] == "No" else int(m[2])
        for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>(No|\d+) contributions?', html)
    }
    days = []
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        d = re.search(r'data-date="([\d-]+)"', td)
        if not d:  # legend swatches have no date
            continue
        cell_id = re.search(r'\bid="([^"]+)"', td)[1]
        level = int(re.search(r'data-level="(\d)"', td)[1])
        days.append((date.fromisoformat(d[1]), tips.get(cell_id, 0), level))
    days.sort()
    if len(days) < 360 or (sum(c for _, c, _ in days) == 0 and any(l for *_, l in days)):
        sys.exit(f"contribution calendar did not parse ({len(days)} days); markup changed?")
    return days


def longest_streak(days):
    best = run = 0
    for _, count, _ in days:
        run = run + 1 if count else 0
        best = max(best, run)
    return best


# ---------------------------------------------------------------- year ----
CYCLE = 14.0  # seconds; every animated element shares it so nothing drifts
SWEEP = 8.0  # seconds the spark takes to cross the year

YEAR = Template("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $W $H" width="$W" height="$H" role="img" aria-label="$alt">
<defs>
<linearGradient id="bg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="$H"><stop offset="0" stop-color="$bg0"/><stop offset="1" stop-color="$bg1"/></linearGradient>
<linearGradient id="core" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="$beam"/><stop offset=".85" stop-color="$beam" stop-opacity=".55"/><stop offset="1" stop-color="$beam" stop-opacity="0"/></linearGradient>
<linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent" stop-opacity=".38"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>
<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="$hot" stop-opacity="0"/><stop offset="1" stop-color="$hot"/></linearGradient>
<filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3.5"/></filter>
</defs>
<style>
text{font-family:$sans}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.2em;fill:$accent}
.small{font-size:11px;fill:$muted}
.num{font-size:26px;font-weight:800;fill:$text}
.label{font-size:11px;letter-spacing:.08em;fill:$muted}
.c,.ring,.spark{transform-box:fill-box;transform-origin:center}
.c{animation-duration:${cycle}s;animation-iteration-count:infinite}
.beam{animation:beam ${cycle}s linear infinite}
.ring{fill:none;stroke:$hot;stroke-width:1.2;opacity:0;animation:ring ${cycle}s ease-out infinite}
.spark{fill:$hot;opacity:0;animation:spark ${cycle}s ease-out infinite}
@keyframes beam{0%{transform:translateX(${x0}px);opacity:0}1.5%{opacity:1}$sweep_pct%{transform:translateX(${x1}px);opacity:1}$sweep_end%,100%{transform:translateX(${x1}px);opacity:0}}
@keyframes ring{0%{opacity:.95;transform:scale(.5)}7%{opacity:0;transform:scale(3.6)}100%{opacity:0;transform:scale(3.6)}}
@keyframes spark{0%{opacity:1;transform:translateY(0)}9%{opacity:0;transform:translateY(-38px)}100%{opacity:0;transform:translateY(-38px)}}
$col_keyframes
@media (prefers-reduced-motion:reduce){*{animation:none!important}.beam,.ring,.spark{display:none}}
</style>
<rect x=".5" y=".5" width="${Wm}" height="${Hm}" rx="16" fill="url(#bg)" stroke="$border"/>
<text class="eyebrow" x="$PAD" y="40">365 DAYS, REPLAYED</text>
$legend
$cells
$months
<g class="beam">
<rect x="-24" y="$glow_y" width="48" height="$glow_h" fill="url(#glow)"/>
<rect x="-1" y="$orb_y" width="2" height="$core_h" fill="url(#core)"/>
<rect x="-36" y="$trail_y" width="36" height="2" rx="1" fill="url(#trail)"/>
<circle cx="0" cy="$orb_y" r="9" fill="$hot" filter="url(#soft)"/>
<circle cx="0" cy="$orb_y" r="3.6" fill="$beam"/>
</g>
$bursts
<line x1="$PAD" x2="$right" y1="$rule_y" y2="$rule_y" stroke="$border"/>
$stats
</svg>
""")


def year_svg(days, t):
    pitch = (W - 2 * PAD) / 53
    size, top = pitch - 3, 76
    grid_h = 7 * pitch
    first = days[0][0]
    H = 306

    def pos(d):  # calendar layout: one column per week, Sunday on top
        offset = (d - first).days + (first.weekday() + 1) % 7
        return offset // 7, offset % 7

    def lit_at(col):  # second the spark reaches this column
        return SWEEP * (col + 0.5) / 53

    cells, cols = [], set()
    for d, count, level in days:
        col, row = pos(d)
        x, y = PAD + col * pitch, top + row * pitch
        cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="2.6" fill="{t["levels"][0]}"/>')
        if count:
            cols.add(col)
            cells.append(
                f'<rect class="c" style="animation-name:k{col}" x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" '
                f'height="{size:.1f}" rx="2.6" fill="{t["levels"][max(level, 1)]}"/>'
            )

    keyframes = []
    for col in sorted(cols):
        p = lit_at(col) / CYCLE * 100
        keyframes.append(
            f"@keyframes k{col}{{0%,{p:.2f}%{{opacity:0;transform:scale(.3)}}"
            f"{p + 1.4:.2f}%{{opacity:1;transform:scale(1.45)}}{p + 3.4:.2f}%,90%{{opacity:1;transform:scale(1)}}"
            f"95.5%,100%{{opacity:0;transform:scale(1)}}}}"
        )

    bursts = []
    for d, count, _ in sorted(days, key=lambda day: -day[1])[:6]:
        if not count:
            break
        col, row = pos(d)
        cx, cy = PAD + col * pitch + size / 2, top + row * pitch + size / 2
        delay = f'style="animation-delay:{lit_at(col):.2f}s"'
        bursts.append(f'<circle class="ring" {delay} cx="{cx:.1f}" cy="{cy:.1f}" r="{size / 2:.1f}"/>')
        bursts.append(f'<circle class="spark" {delay} cx="{cx:.1f}" cy="{cy:.1f}" r="1.9"/>')

    months, last_col = [], -9
    for d, _, _ in days:
        col, _ = pos(d)
        if d.day == 1 and col - last_col >= 3 and col < 52:
            months.append(f'<text class="small" x="{PAD + col * pitch:.1f}" y="{top + grid_h + 16:.0f}">{d:%b}</text>')
            last_col = col

    legend = [f'<text class="small" x="{W - PAD}" y="40" text-anchor="end">more</text>']
    for i in range(5):
        legend.append(f'<rect x="{W - PAD - 100 + i * 14}" y="30" width="11" height="11" rx="2.6" fill="{t["levels"][i]}"/>')
    legend.append(f'<text class="small" x="{W - PAD - 106}" y="40" text-anchor="end">less</text>')

    total = sum(c for _, c, _ in days)
    best = max(days, key=lambda day: day[1])
    stats_data = [
        (f"{total:,}", "CONTRIBUTIONS"),
        (str(sum(1 for _, c, _ in days if c)), "ACTIVE DAYS"),
        (f"{longest_streak(days)} days", "LONGEST STREAK"),
        (str(best[1]), f"BEST DAY · {best[0]:%b} {best[0].day}".upper()),
    ]
    stats = []
    for i, (num, label) in enumerate(stats_data):
        x = PAD + i * (W - 2 * PAD) / 4
        stats.append(f'<text class="num" x="{x:.0f}" y="{H - 48}">{num}</text><text class="label" x="{x:.0f}" y="{H - 28}">{label}</text>')

    orb_y = top - 12
    return YEAR.substitute(
        t, W=W, H=H, Wm=W - 1, Hm=H - 1, PAD=PAD, right=W - PAD, sans=SANS, cycle=f"{CYCLE:g}",
        alt="A spark crosses the last year of contributions, lighting every active day; the busiest days burst.",
        x0=f"{PAD:.1f}", x1=f"{PAD + 53 * pitch:.1f}",
        sweep_pct=f"{SWEEP / CYCLE * 100:.2f}", sweep_end=f"{SWEEP / CYCLE * 100 + 2:.2f}",
        col_keyframes="\n".join(keyframes), legend="".join(legend), cells="\n".join(cells),
        months="".join(months), bursts="".join(bursts), stats="".join(stats),
        orb_y=orb_y, trail_y=orb_y - 1, core_h=f"{grid_h + 14:.0f}", glow_y=top - 4, glow_h=f"{grid_h + 4:.0f}",
        rule_y=H - 92,
    )


# ---------------------------------------------------------------- hero ----
HERO = Template("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $W $H" width="$W" height="$H" role="img" aria-label="$alt">
<defs>
<linearGradient id="bg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="$H"><stop offset="0" stop-color="$bg0"/><stop offset="1" stop-color="$bg1"/></linearGradient>
<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="$PAD" y1="0" x2="470" y2="0"><stop offset="0" stop-color="$text"/><stop offset=".55" stop-color="$text"/><stop offset="1" stop-color="$accent"/></linearGradient>
<linearGradient id="line" gradientUnits="userSpaceOnUse" x1="$PAD" y1="0" x2="$right" y2="0"><stop offset="0" stop-color="$accent"/><stop offset="1" stop-color="$hot"/></linearGradient>
<filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3.5"/></filter>
</defs>
<style>
text{font-family:$sans}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.24em;fill:$accent}
.name{font-size:58px;font-weight:800;letter-spacing:-.02em;fill:url(#name);animation:rise 1s cubic-bezier(.2,.8,.2,1) both}
.mono{font-family:$mono;font-size:16px}
.star{fill:$star;animation:twinkle 5s ease-in-out infinite}
.line{transform-box:fill-box;transform-origin:left center;animation:draw ${cycle}s cubic-bezier(.6,0,.3,1) infinite}
.orb{animation:orb ${cycle}s cubic-bezier(.6,0,.3,1) infinite}
.ring{fill:none;transform-origin:${ex}px ${ey}px;animation:spin linear infinite}
.pulse{transform-origin:${ex}px ${ey}px;animation:pulse 3s ease-in-out infinite}
.tag{opacity:0;animation-duration:${cycle}s;animation-iteration-count:infinite;animation-fill-mode:backwards}
.curtain{animation-duration:${cycle}s;animation-iteration-count:infinite;animation-fill-mode:backwards}
.caret{fill:$accent;animation:blink .9s steps(1) infinite}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:.9}}
@keyframes draw{0%{transform:scaleX(0);opacity:1}16%,92%{transform:scaleX(1);opacity:1}98%,100%{transform:scaleX(1);opacity:0}}
@keyframes orb{0%{transform:translateX(0);opacity:1}16%{transform:translateX(${line_w}px);opacity:1}19%,100%{transform:translateX(${line_w}px);opacity:0}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.5}50%{transform:scale(1.25);opacity:.15}}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
@keyframes show{0%{opacity:0}.4%,32.6%{opacity:1}33.3%,100%{opacity:0}}
$tag_keyframes
@media (prefers-reduced-motion:reduce){*{animation:none!important}.orb,.curtain,.t1,.t2{display:none}.t0{opacity:1}}
</style>
<rect x=".5" y=".5" width="${Wm}" height="${Hm}" rx="16" fill="url(#bg)" stroke="$border"/>
$stars
<text class="eyebrow" x="$PAD" y="66">HELLO, I'M</text>
<text class="name" x="$PAD" y="128">$name</text>
<rect class="line" x="$PAD" y="151" width="$line_w" height="2" rx="1" fill="url(#line)"/>
<g class="orb"><circle cx="$PAD" cy="152" r="9" fill="$hot" filter="url(#soft)"/><circle cx="$PAD" cy="152" r="3.4" fill="$beam"/></g>
<text class="mono" x="$PAD" y="194" fill="$accent">&gt;</text>
$tags
<g>
<circle class="pulse" cx="$ex" cy="$ey" r="30" fill="$accent"/>
<circle class="ring" style="animation-duration:22s" cx="$ex" cy="$ey" r="68" stroke="$border" stroke-width="1.5" stroke-dasharray="2 9"/>
<circle class="ring" style="animation-duration:14s;animation-direction:reverse" cx="$ex" cy="$ey" r="54" stroke="$accent" stroke-width="2" stroke-linecap="round" stroke-dasharray="70 30 8 30 120 82"/>
<circle class="ring" style="animation-duration:8s" cx="$ex" cy="$ey" r="41" stroke="$hot" stroke-width="2" stroke-linecap="round" stroke-dasharray="36 222"/>
<circle cx="$ex" cy="$ey" r="30" fill="$bg0" stroke="$border"/>
<text class="mono" x="$ex" y="${ey_text}" text-anchor="middle" font-weight="700" style="font-size:19px" fill="$text">$initials</text>
</g>
</svg>
""")


def hero_svg(t):
    H, cycle = 236, 13.5
    tag_x, char_w = PAD + 22, 9.6
    rng = random.Random(7)  # fixed seed: the same sky every run
    stars = "".join(
        f'<circle class="star" style="animation-delay:-{rng.uniform(0, 5):.1f}s" cx="{rng.uniform(20, W - 20):.0f}" '
        f'cy="{rng.uniform(16, H - 16):.0f}" r="{rng.choice([0.7, 0.9, 1.2]):g}"/>'
        for _ in range(46)
    )
    tags, keyframes = [], []
    for i, line in enumerate(TAGLINES):
        n, width = len(line), len(line) * char_w
        delay = i * cycle / 3
        # the curtain uncovers the line one character at a time, holds, then covers it again
        keyframes.append(
            f"@keyframes type{i}{{0%{{transform:translateX(0);animation-timing-function:steps({n})}}"
            f"11%,26%{{transform:translateX({width:.1f}px);animation-timing-function:steps({n})}}"
            f"31%,100%{{transform:translateX(0)}}}}"
        )
        tags.append(
            f'<g class="tag t{i}" style="animation-name:show;animation-delay:{delay:.2f}s">'
            f'<text class="mono" x="{tag_x}" y="194" textLength="{width:.1f}" lengthAdjust="spacing" fill="{t["text"]}">{line}</text>'
            f'<g class="curtain" style="animation-name:type{i};animation-delay:{delay:.2f}s">'
            f'<rect x="{tag_x}" y="176" width="{width + 14:.1f}" height="28" fill="url(#bg)"/>'
            f'<rect class="caret" x="{tag_x + 2}" y="180" width="8" height="18" rx="1"/></g></g>'
        )
    ex, ey = W - PAD - 82, H / 2
    return HERO.substitute(
        t, W=W, H=H, Wm=W - 1, Hm=H - 1, PAD=PAD, right=W - PAD, sans=SANS, mono=MONO, cycle=f"{cycle:g}",
        alt=f"{NAME}: {'; '.join(TAGLINES)}.", name=NAME, initials=INITIALS, stars=stars,
        line_w=W - 2 * PAD - 190, ex=f"{ex:g}", ey=f"{ey:g}", ey_text=f"{ey + 6.5:g}",
        tags="\n".join(tags), tag_keyframes="\n".join(keyframes),
    )


def main():
    if len(sys.argv) > 1:
        html = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        url = f"https://github.com/users/{USER}/contributions"
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-generator"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    days = load_days(html)
    OUT.mkdir(exist_ok=True)
    for theme, palette in THEMES.items():
        (OUT / f"hero-{theme}.svg").write_text(hero_svg(palette), encoding="utf-8", newline="\n")
        (OUT / f"year-{theme}.svg").write_text(year_svg(days, palette), encoding="utf-8", newline="\n")
    print(f"{len(days)} days, {sum(c for _, c, _ in days)} contributions -> {OUT}")


if __name__ == "__main__":
    main()
