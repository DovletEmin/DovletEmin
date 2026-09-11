# -*- coding: utf-8 -*-
"""Weaves a year of GitHub contributions into a Turkmen carpet.

53 weeks x 7 days is already a knot grid. Everything is drawn on a real knot
lattice, so motifs step the way a weave forces them to and never run on a
smooth diagonal. The ground carries abrash, the banding left by different dye
lots, and the pile texture sits over the whole field. Dyes follow the
traditional madder / cochineal / saffron / undyed-wool progression.

Rebuilt daily by .github/workflows/weave.yml. Every variation is seeded from
the knot coordinates, so identical data always produces an identical rug and
the workflow never churns commits.
"""
import json
import sys
import datetime
import colorsys
import typeset as T

FONTS = 'fonts/'
MONO = T.load(FONTS + 'IBMPlexMono-Medium.ttf')

# --- traditional dyes -----------------------------------------------------
GROUND = '#5E211C'   # madder ground, the classic Tekke field
L1 = '#8E4636'       # thin madder
L2 = '#C24C31'       # full madder
L3 = '#D79A4E'       # saffron
L4 = '#EFE4D0'       # undyed wool, the brightest knot
INDIGO = '#22303E'   # border ground
IVORY = '#EFE4D0'
CORD = '#1A242F'     # selvedge cord
MUTED = '#8C8175'
FAINT = '#6E6459'

KW, KH = 2.45, 2.40      # one knot
CK = 7                   # knots per day cell, each way
CELL_W, CELL_H = KW * CK, KH * CK
ROWS = 7
GUARD, BAND = 4, 20
FRINGE = 24
MARGIN = 8
CAPTION_H = 44


# --- small helpers --------------------------------------------------------
def shift(hex_colour, dl=0.0, dh=0.0):
    """Nudge a colour in HLS. Real wool is never one flat value."""
    h = hex_colour.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb((hh + dh) % 1.0, min(1.0, max(0.0, ll + dl)), ss)
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def noise(*key):
    """Deterministic value in [-1, 1] from integer coordinates."""
    n = 2166136261
    for k in key:
        n = ((n ^ (int(k) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return (n % 2000) / 1000.0 - 1.0


def load(path):
    d = json.load(open(path, encoding='utf-8'))['data']['user']
    c = d['contributionsCollection']
    return c, c['contributionCalendar']['weeks']


def thresholds(weeks):
    """Dye levels taken from the real distribution, not arbitrary cut-offs."""
    vals = sorted(x['contributionCount'] for w in weeks
                  for x in w['contributionDays'] if x['contributionCount'] > 0)
    if not vals:
        return 1, 2, 3

    def q(p):
        return vals[min(len(vals) - 1, int(len(vals) * p))]
    return q(0.25), q(0.55), q(0.82)


# --- the weave ------------------------------------------------------------
def stepped_diamond(cx, cy, n, fill):
    """A diamond as a weave actually makes it: a staircase of knot runs."""
    out = []
    for i in range(-n, n + 1):
        half = n - abs(i)
        w = (2 * half + 1) * KW
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (cx - w / 2, cy + i * KH - KH / 2, w, KH, fill))
    return out


def motif(cx, cy, lvl, wk, dy):
    """One day. Size, dye and a little wool variation all come from the data."""
    n = (0, 1, 2, 3, 3)[lvl]
    base = (None, L1, L2, L3, L4)[lvl]
    fill = shift(base, dl=0.035 * noise(wk, dy, 7), dh=0.004 * noise(wk, dy, 11))
    cx += 0.45 * noise(wk, dy, 3)      # a hand does not land every knot on a line
    cy += 0.40 * noise(wk, dy, 5)
    out = stepped_diamond(cx, cy, n, fill)
    if lvl >= 3:                       # hooks step out of the heavier motifs
        for dxk, dyk in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                       % (cx + dxk * KW - KW / 2, cy + dyk * KH - KH / 2, KW, KH, fill))
    if lvl == 4:                       # an eye of ground colour, as in a real gul
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (cx - KW / 2, cy - KH / 2, KW, KH, shift(GROUND, dl=0.02)))
    return ''.join(out)


def border_run(x0, y0, length, horizontal, unit=CELL_W):
    """Running hook-and-diamond band, stepped like the field."""
    out = []
    n = max(1, int(length // unit))
    pad = (length - n * unit) / 2
    for i in range(n):
        if horizontal:
            cx, cy = x0 + pad + i * unit + unit / 2, y0 + BAND / 2
        else:
            cx, cy = x0 + BAND / 2, y0 + pad + i * unit + unit / 2
        col = shift(IVORY if i % 2 == 0 else L3, dl=0.03 * noise(i, int(horizontal), 13))
        out += stepped_diamond(cx, cy, 3, col)
    return ''.join(out)


def fringe(x, y, height, direction):
    """Warp threads left loose at the short ends of the rug."""
    out = ['<rect x="%.1f" y="%.1f" width="4" height="%.1f" fill="%s"/>'
           % (x if direction > 0 else x - 4, y, height, shift(IVORY, dl=-0.10))]
    step = KH
    for i in range(int(height // step)):
        yy = y + i * step + step / 2
        ln = FRINGE * (0.52 + 0.45 * abs(noise(i, 17)))
        x2 = x + direction * ln
        sag = 1.5 * noise(i, 19)
        out.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" stroke="%s" '
                   'stroke-width=".9" fill="none" opacity="%.1f"/>'
                   % (x, yy, (x + x2) / 2, yy + sag, x2, yy + sag * 1.7,
                      shift(IVORY, dl=-0.05 + 0.05 * noise(i, 23)),
                      0.5 + 0.4 * abs(noise(i, 29))))
    return ''.join(out)


def selvedge(x, y, length):
    """The wrapped cord along the long sides."""
    out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="3.6" fill="%s"/>' % (x, y, length, CORD)]
    step = 5.0
    for i in range(int(length // step)):
        xx = x + i * step
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f" stroke="%s" stroke-width="1" opacity=".5"/>'
                   % (xx, y + 3.6, xx + 2.6, y, shift(CORD, dl=0.16)))
    return ''.join(out)


def build(contrib_path):
    c, weeks = load(contrib_path)
    cal = c['contributionCalendar']
    weeks = weeks[-53:]
    t1, t2, t3 = thresholds(weeks)

    field_w, field_h = len(weeks) * CELL_W, ROWS * CELL_H
    inset = GUARD + BAND + GUARD
    panel_w, panel_h = field_w + 2 * inset, field_h + 2 * inset
    px, py = MARGIN + FRINGE, 10
    W, H = panel_w + 2 * (MARGIN + FRINGE), panel_h + CAPTION_H
    fx, fy = px + inset, py + inset

    def lvl(n):
        if n == 0:
            return 0
        return 1 if n <= t1 else 2 if n <= t2 else 3 if n <= t3 else 4

    knots = []
    for ci, wk in enumerate(weeks):
        for ri, day in enumerate(wk['contributionDays']):
            level = lvl(day['contributionCount'])
            if level:
                knots.append(motif(fx + ci * CELL_W + CELL_W / 2,
                                   fy + ri * CELL_H + CELL_H / 2, level, ci, ri))

    # abrash: horizontal banding from different dye lots
    stops = ''.join('<stop offset="%.3f" stop-color="%s"/>'
                    % (i / 8.0, shift(GROUND, dl=0.030 * noise(i, 31))) for i in range(9))

    total = cal['totalContributions']
    repos = c['totalRepositoriesWithContributedCommits']
    first = weeks[0]['contributionDays'][0]['date']
    last = weeks[-1]['contributionDays'][-1]['date']

    def fmt(s):
        return datetime.date.fromisoformat(s).strftime('%b %Y').upper()

    cap_y = py + panel_h + 27
    cap = '%s CONTRIBUTIONS   ·   %d REPOSITORIES   ·   %s — %s' % (
        format(total, ','), repos, fmt(first), fmt(last))
    cap_d, _ = T.typeset(MONO, cap, 11, px, cap_y, tracking=0.13)

    busy_w = T.width(MONO, 'BUSY', 9.5, 0.13)
    quiet_w = T.width(MONO, 'QUIET', 9.5, 0.13)
    busy_d, _ = T.typeset(MONO, 'BUSY', 9.5, px + panel_w - busy_w, cap_y - 0.5, tracking=0.13)
    leg, lx = [], px + panel_w - busy_w - 15
    for col in (L4, L3, L2, L1):
        leg += stepped_diamond(lx, cap_y - 4, 2, col)
        lx -= 16
    quiet_d, _ = T.typeset(MONO, 'QUIET', 9.5, lx + 16 - 9 - quiet_w, cap_y - 0.5, tracking=0.13)

    label = ('%s GitHub contributions over the past year, woven as a Turkmen carpet. '
             'Each knot is one day.' % format(total, ','))

    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="{label}">
  <style>
    /* The rug is fully woven by default. The animation only replays the
       weaving on load, so a renderer that ignores it still shows the rug. */
    #loom {{ transform-origin: 0 0; animation: weave 2.4s cubic-bezier(.25,.6,.35,1) 1 forwards; }}
    #shuttle {{ opacity: 0; animation: pass 2.4s cubic-bezier(.25,.6,.35,1) 1 forwards; }}
    @keyframes weave {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    @keyframes pass {{
      from {{ transform: translateX(0); opacity: .85; }}
      90% {{ opacity: .85; }}
      to {{ transform: translateX({W:.0f}px); opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      #loom, #shuttle {{ animation: none; }}
      #shuttle {{ display: none; }}
    }}
  </style>
  <defs>
    <mask id="loomMask"><rect id="loom" x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/></mask>
    <linearGradient id="abrash" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>
    <pattern id="pile" width="{KW:.2f}" height="{KH:.2f}" patternUnits="userSpaceOnUse">
      <line x1="0" y1="{KH:.2f}" x2="{KW:.2f}" y2="{KH:.2f}" stroke="#000" stroke-opacity=".20" stroke-width=".55"/>
      <line x1="{KW:.2f}" y1="0" x2="{KW:.2f}" y2="{KH:.2f}" stroke="#000" stroke-opacity=".09" stroke-width=".45"/>
      <line x1="0" y1=".3" x2="{KW:.2f}" y2=".3" stroke="#fff" stroke-opacity=".05" stroke-width=".40"/>
    </pattern>
  </defs>

  <g mask="url(#loomMask)">
    {fringe_l}{fringe_r}
    <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="{panel_h:.1f}" fill="{INDIGO}"/>
    {borders}
    <rect x="{fx:.1f}" y="{fy:.1f}" width="{field_w:.1f}" height="{field_h:.1f}" fill="url(#abrash)"/>
    {knots}
    <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="{panel_h:.1f}" fill="url(#pile)"/>
    {selv_t}{selv_b}

    <path d="{cap_d}" fill="{MUTED}"/>
    <path d="{quiet_d}" fill="{FAINT}"/>
    <path d="{busy_d}" fill="{FAINT}"/>
    {leg}
  </g>
  <rect id="shuttle" x="-2" y="{py:.1f}" width="2" height="{panel_h:.1f}" fill="{IVORY}"/>
</svg>
'''.format(
        W=W, H=H, label=label, px=px, py=py, panel_w=panel_w, panel_h=panel_h,
        fx=fx, fy=fy, field_w=field_w, field_h=field_h, KW=KW, KH=KH,
        INDIGO=INDIGO, IVORY=IVORY, MUTED=MUTED, FAINT=FAINT, stops=stops,
        borders=(border_run(px + GUARD, py + GUARD, panel_w - 2 * GUARD, True)
                 + border_run(px + GUARD, py + panel_h - GUARD - BAND, panel_w - 2 * GUARD, True)
                 + border_run(px + GUARD, py + GUARD + BAND, panel_h - 2 * GUARD - 2 * BAND, False)
                 + border_run(px + panel_w - GUARD - BAND, py + GUARD + BAND,
                              panel_h - 2 * GUARD - 2 * BAND, False)),
        fringe_l=fringe(px, py, panel_h, -1),
        fringe_r=fringe(px + panel_w, py, panel_h, 1),
        selv_t=selvedge(px, py - 3.2, panel_w),
        selv_b=selvedge(px, py + panel_h, panel_w),
        knots=''.join(knots), cap_d=cap_d, quiet_d=quiet_d, busy_d=busy_d, leg=''.join(leg))


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'contrib.json'
    out = sys.argv[2] if len(sys.argv) > 2 else 'out/carpet.svg'
    open(out, 'w', encoding='utf-8').write(build(src))
    print('woven ->', out)
