"""Text -> SVG path outlines, so the banner renders identically everywhere."""
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

_cache = {}

def load(path, **axes):
    key = (path, tuple(sorted(axes.items())))
    if key in _cache:
        return _cache[key]
    f = TTFont(path)
    if axes:
        f = instancer.instantiateVariableFont(f, axes, inplace=False, updateFontNames=False)
    _cache[key] = f
    return f

def typeset(font, text, size, x, y, tracking=0.0):
    """Return (path_d, advance_width). tracking is in em units. y = baseline."""
    upem = font['head'].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font['hmtx']
    track_units = tracking * upem
    parts, pen_x = [], 0.0
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            gname = cmap.get(ord(' '))
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}")
        # flip Y (font space is up-positive, SVG is down-positive)
        t = Transform(scale, 0, 0, -scale, x + pen_x * scale, y)
        gs[gname].draw(TransformPen(pen, t))
        d = pen.getCommands()
        if d:
            parts.append(d)
        pen_x += hmtx[gname][0] + track_units
    return " ".join(parts), (pen_x - track_units) * scale

def width(font, text, size, tracking=0.0):
    return typeset(font, text, size, 0, 0, tracking)[1]
