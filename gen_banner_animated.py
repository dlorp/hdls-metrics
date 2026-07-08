#!/usr/bin/env python3
"""
HDLS Animated Banner — trefoil knot with fBM domain warping.

30 frames at 15fps = 2 second loop. 1280x320. Amber on #0E0B02.
Domain warping: f(p + h(p)) where h is fBM-based displacement.
Each frame: slightly different warp offset → knot breathes/ripples.

Brand: #0E0B02 background, #FFB800 amber primary, monospace paths (no fonts).
"""

import math
import os
import subprocess
import tempfile
from PIL import Image

W, H = 1280, 320
FRAMES = 30
FPS = 15
BG = "#0E0B02"
AMBER = "#FFB800"
AMBER_MID = "#C47A00"
AMBER_DIM = "#7A5200"

OUTPUT_DIR = "/Users/lorp/repos/hdls-metrics"
OUTPUT_SVG = os.path.join(OUTPUT_DIR, "hdls-banner-animated.svg")
OUTPUT_GIF = os.path.join(OUTPUT_DIR, "hdls-banner-animated.gif")

# ── fBM noise (pure Python, no deps) ────────────────────────────────
# Simple value noise with smooth interpolation + octave summation.
# Matches Quilez's fBM: H=1, gain=0.5, lacunarity=2.0.


def _hash2(ix, iy):
    """Deterministic hash for integer grid point."""
    n = ix * 374761393 + iy * 668265263
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0x7FFFFFFF) / 0x7FFFFFFF


def _smooth(t):
    """Quintic smoothstep (C2 continuous, per Quilez)."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def value_noise_2d(x, y):
    """2D value noise with quintic interpolation."""
    ix = int(math.floor(x))
    iy = int(math.floor(y))
    fx = x - ix
    fy = y - iy
    sx = _smooth(fx)
    sy = _smooth(fy)

    n00 = _hash2(ix, iy)
    n10 = _hash2(ix + 1, iy)
    n01 = _hash2(ix, iy + 1)
    n11 = _hash2(ix + 1, iy + 1)

    nx0 = n00 + sx * (n10 - n00)
    nx1 = n01 + sx * (n11 - n01)
    return nx0 + sy * (nx1 - nx0)


def fbm(x, y, octaves=4, lacunarity=2.0, gain=0.5):
    """Fractional Brownian Motion (H=1, G=0.5). Matches Quilez's validated params."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    for _ in range(octaves):
        value += amplitude * value_noise_2d(x * frequency, y * frequency)
        amplitude *= gain
        frequency *= lacunarity
    return value


# ── Domain warping ──────────────────────────────────────────────────
# f(p + h(p)) where h is a 2D fBM-based displacement vector.
# Time-varying: offset the noise sampling by t for animation.


def domain_warp(px, py, t, scale=0.008, strength=12.0):
    """Apply time-varying domain warping to a point.
    Returns warped (x, y) displacement."""
    # Primary warp: fBM sampled at point + time offset
    qx = fbm(px * scale + t * 0.3, py * scale + 1.7, octaves=4)
    qy = fbm(px * scale + 5.2 + t * 0.2, py * scale + 9.2, octaves=4)

    # Secondary (recursive) warp: warp the warp
    rx = fbm(px * scale + 3.0 * qx + t * 0.4, py * scale + 3.0 * qy + 2.5, octaves=3)
    ry = fbm(
        px * scale + 3.0 * qx + 7.1 + t * 0.35, py * scale + 3.0 * qy + 5.8, octaves=3
    )

    # Combine: displacement from both levels
    dx = (qx * 0.6 + rx * 0.4) * strength
    dy = (qy * 0.6 + ry * 0.4) * strength

    return dx, dy


# ── HDLS blocky letterforms (same as gen_banner_v3.py) ─────────────
def hdls_blocky(ox, oy, h=100, thick=14):
    """Blocky monospace HDLS letterforms as filled SVG paths."""
    s = h / 100
    t = thick * s
    cy = oy
    cb = oy + h
    cw = 50 * s
    gap = 18 * s
    paths = []

    x = ox
    paths.append(
        f"M{x},{cy} L{x + t},{cy} L{x + t},{cy + h * 0.42} L{x + cw - t},{cy + h * 0.42}"
        f" L{x + cw - t},{cy} L{x + cw},{cy} L{x + cw},{cb} L{x + cw - t},{cb}"
        f" L{x + cw - t},{cy + h * 0.58} L{x + t},{cy + h * 0.58} L{x + t},{cb} L{x},{cb} Z"
    )
    x += cw + gap
    paths.append(
        f"M{x},{cy} L{x + t * 1.5},{cy} L{x + t * 1.5},{cy + h * 0.3}"
        f" Q{x + cw * 0.7},{cy} {x + cw * 0.7},{cy + h * 0.2}"
        f" L{x + cw * 0.7},{cy + h * 0.8}"
        f" Q{x + cw * 0.7},{cb} {x + t * 1.5},{cb - h * 0.3}"
        f" L{x + t * 1.5},{cb} L{x},{cb} Z"
    )
    x += cw + gap
    paths.append(
        f"M{x},{cy} L{x + t},{cy} L{x + t},{cb - t} L{x + cw},{cb - t} L{x + cw},{cb} L{x},{cb} Z"
    )
    x += cw + gap
    paths.append(
        f"M{x + cw},{cy} L{x + t * 1.5},{cy}"
        f" Q{x},{cy} {x},{cy + h * 0.15}"
        f" L{x},{cy + h * 0.4}"
        f" Q{x},{cy + h * 0.5} {x + t * 1.5},{cy + h * 0.5}"
        f" L{x + cw - t * 1.5},{cy + h * 0.5}"
        f" Q{x + cw},{cy + h * 0.5} {x + cw},{cy + h * 0.6}"
        f" L{x + cw},{cy + h * 0.85}"
        f" Q{x + cw},{cb} {x + cw - t * 1.5},{cb}"
        f" L{x},{cb} L{x},{cb - t}"
        f" L{x + cw - t * 1.5},{cb - t}"
        f" Q{x + cw},{cb - t} {x + cw},{cb - h * 0.15}"
        f" L{x + cw},{cy + h * 0.65}"
        f" Q{x + cw},{cy + h * 0.58} {x + cw - t * 1.5},{cy + h * 0.58}"
        f" L{x + t * 1.5},{cy + h * 0.58}"
        f" Q{x},{cy + h * 0.58} {x},{cy + h * 0.5}"
        f" L{x},{cy + h * 0.15}"
        f" Q{x},{cy} {x + t * 1.5},{cy} Z"
    )

    return "\n  ".join(f'<path d="{p}" fill="{AMBER}"/>' for p in paths)


# ── Trefoil knot math (p=2, q=3 torus knot) ───────────────────────
KNOT_STEPS = 300
KNOT_R = 70
KNOT_r = 25
KNOT_CX = 1020
KNOT_CY = 160


def trefoil_points_raw(n=KNOT_STEPS):
    """Generate raw 3D trefoil knot points."""
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x = (KNOT_R + KNOT_r * math.cos(3 * t)) * math.cos(2 * t)
        y = (KNOT_R + KNOT_r * math.cos(3 * t)) * math.sin(2 * t)
        z = KNOT_r * math.sin(3 * t)
        pts.append((x, y, z))
    return pts


def rotate3d(x, y, z, ax, ay):
    """Rotate point by angles ax (around X) and ay (around Y)."""
    y1 = y * math.cos(ax) - z * math.sin(ax)
    z1 = y * math.sin(ax) + z * math.cos(ax)
    x2 = x * math.cos(ay) + z1 * math.sin(ay)
    z2 = -x * math.sin(ay) + z1 * math.cos(ay)
    return x2, y1, z2


def trefoil_2d(frame_t=0.0, warp_strength=10.0):
    """Generate warped 2D trefoil knot points for a given frame time."""
    raw = trefoil_points_raw()
    ax_rot = math.radians(30)
    ay_rot = math.radians(20)

    pts = []
    for i, (x, y, z) in enumerate(raw):
        rx, ry, rz = rotate3d(x, y, z, ax_rot, ay_rot)
        # Apply domain warping to the 2D projection
        dx, dy = domain_warp(rx, ry, frame_t, scale=0.015, strength=warp_strength)
        px = KNOT_CX + rx + dx
        py = KNOT_CY + ry + dy
        pts.append((px, py, rz))
    return pts


# ── Crossing detection & segment building (from gen_banner_v3.py) ──
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
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy, t, u)
    return None


def detect_crossings(pts):
    """Detect crossings in the projected 2D knot."""
    crossings = []
    n = len(pts) - 1
    for i in range(n):
        for j in range(i + 8, n):
            result = seg_intersect(pts[i], pts[i + 1], pts[j], pts[j + 1])
            if result:
                ix, iy, t_param, u_param = result
                # z at intersection for depth ordering
                z_i = pts[i][2] + t_param * (pts[i + 1][2] - pts[i][2])
                z_j = pts[j][2] + u_param * (pts[j + 1][2] - pts[j][2])
                over = "i" if z_i > z_j else "j"
                crossings.append(
                    {
                        "i": i,
                        "t": t_param,
                        "j": j,
                        "u": u_param,
                        "x": ix,
                        "y": iy,
                        "over": over,
                    }
                )
    return crossings


def build_knot_segments(pts, crossings, gap=0.035):
    """Walk the knot, break the 'under' strand at each crossing."""
    under_breaks = []
    for cr in crossings:
        if cr["over"] == "j":
            under_breaks.append((cr["i"], cr["t"]))
        else:
            under_breaks.append((cr["j"], cr["u"]))
    under_breaks.sort()

    break_dict = {}
    for seg_idx, param in under_breaks:
        break_dict[seg_idx] = param

    segments = []
    current = [(pts[0][0], pts[0][1])]

    for i in range(len(pts) - 1):
        p = (pts[i][0], pts[i][1])
        p_next = (pts[i + 1][0], pts[i + 1][1])

        if i in break_dict:
            param = break_dict[i]
            t_before = max(0, param - gap)
            t_after = min(1, param + gap)
            bx_before = (
                p[0] + t_before * (p_next[0] - p[0]),
                p[1] + t_before * (p_next[1] - p[1]),
            )
            bx_after = (
                p[0] + t_after * (p_next[0] - p[0]),
                p[1] + t_after * (p_next[1] - p[1]),
            )
            current.append(bx_before)
            segments.append(current)
            current = [bx_after]
        else:
            current.append(p_next)

    if current:
        segments.append(current)
    return segments


# ── SVG frame builder ─────────────────────────────────────────────
def build_frame_svg(knot_segments, frame_idx):
    """Build a single SVG frame."""
    svg = []
    svg.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
    )
    svg.append("<defs>")

    # Glow for knot
    svg.append('  <filter id="knotglow" x="-15%" y="-15%" width="130%" height="130%">')
    svg.append('    <feGaussianBlur stdDeviation="2" result="blur"/>')
    svg.append(
        '    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
    )
    svg.append("  </filter>")

    # Glow for text
    svg.append('  <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">')
    svg.append('    <feGaussianBlur stdDeviation="1.5" result="blur"/>')
    svg.append(
        '    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
    )
    svg.append("  </filter>")

    # Scanlines
    svg.append(
        '  <pattern id="scanlines" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">'
    )
    svg.append(
        '    <rect x="0" y="2" width="4" height="2" fill="#000" opacity="0.12"/>'
    )
    svg.append("  </pattern>")

    # Vignette
    svg.append('  <radialGradient id="vignette" cx="50%" cy="50%" r="70%">')
    svg.append('    <stop offset="55%" stop-color="#000" stop-opacity="0"/>')
    svg.append('    <stop offset="100%" stop-color="#000" stop-opacity="0.6"/>')
    svg.append("  </radialGradient>")

    svg.append("</defs>")

    # Background
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')

    # Trefoil knot: 3-layer stroke (shadow, main, highlight)
    svg.append('<g filter="url(#knotglow)">')
    for seg in knot_segments:
        if len(seg) < 2:
            continue
        d = f"M{seg[0][0]:.1f},{seg[0][1]:.1f}"
        for pt in seg[1:]:
            d += f"L{pt[0]:.1f},{pt[1]:.1f}"
        # Shadow layer
        svg.append(
            f'<path d="{d}" fill="none" stroke="#3d2400" stroke-width="6" stroke-linecap="round" opacity="0.5"/>'
        )
    for seg in knot_segments:
        if len(seg) < 2:
            continue
        d = f"M{seg[0][0]:.1f},{seg[0][1]:.1f}"
        for pt in seg[1:]:
            d += f"L{pt[0]:.1f},{pt[1]:.1f}"
        # Main stroke
        svg.append(
            f'<path d="{d}" fill="none" stroke="{AMBER_MID}" stroke-width="2.5" stroke-linecap="round" opacity="0.95"/>'
        )
    for seg in knot_segments:
        if len(seg) < 2:
            continue
        d = f"M{seg[0][0]:.1f},{seg[0][1]:.1f}"
        for pt in seg[1:]:
            d += f"L{pt[0]:.1f},{pt[1]:.1f}"
        # Inner highlight
        svg.append(
            f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="0.8" stroke-linecap="round" opacity="0.45"/>'
        )
    svg.append("</g>")

    # HDLS logo (filled SVG paths, no font dependency)
    svg.append('<g transform="translate(80, 115)" filter="url(#glow)">')
    svg.append(f"  {hdls_blocky(0, 0, h=80, thick=12)}")
    svg.append("</g>")

    # Tagline
    svg.append(
        '<text x="84" y="212" font-family="monospace" font-size="14" fill="#CC8800" letter-spacing="3" opacity="0.85">METRICS // SIGNAL CHAIN</text>'
    )

    # Decorative line
    svg.append(
        f'<line x1="80" y1="228" x2="480" y2="228" stroke="{AMBER_MID}" stroke-width="0.5" opacity="0.35"/>'
    )

    # BBS-style annotations
    svg.append(
        f'<text x="80" y="248" font-family="monospace" font-size="10" fill="{AMBER_DIM}" letter-spacing="1" opacity="0.5">// trefoil_knot // fBM_domain_warp</text>'
    )
    svg.append(
        f'<text x="80" y="264" font-family="monospace" font-size="10" fill="{AMBER_DIM}" letter-spacing="1" opacity="0.4">/// frame {frame_idx:02d}/{FRAMES}</text>'
    )

    # Corner brackets
    tick = AMBER_DIM
    tw = 14
    svg.append(
        f'<polyline points="10,10 10,{10 + tw} {10 + tw},10" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>'
    )
    svg.append(
        f'<polyline points="{W - 10},10 {W - 10},{10 + tw} {W - 10 - tw},10" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>'
    )
    svg.append(
        f'<polyline points="10,{H - 10} 10,{H - 10 - tw} {10 + tw},{H - 10}" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>'
    )
    svg.append(
        f'<polyline points="{W - 10},{H - 10} {W - 10},{H - 10 - tw} {W - 10 - tw},{H - 10}" fill="none" stroke="{tick}" stroke-width="0.8" opacity="0.5"/>'
    )

    # Corner annotation
    svg.append(
        f'<text x="{W - 20}" y="{H - 18}" font-family="monospace" font-size="9" fill="{AMBER_DIM}" text-anchor="end" opacity="0.5">1280x320 // TREFOIL // ANIMATED</text>'
    )

    # Scanline overlay
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#scanlines)"/>')

    # Vignette
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#vignette)"/>')

    svg.append("</svg>")
    return "\n".join(svg)


# ── Main: generate all frames, assemble GIF ───────────────────────
def main():
    print(f"Generating {FRAMES} frames at {FPS}fps ({W}x{H})...")
    print("Domain warping: fBM octaves=3, gain=0.5, lacunarity=2.0")

    tmpdir = tempfile.mkdtemp(prefix="hdls_anim_")
    png_frames = []

    for frame_idx in range(FRAMES):
        t = frame_idx / FRAMES  # 0..1 normalized time
        frame_t = t * 2 * math.pi  # full cycle over all frames

        # Warp strength oscillates slightly for breathing effect
        warp_strength = 18.0 + 6.0 * math.sin(frame_t * 0.5)

        # Generate warped trefoil for this frame
        pts = trefoil_2d(frame_t, warp_strength)
        crossings = detect_crossings(pts)
        segments = build_knot_segments(pts, crossings)

        # Build SVG
        svg_content = build_frame_svg(segments, frame_idx)
        svg_path = os.path.join(tmpdir, f"frame_{frame_idx:03d}.svg")
        png_path = os.path.join(tmpdir, f"frame_{frame_idx:03d}.png")

        with open(svg_path, "w") as f:
            f.write(svg_content)

        # Convert SVG to PNG via rsvg-convert
        result = subprocess.run(
            ["rsvg-convert", svg_path, "-o", png_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ERROR frame {frame_idx}: {result.stderr.strip()}")
            continue

        png_frames.append(png_path)

        if frame_idx % 5 == 0:
            print(
                f"  frame {frame_idx:02d}: {len(crossings)} crossings, "
                f"warp={warp_strength:.1f}, segments={len(segments)}"
            )

    print(f"\n{len(png_frames)} frames rendered. Assembling GIF...")

    # Assemble GIF using PIL
    images = []
    for png_path in png_frames:
        img = Image.open(png_path)
        images.append(img)

    # Save as animated GIF
    frame_duration = int(1000 / FPS)  # ms per frame
    images[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=images[1:],
        duration=frame_duration,
        loop=0,  # infinite loop
        optimize=True,
    )

    # Also save the last frame as the final static SVG
    last_svg = build_frame_svg(
        build_knot_segments(
            trefoil_2d(2 * math.pi, 18.0 + 6.0 * math.sin(math.pi)),
            detect_crossings(trefoil_2d(2 * math.pi, 18.0 + 6.0 * math.sin(math.pi))),
        ),
        FRAMES - 1,
    )
    with open(OUTPUT_SVG, "w") as f:
        f.write(last_svg)

    gif_size = os.path.getsize(OUTPUT_GIF)
    print("\nDone!")
    print(f"  GIF: {OUTPUT_GIF} ({gif_size:,} bytes, {FRAMES} frames @ {FPS}fps)")
    print(f"  SVG: {OUTPUT_SVG}")
    print(f"  Temp: {tmpdir}")

    # Cleanup temp files (keep the temp dir for debugging)
    # Uncomment to clean up:
    # import shutil
    # shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
