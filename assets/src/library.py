# -*- coding: utf-8 -*-
"""Digital Information System: one library, built twice.

The same upload runs through both builds side by side. The monolith is one
Django app behind Nginx, with a Celery worker indexing into Elasticsearch
through Redis. The split build is six services: a Node gateway, Go auth and
media, FastAPI content and search, a Node activity service, and RabbitMQ
carrying content.created from content to search.

Then one process falls over in each. In the monolith that is the whole site;
in the split, only uploads stop. The bill comes last, woven as a ledger:
deployables, languages, data stores, and how much goes down with one crash.

Every service, store and event is taken from the two repositories' READMEs.
"""
import card
from card import IVORY, SAFFRON, ORANGE, INDIGO

UP0 = 0.5                       # the upload starts
CRASH, BACK = 9.0, 13.5
BILL = 15.0
FEATURES = ['AUTH', 'BROWSE', 'SEARCH', 'UPLOAD', 'BOOKMARKS']


def build(theme):
    k = card.Card(theme, 24.0)
    c = k.c
    b = k.body
    k.header('DIGITAL INFORMATION SYSTEM', 'ONE LIBRARY, BUILT TWICE', '')

    # ---- the monolith ------------------------------------------------------------
    b.append(k.panel(48, 92, 460, 226, 'MONOLITH · ONE DJANGO APP'))
    NG, DJ, PG = (64, 124, 96, 50), (196, 120, 140, 58), (372, 124, 120, 50)
    RD, CE, ES = (64, 214, 96, 50), (196, 214, 140, 50), (372, 214, 120, 50)
    m_req = [(160, 149), (196, 149)]
    m_db = [(336, 149), (372, 149)]
    m_task = [(220, 178), (220, 196), (112, 196), (112, 214)]
    m_work = [(160, 239), (196, 239)]
    m_idx = [(336, 239), (372, 239)]
    for e in (m_req, m_db, m_task, m_work, m_idx):
        b.append(k.line(e))
    b += [k.node(*NG, 'NGINX', 'proxy', size=13), k.node(*DJ, 'DJANGO', 'gunicorn · the app', True),
          k.node(*PG, 'POSTGRES', 'one database', size=13), k.node(*RD, 'REDIS', 'broker', size=13),
          k.node(*CE, 'CELERY', 'same codebase', size=13), k.node(*ES, 'ELASTIC', 'search index', size=13)]
    t = UP0
    for e in ([(48, 149), (64, 149)], m_req, m_db, m_task, m_work, m_idx):
        b.append(k.packets([(t, t + 0.5)], e, dur=0.5, cols=[IVORY]))
        t += 0.55

    # ---- the split -----------------------------------------------------------------
    b.append(k.panel(532, 92, 468, 226, 'MICROSERVICES · SIX SERVICES'))
    GW = (548, 124, 84, 50)
    AU, CO, ME = (644, 124, 104, 50), (760, 124, 112, 50), (884, 124, 104, 50)
    AC, RB, SE = (644, 214, 104, 50), (760, 214, 112, 50), (884, 214, 104, 50)
    bus = [(590, 124), (590, 117), (936, 117), (936, 124)]
    b.append(k.line(bus))
    b.append(k.line([(696, 117), (696, 124)]))
    b.append(k.line([(816, 117), (816, 124)]))
    s_act = [(590, 174), (590, 239), (644, 239)]
    s_evt = [(816, 174), (816, 214)]
    s_idx = [(872, 239), (884, 239)]
    for e in (s_act, s_evt, s_idx):
        b.append(k.line(e))
    b.append(k.text('content.created', 822, 198, 8.5, c['muted']))
    b += [k.node(*GW, 'GATEWAY', 'node · jwt', True, size=12, sub_size=8),
          k.node(*AU, 'AUTH', 'go · postgres', size=13, sub_size=8),
          k.node(*CO, 'CONTENT', 'fastapi · postgres', size=13, sub_size=8),
          k.node(*ME, 'MEDIA', 'go · minio', size=13, sub_size=8),
          k.node(*AC, 'ACTIVITY', 'node · mongo', size=13, sub_size=8),
          k.node(*RB, 'RABBITMQ', 'events', size=13, sub_size=8),
          k.node(*SE, 'SEARCH', 'fastapi · elastic', size=13, sub_size=8)]
    s_media = [(590, 124), (590, 117), (936, 117), (936, 124)]
    s_content = [(590, 124), (590, 117), (816, 117), (816, 124)]
    t = UP0
    for e in ([(532, 149), (548, 149)], s_media, s_content, s_evt, s_idx):
        b.append(k.packets([(t, t + 0.6)], e, dur=0.6, cols=[IVORY]))
        t += 0.65

    # ---- the crash ---------------------------------------------------------------
    def down(box):
        x, y, w, h = box
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" fill-opacity=".18" '
                'stroke="%s" stroke-width="1.5"/>'
                '<path d="M%.1f,%.1f l10,10 M%.1f,%.1f l-10,10" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>'
                % (x, y, w, h, c['madder'], c['madder'], x + w - 16, y + 6, x + w - 6, y + 6, c['madder']))
    b.append(k.show([(CRASH, BACK)], down(DJ)))
    b.append(k.show([(CRASH, BACK)], down(ME)))

    # feature lights under each build
    def chips(x0, dead):
        out, cx = [], x0
        for f in FEATURES:
            w = k.width(f, 8.5, track=0.14) + 26
            out.append('<rect x="%.1f" y="282" width="%.1f" height="20" rx="10" fill="none" stroke="%s" stroke-opacity=".2"/>'
                       % (cx, w, c['rule']))
            out.append('<circle cx="%.1f" cy="292" r="3.5" fill="%s"/>' % (cx + 11, c['verd']))
            if f in dead:
                out.append(k.show([(CRASH, BACK)], '<circle cx="%.1f" cy="292" r="3.5" fill="%s"/>' % (cx + 11, c['madder'])))
            out.append(k.text(f, cx + 19, 295, 8.5, c['muted'], track=0.14))
            cx += w + 6
        return ''.join(out)
    b.append(chips(64, FEATURES))
    b.append(chips(548, ['UPLOAD']))

    # ---- counters ----------------------------------------------------------------
    b.append(k.rule(334))
    b.append(k.counter(48, 390, 'MONOLITH · FEATURES UP', [(0.0, 5), (CRASH, 0), (BACK, 5)], 1, 5, '/ 5'))
    b.append(k.counter(286, 390, 'MICROSERVICES · FEATURES UP', [(0.0, 5), (CRASH, 4), (BACK, 5)], 1, 5, '/ 5'))
    b.append(k.word(524, 387, 'NEW PAPER · MONOLITH', [
        (UP0 + 1.4, UP0 + 3.3, 'SAVED', None), (UP0 + 3.3, k.reset0, 'SEARCHABLE', 'verd')]))
    b.append(k.word(762, 387, 'NEW PAPER · MICROSERVICES', [
        (UP0 + 2.0, UP0 + 3.2, 'SAVED', None), (UP0 + 3.2, k.reset0, 'SEARCHABLE', 'verd')]))

    # ---- the ledger, woven -------------------------------------------------------
    LY = 430
    b.append(k.text('THE COST OF THE SPLIT', 48, 418, 9, c['muted'], track=0.14))
    MX, SX = 420, 700
    b.append(k.text('MONOLITH', MX, 418, 9, c['dim'], track=0.14))
    b.append(k.text('MICROSERVICES', SX, 418, 9, c['dim'], track=0.14))
    ledger = [
        ('deployables', 1, 6, BILL),
        ('languages', 1, 3, BILL + 1.0),
        ('data stores to run', 3, 6, BILL + 2.0),
        ('features lost to one crash', 5, 1, CRASH + 0.3),
    ]
    pal_m = [SAFFRON, ORANGE]
    pal_s = [IVORY, INDIGO]
    for i, (label, m, s, t0) in enumerate(ledger):
        y = LY + 14 + i * 32
        b.append(k.text(label, 48, y + 4, 11, c['text'], card.BODY, 0))
        b.append('<line x1="48" y1="%d" x2="1000" y2="%d" stroke="%s" stroke-opacity=".07"/>' % (y + 16, y + 16, c['rule']))
        for j in range(6):
            b.append('<rect x="%.1f" y="%.1f" width="20" height="20" rx="2" fill="%s" stroke="%s"/>'
                     % (MX + j * 24, y - 10, c['slot'], c['slot_line']))
            b.append('<rect x="%.1f" y="%.1f" width="20" height="20" rx="2" fill="%s" stroke="%s"/>'
                     % (SX + j * 24, y - 10, c['slot'], c['slot_line']))
        for j in range(m):
            b.append(k.show_from(t0 + j * 0.12, k.knot(MX + 10 + j * 24, y, 20,
                                                         c['madder'] if i == 3 else pal_m[j % 2])))
        for j in range(s):
            b.append(k.show_from(t0 + 0.3 + j * 0.12, k.knot(SX + 10 + j * 24, y, 20,
                                                               c['madder'] if i == 3 else pal_s[j % 2])))
        b.append(k.show_from(t0 + 0.2, k.text(str(m), MX + 6 * 24 + 10, y + 5, 15, c['text'], card.DISP)))
        b.append(k.show_from(t0 + 0.5 + s * 0.12, k.text(str(s), SX + 6 * 24 + 10, y + 5, 15, c['text'], card.DISP)))

    # ---- story -------------------------------------------------------------------
    k.story([
        (0.2, UP0 + 3.6, 'A librarian uploads a dissertation. Both builds save it, then index it for search in the background.'),
        (UP0 + 3.6, CRASH, 'One Django app and a Celery worker, against four services and a RabbitMQ event.'),
        (CRASH, BACK, 'Then one process dies. In the monolith that is the whole site. In the split, only uploads stop.'),
        (BACK, BILL + 2.6, 'Isolation is not free: six deployables, three languages, six data stores to run and keep in step.'),
        (BILL + 2.6, k.reset0, 'Building it both ways is how I learned where that line is worth drawing.'),
    ], [(UP0, 'UPLOAD', False), (UP0 + 2.2, 'INDEX', False), (CRASH, 'CRASH', True),
        (BACK, 'RECOVER', False), (BILL, 'COST', False)])

    return k.render(
        'Digital Information System, built twice. The same dissertation upload runs through a Django monolith with a '
        'Celery worker and through six services linked by a RabbitMQ content.created event. When one process dies, the '
        'monolith loses all five features and the split build loses only uploads. The cost of the split: six deployables '
        'instead of one, three languages instead of one, six data stores instead of three.')


if __name__ == '__main__':
    card.write('library', build)
