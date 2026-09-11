# -*- coding: utf-8 -*-
"""Builds the profile header SVGs. Text is outlined; motif is an abstracted
Turkmen carpet gul that doubles as a network topology."""
import typeset as T

F = 'fonts/'
DISP = T.load(F + 'Archivo-var.ttf', wght=800, wdth=118)
BODY = T.load(F + 'Archivo-var.ttf', wght=450, wdth=100)
MONO = T.load(F + 'IBMPlexMono-Medium.ttf')

W, H = 1040, 300
PAD = 64

THEMES = {
    'dark': dict(
        ground='#141110', name='#EAE3D9', tag='#BDB3A6', muted='#8C8175',
        madder='#C9452E', verdigris='#6E9B8A', line='#EAE3D9',
        line_op=0.20, node_op=0.38,
    ),
    'light': dict(
        ground='#F1EBE2', name='#191411', tag='#443C34', muted='#6E6459',
        madder='#B33A24', verdigris='#4C7A68', line='#6B5E4F',
        line_op=0.26, node_op=0.42,
    ),
}

# ---- the gul motif -------------------------------------------------------
R = 52
CX0, CY = 672, 150
COLS = [CX0 + i * 2 * R for i in range(5)]
OFF = [CX0 + R + i * 2 * R for i in range(5)]


def gul(cx, cy, r):
    """One medallion: outer diamond, inner diamond, four axial spokes."""
    p = []
    p.append(f"M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy} Z")
    ir = r * 0.46
    p.append(f"M{cx},{cy-ir:.1f} L{cx+ir:.1f},{cy} L{cx},{cy+ir:.1f} L{cx-ir:.1f},{cy} Z")
    hr = r * 0.17
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        x1, y1 = cx + dx * ir, cy + dy * ir
        x2, y2 = cx + dx * r, cy + dy * r
        p.append(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}")
        # stepped hook at each outer vertex -> reads as a network node
        p.append(f"M{x2-hr*(1-abs(dx)):.1f},{y2-hr*(1-abs(dy)):.1f} "
                 f"L{x2+hr*abs(dy):.1f},{y2+hr*abs(dx):.1f} "
                 f"L{x2+hr*(1-abs(dx)):.1f},{y2+hr*(1-abs(dy)):.1f} "
                 f"L{x2-hr*abs(dy):.1f},{y2-hr*abs(dx):.1f} Z")
    return " ".join(p)


def field():
    centers = []
    for k in (-3, -1, 1, 3):
        centers += [(x, CY + k * R) for x in OFF]
    for k in (-2, 0, 2):
        centers += [(x, CY + k * R) for x in COLS]
    return " ".join(gul(cx, cy, R) for cx, cy in centers), centers


def zigzag(y_peak):
    """A path that runs along real diamond edges - the signal route."""
    pts, x = [], CX0 - R
    up = True
    while x <= W + R:
        pts.append((x, CY))
        pts.append((x + R, y_peak))
        x += 2 * R
    return "M" + " L".join(f"{a},{b}" for a, b in pts)


def build(theme):
    c = THEMES[theme]
    motif, centers = field()
    nodes = "".join(
        f'<circle cx="{x}" cy="{y}" r="2"/>' for x, y in centers)

    # type
    eyebrow_d, _ = T.typeset(MONO, 'FULL-STACK ENGINEER  \u00b7  GO  \u00b7  PYTHON  \u00b7  TYPESCRIPT',
                             13, PAD, 78, tracking=0.16)
    name_d, name_w = T.typeset(DISP, 'DOVLET EMINOV', 50, PAD, 144, tracking=0.015)
    tag1_d, _ = T.typeset(BODY, 'I build systems that keep running', 20, PAD, 212)
    tag2_d, _ = T.typeset(BODY, 'when the network doesn\u2019t.', 20, PAD, 238)
    stat_d, stat_w = T.typeset(MONO, 'AVAILABLE FOR REMOTE WORK', 11.5, PAD + 16, 272, tracking=0.14)
    loc_d, _ = T.typeset(MONO, 'ASHGABAT, TM  \u00b7  UTC+5', 11.5, PAD + 16 + stat_w + 58, 272, tracking=0.14)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Dovlet Eminov, full-stack engineer. I build systems that keep running when the network doesn't.">
  <style>
    .sig {{ stroke-dasharray: 150 1000; animation: run 13s linear infinite; }}
    .sig2 {{ animation-delay: -6.5s; }}
    .beat {{ animation: beat 6s ease-in-out infinite; }}
    .b2 {{ animation-delay: -2s; }} .b3 {{ animation-delay: -4s; }}
    @keyframes run {{ from {{ stroke-dashoffset: 1040; }} to {{ stroke-dashoffset: -150; }} }}
    @keyframes beat {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .sig, .beat {{ animation: none; }} .sig {{ opacity: .5; }}
    }}
  </style>
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>
    <linearGradient id="reveal" gradientUnits="userSpaceOnUse" x1="616" x2="812">
      <stop offset="0" stop-color="#000"/>
      <stop offset="1" stop-color="#fff"/>
    </linearGradient>
    <mask id="edge"><rect width="{W}" height="{H}" fill="url(#reveal)"/></mask>
  </defs>

  <rect width="{W}" height="{H}" fill="{c['ground']}"/>

  <g clip-path="url(#frame)" mask="url(#edge)">
    <g stroke="{c['line']}" stroke-opacity="{c['line_op']}" stroke-width="1" fill="none">
      <path d="{motif}"/>
    </g>
    <g fill="{c['line']}" fill-opacity="{c['node_op']}">{nodes}</g>
    <g fill="none" stroke="{c['madder']}" stroke-width="2" stroke-linecap="round" opacity=".85">
      <path class="sig" pathLength="1000" d="{zigzag(CY - R)}"/>
      <path class="sig sig2" pathLength="1000" d="{zigzag(CY + R)}"/>
    </g>
    <g fill="{c['madder']}">
      <circle class="beat" cx="{COLS[0]}" cy="{CY}" r="2.9"/>
      <circle class="beat b2" cx="{OFF[0]}" cy="{CY - R}" r="2.9"/>
      <circle class="beat b3" cx="{OFF[1]}" cy="{CY + R}" r="2.9"/>
    </g>
  </g>

  <path d="{eyebrow_d}" fill="{c['muted']}"/>
  <path d="{name_d}" fill="{c['name']}"/>
  <rect x="{PAD}" y="164" width="96" height="3" fill="{c['madder']}"/>
  <path d="{tag1_d}" fill="{c['tag']}"/>
  <path d="{tag2_d}" fill="{c['tag']}"/>
  <circle cx="{PAD + 4}" cy="268" r="3.5" fill="{c['verdigris']}"/>
  <circle cx="{PAD + 4}" cy="268" r="7" fill="none" stroke="{c['verdigris']}" stroke-opacity=".35"/>
  <path d="{stat_d}" fill="{c['muted']}"/>
  <path d="{loc_d}" fill="{c['muted']}" fill-opacity=".72"/>
</svg>
'''


import os
os.makedirs('out', exist_ok=True)
for t in THEMES:
    open(f'out/header-{t}.svg', 'w', encoding='utf-8').write(build(t))
    print(t, os.path.getsize(f'out/header-{t}.svg'), 'bytes')
