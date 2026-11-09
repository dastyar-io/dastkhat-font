# Making Dastkhat a successful open font

A practical checklist, in the order that matters.

## 1. Quality gate before you announce (1-2 weeks)
Open fonts live or die on technical quality. Run these and fix every FAIL:
```bash
pip install fontbakery gftools fonttools
fontbakery check-googlefonts Fonts/Main/Dastkhat/TTF/*.ttf
fontbakery check-googlefonts "Fonts/Main/Dastkhat/Variable/Dastkhat[wght].ttf"
```
Also check: Persian shaping in Chrome, Safari, Firefox, Word, Figma, Photoshop; digits, ZWNJ (half-space), kashida, Arabic-Indic vs Persian digits, kerning in dense UI text, hinting/rendering on Windows. Test with real Persian pages, not just specimens.

## 2. Repo hygiene (done / to do)
- [x] `OFL.txt`, copyright and license in font name table
- [x] `FONTLOG.txt`, `CONTRIBUTING.md`, `FUNDING.yml`
- [ ] Put editable **source files** in the repo (Glyphs/UFO/designspace). Google Fonts, forks and contributors need sources, and a font with only binaries is not really open source. `Source/` has build scripts but not the master outlines.
- [ ] Add GitHub topics: `font`, `persian`, `farsi`, `arabic-script`, `open-font`, `variable-font`, `ofl`
- [ ] Create a GitHub Release with a ZIP, and add GitHub issue templates
- [ ] Add a short `OFL-FAQ` link and a screenshot-heavy README (already strong)

## 3. Distribution (publish everywhere)
| Channel | How | Notes |
|---|---|---|
| **GitHub Releases** | Attach `Dastkhat-v1.200.zip` | Your canonical download |
| **npm / Fontsource** | `npm publish`, or PR to fontsource/font-files | Lets devs `npm i @fontsource/dastkhat`. Huge for web adoption |
| **jsDelivr CDN** | Free, automatic from GitHub/npm | `cdn.jsdelivr.net/gh/dastyar-io/dastkhat-font@v1.200/...` |
| **Google Fonts** | PR to `google/fonts`, or issue at `google/fonts` "New font" | Highest reach; strict quality review; they will require sources and may ask for family consolidation |
| **Homebrew / package managers** | `brew install --cask font-dastkhat` via homebrew-cask-fonts | Mac designers |
| **Font Library, Open Font Library** | Upload ZIP | OFL friendly |
| **Figma / Canva / Adobe** | Only via Google Fonts inclusion | Another reason to pursue Google Fonts |
| **Persian communities** | Virgool, Twitter/X, Telegram, Persian Dribbble/Behance, FarsiNet, Reddit r/graphic_design | Your core audience |

## 4. Make people want to use it
- A **landing page** with live type tester (you have one in `Demos/`: host it with GitHub Pages at a short URL).
- **Real-world demos**: a fake e-commerce page, dashboard, article. UI fonts are chosen by developers who want copy-paste.
- **One-line install** on the front page of the README for CSS, npm and Figma.
- Give **three clear choices**, not 27 files. Lead with `Dastkhat` Main; explain Diamond/Bar/FaNum/NoEn as options.
- Compare honestly with Vazirmatn, Yekan Bakh, IRANSans, Estedad so people know why to pick yours.
- Ship **Persian digits** by default decisions clearly documented (FaNum).

## 5. Build community
- Respond to issues within 48 hours at first. Tag `good first issue`.
- Publish a roadmap (Kurdish, Pashto, Urdu extras, italics/slanted, ss01 alternates).
- Release on a rhythm (monthly patches, semver-like version numbers) and keep `FONTLOG.txt` current.
- Ask early adopters (startups, Persian blogs) for a testimonial and a logo on the site.

## 6. Sustain it
- GitHub Sponsors / Open Collective button (the FUNDING file is added).
- Paid, optional services through Dastyar: custom weights, brand versions, extra scripts, consulting.
- Keep the font name "Dastkhat" a **trademark** of Dastyar (already in name ID 7). OFL permits this and it protects your brand.

## 7. Legal safety
- You derive from Vazirmatn (OFL). OFL derivatives **must** stay OFL, so the earlier commercial EULA could not legally apply to the derived glyphs; the switch fixes that.
- Keep Vazirmatn's copyright line and credit Saber Rastikerdar prominently.
- Latin from Roboto (Apache 2.0): keep the notice in `License/THIRD-PARTY-NOTICES.txt`.
- Not legal advice. A short consult with an IP lawyer is cheap insurance before registering the trademark.
