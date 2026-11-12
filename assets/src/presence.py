# -*- coding: utf-8 -*-
"""Presence Service: one user, three devices, and a phone that dies quietly.

Each device holds a WebSocket and sends a heartbeat every 30 seconds; each
heartbeat is knotted onto that device's thread. The phone goes into a tunnel
and stops without a close frame. The monitor sweeps every 10 seconds and
reaps the session once it has been silent for 60. The user stays online,
because online outranks everything and the web session is still online.
Then the web tab goes away, the effective status drops to away, and one
PUBLISH to Redis reaches watchers connected to another instance.

Numbers and rules are the service's own: 30 s heartbeat, 60 s timeout, a
10 s monitor loop, and the priority online > in_call > away > idle > offline.
"""
import card
from card import IVORY, SAFFRON, ORANGE

T0, SPAN = 1.5, 0.1               # real seconds at simulated 0, real per simulated


def T(s):
    return T0 + s * SPAN


HB = {                            # simulated heartbeat times
    'web': [30, 60, 90, 120, 155],
    'mobile': [30, 60],
    'desktop': [15, 45, 75, 105, 135, 165],
}
SILENT, REAPED, AWAY, END = 60, 130, 150, 180


def build(theme):
    k = card.Card(theme, 24.0)
    c = k.c
    b = k.body
    k.header('PRESENCE SERVICE', 'WHEN ONE OF YOUR DEVICES DIES QUIETLY',
             'FASTAPI  ·  REDIS  ·  GO PORT')

    # ---- diagram ---------------------------------------------------------------
    dev = {'web': (48, 100), 'mobile': (48, 158), 'desktop': (48, 216)}
    wires = {
        'web': [(160, 123), (186, 123), (186, 170), (212, 170)],
        'mobile': [(160, 181), (212, 181)],
        'desktop': [(160, 239), (186, 239), (186, 192), (212, 192)],
    }
    a_to_r = [(352, 181), (392, 181)]
    r_to_b = [(496, 170), (516, 170), (516, 123), (536, 123)]
    b_to_w = [(588, 146), (588, 216)]
    for w in wires.values():
        b.append(k.line(w))
    b += [k.line(a_to_r), k.line(r_to_b), k.line(b_to_w)]
    b.append(k.text('SET', 372, 173, 9, c['muted'], anchor='middle'))
    b.append(k.text('PUBLISH', 506, 112, 9, c['muted'], anchor='middle'))
    b.append(k.text('presence_update', 588, 280, 9, c['muted'], anchor='middle'))
    b.append(k.text('monitor · every 10 s · timeout 60 s', 302, 236, 9, c['muted'], anchor='middle'))
    b.append(k.text('websocket · heartbeat every 30 s', 48, 284, 9, c['dim']))
    for name, (x, y) in dev.items():
        b.append(k.node(x, y, 112, 46, name.upper(), None, size=12))
    b.append(k.node(212, 148, 140, 66, 'INSTANCE A', 'fastapi · websocket', True))
    b.append(k.node(392, 148, 104, 66, 'REDIS', 'sessions · pub/sub'))
    b.append(k.node(536, 100, 104, 46, 'INSTANCE B', None, size=12))
    b.append(k.node(536, 216, 104, 46, 'WATCHERS', None, size=12))

    tone = {'web': SAFFRON, 'mobile': SAFFRON, 'desktop': ORANGE}
    for d in dev:
        b.append(k.packets([(T(0), T(0) + 0.5)], wires[d], dur=0.5, cols=[IVORY]))
        for s in HB[d]:
            col = ORANGE if (d == 'web' and s > AWAY) else tone[d]
            b.append(k.packets([(T(s), T(s) + 0.45)], wires[d], dur=0.45, cols=[col]))
    b.append(k.packets([(T(0) + 0.5, T(0) + 1.0)], a_to_r, dur=0.4))
    # the phone's wire goes quiet, then is cut
    mob = wires['mobile']
    b.append(k.show([(T(SILENT + 10), T(REAPED))],
                    '<line x1="160" y1="181" x2="212" y2="181" stroke="%s" stroke-width="2" '
                    'stroke-dasharray="2 4"/>' % c['madder']))
    b.append(k.show_from(T(REAPED),
                         '<rect x="176" y="172" width="20" height="18" fill="%s"/>'
                         '<path d="M181,176 L191,186 M191,176 L181,186" stroke="%s" stroke-width="2.4" '
                         'stroke-linecap="round"/>' % (c['ink'], c['madder']), transient=True))
    # the fan-out when the user goes away
    b.append(k.packets([(T(AWAY) + 0.3, T(AWAY) + 0.8)], a_to_r, dur=0.4))
    b.append(k.packets([(T(AWAY) + 0.8, T(AWAY) + 1.3)], r_to_b, dur=0.45))
    b.append(k.packets([(T(AWAY) + 1.3, T(AWAY) + 1.8)], b_to_w, dur=0.4, n=3, cols=[ORANGE, SAFFRON, IVORY]))
    del mob

    # ---- log -------------------------------------------------------------------
    b.append(k.log(672, 96, 328, 214, [
        (T(0), 'web', 'connect · online', 'ack', None),
        (T(0) + 0.3, 'mobile', 'connect · online', 'ack', None),
        (T(0) + 0.6, 'desktop', 'connect · away', 'ack', None),
        (T(REAPED - 10), 'monitor', 'mobile silent 60 s · at the limit', '', None),
        (T(REAPED), 'monitor', 'mobile session timed out', '×', 'madder'),
        (T(REAPED) + 0.4, 'status', 'web online beats away', 'online', 'verd'),
        (T(AWAY), 'web', 'status_change · away', '', None),
        (T(AWAY) + 0.3, 'status', 'nothing online left', 'away', None),
        (T(AWAY) + 1.3, 'pub/sub', 'presence_update · online → away', '3', 'verd'),
    ], title='WIRE', who_w=60))

    # ---- counters --------------------------------------------------------------
    b.append(k.rule(326))
    sessions = [(T(0), 1), (T(0) + 0.3, 2), (T(0) + 0.6, 3), (T(REAPED), 2)]
    beats = sorted(T(s) for d in HB for s in HB[d])
    b.append(k.counter(48, 384, 'LIVE SESSIONS', sessions, 1, 2))
    b.append(k.counter(286, 384, 'HEARTBEATS', [(t, i + 1) for i, t in enumerate(beats)], 2, len(beats)))
    b.append(k.word(524, 381, 'EFFECTIVE STATUS', [
        (T(0), T(AWAY) + 0.3, 'ONLINE', 'verd'),
        (T(AWAY) + 0.3, k.reset0, 'AWAY', None)]))
    b.append(k.counter(762, 384, 'WATCHERS TOLD', [(T(AWAY) + 1.8, 3)], 1, 3))

    # ---- the threads -----------------------------------------------------------
    X0, X1 = 140, 1000

    def x(s):
        return X0 + s * (X1 - X0) / END

    lanes = {'web': 456, 'mobile': 490, 'desktop': 524}
    eff_y = 420
    b.append(k.text('EFFECTIVE', 48, eff_y + 3, 9, c['muted'], track=0.16))
    for d, y in lanes.items():
        b.append(k.text(d.upper(), 48, y + 3, 9, c['muted'], track=0.16))

    def reveal(x0, x1, y, h, t0, t1, inner):
        """Draw `inner`, uncovered from x0 to x1 between t0 and t1."""
        cid = k.name('r')
        k.defs.append('<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>'
                      % (cid, x0, y - h / 2, x1 - x0, h))
        name = k.name('m')
        k.css.append('@keyframes %s{0%%{transform:translateX(0)}%s{transform:translateX(0)}%s{transform:translateX(%.1fpx)}'
                     '%s{transform:translateX(%.1fpx)}%s{transform:translateX(0)}100%%{transform:translateX(0)}}'
                     % (name, k.pct(t0), k.pct(t1), x1 - x0, k.pct(k.reset1 - 0.01), x1 - x0, k.pct(k.reset1)))
        cover = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" class="a t" '
                 'style="animation:%s %ss linear infinite"/>' % (x0, y - h / 2, x1 - x0, h, c['ink'], name, k.D))
        return '<g clip-path="url(#%s)">%s%s</g>' % (cid, inner, cover)

    # bare warp first, then the threads as time reaches them
    for d, y in lanes.items():
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>' % (X0, y, X1, y, c['slot_line']))
    for d in ('web', 'desktop'):
        y = lanes[d]
        b.append(reveal(X0, X1, y, 8, T(0), T(END),
                        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>' % (X0, y, X1, y, c['muted'])))
    my = lanes['mobile']
    b.append(reveal(X0, x(SILENT), my, 8, T(0), T(SILENT),
                    '<line x1="%d" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="3"/>' % (X0, my, x(SILENT), my, c['muted'])))
    b.append(reveal(x(SILENT), x(REAPED), my, 8, T(SILENT), T(REAPED),
                    '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2" stroke-dasharray="3 4"/>'
                    % (x(SILENT), my, x(REAPED), my, c['madder'])))
    # the 60 s of silence the monitor waits out
    b.append(k.show_from(T(SILENT + 10),
                         k.line([(x(SILENT), my - 12), (x(SILENT), my - 16), (x(REAPED - 10), my - 16),
                                 (x(REAPED - 10), my - 12)], col=c['madder'], op='.8')
                         + k.text('60 s without a heartbeat', (x(SILENT) + x(REAPED - 10)) / 2, my - 20, 8.5,
                                  c['madder'], anchor='middle'), transient=True))
    b.append(k.show_from(T(REAPED),
                         '<path d="M%.1f,%d l10,10 M%.1f,%d l-10,10" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
                         % (x(REAPED) - 5, my - 5, x(REAPED) + 5, my - 5, c['madder'])
                         + k.text('reaped', x(REAPED) + 10, my + 4, 9, c['madder']), transient=True))

    # effective status ribbon
    b.append('<rect x="%d" y="%d" width="%d" height="8" rx="2" fill="%s"/>' % (X0, eff_y - 4, X1 - X0, c['slot']))
    b.append(reveal(X0, x(AWAY), eff_y, 10, T(0), T(AWAY),
                    '<rect x="%d" y="%d" width="%.1f" height="8" rx="2" fill="%s" fill-opacity=".75"/>'
                    % (X0, eff_y - 4, x(AWAY) - X0, c['verd'])))
    b.append(reveal(x(AWAY), X1, eff_y, 10, T(AWAY), T(END),
                    '<rect x="%.1f" y="%d" width="%.1f" height="8" rx="2" fill="%s"/>' % (x(AWAY), eff_y - 4, X1 - x(AWAY), ORANGE)))

    # legend
    for i, (lab, col) in enumerate((('online', SAFFRON), ('away', ORANGE), ('connect', IVORY))):
        lx = 1000 - 200 + i * 70
        b.append('<rect x="%d" y="398" width="9" height="9" rx="1.5" fill="%s"/>' % (lx, col))
        b.append(k.text(lab, lx + 14, 406, 8.5, c['muted']))
    # monitor sweeps
    for s in range(10, END + 1, 10):
        hot = s == REAPED
        b.append(k.show_from(T(s), '<circle cx="%.1f" cy="438" r="%s" fill="%s"/>'
                             % (x(s), 2.2 if hot else 1.4, c['madder'] if hot else c['dim'])))

    # knots: a connect, then a heartbeat every 30 s
    k.defs.append('<radialGradient id="kd" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".18"/>'
                  '<stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/>'
                  '</radialGradient><pattern id="k3" width="1" height="1" patternUnits="objectBoundingBox" '
                  'patternContentUnits="objectBoundingBox">%s</pattern>'
                  % ''.join('<rect x="%.3f" y="%.3f" width=".3" height=".3" rx=".08" fill="url(#kd)"/>'
                            % (0.02 + i / 3, 0.02 + j / 3) for i in range(3) for j in range(3)))

    def knot(s, y, col):
        kx = x(s)
        sq = ('<rect x="%.1f" y="%.1f" width="13" height="13" rx="2" fill="%s"/>'
              '<rect x="%.1f" y="%.1f" width="13" height="13" rx="2" fill="url(#k3)"/>'
              % (kx - 6.5, y - 6.5, col, kx - 6.5, y - 6.5))
        return k.show_from(T(s), sq)

    for d, y in lanes.items():
        b.append(knot(0, y, IVORY))
        for s in HB[d]:
            col = ORANGE if (d == 'web' and s > AWAY) else tone[d]
            b.append(knot(s, y, col))
    b.append(knot(AWAY, lanes['web'], ORANGE))

    # time axis and playhead
    for s in range(0, END + 1, 30):
        b.append(k.text('%d:%02d' % (s // 60, s % 60), x(s), 548, 8.5, c['dim'], anchor='middle'))
    k.css.append('@keyframes ph{0%%{transform:translateX(0)}%s{transform:translateX(0)}%s{transform:translateX(%dpx)}100%%{transform:translateX(%dpx)}}'
                 % (k.pct(T(0)), k.pct(T(END)), X1 - X0, X1 - X0))
    b.append(k.show([(T(0), T(END) + 0.4)],
                    '<line x1="%d" y1="410" x2="%d" y2="534" stroke="%s" stroke-width="1.5" class="a" '
                    'style="animation:ph %ss linear infinite"/>' % (X0, X0, c['madder'], k.D)))

    # ---- story -----------------------------------------------------------------
    k.story([
        (0.2, T(SILENT + 10), 'One user, three devices. Each holds a WebSocket and sends a heartbeat every 30 seconds.'),
        (T(SILENT + 10), T(REAPED), 'The phone drives into a tunnel. No close frame, no goodbye: its heartbeats just stop.'),
        (T(REAPED), T(AWAY), 'The monitor sweeps every 10 s and reaps it after 60 s of silence. Web is online, so the user is too.'),
        (T(AWAY), T(AWAY) + 1.3, 'The web tab goes away. With nothing online left, the user is now away.'),
        (T(AWAY) + 1.3, k.reset0, 'One PUBLISH to Redis, and watchers on another instance hear it. No instance holds everyone.'),
    ], [(T(0), 'CONNECT', False), (T(SILENT + 10), 'SILENT', False), (T(REAPED), 'REAPED', True),
        (T(AWAY), 'AWAY', False), (T(AWAY) + 1.3, 'FAN-OUT', False)])

    return k.render(
        'Presence Service: one user on web, mobile and desktop, each sending a heartbeat every 30 seconds. '
        'The phone stops without a close frame; the monitor, sweeping every 10 seconds, reaps its session after '
        '60 seconds of silence while the user stays online through the web session. When the web tab goes away '
        'the effective status becomes away, and one Redis PUBLISH reaches watchers on another instance.')


if __name__ == '__main__':
    card.write('presence', build)
