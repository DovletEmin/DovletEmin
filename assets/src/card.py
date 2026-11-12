# -*- coding: utf-8 -*-
"""Shared parts for the animated project cards.

Every card tells one story on a loop: a header, a diagram, a live log,
odometer counters, a woven strip that carries the story, and a caption with
a timeline. Text is outlined once per glyph into <defs> and placed with
<use>, so nothing depends on installed fonts and files stay small. Each card
is written in a dark and a light version.
"""
import os
import typeset as T

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
DISP = T.load(os.path.join(FONTS, 'Archivo-var.ttf'), wght=760, wdth=115)
BODY = T.load(os.path.join(FONTS, 'Archivo-var.ttf'), wght=450, wdth=100)
MONO = T.load(os.path.join(FONTS, 'IBMPlexMono-Medium.ttf'))

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


class Card:
    def __init__(self, theme, duration):
        self.theme = theme
        self.c = THEMES[theme]
        self.D = duration
        self.reset0, self.reset1 = duration - 0.7, duration - 0.15
        self.css, self.body, self.defs = [], [], []
        self.glyphs, self.font_ids = {}, {}
        self.uid = 0

    # ---- time ----------------------------------------------------------------
    def pct(self, t):
        return '%.3f%%' % (max(0.0, min(self.D, t)) / self.D * 100.0)

    def name(self, prefix='a'):
        self.uid += 1
        return '%s%d' % (prefix, self.uid)

    def gate(self, windows, fade=0.2, peak=1, name=None):
        """Keyframes that show something during each (start, end) window."""
        name = name or self.name('g')
        marks = [(0.0, 0)]
        for a, b in windows:
            marks += [(max(0.001, a - fade), 0), (a, peak), (b, peak),
                      (min(self.D - 0.001, b + fade), 0)]
        marks.append((self.D, 0))
        marks.sort(key=lambda m: m[0])
        self.css.append('@keyframes %s{%s}' % (
            name, ''.join('%s{opacity:%s}' % (self.pct(t), v) for t, v in marks)))
        return name

    def keep(self, on, fade=0.15):
        """Shown from `on` until the loop resets."""
        return self.gate([(on, self.reset0)], fade)

    def anim(self, name, inner, transient=True, extra=''):
        """Wrap content in a group driven by a loop-long keyframe set."""
        return '<g class="a%s" style="animation:%s %ss linear infinite"%s>%s</g>' % (
            ' t' if transient else '', name, self.D, extra, inner)

    def show(self, windows, inner, transient=True, fade=0.2):
        return self.anim(self.gate(windows, fade), inner, transient)

    def show_from(self, on, inner, transient=False, fade=0.15):
        return self.anim(self.keep(on, fade), inner, transient)

    def travel(self, pts):
        name = self.name('k')
        lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(pts, pts[1:])]
        total, acc, marks = sum(lens) or 1.0, 0.0, []
        for i, (x, y) in enumerate(pts):
            marks.append((acc / total * 100.0, x, y))
            if i < len(lens):
                acc += lens[i]
        self.css.append('@keyframes %s{%s}' % (name, ''.join(
            '%.2f%%{transform:translate(%.1fpx,%.1fpx)}' % m for m in marks)))
        return name

    def packets(self, windows, pts, n=1, dur=0.8, size=6, cols=None):
        """Small squares running along a polyline while a window is open."""
        mv = self.travel(pts)
        cols = cols or [self.c['madder']]
        inner = ''.join(
            '<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="1" fill="%s" class="a" '
            'style="animation:%s %ss linear infinite;animation-delay:-%.2fs"/>'
            % (-size / 2, -size / 2, size, size, cols[i % len(cols)], mv, dur, i * dur / n)
            for i in range(n))
        return self.show(windows, inner, fade=0.1)

    # ---- type ----------------------------------------------------------------
    def glyph(self, font, size, ch):
        key = (id(font), size, ch)
        if key not in self.glyphs:
            d, adv = T.typeset(font, ch, size, 0, 0)
            if id(font) not in self.font_ids:
                self.font_ids[id(font)] = 'xyz'[len(self.font_ids)]
            fid = self.font_ids[id(font)]
            self.glyphs[key] = ('%s%d' % (fid, len(self.glyphs)), d, adv)
        return self.glyphs[key]

    def width(self, s, size, font=MONO, track=0.12):
        if not s:
            return 0.0
        return sum(self.glyph(font, size, ch)[2] for ch in s) + track * size * (len(s) - 1)

    def text(self, s, x, y, size, col, font=MONO, track=0.12, anchor='start'):
        w = self.width(s, size, font, track)
        if anchor == 'end':
            x -= w
        elif anchor == 'middle':
            x -= w / 2
        out, pen = [], x
        for ch in s:
            gid, d, adv = self.glyph(font, size, ch)
            if d:
                out.append('<use href="#%s" x="%.1f"/>' % (gid, pen))
            pen += adv + track * size
        return '<g fill="%s" transform="translate(0 %.1f)">%s</g>' % (col, y, ''.join(out))

    # ---- shapes --------------------------------------------------------------
    def rule(self, y, x0=48, x1=1000, op='.12'):
        return '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-opacity="%s"/>' % (
            x0, y, x1, y, self.c['rule'], op)

    def line(self, pts, dash=False, op='.28', width=1, col=None):
        return ('<path d="M%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s"%s/>'
                % (' L'.join('%.1f,%.1f' % p for p in pts), col or self.c['rule'], op, width,
                   ' stroke-dasharray="3 3"' if dash else ''))

    def panel(self, x, y, w, h, title=None):
        out = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-opacity=".16"/>' % (
            x, y, w, h, self.c['surf'], self.c['rule'])
        if title:
            out += self.text(title, x + 16, y + 20, 9, self.c['dim'], track=0.2)
        return out

    def node(self, x, y, w, h, name, sub, accent=False, size=15, sub_size=9):
        c = self.c
        out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-opacity="%s"/>'
               % (x, y, w, h, c['surf'], c['madder'] if accent else c['rule'], '.7' if accent else '.16')]
        if accent:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="3" rx="1.5" fill="%s"/>' % (x, y, w, c['madder']))
        if sub:
            out.append(self.text(name, x + w / 2, y + h / 2 + 1, size, c['text'], DISP, 0.05, 'middle'))
            out.append(self.text(sub, x + w / 2, y + h / 2 + 18, sub_size, c['muted'], anchor='middle'))
        else:
            out.append(self.text(name, x + w / 2, y + h / 2 + size * 0.36, size, c['text'], DISP, 0.05, 'middle'))
        return ''.join(out)

    def header(self, title, subtitle, tag):
        c = self.c
        self.body.append(self.text(title, 48, 54, 26, c['text'], DISP, 0.04))
        tw = self.width(title, 26, DISP, 0.04)
        self.body.append(self.text(subtitle, 48 + tw + 22, 53, 11, c['muted'], track=0.16))
        if tag:
            self.body.append(self.text(tag, 1000, 53, 10, c['dim'], track=0.16, anchor='end'))
        self.body.append(self.rule(76))

    # ---- log -----------------------------------------------------------------
    def log(self, x, y, w, h, lines, title='LOG', who_w=54):
        """lines: (time, who, what, result, tone). Each stays once written."""
        c = self.c
        out = [self.panel(x, y, w, h, title)]
        for i, (t, who, what, res, tone) in enumerate(lines):
            ly = y + 42 + i * 18
            col = c[tone] if tone else c['text']
            s = self.text(who, x + 16, ly, 9, c['dim'], track=0.06)
            s += self.text(what, x + 16 + who_w, ly, 9.5, col, track=0.06)
            if res:
                s += self.text(res, x + w - 14, ly, 9.5, col, track=0.06, anchor='end')
            out.append(self.show_from(t, s))
        return ''.join(out)

    # ---- odometers -----------------------------------------------------------
    def digits(self, size):
        key = 'dg%d' % size
        if not any(d.startswith('<path id="%s0"' % key) for d in self.defs):
            for k in range(10):
                self.defs.append('<path id="%s%d" d="%s"/>' % (key, k, T.typeset(MONO, str(k), size, 0, 0)[0]))
        return key

    def wheel(self, x, y, events, col, final, size=30, pitch=38):
        """One digit that jumps at each (time, digit) event."""
        name = self.name('w')
        key = self.digits(size)
        adv = self.width('0', size, track=0)
        marks, cur = [(0.0, 0)], 0
        for t, dg in events:
            if dg != cur:
                marks += [(t - 0.004, cur), (t, dg)]
                cur = dg
        marks += [(self.reset1 - 0.004, cur), (self.reset1, 0), (self.D, 0)]
        self.css.append('@keyframes %s{%s}' % (name, ''.join(
            '%s{transform:translateY(%dpx)}' % (self.pct(t), -dg * pitch) for t, dg in marks)))
        top = y - size * 0.78
        self.defs.append('<clipPath id="c%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%d"/></clipPath>'
                         % (name, x, top - 2, adv + 1, pitch - 4))
        return ('<g clip-path="url(#c%s)"><g class="a" style="animation:%s %ss linear infinite;'
                'transform:translateY(%dpx)" fill="%s">%s</g></g>'
                % (name, name, self.D, -final * pitch, col,
                   ''.join('<use href="#%s%d" x="%.1f" y="%.1f"/>' % (key, k, x, y + k * pitch)
                           for k in range(10)))), adv

    def counter(self, x, y, label, value_events, places, final, suffix='', col=None, size=30):
        """A number of `places` digits driven by (time, value) events."""
        c = self.c
        out = [self.text(label, x, y - 38, 9, c['muted'], track=0.16)]
        wx = x
        for p in range(places - 1, -1, -1):
            ev = [(t, (v // 10 ** p) % 10) for t, v in value_events]
            w, adv = self.wheel(wx, y, ev, col or c['text'], (final // 10 ** p) % 10, size)
            out.append(w)
            wx += adv
        if suffix:
            out.append(self.text(suffix, wx + 4, y, 15, c['muted'], track=0.06))
        return ''.join(out)

    def word(self, x, y, label, states, size=22):
        """A counter-like slot whose value is a word: states = (start, end, text, tone)."""
        c = self.c
        out = [self.text(label, x, y - 38, 9, c['muted'], track=0.16)]
        for a, b, s, tone in states:
            last = b >= self.reset0
            out.append(self.show([(a, b)], self.text(s, x, y, size, c[tone] if tone else c['text'], DISP, 0.04),
                                 transient=not last, fade=0.12))
        return ''.join(out)

    # ---- the woven texture ---------------------------------------------------
    def knot_texture(self, x, y, step, cell, w, h, knots=3):
        kn = (cell - 1.0) / knots
        pid = self.name('p')
        self.defs.append('<radialGradient id="%sd" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff" '
                         'stop-opacity=".16"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>'
                         '<stop offset="1" stop-color="#000" stop-opacity=".38"/></radialGradient>' % pid)
        self.defs.append('<pattern id="%s" x="%.1f" y="%.1f" width="%.2f" height="%.2f" patternUnits="userSpaceOnUse">%s</pattern>'
                         % (pid, x, y, step, step, ''.join(
                             '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.1f" fill="url(#%sd)"/>'
                             % (0.5 + i * kn, 0.5 + j * kn, kn - 0.6, kn - 0.6, kn * 0.22, pid)
                             for i in range(knots) for j in range(knots))))
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#%s)"/>' % (x, y, w, h, pid)

    def knot(self, x, y, size, col, rx=2):
        """One woven square, three knots by three, centred on (x, y)."""
        if not any('id="k3"' in d for d in self.defs):
            self.defs.append(
                '<radialGradient id="kd" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".18"/>'
                '<stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/>'
                '</radialGradient><pattern id="k3" width="1" height="1" patternUnits="objectBoundingBox" '
                'patternContentUnits="objectBoundingBox">%s</pattern>'
                % ''.join('<rect x="%.3f" y="%.3f" width=".3" height=".3" rx=".08" fill="url(#kd)"/>'
                          % (0.02 + i / 3, 0.02 + j / 3) for i in range(3) for j in range(3)))
        h = size / 2
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"/>'
                '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="url(#k3)"/>'
                % (x - h, y - h, size, size, rx, col, x - h, y - h, size, size, rx))

    # ---- caption and timeline ------------------------------------------------
    def story(self, caps, marks):
        """caps: (start, end, sentence); marks: (time, LABEL, alarm)."""
        c = self.c
        for i, (a, b, s) in enumerate(caps):
            last = i == len(caps) - 1
            inner = self.text('0%d' % (i + 1), 48, 586, 11, c['madder']) + self.text(s, 80, 586, 15, c['text'], BODY, 0)
            self.body.append(self.show([(a, b)], inner, transient=not last))
        self.body.append(self.rule(608, op='.18'))
        for t, s, alarm in marks:
            x = 48 + t / self.D * 952
            self.body.append('<line x1="%.1f" y1="604" x2="%.1f" y2="612" stroke="%s" stroke-opacity=".35"/>'
                             % (x, x, c['rule']))
            self.body.append(self.text(s, x + 4, 626, 8.5, c['madder'] if alarm else c['dim'], track=0.16))
        self.css.append('@keyframes play{from{transform:translateX(0)}to{transform:translateX(952px)}}')
        self.body.append('<circle cx="48" cy="608" r="4" fill="%s" class="a t" style="animation:play %ss linear infinite"/>'
                         % (c['madder'], self.D))

    # ---- output --------------------------------------------------------------
    def render(self, label):
        self.css.append('.a{animation-iteration-count:infinite}')
        self.css.append('@media (prefers-reduced-motion:reduce){.a{animation:none!important}.t{display:none}}')
        glyphs = ''.join('<path id="%s" d="%s"/>' % (gid, d) for gid, d, _ in self.glyphs.values() if d)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
                'aria-label="%s"><title>%s</title><style>%s</style><defs>%s%s</defs>'
                '<rect width="%d" height="%d" rx="6" fill="%s"/>%s</svg>\n'
                % (W, H, W, H, label, label, ''.join(self.css), ''.join(self.defs), glyphs,
                   W, H, self.c['ink'], ''.join(self.body)))


def write(name, build):
    os.makedirs('out', exist_ok=True)
    for theme in THEMES:
        path = 'out/%s-%s.svg' % (name, theme)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(build(theme))
        print('drawn ->', path)
