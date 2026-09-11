# -*- coding: utf-8 -*-
"""Weaves a year of GitHub contributions into a Turkmen carpet.

53 weeks x 7 days is already a knot grid. Density and dye come from the real
commit counts; the palette follows the traditional madder / cochineal /
saffron / undyed-wool progression. Regenerated daily by the weave workflow.
"""
import json
import sys
import datetime
import typeset as T

FONTS = 'fonts/'
MONO = T.load(FONTS + 'IBMPlexMono-Medium.ttf')

# --- traditional dyes -----------------------------------------------------
GROUND = '#5C1F1B'   # madder ground, the classic Tekke field
WARP = '#4A1815'     # the weave showing through on unworked days
L1 = '#8C4336'       # thin madder
L2 = '#C04A30'       # full madder
L3 = '#D79A4E'       # saffron
L4 = '#EFE4D0'       # undyed wool, the brightest knot
INDIGO = '#23303F'   # border ground
IVORY = '#EFE4D0'
MUTED = '#8C8175'
FAINT = '#6E6459'

CELL = 17
ROWS = 7
GUARD = 5
BAND = 22
MARGIN_X = 36
CAPTION_H = 46


def load(path):
    d = json.load(open(path, encoding='utf-8'))['data']['user']
    c = d['contributionsCollection']
    return c, c['contributionCalendar']['weeks']


def thresholds(weeks):
    """Four dye levels taken from the real distribution, not arbitrary cut-offs."""
    vals = sorted(x['contributionCount'] for w in weeks
                  for x in w['contributionDays'] if x['contributionCount'] > 0)
    if not vals:
        return 1, 2, 3
    def q(p):
        return vals[min(len(vals) - 1, int(len(vals) * p))]
    return q(0.25), q(0.55), q(0.82)


def knot(cx, cy, lvl):
    """A stepped Turkmen knot, gaining size and structure as the day gets busier."""
    r = (0.0, 0.21, 0.30, 0.38, 0.46)[lvl] * CELL
    fill = (None, L1, L2, L3, L4)[lvl]
    out = ['<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
           % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy, fill)]
    if lvl >= 3:                       # hooks appear on the heavier knots
        h = r * 0.42
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            x, y = cx + dx * r * 0.52, cy + dy * r * 0.52
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%s"/>'
                       % (x - h / 2, y - h / 2, h, h, fill, '.85' if lvl == 4 else '.6'))
    if lvl == 4:                       # an eye of ground colour, as in a real gul
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * 0.22, GROUND))
    return ''.join(out)


def border_run(x0, y0, length, horizontal, unit=2 * CELL):
    """Running hook-and-diamond band, the way a Turkmen border actually repeats."""
    out = []
    n = int(length // unit)
    pad = (length - n * unit) / 2
    for i in range(n):
        if horizontal:
            cx = x0 + pad + i * unit + unit / 2
            cy = y0 + BAND / 2
        else:
            cx = x0 + BAND / 2
            cy = y0 + pad + i * unit + unit / 2
        r = BAND * 0.34
        col = IVORY if i % 2 == 0 else L3
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                   % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy, col))
        h = r * 0.5
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".45"/>'
                   % (cx - unit / 2 + h * 0.4, cy - h / 2, h, h, IVORY))
    return ''.join(out)


def build(contrib_path):
    c, weeks = load(contrib_path)
    cal = c['contributionCalendar']
    weeks = weeks[-53:]
    t1, t2, t3 = thresholds(weeks)

    field_w = len(weeks) * CELL
    field_h = ROWS * CELL
    inset = GUARD + BAND + GUARD
    panel_w = field_w + 2 * inset
    panel_h = field_h + 2 * inset
    W = panel_w + 2 * MARGIN_X
    H = panel_h + CAPTION_H
    px, py = MARGIN_X, 10
    fx, fy = px + inset, py + inset

    def lvl(n):
        if n == 0:
            return 0
        return 1 if n <= t1 else 2 if n <= t2 else 3 if n <= t3 else 4

    knots, warp = [], []
    for ci, wk in enumerate(weeks):
        x = fx + ci * CELL
        warp.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>' % (x, fy, x, fy + field_h))
        for ri, day in enumerate(wk['contributionDays']):
            level = lvl(day['contributionCount'])
            if level:
                knots.append(knot(x + CELL / 2, fy + ri * CELL + CELL / 2, level))

    total = cal['totalContributions']
    repos = c['totalRepositoriesWithContributedCommits']
    first = weeks[0]['contributionDays'][0]['date']
    last = weeks[-1]['contributionDays'][-1]['date']

    def fmt(s):
        return datetime.date.fromisoformat(s).strftime('%b %Y').upper()

    cap_y = py + panel_h + 28
    cap = '%s CONTRIBUTIONS   ·   %d REPOSITORIES   ·   %s — %s' % (
        format(total, ','), repos, fmt(first), fmt(last))
    cap_d, _ = T.typeset(MONO, cap, 11, px, cap_y, tracking=0.13)

    # dye legend, flush with the right edge of the rug
    busy_w = T.width(MONO, 'BUSY', 9.5, 0.13)
    quiet_w = T.width(MONO, 'QUIET', 9.5, 0.13)
    busy_d, _ = T.typeset(MONO, 'BUSY', 9.5, px + panel_w - busy_w, cap_y - 0.5, tracking=0.13)
    leg = []
    lx = px + panel_w - busy_w - 14
    for col in (L4, L3, L2, L1):
        leg.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                   % (lx, cap_y - 8.5, lx + 5, cap_y - 4, lx, cap_y + 0.5, lx - 5, cap_y - 4, col))
        lx -= 15
    quiet_d, _ = T.typeset(MONO, 'QUIET', 9.5, lx + 15 - 5 - 9 - quiet_w, cap_y - 0.5, tracking=0.13)

    label = ('%s GitHub contributions over the past year, woven as a Turkmen carpet. '
             'Each knot is one day.' % format(total, ','))

    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
  <style>
    /* The rug is fully woven by default. The animation only replays the
       weaving on load, so a renderer that ignores it still shows the rug. */
    #loom {{ transform-origin: 0 0; animation: weave 2.2s cubic-bezier(.22,.61,.36,1) 1 forwards; }}
    #shuttle {{ opacity: 0; animation: pass 2.2s cubic-bezier(.22,.61,.36,1) 1 forwards; }}
    @keyframes weave {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    @keyframes pass {{
      from {{ transform: translateX(0); opacity: .9; }}
      90% {{ opacity: .9; }}
      to {{ transform: translateX({W}px); opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      #loom, #shuttle {{ animation: none; }}
      #shuttle {{ display: none; }}
    }}
  </style>
  <defs>
    <mask id="loomMask"><rect id="loom" x="0" y="0" width="{W}" height="{H}" fill="#fff"/></mask>
  </defs>

  <g mask="url(#loomMask)">
    <rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" fill="{INDIGO}"/>
    {borders}

    <rect x="{fx}" y="{fy}" width="{field_w}" height="{field_h}" fill="{GROUND}"/>
    <g stroke="{WARP}" stroke-width="1">{warp}</g>
    {knots}

    <path d="{cap_d}" fill="{MUTED}"/>
    <path d="{quiet_d}" fill="{FAINT}"/>
    <path d="{busy_d}" fill="{FAINT}"/>
    {leg}
  </g>
  <rect id="shuttle" x="-2" y="{py}" width="2" height="{panel_h}" fill="{IVORY}"/>
</svg>
'''.format(
        W=W, H=H, label=label, px=px, py=py, panel_w=panel_w, panel_h=panel_h,
        fx=fx, fy=fy, field_w=field_w, field_h=field_h,
        INDIGO=INDIGO, GROUND=GROUND, WARP=WARP, IVORY=IVORY, MUTED=MUTED, FAINT=FAINT,
        borders=(border_run(px + GUARD, py + GUARD, panel_w - 2 * GUARD, True)
                 + border_run(px + GUARD, py + panel_h - GUARD - BAND, panel_w - 2 * GUARD, True)
                 + border_run(px + GUARD, py + GUARD + BAND, panel_h - 2 * GUARD - 2 * BAND, False)
                 + border_run(px + panel_w - GUARD - BAND, py + GUARD + BAND,
                              panel_h - 2 * GUARD - 2 * BAND, False)),
        warp=''.join(warp), knots=''.join(knots),
        cap_d=cap_d, quiet_d=quiet_d, busy_d=busy_d, leg=''.join(leg))


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'contrib.json'
    out = sys.argv[2] if len(sys.argv) > 2 else 'out/carpet.svg'
    open(out, 'w', encoding='utf-8').write(build(src))
    print('woven ->', out)
