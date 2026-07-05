#!/usr/bin/env python3
"""Generate HDLS banner SVG with Rule 30 CA clipped into trefoil knot shape."""

import math

def rule30_step(cells):
    """Single step of Rule 30 cellular automaton."""
    new_cells = []
    n = len(cells)
    for i in range(n):
        left = cells[(i - 1) % n]
        center = cells[i]
        right = cells[(i + 1) % n]
        # Rule 30: 000→0, 001→1, 010→1, 011→1, 100→1, 101→0, 110→0, 111→0
        pattern = (left << 2) | (center << 1) | right
        new_cells.append(1 if pattern in (1, 2, 3, 4) else 0)
    return new_cells

def generate_rule30_ca(width=400, height=280):
    """Generate Rule 30 pattern starting with single center cell."""
    cells = [0] * width
    cells[width // 2] = 1  # Start with single center cell
    pattern = []
    for _ in range(height):
        pattern.append(cells[:])
        cells = rule30_step(cells)
    return pattern

def generate_trefoil_path_string(cx, cy, scale):
    """Generate trefoil knot path as a filled shape (not a stroke)."""
    # Trefoil knot parametric equations
    points = []
    for i in range(360):
        t = i * math.pi / 180
        x = scale * (math.sin(t) + 2 * math.sin(2 * t))
        y = -scale * (math.cos(t) - 2 * math.cos(2 * t))
        points.append((int(cx + x), int(cy + y)))
    
    # Create closed path string
    path = "M" + " L".join(f"{p[0]},{p[1]}" for p in points)
    path += " Z"
    return path, points

def main():
    width, height = 1280, 320
    
    # Knot position and scale
    knot_cx, knot_cy = 950, 160
    knot_scale = 45
    
    # Generate Rule 30 pattern
    ca_width, ca_height = 400, 280
    ca_pattern = generate_rule30_ca(ca_width, ca_height)
    
    # Generate trefoil path for clipping
    trefoil_path, trefoil_points = generate_trefoil_path_string(knot_cx, knot_cy, knot_scale)
    
    # Calculate bounding box of knot for clip region
    min_x = min(p[0] for p in trefoil_points)
    max_x = max(p[0] for p in trefoil_points)
    min_y = min(p[1] for p in trefoil_points)
    max_y = max(p[1] for p in trefoil_points)
    
    svg = ['<?xml version="1.0" encoding="UTF-8"?>']
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <defs>')
    
    # Glow filter
    svg.append('    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">')
    svg.append('      <feGaussianBlur stdDeviation="2" result="blur"/>')
    svg.append('      <feMerge>')
    svg.append('        <feMergeNode in="blur"/>')
    svg.append('        <feMergeNode in="SourceGraphic"/>')
    svg.append('      </feMerge>')
    svg.append('    </filter>')
    
    # Vignette gradient
    svg.append('    <radialGradient id="vignette" cx="50%" cy="50%" r="70%">')
    svg.append('      <stop offset="0%" stop-color="#000" stop-opacity="0"/>')
    svg.append('      <stop offset="50%" stop-color="#000" stop-opacity="0"/>')
    svg.append('      <stop offset="100%" stop-color="#000" stop-opacity="0.5"/>')
    svg.append('    </radialGradient>')
    
    # Rule 30 CA pattern as a symbol/pattern
    svg.append('    <pattern id="rule30" x="0" y="0" width="3" height="3" patternUnits="userSpaceOnUse">')
    # Add a few cells as representative pattern - we'll draw actual cells directly
    svg.append('      <rect width="3" height="3" fill="none"/>')
    svg.append('    </pattern>')
    
    # Trefoil clipPath - the knot shape that clips the CA
    svg.append('    <clipPath id="trefoil-clip">')
    svg.append(f'      <path d="{trefoil_path}"/>')
    svg.append('    </clipPath>')
    
    # Slightly expanded version for glow effect
    expand = 3
    glow_path, _ = generate_trefoil_path_string(knot_cx, knot_cy, knot_scale * 1.05)
    svg.append('    <clipPath id="trefoil-clip-glow">')
    svg.append(f'      <path d="{glow_path}"/>')
    svg.append('    </clipPath>')
    
    svg.append('  </defs>')
    
    # Background
    svg.append(f'  <rect width="{width}" height="{height}" fill="#0a0a0a"/>')
    
    # Rule 30 CA pattern - drawn once
    cell_size = 3
    # Center the CA within the knot area
    ca_start_x = knot_cx - ca_width * cell_size // 2
    ca_start_y = knot_cy - ca_height * cell_size // 2
    
    ca_rects = []
    for y, row in enumerate(ca_pattern):
        for x, cell in enumerate(row):
            if cell == 1:
                cx = ca_start_x + x * cell_size
                cy = ca_start_y + y * cell_size
                # Vary opacity for visual interest
                opacity = 0.15 + (x / ca_width) * 0.15
                ca_rects.append(f'<rect x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}" fill="#ff9500" opacity="{opacity:.2f}"/>')
    
    # Group 1: The CA pattern CLIPPED to the trefoil knot shape (the core idea)
    svg.append('  <!-- Rule 30 CA clipped into trefoil knot -->')
    svg.append('  <g clip-path="url(#trefoil-clip)">')
    svg.extend(ca_rects)
    svg.append('  </g>')
    
    # Group 2: Glow effect by drawing the clipped pattern again with blur
    svg.append('  <g clip-path="url(#trefoil-clip-glow)" filter="url(#glow)" opacity="0.6">')
    svg.extend(ca_rects)
    svg.append('  </g>')
    
    # Knot outline for definition
    svg.append('  <!-- Knot outline -->')
    svg.append(f'  <path d="{trefoil_path}" fill="none" stroke="#ff9500" stroke-width="1" opacity="0.4"/>')
    
    # HDLS text in Courier New
    svg.append('  <!-- Text group -->')
    svg.append('  <g transform="translate(80, 165)" fill="#ff9500">')
    svg.append('    <text x="0" y="0" font-family="Courier New, monospace" font-size="110" font-weight="bold" opacity="0.3" filter="url(#glow)">HDLS</text>')
    svg.append('    <text x="0" y="0" font-family="Courier New, monospace" font-size="110" font-weight="bold">HDLS</text>')
    svg.append('    <text x="2" y="-2" font-family="Courier New, monospace" font-size="110" font-weight="bold" fill="#ffcc00" opacity="0.2">HDLS</text>')
    svg.append('  </g>')
    
    # Tagline
    svg.append('  <text x="82" y="195" font-family="Courier New, monospace" font-size="12" fill="#b36800" letter-spacing="3">HARDWARE DESCRIPTION LANGUAGE SYSTEMS</text>')
    
    # Corner brackets
    svg.append('  <!-- Corner brackets -->')
    svg.append('  <g stroke="#ff9500" stroke-width="2" fill="none" opacity="0.5">')
    # TL
    svg.append('    <polyline points="30,30 30,15 45,15"/>')
    svg.append('    <polyline points="15,45 15,30 30,30"/>')
    # TR
    svg.append('    <polyline points="1235,15 1250,15 1250,30"/>')
    svg.append('    <polyline points="1250,30 1265,30 1265,45"/>')
    # BL
    svg.append('    <polyline points="15,275 15,290 30,290"/>')
    svg.append('    <polyline points="30,290 30,305 45,305"/>')
    # BR
    svg.append('    <polyline points="1235,305 1250,305 1250,290"/>')
    svg.append('    <polyline points="1250,290 1265,290 1265,275"/>')
    svg.append('  </g>')
    
    # Scanlines
    svg.append('  <!-- Scanlines -->')
    svg.append('  <g opacity="0.25">')
    for y in range(0, height, 2):
        svg.append(f'    <line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#000" stroke-width="1"/>')
    svg.append('  </g>')
    
    # Vignette overlay
    svg.append('  <rect width="1280" height="320" fill="url(#vignette)"/>')
    
    svg.append('</svg>')
    
    with open('/tmp/hdls-metrics/hdls-banner.svg', 'w') as f:
        f.write('\n'.join(svg))
    
    print("Banner written to /tmp/hdls-metrics/hdls-banner.svg")

if __name__ == '__main__':
    main()
