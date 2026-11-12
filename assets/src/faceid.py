# -*- coding: utf-8 -*-
"""Face ID: a photo is flat, a face is not.

Two attempts at the same login. First, a photo of the user held up on a
phone: the RealSense D415 measures depth as well as colour, the depth comes
back as one flat plane, and the 3D structure check fails. Then the user:
the nose stands out from the cheeks, all four depth checks pass, ArcFace
makes a 512-number embedding, pgvector finds the enrolled face above the
0.60 cosine threshold, and the auth service issues a JWT.

The depth maps are knotted, one knot per depth sample, in the same dyes as
the carpet: the nearer the surface, the paler the wool. The checks, the
threshold and the services are the project's own.
"""
import math
import card
from card import IVORY, SAFFRON, ORANGE, RED, LAT, INDIGO

A1, A2 = 0.3, 6.0                 # the two attempts
SCAN = 2.0
REJECT = 3.8
CHECKS = [9.8, 10.1, 10.4, 10.7]
EMBED, MATCH, JWT = 11.0, 12.4, 13.8

GC, GR, GS = 22, 28, 4.4          # depth grid: columns, rows, step
CELL = 3.9


def nearness(u, v):
    """A face as a height field, 0 far to 1 near; None outside the head."""
    r2 = (u / 0.8) ** 2 + (v / 0.96) ** 2
    if r2 > 1:
        return None
    z = 0.30 + 0.38 * math.sqrt(1 - r2)
    g = lambda cu, cv, su, sv: math.exp(-((u - cu) / su) ** 2 - ((v - cv) / sv) ** 2)
    z += 0.42 * g(0, 0.08, 0.13, 0.30)                          # nose
    z -= 0.24 * (g(-0.34, -0.16, 0.16, 0.10) + g(0.34, -0.16, 0.16, 0.10))   # eye sockets
    z += 0.07 * g(0, -0.40, 0.45, 0.08)                         # brow
    z += 0.08 * g(0, 0.55, 0.22, 0.06)                          # lips
    return max(0.0, min(1.0, z))


def dye(z):
    if z is None:
        return None
    for lim, col in ((0.34, LAT), (0.46, RED), (0.58, ORANGE), (0.72, SAFFRON)):
        if z < lim:
            return col
    return IVORY


def build(theme):
    k = card.Card(theme, 22.0)
    c = k.c
    b = k.body
    k.header('FACE ID', 'A PHOTO IS FLAT. A FACE IS NOT.', 'REALSENSE D415  ·  INSIGHTFACE  ·  PGVECTOR')

    # ---- diagram ---------------------------------------------------------------
    BR, GW, AU = (48, 104, 130, 62), (250, 104, 130, 62), (510, 104, 130, 62)
    CA, FA, PG = (48, 222, 130, 62), (250, 222, 130, 62), (510, 222, 130, 62)
    e_login = [(178, 135), (250, 135)]
    e_auth = [(380, 135), (510, 135)]
    e_cam = [(270, 166), (270, 192), (113, 192), (113, 222)]
    e_frame = [(178, 253), (250, 253)]
    e_vec = [(380, 253), (510, 253)]
    e_face = [(345, 222), (345, 166)]
    e_back = [(250, 150), (178, 150)]
    for e in (e_login, e_auth, e_cam, e_frame, e_vec, e_face):
        b.append(k.line(e))
    b.append(k.line(e_back, dash=True, op='.18'))
    b.append(k.text('login', 214, 127, 9, c['muted'], anchor='middle'))
    b.append(k.text('verify · issue', 445, 127, 9, c['muted'], anchor='middle'))
    b.append(k.text('capture', 190, 186, 9, c['muted'], anchor='middle'))
    b.append(k.text('frames', 214, 245, 9, c['muted'], anchor='middle'))
    b.append(k.text('rgb + depth', 113, 300, 9, c['dim'], anchor='middle'))
    b.append(k.text('cosine ≥ 0.60', 445, 245, 9, c['muted'], anchor='middle'))
    b.append(k.text('512-d · hnsw', 445, 270, 9, c['dim'], anchor='middle'))
    b.append(k.text('verdict', 352, 196, 9, c['dim']))
    b += [k.node(*BR, 'BROWSER', 'react · typescript'), k.node(*GW, 'GATEWAY', 'fastapi', True),
          k.node(*AU, 'AUTH', 'jwt'), k.node(*CA, 'CAMERA', 'realsense d415'),
          k.node(*FA, 'FACE', 'retinaface · arcface'), k.node(*PG, 'PGVECTOR', 'enrolled faces')]
    for t0 in (A1, A2):
        b.append(k.packets([(t0, t0 + 0.4)], e_login, dur=0.4))
        b.append(k.packets([(t0 + 0.4, t0 + 1.0)], e_cam, dur=0.6))
        b.append(k.packets([(t0 + 1.0, t0 + 1.5)], e_frame, dur=0.5, n=2, cols=[IVORY, ORANGE]))
    b.append(k.packets([(REJECT - 0.4, REJECT)], e_face, dur=0.4))
    b.append(k.packets([(REJECT, REJECT + 0.4)], e_back, dur=0.4))
    b.append(k.packets([(MATCH, MATCH + 0.4)], e_vec, dur=0.4))
    b.append(k.packets([(MATCH + 0.6, MATCH + 1.0)], list(reversed(e_vec)), dur=0.4, cols=[c['verd']]))
    b.append(k.packets([(JWT - 0.8, JWT - 0.4)], e_face, dur=0.4, cols=[c['verd']]))
    b.append(k.packets([(JWT - 0.4, JWT)], e_auth, dur=0.4, cols=[c['verd']]))
    b.append(k.packets([(JWT, JWT + 0.5)], e_back, dur=0.4, cols=[c['verd']]))

    # ---- the checks ------------------------------------------------------------
    b.append(k.panel(672, 96, 328, 214, 'ANTI-SPOOF · DEPTH CHECKS'))
    px, fx = 900, 964
    b.append(k.text('PHOTO', px, 140, 8.5, c['muted'], track=0.16, anchor='middle'))
    b.append(k.text('FACE', fx, 140, 8.5, c['muted'], track=0.16, anchor='middle'))
    rows = ['3D structure · nose 2–4 cm out', 'smooth depth gradients', 'depth within range',
            'enough valid depth pixels', 'cosine similarity ≥ 0.60']
    for i, r in enumerate(rows):
        y = 164 + i * 24
        b.append(k.text(r, 688, y, 9.5, c['text'], track=0.04))
        b.append('<line x1="688" y1="%d" x2="984" y2="%d" stroke="%s" stroke-opacity=".07"/>' % (y + 9, y + 9, c['rule']))
        # the photo fails at the first check; the rest are not what stops it
        if i == 0:
            b.append(k.show_from(REJECT - 0.3, k.text('×', px, y + 1, 13, c['madder'], anchor='middle')))
        else:
            b.append(k.show_from(REJECT - 0.3, k.text('–', px, y, 10, c['dim'], anchor='middle')))
        t = CHECKS[i] if i < 4 else MATCH + 0.6
        b.append(k.show_from(t, k.text('✓', fx, y, 11, c['verd'], anchor='middle')))
    y = 164 + 5 * 24 + 4
    b.append(k.text('result', 688, y, 9.5, c['muted'], track=0.04))
    b.append(k.show_from(REJECT, k.text('REJECT', px, y, 9.5, c['madder'], anchor='middle')))
    b.append(k.show_from(JWT, k.text('JWT', fx, y, 9.5, c['verd'], anchor='middle')))

    # ---- counters --------------------------------------------------------------
    b.append(k.rule(326))
    b.append(k.counter(48, 384, 'ATTEMPTS', [(A1, 1), (A2, 2)], 1, 2))
    b.append(k.counter(286, 384, 'NOSE STANDS OUT', [(A2 + SCAN + 1.0, 3)], 1, 3, 'cm'))
    b.append(k.counter(524, 384, 'DEPTH CHECKS PASSED', [(t, i + 1) for i, t in enumerate(CHECKS)], 1, 4, '/ 4'))
    b.append(k.word(762, 381, 'RESULT', [
        (A1, REJECT, 'CHECKING', 'muted'), (REJECT, A2, 'REJECTED', 'madder'),
        (A2, JWT, 'CHECKING', 'muted'), (JWT, k.reset0, 'SIGNED IN', 'verd')]))

    # ---- depth, knotted ----------------------------------------------------------
    HY = 428
    b.append(k.text('DEPTH · PALER IS NEARER', 48, 416, 9, c['muted'], track=0.14))
    gx_photo, gx_face = 48, 48 + GC * GS + 22
    gh = GR * GS

    def grid(gx, cells, t0, label):
        """Each row appears as the scan passes it: one path per dye per row."""
        out = [k.text(label, gx, HY + gh + 13, 8, c['dim'], track=0.12)]
        for r in range(GR):
            by = {}
            for col in range(GC):
                fill = cells(col, r)
                if fill:
                    by.setdefault(fill, []).append('M%.1f %.1fh%.1fv%.1fh-%.1fz'
                                                   % (gx + col * GS, HY + r * GS, CELL, CELL, CELL))
            if by:
                out.append(k.show_from(t0 + r * SCAN / GR, ''.join(
                    '<path fill="%s" d="%s"/>' % (f, ''.join(d)) for f, d in sorted(by.items())), fade=0.08))
        return ''.join(out)

    def photo(col, r):
        return ORANGE if 4 <= col <= 17 and 1 <= r <= 26 else None   # a phone screen: one plane

    def face(col, r):
        u = (col - (GC - 1) / 2) / (GC / 2)
        v = (r - (GR - 1) / 2) / (GR / 2)
        return dye(nearness(u, v))

    # empty slots before the scan, as one pattern per grid
    k.defs.append('<pattern id="slots" width="%.1f" height="%.1f" patternUnits="userSpaceOnUse">'
                  '<rect width="%.1f" height="%.1f" rx="1" fill="%s" stroke="%s" stroke-width=".5"/></pattern>'
                  % (GS, GS, CELL, CELL, c['slot'], c['slot_line']))
    for gx in (gx_photo, gx_face):
        b.append('<rect x="%.1f" y="%d" width="%.1f" height="%.1f" fill="url(#slots)" '
                 'style="transform:translate(%.1fpx,%dpx)"/>' % (0, 0, GC * GS, gh, gx, HY))
    b.append(grid(gx_photo, photo, A1 + 1.0, 'PHOTO ON A PHONE'))
    b.append(grid(gx_face, face, A2 + 1.0, 'LIVE FACE'))
    for gx, t0 in ((gx_photo, A1 + 1.0), (gx_face, A2 + 1.0)):
        k.css.append('@keyframes %s{0%%{transform:translateY(0)}%s{transform:translateY(0)}%s{transform:translateY(%dpx)}100%%{transform:translateY(%dpx)}}'
                     % ('sc%d' % gx, k.pct(t0), k.pct(t0 + SCAN), gh, gh))
        b.append(k.show([(t0, t0 + SCAN)], '<rect x="%.1f" y="%d" width="%.1f" height="2" fill="%s" class="a" '
                        'style="animation:sc%d %ss linear infinite"/>' % (gx - 3, HY - 1, GC * GS + 6, c['madder'], gx, k.D),
                        fade=0.1))

    # cross-section through the nose
    CX0, CX1, CY0, CY1 = 300, 660, HY + 6, HY + gh - 4
    b.append(k.text('CROSS-SECTION THROUGH THE NOSE', CX0, 416, 9, c['muted'], track=0.14))
    b.append(k.line([(CX0, CY1), (CX1, CY1)], op='.25'))
    b.append(k.text('nearer ↑', CX0, CY0 + 2, 8.5, c['dim']))
    vrow = 0.12

    def ypos(z):
        return CY1 - 10 - z * (CY1 - CY0 - 20)

    pts_face, us = [], [i / 60 * 2 - 1 for i in range(61)]
    for u in us:
        z = nearness(u * 0.8, vrow)
        pts_face.append((CX0 + (u + 1) / 2 * (CX1 - CX0), ypos(z if z is not None else 0.0)))
    flat = ypos(0.5)
    photo_pts = [(CX0 + 0.19 * (CX1 - CX0), flat), (CX0 + 0.81 * (CX1 - CX0), flat)]

    def drawn(pts, t0, t1, col, width=2):
        name = k.name('dr')
        k.css.append('@keyframes %s{0%%{stroke-dashoffset:1000}%s{stroke-dashoffset:1000}%s{stroke-dashoffset:0}'
                     '100%%{stroke-dashoffset:0}}' % (name, k.pct(t0), k.pct(t1)))
        path = ('<path d="M%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" pathLength="1000" '
                'stroke-dasharray="1000 1000" class="a" style="animation:%s %ss linear infinite"/>'
                % (' L'.join('%.1f,%.1f' % p for p in pts), col, width, name, k.D))
        return k.show_from(t0, path)

    b.append(drawn(photo_pts, A1 + 1.0 + SCAN, A1 + 1.6 + SCAN, ORANGE))
    b.append(k.show_from(A1 + 1.6 + SCAN, k.text('photo · flat', photo_pts[1][0] + 6, flat + 3, 8.5, ORANGE)))
    b.append(drawn(pts_face, A2 + 1.0 + SCAN, A2 + 1.8 + SCAN, IVORY))
    tip = min(pts_face, key=lambda p: p[1])
    cheek = pts_face[18]
    bx = tip[0] + 44
    b.append(k.show_from(A2 + 1.8 + SCAN,
                         k.line([(bx - 4, tip[1]), (bx, tip[1]), (bx, cheek[1]), (bx - 4, cheek[1])],
                                col=c['verd'], op='.9')
                         + k.text('≈ 3 cm', bx + 6, (tip[1] + cheek[1]) / 2 + 3, 9, c['verd'])
                         + k.text('real faces: 2–4 cm', bx + 6, (tip[1] + cheek[1]) / 2 + 16, 8.5, c['dim'])))

    # the embedding
    EX, EC, ER, ES = 712, 19, 8, 15.0
    b.append(k.text('ARCFACE EMBEDDING · 512 NUMBERS', EX, 416, 9, c['muted'], track=0.14))
    b.append(k.text('pgvector · nearest by cosine', EX, HY + ER * ES + 12, 8, c['dim'], track=0.12))
    pal = (LAT, RED, ORANGE, SAFFRON, IVORY, INDIGO)
    for col in range(EC):
        cells = ''
        for r in range(ER):
            n = math.sin(col * 12.9898 + r * 78.233) * 43758.5453
            v = n - math.floor(n)
            cells += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.5" fill="%s"/>'
                      % (EX + col * ES, HY + r * ES, ES - 2, ES - 2, pal[int(v * len(pal)) % len(pal)]))
        b.append(''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.5" fill="%s" stroke="%s" stroke-width=".5"/>'
                         % (EX + col * ES, HY + r * ES, ES - 2, ES - 2, c['slot'], c['slot_line']) for r in range(ER)))
        b.append(k.show_from(EMBED + col * 1.2 / EC, cells, fade=0.08))
    b.append(k.knot_texture(EX, HY, ES, ES - 2, EC * ES - 2, ER * ES - 2, knots=2))

    # ---- story -----------------------------------------------------------------
    k.story([
        (0.2, REJECT, 'First attempt: someone holds the user\'s photo up on a phone. The D415 sees depth as well as colour.'),
        (REJECT, A2, 'The depth is one flat plane. Nothing stands out where a nose should, so the 3D check fails.'),
        (A2, CHECKS[0], 'Second attempt: the user. The nose stands about 3 cm out from the cheeks, as a real face does.'),
        (CHECKS[0], MATCH, 'All four depth checks pass, and ArcFace turns the face into an embedding of 512 numbers.'),
        (MATCH, JWT, 'pgvector finds the nearest enrolled face by cosine similarity, above the 0.60 threshold.'),
        (JWT, k.reset0, 'The auth service issues a JWT. The photo never came close.'),
    ], [(A1, 'PHOTO', False), (REJECT, 'REJECTED', True), (A2, 'FACE', False),
        (CHECKS[0], 'CHECKS', False), (MATCH, 'MATCH', False), (JWT, 'JWT', False)])

    return k.render(
        'Face ID: two login attempts on a RealSense D415. A photo held up on a phone gives one flat depth plane '
        'and fails the 3D structure check. The real face, with the nose standing out from the cheeks, passes all four '
        'depth checks; ArcFace makes a 512-number embedding, pgvector finds the enrolled face above the 0.60 cosine '
        'threshold, and the auth service issues a JWT.')


if __name__ == '__main__':
    card.write('faceid', build)
