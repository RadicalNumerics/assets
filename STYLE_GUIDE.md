# Radical Numerics — Figure & Visual Style Guide

A practical reference for making figures, charts, and diagrams that match the RN website and brand.

---

## 1. Brand essence

- **Monochrome-first.** Near-black on white with a neutral grey scale. Color is used *sparingly* as accent, never as decoration.
- **One accent: RN orange** (`#FA6D0F`). A single warm orange carries emphasis — the active state, the highlighted series, the "look here" dot. Pops on light and dark backgrounds.
- **Quiet, precise, technical.** Thin rules, generous whitespace, mono labels, tight letter-spacing on headings. Figures should read like instrument readouts, not marketing slides.
- **Flat.** No drop shadows, no gradients on UI chrome, no borders where a tone step will do. (Dark figure theme is the one place a subtle glow is allowed.)

---

## 2. Color palette

### Neutrals (the backbone — Tailwind `neutral` scale)

| Token | Hex | Use |
|---|---|---|
| White | `#FFFFFF` | Page / light figure background |
| neutral-50 | `#FAFAFA` | Subtle fill, hover |
| neutral-100 | `#F5F5F5` | Code/panel fill (`#F7F7F7` also used) |
| neutral-200 | `#E5E5E5` | Borders, hairlines, H2 underline |
| divider | `#EBEBEB` | Dashed dividers, scrollbar track |
| neutral-300 | `#D4D4D4` | Muted underlines, faint gridlines |
| neutral-400 | `#A3A3A3` | Secondary text, axis ticks |
| neutral-500 | `#737373` | Muted body text |
| neutral-600 | `#525252` | Body text on light |
| neutral-700 | `#404040` | Strong text, hover-dark |
| neutral-900 | `#171717` | Headings |
| near-black | `#0C0C0C` | Primary text / brand black |

> Rule of thumb: backgrounds from the top of the list, text from the bottom. Most figures need only 4–5 of these greys.

### Accent — RN orange (use for ≤1 emphasized element per figure)

| Token | Hex | Use |
|---|---|---|
| **RN orange** | `#FA6D0F` | Primary accent — active dot, highlighted series |
| orange-600 | `#EA580C` | Accent on light bg (slightly deeper) |
| orange-400 | `#FB923C` | Lighter accent / secondary line |
| orange-50 | `#FFF7ED` | Tinted fill behind accent content |
| orange-deep | `#854F0B` / `#412402` | Accent text on tinted fill |

### Secondary accent — violet (only when a 2nd category is unavoidable)

| Token | Hex |
|---|---|
| violet-600 | `#7C3AED` |
| violet-400 | `#A78BFA` |

### Categorical sequence (when you truly need >2 series)

Order them so the most important is orange:

```
1. #FA6D0F  (RN orange)
2. #171717  (near-black)
3. #7C3AED  (violet)
4. #5B9A8B  (muted teal)
5. #A3A3A3  (neutral-400)
```

Prefer encoding extra categories with **shape / dash / position** before reaching for more hues.

---

## 3. Figure themes (from `build_manifold_*.py`)

**Light**
```python
bg    = "white"
title = "#383A42"   # near-black, slightly warm
sub   = "#9A9A9A"   # muted grey labels
grid  = "#DADADA"   # faint gridlines
glow  = False
```

**Dark**
```python
bg    = "#0D0D12"   # near-black, faint blue cast
title = "#F2F2F2"
sub   = "#8A8A8A"
grid  = "#3A3A44"
glow  = True        # subtle glow allowed on dark only
```

Accent (`#FA6D0F`) is the same in both themes.

---

## 4. Typography

**Web/UI**
- Sans: **Geist Sans** — headings, body, UI.
- Mono: **Geist Mono** — labels, buttons, code, data callouts, axis tick text.
- Serif (rare): Source Serif 4 — long-form editorial only.

**Figures (matplotlib / exported assets)**
- Sans/title: **Helvetica Neue** (`plt.rcParams["font.family"] = "Helvetica Neue"`)
- Mono labels: **Menlo** (axis labels, annotations, small data text)

**Conventions**
- Headings: weight **500** (Medium), tight tracking **-0.06em** (large) / **-0.02em** (small). Never bold-heavy.
- Body: weight 400, tracking -0.02em.
- Figure labels: **mono, small (6.5–9pt), in `sub` grey**, often lowercase.
- Figure titles: ~10–11pt, `title` color; bold acceptable *in-figure* only.

Type scale (web, px):

| Role | Size / line-height | Weight | Tracking |
|---|---|---|---|
| Title 1 | 56 / 60 | 500 | -0.06em |
| H3 | 24 / 32 | 500 | -0.02em |
| Subtitle | 18 / 26 | 400 | -0.02em |
| Body | 16 / 24 | 400 | -0.02em |
| Label/meta | 14 / 20 | 400 | -0.02em |
| Mono button | 13 / 1.0 | 400 | -0.02em |
| Code | 15 / 24 | 400 | 0 |

---

## 5. Shape & layout

- **Corner radius:** UI base `10px`; code/panels `4–6px`. Keep figure panels at `4–6px` or square.
- **Hairlines:** `1px` solid `#E5E5E5`, or the signature **dashed divider** — 4px dash / 4px gap, color `#EBEBEB`, drawn as a bottom rule.
- **H2 sections** get a `1px #E5E5E5` bottom border — echo for figure separators.
- **Spacing:** generous; 8px-ish rhythm (gaps of 16/20/24px). Let figures breathe.
- **Active/progress marker:** a single filled **orange dot** (`#FA6D0F`) against dimmed neutral dots (`#DADADA` light / `#3A3A44` dark).

---

## 6. Matplotlib starter (drop-in)

```python
import matplotlib.pyplot as plt

THEME = "light"   # or "dark"
TH = {
    "light": dict(bg="white",   title="#383A42", sub="#9A9A9A", grid="#DADADA", glow=False),
    "dark":  dict(bg="#0D0D12", title="#F2F2F2", sub="#8A8A8A", grid="#3A3A44", glow=True),
}[THEME]

ACCENT  = "#FA6D0F"   # RN orange — one emphasized element only
SERIES  = ["#FA6D0F", "#171717", "#7C3AED", "#5B9A8B", "#A3A3A3"]
MONO    = "Menlo"

plt.rcParams.update({
    "font.family":        "Helvetica Neue",
    "figure.facecolor":   TH["bg"],
    "axes.facecolor":     TH["bg"],
    "savefig.facecolor":  TH["bg"],
    "axes.edgecolor":     TH["sub"],
    "axes.linewidth":     0.8,
    "axes.grid":          True,
    "grid.color":         TH["grid"],
    "grid.linewidth":     0.6,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "text.color":         TH["title"],
    "axes.labelcolor":    TH["sub"],
    "xtick.color":        TH["sub"],
    "ytick.color":        TH["sub"],
    "axes.titlesize":     10.5,
    "axes.titleweight":   "bold",   # in-figure titles only
    "font.size":          8.5,
    "legend.frameon":     False,
})

# Mono tick/annotation text:
# ax.text(..., fontfamily=MONO, fontsize=8, color=TH["sub"])
```

Web/SVG export: name light/dark variants explicitly (`*_light.svg`, `*_dark.gif`).

---

## 7. Do / Don't

**Do**
- Keep it monochrome; reserve `#FA6D0F` for the single thing the eye should land on.
- Use mono, lowercase, muted-grey labels.
- Remove top/right spines; use faint gridlines, not boxes.
- Export matched light + dark variants.
- Encode extra categories with dash/shape/position before adding hue.

**Don't**
- Don't use drop shadows or gradients (except the subtle dark-theme glow).
- Don't use bold, heavy headings or default matplotlib blue/orange/green.
- Don't put more than ~5 hues in one chart.
- Don't use pure `#000000` — brand black is `#0C0C0C` / `#171717`.
- Don't mix the orange and violet accents at equal weight; orange leads.
