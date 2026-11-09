# Submitting Dastkhat to Google Fonts

Everything Google asks for is prepared. Font Bakery (`check-googlefonts`) reports **0 FAIL** on the Main `Dastkhat` variable font and all nine statics.

## What is in the repo
| Need | Where |
|---|---|
| License | `OFL.txt` (Google's canonical body text, one copyright line) |
| Editable sources | `Source/ufo/Dastkhat/` (3 UFO masters + designspace) |
| Build recipe | `Source/config.yaml`, `Source/build_all.sh` |
| Fonts | `Fonts/Main/Dastkhat/Variable/Dastkhat[wght].ttf` |
| Metadata | `GoogleFonts/<Family>/METADATA.pb` and `DESCRIPTION.en_us.html` |

## Steps
1. Push this repo to **github.com/dastyar-io/dastkhat-font** (public) and tag a release: `git tag v1.201 && git push --tags`.
2. Fork `github.com/google/fonts`, then create `ofl/dastkhat/` and copy in:
   `OFL.txt`, `Dastkhat[wght].ttf`, `DESCRIPTION.en_us.html`, `METADATA.pb` (all from the places above).
   Fill `commit:` in the `source { }` block of `METADATA.pb` with the release commit hash.
3. Run the same checks Google runs and fix anything new:
   ```bash
   pip install fontbakery gftools
   fontbakery check-googlefonts "ofl/dastkhat/Dastkhat[wght].ttf"
   ```
4. Open the pull request. In the description state: designer(s), that it is OFL, that it derives from Vazirmatn (OFL) with credit, the languages covered, and the source repo.
5. A Google Fonts reviewer will comment. Typical asks: a designer profile (`catalog/designers/...` with a photo and bio), proof images, and a review of the Latin glyphs. Reply in the PR.

## Know before you submit
- Google usually accepts **one family per submission**. Submit `Dastkhat` first. Diamond and Bar can follow as separate families once the first is live. FaNum and NoEn builds are not distributed through Google Fonts.
- **Vazirmatn is OFL.** Credit Saber Rastikerdar. A friendly message to him before the PR is good manners and avoids surprises.
- Capital sharp S (U+1E9E) is a first draft derived from ß; have the designer review it. The new combining marks are built from the spacing accents.
- Remaining non-blocking Font Bakery warnings: vendor ID `DSTY` is not registered, hhea line height is 1.56 of the em (Persian needs tall metrics), no ligature carets, and no article/images yet.
- The sources are extracted from the compiled Vazirmatn-based build rather than hand-drawn masters, but they compile back to the same shaping and outlines (verified against the previous release at 5 weights).
