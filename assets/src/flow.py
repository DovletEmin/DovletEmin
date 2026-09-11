# -*- coding: utf-8 -*-
"""An animated walkthrough of the upload path in Paylas.

Every claim comes from the project's own README: presigned multipart straight
to MinIO, the browser reaching MinIO's S3 port directly so the app server never
carries the bytes, and a transfer that survives a dropped connection. Text is
outlined, so the diagram depends on no installed fonts.
"""
import typeset as T

FONTS = 'fonts/'
DISP = T.load(FONTS + 'Archivo-var.ttf', wght=700, wdth=112)
BODY = T.load(FONTS + 'Archivo-var.ttf', wght=450, wdth=100)
MONO = T.load(FONTS + 'IBMPlexMono-Medium.ttf')

NAME = 'PAÝLAŞ'          # PAYLAS in Turkmen orthography

INK = '#141110'
SURF = '#1E1917'
BONE = '#EAE3D9'
TAUPE = '#8C8175'
DIM = '#5B534B'
MADDER = '#C9452E'
VERD = '#6E9B8A'

W, H = 1040, 470
D = 22.0                            # one full pass of the story


def pct(t):
    return '%.2f%%' % (t / D * 100.0)


def gate(name, windows, fade=0.28):
    """Opacity keyframes that switch a group on during each window."""
    marks = [(0.0, 0)]
    for a, b in windows:
        marks += [(max(0.01, a - fade), 0), (a, 1), (b, 1), (min(D - 0.01, b + fade), 0)]
    marks.append((D, 0))
    marks.sort(key=lambda m: m[0])
    return '@keyframes %s{%s}' % (
        name, ' '.join('%s{opacity:%d}' % (pct(t), v) for t, v in marks))


def seglens(pts):
    return [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(pts, pts[1:])]


def travel(name, pts):
    """Move a packet along an orthogonal polyline, timed by segment length."""
    lens = seglens(pts)
    total = sum(lens) or 1.0
    marks, acc = [], 0.0
    for i, (x, y) in enumerate(pts):
        marks.append((acc / total * 100.0, x, y))
        if i < len(lens):
            acc += lens[i]
    return '@keyframes %s{%s}' % (name, ' '.join(
        '%.2f%%{transform:translate(%.1fpx,%.1fpx)}' % m for m in marks))


def point_at(pts, frac):
    """Where along the polyline a given fraction of the length falls."""
    lens = seglens(pts)
    want = sum(lens) * frac
    for (x1, y1), (x2, y2), L in zip(pts, pts[1:], lens):
        if want <= L:
            k = want / L if L else 0
            return x1 + (x2 - x1) * k, y1 + (y2 - y1) * k
        want -= L
    return pts[-1]


def edge_path(pts):
    return 'M' + ' L'.join('%.1f,%.1f' % p for p in pts)


def node(x, y, w, h, name, sub, accent=False):
    _, nw = T.typeset(DISP, name, 17, 0, 0, tracking=0.05)
    _, sw = T.typeset(MONO, sub, 10, 0, 0, tracking=0.12)
    nd, _ = T.typeset(DISP, name, 17, x + (w - nw) / 2, y + h / 2 - 3, tracking=0.05)
    sd, _ = T.typeset(MONO, sub, 10, x + (w - sw) / 2, y + h / 2 + 19, tracking=0.12)
    return ('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s" '
            'stroke-opacity="%s"/><path d="%s" fill="%s"/><path d="%s" fill="%s"/>'
            % (x, y, w, h, SURF, MADDER if accent else BONE,
               '.55' if accent else '.20', nd, BONE, sd, TAUPE))


def label(text, x, y, size=10.5, col=None, anchor='start'):
    _, w = T.typeset(MONO, text, size, 0, 0, tracking=0.12)
    if anchor == 'end':
        x -= w
    elif anchor == 'middle':
        x -= w / 2
    d, _ = T.typeset(MONO, text, size, x, y, tracking=0.12)
    return '<path d="%s" fill="%s"/>' % (d, col or TAUPE)


def packets(anim, dur, n=3, col=None, size=7):
    return ''.join(
        '<rect class="pkt" x="%.1f" y="%.1f" width="%d" height="%d" rx="1" fill="%s" '
        'style="animation-name:%s;animation-duration:%ss;animation-delay:-%.2fs"/>'
        % (-size / 2., -size / 2., size, size, col or MADDER, anim, dur, i * dur / n)
        for i in range(n))


def build():
    BR, PA = (48, 150, 160, 88), (386, 150, 230, 88)
    PG, MI = (824, 66, 176, 76), (824, 246, 176, 76)
    TRACK_Y, TRACK_X0, TRACK_X1 = 396, 128, 912

    e1 = [(208, 194), (386, 194)]
    e1b = [(386, 208), (208, 208)]
    e2 = [(616, 176), (690, 176), (690, 104), (824, 104)]
    e3 = [(616, 212), (690, 212), (690, 284), (824, 284)]
    e4 = [(128, 238), (128, TRACK_Y), (TRACK_X1, TRACK_Y), (TRACK_X1, 334)]
    STALL = 0.38

    css = [gate('gAsk', [(0.3, 3.0), (14.9, 17.4)]),
           gate('gRep', [(1.4, 3.1)]),
           gate('gMeta', [(3.4, 6.2)]),
           gate('gPre', [(3.4, 6.2)]),
           gate('gData', [(6.6, 12.0), (17.8, 21.4)]),
           gate('gBreak', [(12.2, 14.6)]),
           gate('gDone', [(20.4, 21.9)])]
    for i, (a, b) in enumerate([(0.2, 3.2), (3.2, 6.4), (6.4, 12.2),
                                (12.2, 14.8), (14.8, 17.6), (17.6, 21.8)]):
        css.append(gate('gCap%d' % (i + 1), [(a, b)], fade=0.22))
        css.append(gate('gPip%d' % (i + 1), [(a, D - 0.02)], fade=0.18))
    for nm, pts in (('tAsk', e1), ('tRep', e1b), ('tMeta', e2), ('tPre', e3), ('tData', e4)):
        css.append(travel(nm, pts))

    # the data path doubles as the progress bar: it fills as parts land,
    # stalls through the drop, then completes
    css.append('@keyframes fill{0%%{stroke-dashoffset:1000}%s{stroke-dashoffset:1000}'
               '%s{stroke-dashoffset:%d}%s{stroke-dashoffset:%d}'
               '%s{stroke-dashoffset:0}100%%{stroke-dashoffset:0}}'
               % (pct(6.4), pct(12.0), round(1000 * (1 - STALL)),
                  pct(17.8), round(1000 * (1 - STALL)), pct(21.4)))
    css.append('.pkt{animation-timing-function:linear;animation-iteration-count:infinite}')
    css.append('.g{animation-duration:%ss;animation-iteration-count:infinite;'
               'animation-timing-function:linear;opacity:0}' % D)
    css.append('#fill{animation:fill %ss linear infinite}' % D)
    css.append('@media (prefers-reduced-motion:reduce){.g,#fill{animation:none}'
               '.g{opacity:1}.pkt,#brk,#done{display:none}'
               '.cap{display:none}#capKey{display:block}'
               '#fill{stroke-dashoffset:0;stroke-opacity:.5}}')

    title, _ = T.typeset(MONO, NAME + '   ·   HOW A 100 GB UPLOAD ACTUALLY MOVES',
                         12, 48, 40, tracking=0.17)
    edges = ''.join('<path d="%s" fill="none" stroke="%s" stroke-opacity=".28" '
                    'stroke-width="1"/>' % (edge_path(p), BONE) for p in (e1, e2, e3))

    caps = ['The browser asks %s to start a 100 GB upload.' % NAME.title(),
            '%s records it in Postgres, opens a multipart upload in MinIO, and hands back '
            'presigned part URLs.' % NAME.title(),
            'Parts go straight from the browser to MinIO on :9000. The Go binary never '
            'carries a byte.',
            'The connection drops after part 76 of 200.',
            'The browser asks which parts already landed, then resumes at 77.',
            'Stored. One binary in the control path, and none of it in the data path.']
    cap_g = ''.join(
        '<g class="g cap"%s style="animation-name:gCap%d"><path d="%s" fill="%s"/>'
        '<path d="%s" fill="%s"/></g>'
        % (' id="capKey"' if i == 2 else '', i + 1,
           T.typeset(MONO, '0%d' % (i + 1), 11, 48, 446, tracking=0.12)[0], MADDER,
           T.typeset(BODY, t, 15, 78, 446)[0], BONE)
        for i, t in enumerate(caps))

    pips = ''
    for i in range(6):
        x = 906 + i * 15
        dia = 'M%d,441 L%d,446 L%d,451 L%d,446 Z' % (x, x + 5, x, x - 5)
        pips += ('<path d="%s" fill="%s" opacity=".20"/>'
                 '<g class="g" style="animation-name:gPip%d"><path d="%s" fill="%s"/></g>'
                 % (dia, BONE, i + 1, dia, MADDER))

    bx, by = point_at(e4, STALL)

    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="How a 100 GB upload moves through Paylas. The browser asks the Go binary to start it; the binary records it in Postgres and opens a presigned multipart upload in MinIO; the browser then sends the parts straight to MinIO, and after a dropped connection it resumes from the last completed part.">
  <style>{css}</style>
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <path d="{title}" fill="{BONE}"/>{tag}
  <line x1="48" y1="58" x2="1000" y2="58" stroke="{BONE}" stroke-opacity=".12"/>

  {edges}
  <path d="{e1b}" fill="none" stroke="{BONE}" stroke-opacity=".15" stroke-width="1" stroke-dasharray="3 3"/>
  {l_ask}{l_rep}{l_meta}{l_pre}{l_data}

  <path d="{e4}" fill="none" stroke="{BONE}" stroke-opacity=".13" stroke-width="6" stroke-linejoin="round"/>
  <path id="fill" d="{e4}" pathLength="1000" stroke-dasharray="1000 1000" stroke-dashoffset="1000"
        fill="none" stroke="{MADDER}" stroke-opacity=".5" stroke-width="6" stroke-linejoin="round"/>

  {nodes}

  <g class="g" style="animation-name:gAsk">{p_ask}</g>
  <g class="g" style="animation-name:gRep">{p_rep}</g>
  <g class="g" style="animation-name:gMeta">{p_meta}</g>
  <g class="g" style="animation-name:gPre">{p_pre}</g>
  <g class="g" style="animation-name:gData">{p_data}</g>

  <g id="brk" class="g" style="animation-name:gBreak">
    <line x1="{bx1:.1f}" y1="{by1:.1f}" x2="{bx2:.1f}" y2="{by2:.1f}" stroke="{MADDER}" stroke-width="2.5"/>
    <line x1="{bx1:.1f}" y1="{by2:.1f}" x2="{bx2:.1f}" y2="{by1:.1f}" stroke="{MADDER}" stroke-width="2.5"/>
    {l_brk}
  </g>
  <g id="done" class="g" style="animation-name:gDone">{l_done}</g>

  {caps}{pips}
</svg>
'''.format(
        W=W, H=H, INK=INK, BONE=BONE, MADDER=MADDER, css=''.join(css), title=title,
        tag=label('RESUMABLE  ·  PRESIGNED MULTIPART  ·  NO PROXY IN THE DATA PATH',
                  1000, 40, 10, DIM, 'end'),
        edges=edges, e1b=edge_path(e1b), e4=edge_path(e4),
        l_ask=label('1  start an upload', 297, 184, 10.5, TAUPE, 'middle'),
        l_rep=label('presigned part urls', 297, 226, 9.5, DIM, 'middle'),
        l_meta=label('2  record it', 757, 96, 10.5, TAUPE, 'middle'),
        l_pre=label('3  presign parts', 757, 276, 10.5, TAUPE, 'middle'),
        l_data=label('4  parts go direct to :9000  ·  the app server is not in this path',
                     TRACK_X0 + 28, TRACK_Y - 17, 10.5, BONE),
        nodes=(node(*BR, name='BROWSER', sub='plain js, no build')
               + node(*PA, name=NAME, sub='single go binary', accent=True)
               + node(*PG, name='POSTGRES', sub='metadata')
               + node(*MI, name='MINIO', sub='s3 multipart')),
        p_ask=packets('tAsk', 1.3), p_rep=packets('tRep', 1.4, n=2, col=DIM, size=5),
        p_meta=packets('tMeta', 1.5, n=2), p_pre=packets('tPre', 1.5, n=2),
        p_data=packets('tData', 2.4, n=5, size=8, col=BONE),
        bx1=bx - 7, bx2=bx + 7, by1=by - 7, by2=by + 7,
        l_brk=label('connection lost  ·  part 76 / 200', bx - 6, by + 20, 10, MADDER),
        l_done=label('100 GB stored  ·  200 / 200 parts', TRACK_X1 - 16, TRACK_Y - 17,
                     10, VERD, 'end'),
        caps=cap_g, pips=pips)


if __name__ == '__main__':
    open('out/upload-path.svg', 'w', encoding='utf-8').write(build())
    print('drawn -> out/upload-path.svg')
