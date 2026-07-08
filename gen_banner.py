#!/usr/bin/env python3
"""
HDLS Banner Generator — demoscene title card.
Computes Rule 30 cellular automata background and trefoil knot coordinates,
emits a single self-contained SVG.
"""
import math

W, H = 1280, 320

# ── Rule 30 cellular automata ──────────────────────────────────────
# Single black cell at center, evolve downward. We sample a window
# and render as a texture pattern of faint amber dots.

CA_COLS = 160   # cells across
CA_ROWS = 40    # rows down
CELL = W / CA_COLS  # pixel size per cell

def rule30():
    """Generate Rule 30 CA grid. Returns list of rows (each a list of 0/1)."""
    grid = []
    row = [0] * CA_COLS
    row[CA_COLS // 2] = 1  # single seed
    grid.append(row)
    for _ in range(CA_ROWS - 1):
        prev = grid[-1]
        new = [0] * CA_COLS
        for i in range(CA_COLS):
            left = prev[(i - 1) % CA_COLS]
            center = prev[i]
            right = prev[(i + 1) % CA_COLS]
            # Rule 30: 111->0, 110->0, 101->0, 100->1,
            #          011->1, 010->1, 001->1, 000->0
            idx = (left << 2) | (center << 1) | right
            new[i] = 1 if (30 >> idx) & 1 else 0
        grid.append(new)
    return grid

ca_grid = rule30()

# Build a path string of small rects for the CA texture.
# We'll use a single <path> with M/h/v commands for efficiency.
ca_path_parts = []
for r, row in enumerate(ca_grid):
    for c, cell in enumerate(row):
        if cell:
            x = c * CELL
            y = r * CELL
            ca_path_parts.append(f"M{x:.1f},{y:.1f}h{CELL:.1f}v{CELL:.1f}h-{CELL:.1f}z")
ca_path = " ".join(ca_path_parts)


# ── Trefoil knot ───────────────────────────────────────────────────
# Parametric trefoil: (sin t + 2 sin 2t, cos t - 2 cos 2t, -sin 3t)
# Project to 2D, scale, center. Compute over/under crossings.

TREFOIL_STEPS = 600
t_vals = [2 * math.pi * i / TREFOIL_STEPS for i in range(TREFOIL_STEPS + 1)]

# Raw 3D coordinates
pts3d = []
for t in t_vals:
    x = math.sin(t) + 2 * math.sin(2 * t)
    y = math.cos(t) - 2 * math.cos(2 * t)
    z = -math.sin(3 * t)
    pts3d.append((x, y, z))

# Project to 2D (simple orthographic, slight z-influence for depth)
# Center the knot on the right side of the banner
knot_cx = 1000
knot_cy = 160
knot_scale = 38

pts2d = []
for (x, y, z) in pts3d:
    # Slight perspective: z shifts x slightly
    px = knot_cx + x * knot_scale + z * 3
    py = knot_cy + y * knot_scale
    pts2d.append((px, py, z))

# Find crossing points: where the projected 2D curve crosses itself.
# For a trefoil there are exactly 3 crossings. We detect them by
# checking segment intersections.
def seg_intersect(p1, p2, p3, p4):
    """Return intersection point if segments [p1,p2] and [p3,p4] cross, else None."""
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 < t < 1 and 0 < u < 1:
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy, t, u)
    return None

# Find crossings
crossings = []
N = len(pts2d) - 1
for i in range(N):
    p1 = pts2d[i]
    p2 = pts2d[i + 1]
    for j in range(i + 5, N):  # skip nearby segments
        p3 = pts2d[j]
        p4 = pts2d[j + 1]
        result = seg_intersect(p1, p2, p3, p4)
        if result:
            ix, iy, t_param, u_param = result
            # Which strand is "over"? The one with higher z (closer to viewer)
            z_i = pts3d[i][2] + t_param * (pts3d[i+1][2] - pts3d[i][2])
            z_j = pts3d[j][2] + u_param * (pts3d[j+1][2] - pts3d[j][2])
            over = 'i' if z_i > z_j else 'j'
            crossings.append({
                'i': i, 't': t_param,
                'j': j, 'u': u_param,
                'x': ix, 'y': iy,
                'over': over
            })

# Build knot path segments with breaks at under-crossings.
# At each crossing, the "under" strand gets a gap (break) to simulate
# the over/under weaving of a knot diagram.
def build_knot_segments(pts, crossings, gap_size=0.04):
    """
    Walk the knot. At each crossing, if this segment index is the 'under'
    strand, introduce a gap around the crossing parameter.
    Returns a list of sub-paths (each a list of points).
    """
    # Build a set of (segment_index, is_under) for quick lookup
    under_breaks = []  # list of (segment_index, param_on_segment, gap_before, gap_after)
    for cr in crossings:
        if cr['over'] == 'j':
            # segment i is under at parameter t
            under_breaks.append((cr['i'], cr['t']))
        else:
            # segment j is under at parameter u
            under_breaks.append((cr['j'], cr['u']))

    # Sort breaks by segment index
    under_breaks.sort()

    # We'll build sub-paths. Walk through all points.
    # When we hit a segment that has an under-break, we split around it.
    segments = []
    current = [(pts[0][0], pts[0][1])]  # start with first point (x, y only)

    break_dict = {}  # seg_index -> param
    for seg_idx, param in under_breaks:
        break_dict[seg_idx] = param

    for i in range(len(pts) - 1):
        p = (pts[i][0], pts[i][1])
        p_next = (pts[i + 1][0], pts[i + 1][1])

        if i in break_dict:
            param = break_dict[i]
            # Compute break points: slightly before and after the crossing
            bx1 = p[0] + param * (p_next[0] - p[0]) - (1 - param) * 0  # before
            # Simpler: interpolate to param, back off by gap
            gap = gap_size
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

    return segments

knot_segments = build_knot_segments(pts2d, crossings)

# Convert segments to SVG path strings
knot_paths = []
for seg in knot_segments:
    if len(seg) < 2:
        continue
    d = f"M{seg[0][0]:.1f},{seg[0][1]:.1f}"
    for pt in seg[1:]:
        d += f"L{pt[0]:.1f},{pt[1]:.1f}"
    knot_paths.append(d)


# ── Assemble SVG ───────────────────────────────────────────────────

svg_parts = []
svg_parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
svg_parts.append(f'<defs>')

# Subtle phosphor glow
svg_parts.append(f'''  <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur stdDeviation="1.2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>''')

# Stronger glow for the knot
svg_parts.append(f'''  <filter id="knotglow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>''')

# Scanline pattern - use Root Dark for scanlines, not pure black
svg_parts.append(f'''  <pattern id="scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="1" height="1" fill="#0E0B02" opacity="0.3"/>
  </pattern>''')

# Vignette gradient
svg_parts.append(f'''  <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
    <stop offset="60%" stop-color="#000000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.85"/>
  </radialGradient>''')

# CA gradient mask (fade CA toward edges)
svg_parts.append(f'''  <linearGradient id="caFade" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="white" stop-opacity="0.5"/>
    <stop offset="40%" stop-color="white" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="white" stop-opacity="0"/>
  </linearGradient>''')

svg_parts.append(f'''  <mask id="caMask">
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#caFade)"/>
  </mask>''')

svg_parts.append(f'</defs>')

# Background - Root Dark from myc3lium brand register
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0E0B02"/>')

# Rule 30 CA texture - Amber Primary #FFB800
svg_parts.append(f'<g mask="url(#caMask)" opacity="0.35">')
svg_parts.append(f'<path d="{ca_path}" fill="#FFB800"/>')
svg_parts.append(f'</g>')

# HDLS text — big, monospace, amber phosphor
# Main title - Amber Primary #FFB800
svg_parts.append(f'''<text x="80" y="175" font-family="Courier New, monospace" font-size="96" font-weight="bold"
  fill="#FFB800" letter-spacing="8" filter="url(#glow)">HDLS</text>''')

# Subtitle / tagline - Amber Tertiary #C47A00
svg_parts.append(f'''<text x="84" y="215" font-family="Courier New, monospace" font-size="13"
  fill="#C47A00" letter-spacing="3" opacity="0.8">HOUSE OF THE DISTRIBUTED LEARNING SYSTEM</text>''')

# Decorative line under text - Amber Secondary #E88A00
svg_parts.append(f'<line x1="80" y1="232" x2="520" y2="232" stroke="#E88A00" stroke-width="0.5" opacity="0.4"/>')

# Small annotations (BBS-style) - Amber Dim #7A5200
svg_parts.append(f'''<text x="80" y="255" font-family="Courier New, monospace" font-size="10"
  fill="#7A5200" letter-spacing="1" opacity="0.6">// amber_phosphor // trefoil_knot // rule30_ca</text>''')

svg_parts.append(f'''<text x="80" y="272" font-family="Courier New, monospace" font-size="10"
  fill="#7A5200" letter-spacing="1" opacity="0.5">/// distribute_impurity_evenly</text>''')


# Trefoil knot - using brand amber spectrum
svg_parts.append(f'<g filter="url(#knotglow)">')
# Shadow/back layer — Amber Trace #3D2900
for d in knot_paths:
    svg_parts.append(f'<path d="{d}" fill="none" stroke="#3D2900" stroke-width="5" stroke-linecap="round" opacity="0.6"/>')
# Main knot strokes - Amber Primary #FFB800
for d in knot_paths:
    svg_parts.append(f'<path d="{d}" fill="none" stroke="#FFB800" stroke-width="2.5" stroke-linecap="round" opacity="0.95"/>')
# Inner highlight - Amber Hot #FFD060
for d in knot_paths:
    svg_parts.append(f'<path d="{d}" fill="none" stroke="#FFD060" stroke-width="0.8" stroke-linecap="round" opacity="0.5"/>')
svg_parts.append(f'</g>')

# Scanline overlay
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#scanlines)" opacity="0.5"/>')

# Vignette
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#vignette)"/>')

# Corner markers (demoscene frame ticks) - Amber Primary
tick = '#FFB800'
tw = 12
# Top-left
svg_parts.append(f'<polyline points="10,10 10,{10+tw} {10+tw},10" fill="none" stroke="{tick}" stroke-width="0.5" opacity="0.4"/>')
# Top-right
svg_parts.append(f'<polyline points="{W-10},10 {W-10},{10+tw} {W-10-tw},10" fill="none" stroke="{tick}" stroke-width="0.5" opacity="0.4"/>')
# Bottom-left
svg_parts.append(f'<polyline points="10,{H-10} 10,{H-10-tw} {10+tw},{H-10}" fill="none" stroke="{tick}" stroke-width="0.5" opacity="0.4"/>')
# Bottom-right
svg_parts.append(f'<polyline points="{W-10},{H-10} {W-10},{H-10-tw} {W-10-tw},{H-10}" fill="none" stroke="{tick}" stroke-width="0.5" opacity="0.4"/>')

# Bottom-right timestamp / sigil - Amber Dim
svg_parts.append(f'''<text x="{W-20}" y="{H-18}" font-family="Courier New, monospace" font-size="9"
  fill="#7A5200" text-anchor="end" opacity="0.5">1280x320 // TREFOIL // RULE30 // v3</text>''')

svg_parts.append(f'</svg>')

svg_content = '\n'.join(svg_parts)

with open('/tmp/hdls-metrics/hdls-banner.svg', 'w') as f:
    f.write(svg_content)

print(f"SVG written: {len(svg_content)} bytes")
print(f"CA cells: {len(ca_path_parts)}")
print(f"Trefoil segments: {len(knot_paths)}")
print(f"Crossings detected: {len(crossings)}")
for i, cr in enumerate(crossings):
    print(f"  crossing {i}: seg {cr['i']} x seg {cr['j']}, over={cr['over']}, at ({cr['x']:.1f},{cr['y']:.1f})")
