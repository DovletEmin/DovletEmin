# -*- coding: utf-8 -*-
"""Weaves a year of GitHub contributions into a Tekke Turkmen carpet.

The rug is built the way a real one is. Everything sits on a knot lattice, so
every motif steps the way a loom forces it to. From the centre out:

  field        one gul per day, linked by the dark lattice Tekke rugs are known
               for. The busier the day, the larger and paler the gul.
  guards       three minor stripes: pearls, a reciprocal barber-pole, pearls
               on dark.
  main border  octagons alternating with stars, spaced the way a weaver counts
               them, so the corners do not quite resolve. Real ones rarely do.
  elem         the skirt panels at both ends, a column of hooked diamonds.
  kilim        a band of flat weave where the knotting stops.
  fringe       the loose warp, knotted in bundles.
  selvedge     the wrapped cord along the long sides.

Realism comes from the filters, not from extra geometry. Wool pile is a noise
height field lit from one side; knot edges are displaced so colours bleed into
each other like yarn; abrash runs across the warp in bands, because that is
how a new dye lot shows up as the weaver works along the rug; and the whole
piece is bowed very slightly, since no hand-knotted rug is truly square.

Every variation is seeded from coordinates, so identical data always produces
a byte-identical file and the daily workflow never commits noise.
"""
import os
import re
import json
import sys
import datetime
import colorsys
import typeset as T

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
MONO = T.load(os.path.join(FONTS, 'IBMPlexMono-Medium.ttf'))

K = 2                       # one knot, in px

# --- natural dyes ---------------------------------------------------------
RED = '#7B2521'             # madder, the Tekke field
RED_DK = '#4B1918'          # madder over a brown base, border ground
LATTICE = '#4F181B'         # the dark lines that link the guls
INDIGO = '#1C2231'
IVORY = '#E3D5B8'           # undyed wool
SAFFRON = '#C58C3D'
ORANGE = '#B4432B'
RUST = '#93392B'
CORD = '#2A1716'            # selvedge wrap
WARP = '#E4DAC6'            # undyed warp, seen in the fringe
CAPTION = '#8C8175'
FAINT = '#6E6459'

# --- layout, in knots -----------------------------------------------------
CELL = 9                    # one day
ROWS = 7
WEEKS = 53
GUARD = 3
BORDER = 13
ELEM = 14
KILIM = 5

FIELD_W, FIELD_H = WEEKS * CELL, ROWS * CELL
FX = GUARD + ELEM + GUARD + BORDER + GUARD          # field origin
FY = GUARD + GUARD + BORDER + GUARD
PILE_W = FX * 2 + FIELD_W
PILE_H = FY * 2 + FIELD_H

FRINGE = 26                 # px
MARGIN = 14                 # px, room for the shadow
CAPTION_H = 40              # px


# --- small helpers --------------------------------------------------------
def shift(hex_colour, dl=0.0, ds=0.0):
    """Nudge a colour in HLS. Real wool is never one flat value."""
    h = hex_colour.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hh, min(1.0, max(0.0, ll + dl)), min(1.0, max(0.0, ss + ds)))
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))


def noise(*key):
    """Deterministic value in [-1, 1] from integer coordinates."""
    n = 2166136261
    for k in key:
        n = ((n ^ (int(k) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 0x5bd1e995) & 0xFFFFFFFF
    n ^= n >> 15
    return (n % 20001) / 10000.0 - 1.0


def paths(knots, ox=0, oy=0):
    """{(x, y): colour} in knots -> one <path> per colour, one rect per run."""
    rows, by = {}, {}
    for (x, y), c in knots.items():
        rows.setdefault(y, []).append((x, c))
    for y in sorted(rows):
        row = sorted(rows[y])
        i = 0
        while i < len(row):
            x0, c = row[i]
            j = i
            while j + 1 < len(row) and row[j + 1][0] == row[j][0] + 1 and row[j + 1][1] == c:
                j += 1
            n = (j - i + 1) * K
            by.setdefault(c, []).append('M%d %dh%dv%dh-%dz' % (ox + x0 * K, oy + y * K, n, K, n))
            i = j + 1
    return ''.join('<path fill="%s" d="%s"/>' % (c, ''.join(d)) for c, d in sorted(by.items()))


def rect(x, y, w, h, fill, extra=''):
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"%s/>' % (x, y, w, h, fill, extra)


# --- motifs ---------------------------------------------------------------
def octagon(r, trim=0):
    lim = r + r // 2 - trim
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1)
            if abs(x) + abs(y) <= lim}


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) <= r}


def gul(r, a, b, eye, line=INDIGO, dot=None, hooks=None):
    """A quartered octagon: opposite quarters share a dye, as on a Tekke gul."""
    full = octagon(r)
    inner = {p for p in octagon(r, 1) if abs(p[0]) < r and abs(p[1]) < r}
    k = {}
    for p in full:
        x, y = p
        if p not in inner:
            k[p] = line
        elif x == 0 or y == 0:
            k[p] = line
        else:
            k[p] = a if x * y > 0 else b
    if dot and r >= 4:
        for sx in (-1, 1):
            for sy in (-1, 1):
                k[(2 * sx, 2 * sy)] = dot
    k[(0, 0)] = eye
    if hooks:
        for sx in (-1, 1):
            for sy in (-1, 1):
                k[(r * sx, r * sy)] = hooks
    return k


def small(r, fill, line, eye):
    k = {p: (line if abs(p[0]) + abs(p[1]) == r else fill) for p in diamond(r)}
    k[(0, 0)] = eye
    return k


def ashik(c):
    """Hooked diamond of the elem panels."""
    k = {p: c for p in diamond(4) if abs(p[0]) + abs(p[1]) == 4}
    k.update({p: INDIGO for p in diamond(1)})
    k[(0, 0)] = c
    for sx, sy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        k[(2 * sx, 2 * sy)] = c          # hooks turning inward
    return k


# Day guls, quiet to busy. Each has two colourings, alternated across the
# field the way neighbouring guls swap dyes on a real rug.
DAY = {
    1: (small(1, RUST, RUST, INDIGO), small(1, RUST, RUST, INDIGO)),
    2: (small(2, ORANGE, INDIGO, SAFFRON), small(2, ORANGE, INDIGO, IVORY)),
    3: (gul(3, SAFFRON, ORANGE, IVORY), gul(3, ORANGE, SAFFRON, IVORY)),
    4: (gul(4, IVORY, SAFFRON, ORANGE, dot=ORANGE, hooks=SAFFRON),
        gul(4, SAFFRON, IVORY, ORANGE, dot=INDIGO, hooks=IVORY)),
}
BORDER_OCT = (gul(4, IVORY, ORANGE, INDIGO, dot=INDIGO), gul(4, ORANGE, IVORY, INDIGO, dot=IVORY))
BORDER_STAR = small(2, SAFFRON, INDIGO, RED_DK)
ELEM_MOTIF = (ashik(IVORY), ashik(SAFFRON))


def symbol(sid, knots):
    """Motif centred on the top-left corner of its middle knot."""
    return '<g id="%s">%s</g>' % (sid, paths(knots))


def use(sid, kx, ky, extra=''):
    return '<use href="#%s" x="%d" y="%d"%s/>' % (sid, kx * K, ky * K, extra)


# --- stripes and frames ---------------------------------------------------
def frame(x0, y0, w, h, t, colour):
    """Knots of a rectangular band t knots thick. colour(along, across)."""
    k = {}
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            d = min(x - x0, y - y0, x0 + w - 1 - x, y0 + h - 1 - y)
            if d >= t:
                continue
            horizontal = min(y - y0, y0 + h - 1 - y) <= min(x - x0, x0 + w - 1 - x)
            k[(x, y)] = colour(x if horizontal else y, d)
    return k


def pearls(on, pearl_cols):
    def c(along, across):
        if across != 1:
            return on
        return pearl_cols[along % len(pearl_cols)]
    return c


def barber(along, across):
    return (INDIGO, IVORY, ORANGE)[((along + across) // 2) % 3]


def spaced(a, b, period):
    """Evenly spaced knot positions from a to b, an even count of steps."""
    n = max(2, round((b - a) / period))
    n += n % 2
    return [round(a + i * (b - a) / n) for i in range(n + 1)]


# --- data -----------------------------------------------------------------
def parse(data):
    c = data['data']['user']['contributionsCollection']
    return c, c['contributionCalendar']['weeks'][-WEEKS:]


def thresholds(weeks):
    """Dye levels taken from the real distribution, not arbitrary cut-offs."""
    vals = sorted(x['contributionCount'] for w in weeks
                  for x in w['contributionDays'] if x['contributionCount'] > 0)
    if not vals:
        return 1, 2, 3

    def q(p):
        return vals[min(len(vals) - 1, int(len(vals) * p))]
    return q(0.25), q(0.55), q(0.82)


# --- the rug --------------------------------------------------------------
def pile_layers(weeks):
    t1, t2, t3 = thresholds(weeks)

    def level(n):
        if n == 0:
            return 0
        return 1 if n <= t1 else 2 if n <= t2 else 3 if n <= t3 else 4

    out = []
    # ground: guards first, then the red of field and elem with its abrash
    out.append(rect(0, 0, PILE_W * K, PILE_H * K, RED_DK))
    ground = [(GUARD, GUARD, ELEM, PILE_H - 2 * GUARD),
              (PILE_W - GUARD - ELEM, GUARD, ELEM, PILE_H - 2 * GUARD),
              (FX, FY, FIELD_W, FIELD_H)]
    for gx, gy, gw, gh in ground:
        out.append(rect(gx * K, gy * K, gw * K, gh * K, RED))

    # abrash: bands across the warp, wherever a new dye lot was started
    x, i = 0, 0
    while x < PILE_W:
        w = 8 + int(abs(noise(i, 41)) * 46)
        dl = 0.032 * noise(i, 43)
        if abs(noise(i, 47)) > 0.85:          # now and then a lot runs out
            dl += 0.022 * (1 if noise(i, 53) > 0 else -1)
        for gx, gy, gw, gh in ground:
            a, b = max(x, gx), min(x + w, gx + gw)
            if a < b:
                out.append(rect(a * K, gy * K, (b - a) * K, gh * K, shift(RED, dl)))
        x += w
        i += 1

    # the lattice that links the guls
    lat = {}
    for r in range(ROWS):
        y = FY + r * CELL + CELL // 2
        for xx in range(FX, FX + FIELD_W):
            lat[(xx, y)] = LATTICE
    for c in range(WEEKS):
        xx = FX + c * CELL + CELL // 2
        for y in range(FY, FY + FIELD_H):
            lat[(xx, y)] = LATTICE
    out.append(paths(lat))

    # one gul per day
    for ci, wk in enumerate(weeks):
        for day in wk['contributionDays']:
            ri = (datetime.date.fromisoformat(day['date']).weekday() + 1) % 7
            lv = level(day['contributionCount'])
            if lv:
                out.append(use('d%d%s' % (lv, 'ab'[(ci + ri) % 2]),
                               FX + ci * CELL + CELL // 2, FY + ri * CELL + CELL // 2))

    # minor stripes
    out.append(paths(frame(0, 0, PILE_W, PILE_H, GUARD, pearls(RED_DK, (INDIGO, INDIGO, IVORY, INDIGO)))))
    mx, my = GUARD + ELEM, GUARD
    mw, mh = PILE_W - 2 * mx, PILE_H - 2 * my
    out.append(paths(frame(mx, my, mw, mh, GUARD, barber)))
    ix, iy = FX - GUARD, FY - GUARD
    out.append(paths(frame(ix, iy, FIELD_W + 2 * GUARD, FIELD_H + 2 * GUARD, GUARD,
                           pearls(INDIGO, (IVORY, INDIGO, SAFFRON, INDIGO)))))

    # main border: octagons and stars, corners left as the count falls
    bx0, by0 = mx + GUARD + BORDER // 2, my + GUARD + BORDER // 2
    bx1, by1 = PILE_W - 1 - bx0, PILE_H - 1 - by0
    xs, ys = spaced(bx0, bx1, 10), spaced(by0, by1, 10)
    spots = [(x, by0) for x in xs] + [(x, by1) for x in xs]
    spots += [(bx0, y) for y in ys[1:-1]] + [(bx1, y) for y in ys[1:-1]]
    for n, (x, y) in enumerate(spots):
        idx = xs.index(x) if y in (by0, by1) else ys.index(y)
        if idx % 2 == 0:
            out.append(use('bo%s' % 'ab'[(idx // 2) % 2], x, y))
        else:
            out.append(use('bs', x, y))

    # elem: a stem with hooked diamonds strung along it
    for ex in (GUARD + ELEM // 2, PILE_W - 1 - GUARD - ELEM // 2):
        out.append(rect(ex * K, (GUARD + 1) * K, K, (PILE_H - 2 * GUARD - 2) * K, LATTICE))
        for n, y in enumerate(spaced(GUARD + 6, PILE_H - 1 - GUARD - 6, 11)):
            out.append(use('e%s' % 'ab'[n % 2], ex, y))
    return ''.join(out)


def fringe_svg(x, y0, height, direction):
    """Loose warp, gathered into bundles and knotted near the kilim.

    Bundles are uneven, threads are cut to different lengths and some stray
    out of their bundle, as they do on any rug that has been walked on."""
    tones = {}
    knots = []
    y, g = y0 + 1.0, 0
    while y < y0 + height - 4:
        group = 7.0 + 3.0 * abs(noise(g, direction, 1))
        group = min(group, y0 + height - 1.0 - y)
        yc = y + group / 2 + 0.5 * noise(g, direction, 3)
        kx = x + direction * (4.0 + 1.2 * abs(noise(g, direction, 5)))
        length = FRINGE * (0.72 + 0.26 * noise(g, direction, 7))
        bend = 2.6 * noise(g, direction, 9)
        threads = max(4, int(group / 1.4))
        for t in range(threads):
            ys = y + 0.6 + t * (group - 1.2) / (threads - 1)
            spread = (t - (threads - 1) / 2) * (0.8 + 0.5 * abs(noise(g, t, direction)))
            if abs(noise(g, t, direction, 17)) > 0.86:
                spread *= 2.6                       # a stray
            ln = length * (0.78 + 0.22 * noise(g, t, direction, 11))
            ex = x + direction * ln
            ey = yc + spread + bend * (0.6 + 0.4 * noise(g, t, 19))
            d = 'M%.1f %.1fQ%.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1f' % (
                x, ys, (x + kx) / 2, ys, kx, yc + spread * 0.2,
                kx + direction * ln * 0.3, yc + spread * 0.6,
                ex - direction * ln * 0.25, ey - bend * 0.3, ex, ey)
            tone = int((noise(g, t, direction, 13) + 1) * 1.5)
            tones.setdefault(min(tone, 2), []).append(d)
        knots.append('<ellipse cx="%.1f" cy="%.1f" rx="1.1" ry="%.1f"/>'
                     % (kx, yc + 0.2, min(2.2, group * 0.26)))
        y += group + 0.3
        g += 1
    cols = (shift(WARP, -0.12), shift(WARP, -0.05), WARP)
    out = ''.join('<path d="%s" stroke="%s"/>' % (''.join(v), cols[k]) for k, v in sorted(tones.items()))
    return ('<g fill="none" stroke-width="1" stroke-linecap="round">%s</g>'
            '<g fill="%s">%s</g>' % (out, shift(WARP, -0.10), ''.join(knots)))


def build(data, animate=True):
    """data: the GraphQL response for the user's contributionsCollection."""
    c, weeks = parse(data)
    cal = c['contributionCalendar']

    pw, ph = PILE_W * K, PILE_H * K
    kw = KILIM * K
    rx = MARGIN + FRINGE + kw            # pile origin, px
    ry = MARGIN
    W = pw + 2 * rx
    H = ph + 2 * MARGIN + CAPTION_H

    defs = [symbol('d%d%s' % (lv, 'ab'[v]), DAY[lv][v]) for lv in DAY for v in (0, 1)]
    defs += [symbol('bo' + 'ab'[v], BORDER_OCT[v]) for v in (0, 1)]
    defs += [symbol('bs', BORDER_STAR)]
    defs += [symbol('e' + 'ab'[v], ELEM_MOTIF[v]) for v in (0, 1)]

    pile = pile_layers(weeks)

    # kilim ends: flat weave in madder with indigo stripes
    def kilim(x):
        s = [rect(x, ry, kw, ph, shift(RED, -0.02))]
        for off, w, col in ((1, 1, INDIGO), (3, 0.5, IVORY)):
            s.append(rect(x + off * K, ry, w * K, ph, col))
        return ''.join(s)

    total = cal['totalContributions']
    repos = c['totalRepositoriesWithContributedCommits']
    first = weeks[0]['contributionDays'][0]['date']
    last = weeks[-1]['contributionDays'][-1]['date']

    def fmt(s):
        return datetime.date.fromisoformat(s).strftime('%b %Y').upper()

    cap_y = ry + ph + MARGIN + 18
    cap = '%s CONTRIBUTIONS   ·   %d REPOSITORIES   ·   %s — %s' % (
        format(total, ','), repos, fmt(first), fmt(last))
    cap_d, _ = T.typeset(MONO, cap, 11, rx - kw, cap_y, tracking=0.13)

    right = rx + pw + kw
    busy_w = T.width(MONO, 'BUSY', 9.5, 0.13)
    quiet_w = T.width(MONO, 'QUIET', 9.5, 0.13)
    busy_d, _ = T.typeset(MONO, 'BUSY', 9.5, right - busy_w, cap_y - 0.5, tracking=0.13)
    leg, lx = [], right - busy_w - 18
    for lv in (4, 3, 2, 1):
        leg.append('<use href="#d%da" transform="translate(%.1f %.1f) scale(.8)"/>'
                   % (lv, lx - 1, cap_y - 5))
        lx -= 18
    quiet_d, _ = T.typeset(MONO, 'QUIET', 9.5, lx + 18 - 12 - quiet_w, cap_y - 0.5, tracking=0.13)

    label = ('%s GitHub contributions over the past year, woven as a Tekke Turkmen carpet. '
             'Each gul is one day; the busier the day, the larger and paler the gul.'
             % format(total, ','))

    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
  <title>{label}</title>
  <style>
    /* Fully woven by default. The animation only replays the weaving on
       load, so a renderer that ignores it still shows the finished rug. */
    #loom {{ animation: weave 2.6s cubic-bezier(.3,.55,.3,1) both; }}
    #shuttle {{ animation: pass 2.6s cubic-bezier(.3,.55,.3,1) both; }}
    @keyframes weave {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    @keyframes pass {{
      from {{ transform: translateX(0); opacity: .9; }}
      92% {{ opacity: .9; }}
      to {{ transform: translateX({sweep}px); opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      #loom, #shuttle {{ animation: none; }}
      #shuttle {{ display: none; }}
    }}
  </style>
  <defs>
    {defs}
    <mask id="loomMask"><rect id="loom" x="0" y="0" width="{W}" height="{H}" fill="#fff"/></mask>

    <!-- wool pile: yarn bleeds at knot edges, a noise height field is lit
         from the upper left, and each knot gets its own small dome -->
    <filter id="pile" x="-1%" y="-2%" width="102%" height="104%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="fine"/>
      <feDisplacementMap in="SourceGraphic" in2="fine" scale="1.7" xChannelSelector="R" yChannelSelector="B" result="bleed"/>
      <feTurbulence type="fractalNoise" baseFrequency=".62 1.05" numOctaves="3" seed="9" result="hf"/>
      <feDiffuseLighting in="hf" surfaceScale="1.55" diffuseConstant="1.05" lighting-color="#fff" result="lit">
        <feDistantLight azimuth="225" elevation="52"/>
      </feDiffuseLighting>
      <feComposite in="bleed" in2="lit" operator="arithmetic" k1="1.17" result="shaded"/>
      <feTurbulence type="fractalNoise" baseFrequency=".012 .05" numOctaves="2" seed="21" result="wear"/>
      <feColorMatrix in="wear" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -.9 .52" result="wearMask"/>
      <feComposite in="wearMask" in2="shaded" operator="in" result="wearOnPile"/>
      <feBlend in="wearOnPile" in2="shaded" mode="soft-light" result="worn"/>
      <feComposite in="worn" in2="bleed" operator="in"/>
    </filter>

    <filter id="flat" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".08 1.4" numOctaves="2" seed="5" result="rib"/>
      <feDiffuseLighting in="rib" surfaceScale="1.6" diffuseConstant="1" lighting-color="#fff" result="lit">
        <feDistantLight azimuth="225" elevation="55"/>
      </feDiffuseLighting>
      <feComposite in="SourceGraphic" in2="lit" operator="arithmetic" k1="1.18" result="shaded"/>
      <feComposite in="shaded" in2="SourceGraphic" operator="in"/>
    </filter>

    <filter id="fibre" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="2" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="1.1" xChannelSelector="R" yChannelSelector="G"/>
    </filter>

    <!-- how the rug lies: bowed a touch, with a soft shadow on the floor -->
    <filter id="lie" x="-3%" y="-10%" width="106%" height="125%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".0035 .011" numOctaves="1" seed="17" result="bow"/>
      <feDisplacementMap in="SourceGraphic" in2="bow" scale="5" xChannelSelector="R" yChannelSelector="G" result="laid"/>
      <feGaussianBlur in="laid" stdDeviation="3.2" result="blur"/>
      <feOffset in="blur" dx="1.5" dy="3.5" result="drop"/>
      <feColorMatrix in="drop" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .45 0" result="shadow"/>
      <feMerge><feMergeNode in="shadow"/><feMergeNode in="laid"/></feMerge>
    </filter>

    <pattern id="knots" width="{K}" height="{K}" patternUnits="userSpaceOnUse">
      <rect width="{K}" height="{K}" fill="url(#dome)"/>
    </pattern>
    <radialGradient id="dome" cx=".42" cy=".38" r=".75">
      <stop offset="0" stop-color="#fff" stop-opacity=".16"/>
      <stop offset=".5" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".42"/>
    </radialGradient>
    <pattern id="wrap" width="3" height="5" patternUnits="userSpaceOnUse" patternTransform="skewX(-28)">
      <rect width="3" height="5" fill="{CORD}"/>
      <rect width="1" height="5" fill="#000" opacity=".45"/>
      <rect x="1.2" width=".7" height="5" fill="#fff" opacity=".10"/>
    </pattern>
    <linearGradient id="light" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".07"/>
      <stop offset=".5" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".16"/>
    </linearGradient>
  </defs>

  <g mask="url(#loomMask)">
    <g filter="url(#lie)">
      <g filter="url(#fibre)">{fringe_l}{fringe_r}</g>
      <g filter="url(#flat)">{kilim_l}{kilim_r}</g>
      <g transform="translate({rx} {ry})" filter="url(#pile)">
        {pile}
        <rect width="{pw}" height="{ph}" fill="url(#knots)"/>
      </g>
      <rect x="{sx}" y="{st}" width="{sw}" height="4.5" fill="url(#wrap)" filter="url(#flat)"/>
      <rect x="{sx}" y="{sb}" width="{sw}" height="4.5" fill="url(#wrap)" filter="url(#flat)"/>
      <rect x="{sx}" y="{st}" width="{sw}" height="{sh}" fill="url(#light)"/>
    </g>
    <path d="{cap_d}" fill="{CAPTION}"/>
    <path d="{quiet_d}" fill="{FAINT}"/>
    <path d="{busy_d}" fill="{FAINT}"/>
    {leg}
  </g>
  <rect id="shuttle" x="{shx}" y="{st}" width="2" height="{sh}" fill="{IVORY}" opacity="0"/>
</svg>
'''.format(
        W=W, H=H, label=label, K=K, CORD=CORD, IVORY=IVORY, CAPTION=CAPTION, FAINT=FAINT,
        defs=''.join(defs), pile=pile, rx=rx, ry=ry, pw=pw, ph=ph,
        fringe_l=fringe_svg(rx - kw, ry, ph, -1),
        fringe_r=fringe_svg(rx + pw + kw, ry, ph, 1),
        kilim_l=kilim(rx - kw), kilim_r=kilim(rx + pw),
        sx=rx - kw, sw=pw + 2 * kw, st=ry - 2.5, sb=ry + ph - 2, sh=ph + 4.5,
        shx=rx - kw, sweep=pw + 2 * kw,
        cap_d=cap_d, quiet_d=quiet_d, busy_d=busy_d, leg=''.join(leg))
    if not animate:
        svg = re.sub(r'\s*<style>.*?</style>', '', svg, flags=re.S)
        svg = re.sub(r'\s*<mask id="loomMask">.*?</mask>', '', svg)
        svg = re.sub(r'\s*<rect id="shuttle"[^>]*/>', '', svg)
        svg = svg.replace('<g mask="url(#loomMask)">', '<g>')
    return svg


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'contrib.json'
    out = sys.argv[2] if len(sys.argv) > 2 else 'out/carpet.svg'
    with open(src, encoding='utf-8') as f:
        svg = build(json.load(f))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg)
    print('woven ->', out)
