# -*- coding: utf-8 -*-
"""How a 100 GB upload moves through Paylas, woven as it lands.

The file goes up as 200 presigned multipart parts, straight from the browser
to MinIO, and each part that lands is knotted into a runner, so the upload
is woven the same way the contribution carpet above it is. The network drops
at part 77; the browser asks which parts landed, MinIO says 76, and the
weave picks up at 77 instead of starting over. When the last part lands the
runner shows the whole gul pattern.

Around it: the control path (one Go binary, never in the data path), the S3
calls as they happen, and four counters, one of which never leaves zero.

Every claim comes from the project's own README. All text is outlined, so
nothing depends on installed fonts. Writes a dark and a light version.
"""
import typeset as T

FONTS = 'fonts/'
DISP = T.load(FONTS + 'Archivo-var.ttf', wght=760, wdth=115)
BODY = T.load(FONTS + 'Archivo-var.ttf', wght=450, wdth=100)
MONO = T.load(FONTS + 'IBMPlexMono-Medium.ttf')

NAME = 'PAÝLAŞ'

THEMES = {
    'dark': dict(ink='#141110', surf='#1C1715', text='#EAE3D9', muted='#8C8175',
                 dim='#5B534B', rule='#EAE3D9', madder='#D04B33', verd='#7FAE9B',
                 slot='#221C19', slot_line='#3A322D'),
    'light': dict(ink='#F1EBE2', surf='#E8E0D3', text='#191411', muted='#6E6459',
                  dim='#A39888', rule='#191411', madder='#B33A24', verd='#3F7360',
                  slot='#E4DBCD', slot_line='#CFC4B4'),
}

# carpet dyes: a rug is the same colour whatever the theme
RED, RED2, LAT = '#7B2521', '#71231F', '#4F181B'
IVORY, SAFFRON, ORANGE, INDIGO = '#E3D5B8', '#C58C3D', '#B4432B', '#1C2231'

W, H = 1040, 640
D = 24.0                                  # one pass of the story, seconds
PARTS, LOST_AT = 200, 76                  # the drop comes after part 76
P1, P2 = (4.0, 11.0), (15.0, 21.0)        # the two streaming phases
DROP, LIST, DONE = 11.0, 13.2, 21.2
RESET0, RESET1 = 23.3, 23.85

COLS, ROWS = 40, 5                        # the runner, one cell per part
STEP, CELL = 23.8, 22.4
GX, GY = 48 + (952 - (COLS * STEP - (STEP - CELL))) / 2, 436


# --- time ---------------------------------------------------------------------
def pct(t):
    return '%.3f%%' % (max(0.0, min(D, t)) / D * 100.0)


def gate(name, windows, fade=0.25, peak=1):
    marks = [(0.0, 0)]
    for a, b in windows:
        marks += [(max(0.001, a - fade), 0), (a, peak), (b, peak), (min(D - 0.001, b + fade), 0)]
    marks.append((D, 0))
    marks.sort(key=lambda m: m[0])
    return '@keyframes %s{%s}' % (name, ''.join('%s{opacity:%s}' % (pct(t), v) for t, v in marks))


def keep(name, on, fade=0.2):
    """Visible from `on` until the loop resets."""
    return gate(name, [(on, RESET0)], fade)


def t_part(n):
    if n <= LOST_AT:
        return P1[0] + n * (P1[1] - P1[0]) / LOST_AT
    return P2[0] + (n - LOST_AT) * (P2[1] - P2[0]) / (PARTS - LOST_AT)


def travel(name, pts, extra=''):
    lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    total, acc, marks = sum(lens) or 1.0, 0.0, []
    for i, (x, y) in enumerate(pts):
        marks.append((acc / total * 100.0, x, y))
        if i < len(lens):
            acc += lens[i]
    return '@keyframes %s{%s}' % (name, ''.join(
        '%.2f%%{transform:translate(%.1fpx,%.1fpx)%s}' % (m + (extra,)) for m in marks))


# --- type ---------------------------------------------------------------------
# Each glyph is outlined once into <defs> and placed with <use>, which keeps the
# file a fraction of the size of outlining every string separately.
GLYPHS = {}
FONT_IDS = {}


def glyph(font, size, ch):
    key = (id(font), size, ch)
    if key not in GLYPHS:
        d, adv = T.typeset(font, ch, size, 0, 0)
        fid = FONT_IDS.setdefault(id(font), 'abcdefgh'[len(FONT_IDS)])
        GLYPHS[key] = ('%s%d' % (fid, len(GLYPHS)), d, adv)
    return GLYPHS[key]


def width(s, size, font=MONO, track=0.12):
    return sum(glyph(font, size, ch)[2] for ch in s) + track * size * (len(s) - 1)


def text(s, x, y, size, col, font=MONO, track=0.12, anchor='start'):
    w = width(s, size, font, track)
    if anchor == 'end':
        x -= w
    elif anchor == 'middle':
        x -= w / 2
    out, pen = [], x
    for ch in s:
        gid, d, adv = glyph(font, size, ch)
        if d:
            out.append('<use href="#%s" x="%.1f"/>' % (gid, pen))
        pen += adv + track * size
    return '<g fill="%s" transform="translate(0 %.1f)">%s</g>' % (col, y, ''.join(out))


def glyph_defs():
    return ''.join('<path id="%s" d="%s"/>' % (gid, d) for gid, d, _ in GLYPHS.values() if d)


# --- the runner -----------------------------------------------------------------
def motif(col, row):
    """Small Tekke guls, five knots high, with a minor gul between each pair."""
    g, c = col // 8, col % 8
    dx, dy = c - 4, row - 2
    if abs(dx) <= 2 and abs(dy) <= 2 and abs(dx) + abs(dy) <= 3:     # the gul, an octagon
        if max(abs(dx), abs(dy)) == 2:
            return LAT                    # a dark madder outline keeps the red ground in charge
        if dx == 0 and dy == 0:
            return INDIGO
        if dx == 0 or dy == 0:
            return IVORY                  # the gul quartered by a pale cross
        a, b = (SAFFRON, ORANGE) if g % 2 == 0 else (ORANGE, SAFFRON)
        return a if dx * dy > 0 else b    # opposite quarters share a dye
    dc = min(c, 8 - c)
    if dc + abs(dy) == 0:
        return IVORY                      # the minor gul
    if dc + abs(dy) == 1:
        return INDIGO
    return RED if (col // 3) % 2 == 0 else RED2   # a hint of abrash


def cell_xy(n):
    i = n - 1
    return GX + (i // ROWS) * STEP, GY + (i % ROWS) * STEP


def build(theme):
    c = THEMES[theme]
    css, body = [], []
    GLYPHS.clear()

    # ---- header
    body.append(text(NAME, 48, 54, 26, c['text'], DISP, 0.04))
    nw = width(NAME, 26, DISP, 0.04)
    body.append(text('HOW A 100 GB UPLOAD SURVIVES A DROPPED CONNECTION', 48 + nw + 22, 53,
                     11, c['muted'], track=0.16))
    body.append(text('GO  ·  POSTGRES  ·  MINIO', 1000, 53, 10, c['dim'], track=0.16, anchor='end'))
    body.append('<line x1="48" y1="76" x2="1000" y2="76" stroke="%s" stroke-opacity=".12"/>' % c['rule'])

    # ---- the diagram
    def node(x, y, w, h, name, sub, accent=False):
        out = ['<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-opacity="%s"/>'
               % (x, y, w, h, c['surf'], c['madder'] if accent else c['rule'], '.7' if accent else '.16')]
        if accent:
            out.append('<rect x="%d" y="%d" width="%d" height="3" rx="1.5" fill="%s"/>' % (x, y, w, c['madder']))
        out.append(text(name, x + w / 2, y + h / 2 + 1, 15, c['text'], DISP, 0.05, 'middle'))
        out.append(text(sub, x + w / 2, y + h / 2 + 20, 9.5, c['muted'], anchor='middle'))
        return ''.join(out)

    BR, PA, PG, MI = (48, 226, 128, 76), (268, 104, 164, 70), (512, 104, 128, 70), (512, 226, 128, 76)
    e_post = [(112, 226), (112, 139), (268, 139)]
    e_urls = [(268, 155), (128, 155), (128, 226)]
    e_db = [(432, 139), (512, 139)]
    e_s3 = [(412, 174), (412, 200), (576, 200), (576, 226)]
    e_s3_back = list(reversed(e_s3))
    band = [(176, 264), (512, 264)]

    def line(pts, dash=False, op='.28'):
        return ('<path d="M%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="1"%s/>'
                % (' L'.join('%d,%d' % p for p in pts), c['rule'], op,
                   ' stroke-dasharray="3 3"' if dash else ''))

    body += [line(e_post), line(e_urls, True, '.18'), line(e_db), line(e_s3)]
    # the data path: thick, and nowhere near the Go binary
    body.append('<line x1="176" y1="264" x2="512" y2="264" stroke="%s" stroke-width="12" '
                'stroke-linecap="butt"/>' % c['slot_line'])
    css.append(gate('gFlow', [P1, P2], fade=0.15, peak=.35))
    body.append('<line x1="176" y1="264" x2="512" y2="264" stroke="%s" stroke-width="12" class="a t" '
                'style="animation:gFlow %ss linear infinite"/>' % (c['madder'], D))
    body.append('<line x1="176" y1="264" x2="512" y2="264" stroke="%s" stroke-opacity=".10"/>' % c['rule'])
    body.append(text('POST /api/uploads', 124, 131, 9.5, c['muted']))
    body.append(text('presigned urls', 140, 170, 9, c['dim']))
    body.append(text('INSERT', 472, 131, 9.5, c['muted'], anchor='middle'))
    body.append(text('CreateMultipartUpload', 424, 194, 9.5, c['muted']))
    body.append(text('PUT part  ·  presigned  ·  straight to :9000', 344, 251, 9.5, c['text'], anchor='middle'))
    body.append(text('the go binary never carries a byte', 344, 304, 9.5, c['muted'], anchor='middle'))
    body += [node(*BR, 'BROWSER', 'plain js'), node(*PA, NAME, 'one go binary', True),
             node(*PG, 'POSTGRES', 'metadata'), node(*MI, 'MINIO', 's3 multipart')]

    # packets on the control path
    def pkt(anim, window, pts, n=1, dur=0.8, size=6, col=None):
        css.append(travel(anim, pts))
        css.append(gate(anim + 'G', [window], fade=0.12))
        return ''.join(
            '<g class="a t" style="animation:%sG %ss linear infinite">'
            '<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="1" fill="%s" class="a" '
            'style="animation:%s %ss linear infinite;animation-delay:-%.2fs"/></g>'
            % (anim, D, -size / 2, -size / 2, size, size, col or c['madder'], anim, dur, i * dur / n)
            for i in range(n))

    body.append(pkt('kPost', (0.4, 1.3), e_post, dur=0.9))
    body.append(pkt('kDb', (1.4, 2.0), e_db, dur=0.6))
    body.append(pkt('kCmu', (2.1, 2.8), e_s3, dur=0.7))
    body.append(pkt('kUrl', (2.9, 3.7), e_urls, dur=0.8, col=c['dim']))
    body.append(pkt('kAsk', (LIST, LIST + 0.6), e_post, dur=0.6))
    body.append(pkt('kList', (LIST + 0.6, LIST + 1.2), e_s3, dur=0.6))
    body.append(pkt('kListB', (LIST + 1.2, LIST + 1.8), e_s3_back, dur=0.6, col=c['verd']))
    body.append(pkt('kDone', (DONE, DONE + 0.6), e_s3, dur=0.6))
    # parts on the data path, in the colours they will be woven in
    css.append(travel('kData', band))
    css.append(gate('kDataG', [P1, P2], fade=0.1))
    body.append('<g class="a t" style="animation:kDataG %ss linear infinite">%s</g>' % (D, ''.join(
        '<rect x="-4" y="-4" width="8" height="8" rx="1" fill="%s" class="a" '
        'style="animation:kData .9s linear infinite;animation-delay:-%.2fs"/>'
        % ((IVORY, SAFFRON, ORANGE)[i % 3], i * 0.15) for i in range(6))))

    # the drop
    css.append(gate('gDrop', [(DROP, LIST)], fade=0.1))
    css.append('@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.25}}')
    body.append(
        '<g class="a t" style="animation:gDrop %ss linear infinite">'
        '<rect x="330" y="252" width="28" height="24" fill="%s"/>'
        '<path d="M337,257 L351,271 M351,257 L337,271" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>'
        '<g class="a" style="animation:blink .8s steps(1) infinite">%s</g></g>'
        % (D, c['ink'], c['madder'],
           text('offline · retrying', 112, 322, 9.5, c['madder'], anchor='middle')))

    # ---- the log
    body.append('<rect x="672" y="104" width="328" height="198" rx="3" fill="%s" stroke="%s" '
                'stroke-opacity=".16"/>' % (c['surf'], c['rule']))
    body.append(text('LOG', 688, 124, 9, c['dim'], track=0.2))
    log = [
        (0.4, 'web→go', 'POST /api/uploads', '201', None),
        (1.5, 'go→pg', 'INSERT upload, 100 GB', 'ok', None),
        (2.2, 'go→s3', 'CreateMultipartUpload', 'ok', None),
        (3.0, 'go→web', 'presigned part urls', '200', None),
        (P1[0], 'web→s3', 'PUT part 1 … 76', '', None),
        (DROP, 'web', 'network lost at part 77', '×', 'madder'),
        (LIST + 0.6, 'go→s3', 'ListParts', '76 found', 'verd'),
        (P2[0], 'web→s3', 'PUT part 77 … 200', '', None),
        (DONE, 'go→s3', 'CompleteMultipartUpload', '✓', 'verd'),
    ]
    for i, (t, who, what, res, tone) in enumerate(log):
        y = 146 + i * 18
        col = c[tone] if tone else c['text']
        css.append(keep('gL%d' % i, t))
        res_t = {4: P1[1], 7: P2[1]}.get(i)
        line_svg = text(who, 688, y, 9, c['dim'], track=0.06) + text(what, 742, y, 9.5, col, track=0.06)
        if res:
            line_svg += text(res, 986, y, 9.5, col, track=0.06, anchor='end')
        body.append('<g class="a" style="animation:gL%d %ss linear infinite">%s</g>' % (i, D, line_svg))
        if res_t:                                    # streaming lines report when they finish
            css.append(keep('gR%d' % i, res_t))
            body.append('<g class="a" style="animation:gR%d %ss linear infinite">%s</g>' % (
                i, D, text('76/200' if i == 4 else '200/200', 986, y, 9.5, c['muted'], track=0.06, anchor='end')))

    # ---- counters, as odometers
    body.append('<line x1="48" y1="326" x2="1000" y2="326" stroke="%s" stroke-opacity=".12"/>' % c['rule'])
    DS, DH = 30, 38                                  # digit size, wheel pitch
    clips = []
    adv = width('0', DS, track=0)
    digits = ''.join('<path id="dg%d" d="%s"/>' % (k, T.typeset(MONO, str(k), DS, 0, 0)[0]) for k in range(10))

    def wheel(name, x, y, events, col, final):
        marks, cur = [(0.0, 0)], 0
        for t, dg in events:
            if dg != cur:
                marks += [(t - 0.004, cur), (t, dg)]
                cur = dg
        marks += [(RESET1 - 0.004, cur), (RESET1, 0), (D, 0)]
        css.append('@keyframes %s{%s}' % (name, ''.join(
            '%s{transform:translateY(%dpx)}' % (pct(t), -dg * DH) for t, dg in marks)))
        top = y - DS * 0.78
        clips.append('<clipPath id="k%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%d"/></clipPath>'
                     % (name, x, top - 2, adv + 1, DH - 4))
        return ('<g clip-path="url(#k%s)"><g class="a" style="animation:%s %ss linear infinite;'
                'transform:translateY(%dpx)" fill="%s">%s</g></g>'
                % (name, name, D, -final * DH, col,
                   ''.join('<use href="#dg%d" x="%.1f" y="%.1f"/>' % (k, x, y + k * DH) for k in range(10))))

    def counter(x, label, wheels, suffix, col=None):
        out = [text(label, x, 346, 9, c['muted'], track=0.16)]
        wx = x
        for name, events, final in wheels:
            out.append(wheel(name, wx, 384, events, col or c['text'], final))
            wx += adv
        if suffix:
            out.append(text(suffix, wx + 4, 384, 15, c['muted'], track=0.06))
        return ''.join(out)

    pe = [(t_part(n), n) for n in range(1, PARTS + 1)]
    body.append(counter(48, 'PARTS STORED', [
        ('wP2', [(t, n // 100) for t, n in pe], 2),
        ('wP1', [(t, (n // 10) % 10) for t, n in pe], 0),
        ('wP0', [(t, n % 10) for t, n in pe], 0)], '/ 200'))
    body.append(counter(286, 'GIGABYTES', [
        ('wG2', [(t, (n // 2) // 100) for t, n in pe], 1),
        ('wG1', [(t, ((n // 2) // 10) % 10) for t, n in pe], 0),
        ('wG0', [(t, (n // 2) % 10) for t, n in pe], 0)], 'GB'))
    body.append(counter(524, 'RESTARTS FROM ZERO', [('wR0', [], 0)], '', c['verd']))
    body.append(counter(762, 'BYTES THROUGH THE GO BINARY', [('wB0', [], 0)], 'B', c['verd']))

    # ---- the runner
    body.append(text('MINIO BUCKET  ·  200 PARTS × 512 MB  ·  EACH ONE KNOTTED IN AS IT LANDS',
                     48, 424, 9, c['muted'], track=0.14))
    body.append(text('RESUMES FROM THE LAST PART', 1000, 424, 9, c['dim'], track=0.14, anchor='end'))
    rw, rh = COLS * STEP - (STEP - CELL), ROWS * STEP - (STEP - CELL)
    # warp threads at both ends, as on a real loom
    for side in (-1, 1):
        x0 = GX - 3 if side < 0 else GX + rw + 3
        for r in range(ROWS * 2):
            y = GY + 4 + r * (rh - 8) / (ROWS * 2 - 1)
            body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-opacity=".5"/>'
                        % (x0, y, x0 + side * (7 + 3 * ((r * 7) % 3)), y, c['dim']))
    for n in range(1, PARTS + 1):
        x, y = cell_xy(n)
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s"/>'
                    % (x, y, CELL, CELL, c['slot'], c['slot_line']))
    for n in range(1, PARTS + 1):
        x, y = cell_xy(n)
        i = n - 1
        css.append(keep('n%d' % n, t_part(n), fade=0.12))
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" class="a" '
                    'style="animation:n%d %ss linear infinite"/>'
                    % (x, y, CELL, CELL, motif(i // ROWS, i % ROWS), n, D))
    # every cell is three knots by three, as if woven
    kn = (CELL - 1.0) / 3
    body.append('<pattern id="knots" x="%.1f" y="%.1f" width="%.1f" height="%.1f" patternUnits="userSpaceOnUse">'
                '%s</pattern>' % (GX, GY, STEP, STEP, ''.join(
                    '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.6" fill="url(#dome)"/>'
                    % (0.5 + i * kn, 0.5 + j * kn, kn - 0.6, kn - 0.6) for i in range(3) for j in range(3))))
    body.append('<radialGradient id="dome" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff" '
                'stop-opacity=".16"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>'
                '<stop offset="1" stop-color="#000" stop-opacity=".38"/></radialGradient>')
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#knots)" pointer-events="none"/>'
                % (GX, GY, rw, rh))
    # the parts in flight when the network went
    lost = ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="%s" '
                   'stroke-width="2"/>' % (cell_xy(n) + (CELL, CELL, c['madder'])) for n in (77, 78, 79))
    body.append('<g class="a t" style="animation:gDrop %ss linear infinite"><g class="a" '
                'style="animation:blink .8s steps(1) infinite">%s</g></g>' % (D, lost))
    # ListParts checks what landed
    scan_x1 = GX + ((LOST_AT - 1) // ROWS) * STEP
    css.append('@keyframes scan{0%%{transform:translateX(0);opacity:0}%s{transform:translateX(0);opacity:0}'
               '%s{opacity:.9}%s{transform:translateX(%.1fpx);opacity:.9}%s{transform:translateX(%.1fpx);opacity:0}'
               '100%%{opacity:0;transform:translateX(%.1fpx)}}'
               % (pct(LIST + 0.6), pct(LIST + 0.7), pct(LIST + 1.7), scan_x1 - GX, pct(LIST + 1.85),
                  scan_x1 - GX, scan_x1 - GX))
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="2" '
                'rx="2" class="a t" style="animation:scan %ss linear infinite"/>'
                % (GX - 2, GY - 2, CELL + 4, rh + 4, c['verd'], D))
    # the shuttle rides the edge of the weave
    sx = [(0.0, 0), (P1[0], 0), (P1[1], LOST_AT), (P2[0], LOST_AT), (P2[1], PARTS), (RESET1, PARTS), (D, 0)]

    def shuttle_x(n):
        return n / ROWS * STEP - (STEP - CELL) / 2 if n else -4

    css.append('@keyframes shuttle{%s}' % ''.join(
        '%s{transform:translateX(%.1fpx)}' % (pct(t), shuttle_x(n)) for t, n in sx))
    css.append(gate('gShut', [(P1[0], DONE)], fade=0.2))
    body.append('<g class="a t" style="animation:gShut %ss linear infinite"><rect x="%.1f" y="%.1f" width="2" '
                'height="%.1f" rx="1" fill="%s" class="a" style="animation:shuttle %ss linear infinite"/></g>'
                % (D, GX, GY - 6, rh + 12, c['madder'], D))
    # done: the whole gul shows
    css.append('@keyframes glow{0%%{opacity:0}%s{opacity:0}%s{opacity:.28}%s{opacity:0}100%%{opacity:0}}'
               % (pct(DONE + 0.5), pct(DONE + 0.9), pct(DONE + 1.8)))
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" class="a t" '
                'style="animation:glow %ss linear infinite"/>' % (GX - 2, GY - 2, rw + 4, rh + 4, IVORY, D))

    # ---- what is happening, and when
    caps = [
        (0.2, P1[0], 'Paýlaş records the upload, opens it in MinIO and hands the browser presigned part URLs.'),
        (P1[0], DROP, 'Parts go straight from the browser to MinIO on :9000. The Go binary never touches a byte.'),
        (DROP, LIST, 'The network drops at part 77. Only the part in flight is lost.'),
        (LIST, P2[0], 'The browser asks which parts landed. MinIO says 76.'),
        (P2[0], DONE, 'The weave picks up at part 77. No restart, nothing sent twice.'),
        (DONE, RESET0, 'MinIO stitches 200 parts into one 100 GB object. The app server carried none of it.'),
    ]
    for i, (a, b, s) in enumerate(caps):
        css.append(gate('gC%d' % i, [(a + 0.15, b - 0.15)], fade=0.15))
        last = i == len(caps) - 1
        body.append('<g class="a%s" style="animation:gC%d %ss linear infinite">%s%s</g>' % (
            '' if last else ' t', i, D, text('0%d' % (i + 1), 48, 586, 11, c['madder']),
            text(s, 80, 586, 15, c['text'], BODY, 0)))

    marks = [(0.0, 'START'), (P1[0], 'UPLOAD'), (DROP, 'DROP'), (LIST, 'CHECK'), (P2[0], 'RESUME'), (DONE, 'DONE')]
    body.append('<line x1="48" y1="608" x2="1000" y2="608" stroke="%s" stroke-opacity=".18"/>' % c['rule'])
    for t, s in marks:
        x = 48 + t / D * 952
        body.append('<line x1="%.1f" y1="604" x2="%.1f" y2="612" stroke="%s" stroke-opacity=".35"/>'
                    % (x, x, c['rule']))
        body.append(text(s, x + 4, 626, 8.5, c['madder'] if s == 'DROP' else c['dim'], track=0.16))
    css.append('@keyframes play{from{transform:translateX(0)}to{transform:translateX(952px)}}')
    body.append('<circle cx="48" cy="608" r="4" fill="%s" class="a t" style="animation:play %ss linear infinite"/>'
                % (c['madder'], D))

    css.append('.a{animation-iteration-count:infinite}')
    css.append('@media (prefers-reduced-motion:reduce){.a{animation:none!important}.t{display:none}}')

    label = ('How a 100 GB upload moves through Paylas. The browser asks the Go binary to start it; '
             'the binary records it in Postgres and opens a presigned multipart upload in MinIO. The browser '
             'sends 200 parts straight to MinIO, each woven into a runner as it lands. The network drops after '
             'part 76; the browser asks which parts landed and resumes at part 77, so nothing restarts and '
             'no byte passes through the app server.')

    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            'role="img" aria-label="{label}"><title>{label}</title><style>{css}</style>'
            '<defs>{digits}{clips}{glyphs}</defs><rect width="{W}" height="{H}" rx="6" fill="{ink}"/>{body}</svg>\n'
            ).format(W=W, H=H, label=label, css=''.join(css), digits=digits, ink=c['ink'], body=''.join(body),
                     clips=''.join(clips), glyphs=glyph_defs())


if __name__ == '__main__':
    import os
    os.makedirs('out', exist_ok=True)
    for theme in THEMES:
        path = 'out/upload-path-%s.svg' % theme
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(build(theme))
        print('drawn ->', path)
