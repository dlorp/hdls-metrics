#!/usr/bin/env python3
"""
HDLS Banner Generator v3 — demoscene title card.
Parametric trefoil knot (torus knot p=2,q=3) with proper over/under crossings.
Smooth wave deformation via low-frequency sinusoidal + subtle fBM.

Brand: #0E0B02 background, #FFB800 amber primary.
All text as filled SVG paths — zero font dependency for GitHub SVG renderer.
Outputs: hdls-banner-v3.png (static), hdls-banner-animated.gif (30 frames, 15fps)
"""

import json
import math
import os
import random
import struct
import subprocess
import sys
import tempfile

# Brand colors
AMBER = "#FFB800"
AMBER_DIM = "#7A5200"
AMBER_MID = "#C47A00"
BG = "#0E0B02"

W, H = 1280, 320
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON39 = "/usr/bin/python3"  # has fonttools + PIL


# ── HDLS from real VT323 font glyphs ────────────────────────────────
def _load_glyphs():
    """Load VT323 glyph paths extracted from the real font."""
    glyph_file = os.path.join(SCRIPT_DIR, "hdls_glyphs.json")
    if os.path.exists(glyph_file):
        with open(glyph_file) as f:
            return json.load(f)
    # Fallback: extract from font
    font_path = "/tmp/VT323.ttf"
    if not os.path.exists(font_path):
        import urllib.request
        url = "https://github.com/google/fonts/raw/main/ofl/vt323/VT323-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
    result = subprocess.run(
        [PYTHON39, "-c", f"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import json
font = TTFont('{font_path}')
glyf = font['glyf']
hmtx = font['hmtx']
cmap = font.getBestCmap()
letters = {{}}
for char in 'HDLS':
    gn = cmap[ord(char)]
    pen = SVGPathPen(font.getGlyphSet())
    font.getGlyphSet()[gn].draw(pen)
    letters[char] = {{'path': pen.getCommands(), 'width': hmtx[gn][0]}}
json.dump(letters, open('{glyph_file}', 'w'))
"""],
        capture_output=True, text=True
    )
    with open(glyph_file) as f:
        return json.load(f)


_GLYPHS = None

def hdls_text(ox, oy, height=110):
    """Render HDLS using real VT323 font glyph outlines as SVG paths."""
    global _GLYPHS
    if _GLYPHS is None:
        _GLYPHS = _load_glyphs()

    # VT323 glyphs are in a ~400x400 coordinate space, upside down (y inverted)
    # Scale factor: target height / font units
    font_height = 400  # VT323 units per em
    scale = height / font_height
    gap = 12 * scale  # spacing between letters

    parts = []
    x = ox
    for char in "HDLS":
        g = _GLYPHS[char]
        # Font paths are in font coordinates (y up). SVG has y down.
        # We need to flip Y and scale + translate.
        path = g["path"]
        # Replace M and L commands: flip Y coordinate
        # Font: y goes up from baseline. SVG: y goes down.
        # Transform: new_y = oy + height - (old_y * scale)
        # Simple approach: wrap in a group with transform
        tx = x
        ty = oy + height  # baseline
        parts.append(
            f'<g transform="translate({tx:.1f},{ty:.1f}) scale({scale:.4f},{-scale:.4f})">'
            f'<path d="{path}" fill="{AMBER}"/></g>'
        )
        x += g["width"] * scale + gap

    return "\n  ".join(parts)


# ── Perlin noise (for subtle fBM) ──────────────────────────────────
def _build_perm():
    rng = random.Random(42)
    p = list(range(256))
    rng.shuffle(p)
    return p * 2

_perm = _build_perm()

def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def _lerp(a, b, t):
    return a + t * (b - a)

def _grad(h, x, y):
    h = h & 3
    if h == 0: return x + y
    elif h == 1: return -x + y
    elif h == 2: return x - y
    else: return -x - y

def perlin2d(x, y):
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = _fade(xf)
    v = _fade(yf)
    p = _perm
    aa = p[p[xi] + yi]
    ab = p[p[xi] + yi + 1]
    ba = p[p[xi + 1] + yi]
    bb = p[p[xi + 1] + yi + 1]
    return _lerp(
        _lerp(_grad(aa, xf, yf), _grad(ba, xf - 1, yf), u),
        _lerp(_grad(ab, xf, yf - 1), _grad(bb, xf - 1, yf - 1), u),
        v
    )

def fbm(x, y, octaves=2, lacunarity=2.0, gain=0.5):
    val = 0.0
    max_val = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(octaves):
        val += amp * perlin2d(x * freq, y * freq)
        max_val += amp
        amp *= gain
        freq *= lacunarity
    return val / max_val if max_val else 0


# ── Trefoil knot ────────────────────────────────────────────────────
KNOT_STEPS = 400
R = 70
r_knot = 25
KNOT_CX = 1020
KNOT_CY = 160

# 3D rotation to show all 3 crossings
ax_rot = math.radians(30)
ay_rot = math.radians(20)

def rotate3d(x, y, z, ax, ay):
    y1 = y * math.cos(ax) - z * math.sin(ax)
    z1 = y * math.sin(ax) + z * math.cos(ax)
    x2 = x * math.cos(ay) + z1 * math.sin(ay)
    z2 = -x * math.sin(ay) + z1 * math.cos(ay)
    return x2, y1, z2

def raw_trefoil(t):
    x = (R + r_knot * math.cos(3 * t)) * math.cos(2 * t)
    y = (R + r_knot * math.cos(3 * t)) * math.sin(2 * t)
    z = r_knot * math.sin(3 * t)
    return x, y, z

def compute_trefoil(time_offset=0.0, warp_amp=0.0):
    pts3d_raw = []
    pts2d = []
    for i in range(KNOT_STEPS + 1):
        t = 2 * math.pi * i / KNOT_STEPS
        x, y, z = raw_trefoil(t)

        # Smooth sinusoidal wave deformation (dominant motion)
        if warp_amp > 0:
            wave_x = math.sin(t * 2 + time_offset) * warp_amp * 0.6
            wave_y = math.cos(t * 3 + time_offset * 0.7) * warp_amp * 0.4
            # Subtle fBM noise on top (low frequency = smooth)
            nx = fbm(x * 0.015 + time_offset * 0.2, y * 0.015, octaves=2)
            ny = fbm(x * 0.015, y * 0.015 + time_offset * 0.2, octaves=2)
            x += wave_x + nx * warp_amp * 0.3
            y += wave_y + ny * warp_amp * 0.3

        xr, yr, zr = rotate3d(x, y, z, ax_rot, ay_rot)
        pts3d_raw.append((xr, yr, zr))
        pts2d.append((KNOT_CX + xr, KNOT_CY + yr, zr))

    return pts2d, pts3d_raw


# ── Crossing detection ──────────────────────────────────────────────
def seg_intersect(p1, p2, p3, p4):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0.02 < t < 0.98 and 0.02 < u < 0.98:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1), t, u)
    return None


def build_knot_segments(pts2d, pts3d, gap=0.035):
    crossings = []
    N = len(pts2d) - 1
    for i in range(N):
        for j in range(i + 3, N):
            result = seg_intersect(pts2d[i], pts2d[i + 1], pts2d[j], pts2d[j + 1])
            if result:
                ix, iy, t_param, u_param = result
                z_i = pts3d[i][2] + t_param * (pts3d[i + 1][2] - pts3d[i][2])
                z_j = pts3d[j][2] + u_param * (pts3d[j + 1][2] - pts3d[j][2])
                over = 'i' if z_i > z_j else 'j'
                crossings.append({'i': i, 't': t_param, 'j': j, 'u': u_param, 'over': over})

    under_breaks = []
    for cr in crossings:
        if cr['over'] == 'j':
            under_breaks.append((cr['i'], cr['t']))
        else:
            under_breaks.append((cr['j'], cr['u']))
    under_breaks.sort()

    break_dict = {}
    for seg_idx, param in under_breaks:
        break_dict[seg_idx] = param

    segments = []
    current = [(pts2d[0][0], pts2d[0][1])]

    for i in range(len(pts2d) - 1):
        p = (pts2d[i][0], pts2d[i][1])
        p_next = (pts2d[i + 1][0], pts2d[i + 1][1])

        if i in break_dict:
            param = break_dict[i]
            t_before = max(0, param - gap)
            t_after = min(1, param + gap)
            bx_before = (p[0] + t_before * (p_next[0] - p[0]),
                         p[1] + t_before * (p_next[1] - p[1]))
            bx_after = (p[0] + t_after * (p_next[0] - p[0]),
                        p[1] + t_after * (p_next[1] - p[1]))
            current.append(bx_before)
            segments.append(current)
            current = [bx_after]
        else:
            current.append(p_next)

    if current:
        segments.append(current)

    return segments, crossings


def segments_to_paths(segments):
    paths = []
    for seg in segments:
        if len(seg) < 2:
            continue
        d = f"M{seg[0][0]:.1f},{seg[0][1]:.1f}"
        for pt in seg[1:]:
            d += f"L{pt[0]:.1f},{pt[1]:.1f}"
        paths.append(d)
    return paths


# ── SVG assembly ────────────────────────────────────────────────────
def build_svg(time_offset=0.0, warp_amp=0.0):
    pts2d, pts3d = compute_trefoil(time_offset, warp_amp)
    segments, crossings = build_knot_segments(pts2d, pts3d)
    knot_paths = segments_to_paths(segments)

    svg = []
    svg.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    svg.append(f'<defs>')

    # Glow filters
    svg.append(f'''  <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur stdDeviation="1.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>''')
    svg.append(f'''  <filter id="knotglow" x="-15%" y="-15%" width="130%" height="130%">
    <feGaussianBlur stdDeviation="2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>''')

    # Scanlines
    svg.append(f'''  <pattern id="scanlines" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect x="0" y="2" width="4" height="2" fill="#0E0B02" opacity="0.12"/>
  </pattern>''')

    # Vignette
    svg.append(f'''  <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
    <stop offset="55%" stop-color="#0E0B02" stop-opacity="0"/>
    <stop offset="100%" stop-color="#0E0B02" stop-opacity="0.6"/>
  </radialGradient>''')

    svg.append(f'</defs>')

    # Background
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')

    # ── Trefoil knot: 3-layer stroke ──
    svg.append(f'<g filter="url(#knotglow)">')
    for d in knot_paths:
        svg.append(f'<path d="{d}" fill="none" stroke="#3d2400" stroke-width="6" stroke-linecap="round" opacity="0.5"/>')
    for d in knot_paths:
        svg.append(f'<path d="{d}" fill="none" stroke="{AMBER_MID}" stroke-width="2.5" stroke-linecap="round" opacity="0.95"/>')
    for d in knot_paths:
        svg.append(f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="0.8" stroke-linecap="round" opacity="0.45"/>')
    svg.append(f'</g>')

    # ── HDLS text (real VT323 glyphs as paths) ──
    svg.append(hdls_text(80, 85, height=110))

    # ── Tagline (bitmap font) ──
    svg.append(f'''<text x="84" y="212"
      font-family="'Courier New', monospace"
      font-size="14"
      fill="#CC8800" letter-spacing="3" opacity="0.85">METRICS // SIGNAL CHAIN</text>''')

    # Decorative line
    svg.append(f'<line x1="80" y1="228" x2="480" y2="228" stroke="{AMBER_MID}" stroke-width="0.5" opacity="0.35"/>')

    # BBS annotations
    svg.append(f'''<text x="80" y="248"
      font-family="'Courier New', monospace"
      font-size="10" fill="{AMBER_DIM}" letter-spacing="1" opacity="0.5">// trefoil_knot // parametric // wave_deform</text>''')
    svg.append(f'''<text x="80" y="264"
      font-family="'Courier New', monospace"
      font-size="10" fill="{AMBER_DIM}" letter-spacing="1" opacity="0.4">/// distribute_impurity_evenly</text>''')

    # ── Corner brackets ──
    tick = AMBER_DIM
    tw = 14
    svg.append(f'<polyline points="10,10 10,{10+tw} {10+tw},10" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>')
    svg.append(f'<polyline points="{W-10},10 {W-10},{10+tw} {W-10-tw},10" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>')
    svg.append(f'<polyline points="10,{H-10} 10,{H-10-tw} {10+tw},{H-10}" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>')
    svg.append(f'<polyline points="{W-10},{H-10} {W-10},{H-10-tw} {W-10-tw},{H-10}" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>')

    # Corner annotation
    svg.append(f'''<text x="{W-20}" y="{H-18}"
      font-family="'Courier New', monospace"
      font-size="9" fill="{AMBER_DIM}" text-anchor="end" opacity="0.5">1280x320 // TREFOIL // v3</text>''')

    # Scanline + vignette overlay
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#scanlines)"/>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#vignette)"/>')

    svg.append(f'</svg>')
    return '\n'.join(svg)


# ── Main ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    out_dir = SCRIPT_DIR

    # Static banner
    svg_content = build_svg(time_offset=0.0, warp_amp=0.0)
    svg_path = os.path.join(out_dir, 'hdls-banner-v3.svg')
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    print(f"SVG written: {len(svg_content)} bytes")

    # Render static PNG
    png_path = os.path.join(out_dir, 'hdls-banner-v3.png')
    subprocess.run(['rsvg-convert', '-w', '2560', '-h', '640', svg_path, '-o', png_path], check=True)
    print(f"PNG written: {png_path}")

    # Animated GIF
    print("Generating animation frames...")
    warp_amplitude = 2.5  # smooth, not chaotic
    n_frames = 30
    frame_dir = tempfile.mkdtemp()
    frame_paths = []

    for i in range(n_frames):
        t = 2 * math.pi * i / n_frames  # full cycle
        svg_frame = build_svg(time_offset=t, warp_amp=warp_amplitude)
        frame_svg = os.path.join(frame_dir, f'frame_{i:03d}.svg')
        frame_png = os.path.join(frame_dir, f'frame_{i:03d}.png')
        with open(frame_svg, 'w') as f:
            f.write(svg_frame)
        subprocess.run(['rsvg-convert', '-w', '1280', '-h', '320', frame_svg, '-o', frame_png], check=True)
        frame_paths.append(frame_png)
        if (i + 1) % 10 == 0:
            print(f"  Frame {i + 1}/{n_frames}")

    # Assemble GIF with PIL
    gif_path = os.path.join(out_dir, 'hdls-banner-animated.gif')
    subprocess.run([
        PYTHON39, '-c', """
from PIL import Image
import glob
paths = sorted(glob.glob('""" + frame_dir + """/frame_*.png'))
frames = []
for p in paths:
    im = Image.open(p)
    frames.append(im.copy())
frames[0].save(
    '""" + gif_path + """',
    save_all=True,
    append_images=frames[1:],
    duration=66,
    loop=0,
    optimize=True
)
print(f'GIF: {len(frames)} frames, {len(paths)} files')
"""
    ], check=True)
    print(f"GIF written: {gif_path}")

    # Cleanup
    import shutil
    shutil.rmtree(frame_dir)
    print("Done.")
