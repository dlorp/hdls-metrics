# HDLS-Metrics Banner Brand Audit
> 0r4cl3 · 2026-07-05 · Task t_e40b4f26

## Consulted
- vault: _meta/brand/ledger.md, _meta/brand/hdls-style-guide.md, _meta/brand/registers/colors.md
- precedents: hdls-profile-banner.svg, hdls-profile-banner-v2.svg
- registers: colors.md, names.md

---

## Current State Analysis

**Files reviewed:**
- `~/repos/hdls-metrics/gen_banner.py` (315 lines, generates Rule 30 CA + trefoil knot)
- `~/repos/hdls-metrics/generate_banner.py` (184 lines, alternate approach with clipPath)
- `~/repos/hdls-metrics/hdls-banner.png` (1280x320, current render)
- `~/repos/hdls-metrics/hdls-banner.svg` (3,226 lines, current SVG source)

**Current composition:**
- 1280x320px banner format (GitHub standard)
- Dark background with Rule 30 cellular automata texture
- Trefoil knot shape with CA clipped inside
- "HDLS" in Courier New, 110px
- Tagline: "HARDWARE DESCRIPTION LANGUAGE SYSTEMS"
- Corner bracket ornaments (demoscene frame ticks)
- Scanline overlay + vignette

---

## Findings

### [ !! BLOCK ] Hard No Violations

**None.** Zero blocking issues. The banner passes all 7 hard nos.

### [ ?? VIBE ] Brand Drift Issues

1. **Background color: `#0a0a0a` vs `#0E0B02` Root Dark**
   - Current: near-black with no warmth
   - Ledger spec: `#0E0B02` — warm near-black with amber undertone
   - Movement: The warm undertone is the character; pure near-black is sterile

2. **Primary amber: `#ff9500` vs `#FFB800` Amber Primary**
   - Current: Amber Canon (`#ff9500`) — more orange, phosphor-forward
   - Ledger spec: `#FFB800` — warmer, more yellow-amber
   - Note: `#ff9500` IS registered as "Amber Canon" for console text, but the **logo/headers** should use `#FFB800` per ledger §Amber Phosphor

3. **Typography: Courier New vs VT323**
   - Current: Courier New (system monospace)
   - Ledger spec: VT323 for display/UI — the canonical pixel/bitmap font
   - The banner is DISPLAY, not body text. VT323 carries the demoscene aesthetic.

4. **Tagline mismatch: "HARDWARE DESCRIPTION LANGUAGE SYSTEMS"**
   - Current text refers to HDLS the organization
   - This repo is `hdls-metrics` — metrics collection for dlorp repos
   - The tagline should reflect the repo's purpose, not the parent org

5. **Visual execution: CA-in-knot is muddy**
   - The Rule 30 pattern clipped inside the trefoil knot is visually indistinct
   - At banner scale, it reads as "textured amber blob" not "CA inside knot"
   - The over/under crossing logic in gen_banner.py is clever but invisible at this resolution

### [ -- NOTE ] Observations

- Two generator scripts exist; `generate_banner.py` (clipPath approach) is cleaner
- The corner brackets are a nice demoscene touch — keep
- Scanlines + vignette are properly executed per CRT Effect Spec
- The "1280x320 // TREFOIL // RULE30 // v2" timestamp in corner is good provenance

---

## Severity Summary
- blocking: 0
- vibe: 5 issues (all fixable)
- note: 1 (structural observation)

---

## Proposed Redesign Direction

### Concept: "Signal Chain Monitor"

The banner should communicate:
1. This is the **metrics** repo — data collection, monitoring, signal aggregation
2. HDLS brand identity (amber phosphor, CRT aesthetic, monospace)
3. The "signal chain" metaphor from the agent pipeline

### Structural Changes

1. **Background**: Migrate to `#0E0B02` Root Dark
2. **Amber**: Use `#FFB800` Amber Primary for "HDLS" logo text
3. **Typography**: VT323 (Google Fonts) with fallback to Courier New
4. **Tagline**: Change to "SIGNAL CHAIN METRICS" or "REPOSITORY TELEMETRY"
5. **Graphic element**: Replace CA-in-knot with one of:
   - **Option A**: Simplified trefoil outline (no CA fill) — clean, iconic
   - **Option B**: Oscilloscope waveform visualization of metrics data
   - **Option C**: Signal chain diagram (9 agents as nodes, amber lines)
   - **Option D**: Minimal amber phosphor grid with data points

### Recommended: Option A (Simplified Trefoil)

- Single clean trefoil knot outline, stroke only
- No fill, no CA clipping (muddiness eliminated)
- Position: right third of banner
- HDLS text: left third, VT323, `#FFB800`
- Tagline: "METRICS // SIGNAL CHAIN" — centered below HDLS, smaller
- Keep corner brackets, scanlines, vignette

---

## Route to r3nd3r

This requires visual production. Create brief and handoff to r3nd3r for SVG render.

---

## Proposed Ledger Updates

None required — current ledger is correct; implementation drifted.

[ END ]
