# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Cursor, Copilot, etc.). Part 1 is for agents **using** Dastkhat in someone's project. Part 2 is for agents **working on this repository**.

Dastkhat (دستخط) is a Persian and Latin UI typeface with geometric dots, published by [Dastyar](https://dastyar.io) under the [SIL OFL 1.1](OFL.txt). It is a derivative of [Vazirmatn](https://github.com/rastikerdar/vazirmatn).

---

## Part 1: Using Dastkhat in a project

### Pick the right file

| Situation | Use |
|---|---|
| Website or web app | `Webfonts/dastkhat.css` plus `Webfonts/fonts/*.woff2` |
| Design tool or desktop app | `fonts/Main/<Family>/TTF/*.ttf` (9 weights) |
| One file, every weight 100 to 900 | `fonts/Main/<Family>/Variable` |

Never install static and variable fonts of the same family on one machine. Identical family names conflict.

### Pick the right family

| Family | Dots | Default for |
|---|---|---|
| `Dastkhat` | Square | UI and body text. **Choose this unless told otherwise.** |
| `Dastkhat Diamond` | Square rotated 45° | A softer, classic look |
| `Dastkhat Bar` | Adjacent dots merge into bars | Logos, headlines, brand marks. Avoid for long text. |
| `Dastkhat Dots` | Circular | The same geometry, softer texture |
| `Dastkhat BarDots` | Adjacent circles merge into capsules | Rounded logos and headlines. Avoid for long text. |
| `Dastkhat Round` | Circular, and the letters have rounded stroke ends and corners | Soft, friendly interfaces and brands |
| `Dastkhat Mono` | Square, dotted zero | Code, terminals, tables. Latin, digits and symbols are fixed-width; Persian letters stay proportional because they join. Main build only (no FaNum or NoEn). |

### Arabic readers only

`Dastkhat Arabic` (+ ` ArNum` / ` NoEn`) is the main square-dot family without Persian-only letters (پ چ ژ گ ک ی), Persian digits and toman signs. Use it for Arabic-language products; ArNum shows Latin digits as Arabic-Indic `٠-٩`. Load `Webfonts/dastkhat-arabic.css`; variables `--font-dastkhat-arabic`, `--font-dastkhat-arabic-arnum`, `--font-dastkhat-arabic-noen`. Files: `fonts/Main/DastkhatArabic`, `fonts/ArNum/DastkhatArabicArNum`, `fonts/NoEn/DastkhatArabicNoEn`. Built by `sources/release_arabic.py`. Set `dir="rtl"` and `lang="ar"`.

### Pick the right build

| Build | Suffix | Use when |
|---|---|---|
| Main | none | Persian and Latin both needed |
| FaNum | ` FaNum` | Latin digits `0-9` should show as Persian `۰-۹` (prices, tables, dashboards). Underlying data and code stay Latin. |
| NoEn | ` NoEn` | Persian only; the project pairs it with its own Latin font (Inter, Geist, ...) |

### Web setup

```html
<link rel="stylesheet" href="/Webfonts/dastkhat.css">
<style>
  body   { font-family: var(--font-dastkhat); }
  .price { font-family: var(--font-dastkhat-fanum); }
  .logo  { font-family: var(--font-dastkhat-bar); font-weight: 900; }
</style>
```

CSS variables: `--font-dastkhat`, `--font-dastkhat-diamond`, `--font-dastkhat-bar`, `--font-dastkhat-dots`, `--font-dastkhat-bardots`, `--font-dastkhat-round`, `--font-dastkhat-round-fanum`, `--font-dastkhat-fanum`. Read `Webfonts/dastkhat.css` for the full list before inventing a name.

- Variable families are named exactly `Dastkhat`, `Dastkhat Diamond`, `Dastkhat Bar`, `Dastkhat Dots`, `Dastkhat BarDots`, `Dastkhat Round` (+ ` FaNum` / ` NoEn`) and `Dastkhat Mono`. Static families use the same names plus ` Static`.
- Variable fonts accept any `font-weight` from 100 to 900.
- Preload the main file for first paint: `<link rel="preload" href="/Webfonts/fonts/Dastkhat-Variable.woff2?v=1.220" as="font" type="font/woff2" crossorigin>`. Keep the `?v=` identical to the one in `dastkhat.css`, or the browser downloads the font twice.
- Keep `font-display: swap` (already set in the stylesheet).
- Always declare a fallback stack, for example `var(--font-dastkhat), system-ui, sans-serif`.

### Persian typography rules agents often get wrong

- Set `dir="rtl"` and `lang="fa"` on the container. Do not fake RTL with `text-align: right` alone.
- Use the half-space (ZWNJ, U+200C) inside compound words: «می‌خواهم», «کتاب‌ها», not a space or a joined form.
- Use Persian digits `۰-۹` in prose, or the FaNum build to get them from Latin digits. Do not hand-convert numbers inside code, IDs, URLs or data.
- Use Persian punctuation: `،` `؛` `؟` and «guillemets» for quotes.
- Mixed text: wrap Latin snippets (code, brand names, URLs) in `<span dir="ltr">` or use `unicode-bidi: isolate`.
- Use logical CSS properties (`margin-inline-start`, `padding-inline-end`, `inset-inline-*`) so layouts flip correctly.
- Persian needs more line height than Latin. Start at `line-height: 1.8` for body text and tighten for headings.
- Never apply `letter-spacing` to Persian or Arabic-script text. It breaks letter joining.
- Never apply `text-transform` expecting an effect on Persian.

### Currency signs

| Want | Use |
|---|---|
| Rial | `﷼` U+FDFC. Standard, works in any font. |
| Toman, as a sign | `U+E000` («ت» whose dots became two bars) or `U+E002` («ن» stacked over «توما») |
| Rial, compact, to pair with toman | `U+E001` (two stems crossed by «ر») |

The toman has no Unicode code point — the UTC rejected the 2017 proposal — so Dastkhat's toman signs are Private Use Area, which means they only render in Dastkhat. Write «تومان» as a word in anything that must survive a fallback font or a copy and paste.

Two opt-in features turn typed words into signs, so the source text stays readable:

```css
.price      { font-feature-settings: 'ss02'; }   /* تومان, ریال -> compact signs */
.price-long { font-feature-settings: 'ss03'; }   /* تومان -> stacked sign, ریال -> ﷼ */
```

Neither is on by default. Don't hand-substitute the PUA characters into data, IDs or URLs; use the feature, or the plain word.

### Licensing, in short

- The font is free to use, embed, modify and redistribute under OFL 1.1, including commercially. It may not be sold by itself.
- Keep `OFL.txt` with any redistributed copy.
- `OFL.txt` declares no Reserved Font Name, but a derivative should still carry the copyright notices and the same license.
- Never claim a different license for the font files.

---

## Part 2: Working on this repository

### Layout

```
sources/      Build scripts and UFO sources (the source of truth)
  ufo/         Dastkhat, DastkhatDiamond, DastkhatBar, DastkhatDots, DastkhatBarDots, DastkhatRound, DastkhatMono (.designspace + UFOs)
  build_all.sh     Full rebuild from UFO to release set
  release_fonts.py Produces Main / FaNum / NoEn as TTF + WOFF2
  gen_pages.py     Generates the HTML demo pages
  round_dots.py    Derives the DastkhatDots and DastkhatBarDots UFOs from the square and bar ones
  make_mono.py     Derives the DastkhatMono UFOs from the Dastkhat ones (fixed cell, dotted zero)
  round_corners.py Derives the DastkhatRound UFOs from the DastkhatDots ones (rounded corners); run after round_dots.py
  patch_ufo_gf.py, extract_ufo.py, render_all.js   Maintenance helpers
fonts/       Built output: Main/, FaNum/, NoEn/ per family
Webfonts/    dastkhat.css, WOFF2 files, webfont-test.html
Demos/       Demo pages, assets/, images/ (generated)
Specimen/    Dastkhat-Specimen.pdf (generated)
Landing/     Persian landing page: index.html, style.css, app.js
Helps/       Installation and usage guide (guide.html)
License/     Third-party notices
docs/        PUBLISHING-GUIDE.md
```

Top level: `README.md` (Persian), `README.en.md` (English), `راهنما.md`, `CONTRIBUTING.md`, `FONTLOG.txt`, `OFL.txt`.

### Build the fonts

```bash
pip install fontmake fonttools brotli
sh sources/build_all.sh <output_dir>
```

Output: `<output_dir>/{Main,FaNum,NoEn}/<Family>/{Variable,TTF,Webfonts}`. Build into a scratch directory, inspect it, and only then copy into `fonts/` and `Webfonts/` when the task is a font release.

Run Python scripts with `python3 -I` as the scripts' own docstrings do.

### Preview the landing page

The landing page is plain HTML, CSS and JS with no build step, in right-to-left Persian. It references fonts via `../Webfonts/` so it must be served from the repo root.

```bash
python3 -m http.server 8765
# open http://localhost:8765/Landing/
```

`.claude/launch.json` defines this server as `dastkhat-landing`.

### Rules

1. **Binaries are off limits unless asked.** Do not regenerate or overwrite `fonts/`, `Webfonts/fonts/`, `Specimen/*.pdf` or `Demos/images/*.png` as a side effect of other work. They are large and produce noisy diffs.
2. **UFO sources are the truth.** Fix glyph problems in `sources/ufo/`, then rebuild. Never hand-edit built TTF/WOFF2 files.
3. **Version bumps touch several places.** Version `1.220` appears in `release_fonts.py` (`VERSION`, `VSTR`), `dastkhat.css`, `FONTLOG.txt`, both READMEs, the landing page and generated pages. Search for the old string before and after.
4. **Update `FONTLOG.txt`** for any visible font change and add contributors to the acknowledgements.
5. **Respect licensing.** Do not copy outlines from fonts with an incompatible license. Keep the Vazirmatn and Dastkhat copyright notices in `release_fonts.py` and `OFL.txt` intact. Latin glyphs derive from Roboto; keep `License/THIRD-PARTY-NOTICES.txt` accurate.
6. **Do not rename families** (`Dastkhat`, `Dastkhat Diamond`, `Dastkhat Bar`, `Dastkhat Dots`, `Dastkhat BarDots`, `Dastkhat Round`, `Dastkhat Mono`, ` FaNum`, ` NoEn`) or CSS variables. Users depend on them.
7. **Docs stay bilingual.** A change in `README.md` needs the matching change in `README.en.md`.
8. **One logical change per commit or PR**, with a clear explanation. See [CONTRIBUTING.md](CONTRIBUTING.md).

### Editing Persian copy (landing, docs, demos)

- Follow the typography rules in Part 1.
- Match the existing tone: short, direct, no marketing filler.
- Keep UI strings in Persian. Keep brand and technical names in Latin (`Dastkhat`, `WOFF2`, `GitHub`).
- Check the page at both desktop and phone widths. The nav hides secondary items under 768px.
- Don't add external scripts, trackers or CDN fonts. The page must work offline from the repo.

### Verifying your work

| Change | Check |
|---|---|
| CSS or HTML | Serve the repo and load `Landing/`, `Demos/`, `Webfonts/webfont-test.html`. No console errors, no 404s for fonts. |
| Font rebuild | Open `Webfonts/webfont-test.html` and `Demos/glyph-map.html`; check Persian joins, dots, digits (FaNum) and the absence of Latin in NoEn. |
| Docs | Links resolve; both languages agree. |

Report exactly what you ran and saw. If you could not verify something, say so.

### Do not

- Commit secrets, local paths, or `.DS_Store`.
- Add dependencies for the landing page.
- Rewrite history or push to `main` without being asked.
- Change the license or the EULA/OFL texts.

### Links

- Product and licensing site: https://dastyar.io
- Upstream: https://github.com/rastikerdar/vazirmatn
- Publishing notes: [docs/PUBLISHING-GUIDE.md](docs/PUBLISHING-GUIDE.md)
