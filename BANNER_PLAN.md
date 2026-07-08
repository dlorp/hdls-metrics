# hdls-metrics GitHub Banner — Design Plan
> hyph4 · 2026-07-05 · For 0r4cl3 review → r3nd3r execution

## Context

dlorp wants a new GitHub banner for `dlorp/hdls-metrics` (daily metrics scan for HDLS repos). The current banner has broken typography (hand-coded SVG paths for D and S are mangled) and the animated trefoil is too chaotic. Prior session produced v6 with real VT323 glyphs via PIL — that's the working baseline.

## Vault Knowledge Mined

**Brand registers** (`_meta/brand/registers/colors.md`):
- Background: `#0E0B02` (Root Dark, warm near-black)
- Logo: `#FFB800` (Amber Primary)
- Display: VT323 pixel font (NOT Courier New for headers)
- CRT effect: scanlines + vignette, always-on
- Hard nos: no green, no pure #000/#fff, no gradients, no rounded corners

**Existing banner assets** (`_meta/brand/0r4cl3-output/`):
- `hdls-profile-banner.svg` (232KB) — prior version
- `hdls-profile-banner-v2.svg` (356KB) — latest prior version

**Prior session working files** (`/tmp/`):
- `gen_banner_v6.py` — working banner with VT323 via PIL + numpy (71KB PNG output)
- `gen_banner_0r4cl3.py` — earlier iteration using PIL rendering
- `hdls-banner-v6.png` — the version dlorp approved before

**Generative design vault entries**:
- `generative-algorithms/inigo-quilez-sdf-raymarching.md` — SDF foundations
- `generative-algorithms/2026-06-18-quilez-domain-warping.md` — fBM warp technique
- `demoscene/2026-05-25-shader-showdown-livecoding-virgo-1302-synthesis.md` — GLSL livecoding
- `generative-algorithms/2026-06-18-bookofshaders-cellular-noise.md` — Voronoi/Worley

## Options for dlorp

### Option A: Static Banner (refined v6)
- Use `/tmp/gen_banner_v6.py` as base (PIL + numpy, real VT323 glyphs)
- Fix: ensure HDLS renders correctly with VT323 at 110px
- Keep: Rule 30 CA texture, corner brackets, scanlines, vignette
- Format: PNG at 2560x640 (2x, GitHub downscales)
- **Deliverable:** `hdls-banner-final.png` pushed to `dlorp/hdls-metrics`

### Option B: Static Banner + Animated GIF
- Same as Option A for static
- Add: 30-frame animated GIF with smooth wave deformation on the trefoil knot
- Animation: sinusoidal wave (not chaotic fBM), warp_amp=2.5
- Format: GIF at 1280x320, 15fps, 2-sec loop
- **Deliverable:** `hdls-banner-final.png` + `hdls-banner-animated.gif`

### Option C: Shader-Based Animated Banner
- Render the trefoil as an SDF in a fragment shader (GLSL)
- Domain warping from vault's quilez technique
- Render via Chrome headless or ffmpeg from shader frames
- Highest quality but most complex
- **Deliverable:** `hdls-banner-final.png` + `hdls-banner-animated.gif`

## Recommendation

**Option B.** The static banner from v6 already worked. The animated GIF adds the visual interest dlorp wants without the complexity of a full shader pipeline. The wave deformation should be smooth (sinusoidal dominant, subtle fBM accent), not chaotic.

## Execution Plan

1. **0r4cl3 reviews this plan** — confirms brand compliance, selects option
2. **r3nd3r executes** — uses gen_banner_v6.py as base, fixes any issues
3. **3tch handles code** — if shader approach (Option C) is chosen
4. **hyph4 monitors** — sends final PNG/GIF to Discord, pushes to repo

## Notes for r3nd3r

- The font MUST be VT323 rendered via PIL (not SVG font-family — GitHub renderer lacks it)
- Use `/usr/bin/python3` for PIL (has fonttools + PIL installed)
- `rsvg-convert` works for SVG→PNG but doesn't handle Google Fonts
- The trefoil knot parametric: `(R + r·cos(3t))·cos(2t)` with 3D rotation for 3 crossings
- Corner brackets: 14px L-shapes in `#7A5200`, opacity 0.5
- Scanlines: 2px pitch, `#000` at 0.12 opacity
- Vignette: radial gradient, 55% clear → 100% at 0.6 opacity
