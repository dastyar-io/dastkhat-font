Title: Font request: Dastkhat (Persian and Latin UI typeface)

Hello Google Fonts team, and thank you for the guidance on my earlier pull requests (#11268, #11269, #11270). I am opening this issue so you can review the font first, as you suggested.

## Font

**Dastkhat** (دستخط) is a Persian (Arabic script) and Latin UI typeface with geometric dots, built for product interfaces, e-commerce pages and dense Persian text on screens.

- Repository: https://github.com/dastyar-io/dastkhat-font
- Version: 1.210
- License: SIL Open Font License 1.1 (`OFL.txt` in the repo)
- Publisher: Dastyar (https://dastyar.io)
- Designer / maintainer: Alireza Eskandari

## What is in the family

| Family | Description |
|---|---|
| Dastkhat | Square dots. The main family. |
| Dastkhat Diamond | Square dots rotated 45 degrees. |
| Dastkhat Bar | Adjacent dots merge into bars. For headlines and brand marks. |

Each family is a variable font on the `wght` axis (100 to 900) with 9 named instances. I understand that Google usually takes one family per submission, so I propose **Dastkhat first**, with Diamond and Bar as separate follow-ups if you want them.

## Origin and credit

- Dastkhat is a derivative of **Vazirmatn** by Saber Rastikerdar (OFL 1.1): https://github.com/rastikerdar/vazirmatn. His copyright notice is kept in the font and in `OFL.txt`.
- The Latin glyphs reach us through Vazirmatn and derive from **Roboto** (Apache 2.0). The notice is in `License/THIRD-PARTY-NOTICES.txt`.

## Sources and tooling

- Editable sources: UFO masters and designspace in `sources/ufo/`
- Build recipe: `sources/config.yaml` and `sources/build_all.sh`
- Ready-made `METADATA.pb` and `DESCRIPTION.en_us.html` per family in `GoogleFonts/`
- Font Bakery `check-googlefonts`: 0 FAIL on the variable font and the nine statics of the main family

Known non-blocking warnings: vendor ID `DSTY` is not registered, hhea line height is 1.56 em (Persian needs tall metrics), and there are no ligature carets yet.

## Images

Specimen images are in the repo under `Demos/images/` (cover, dot styles, weights, UI sample, glyph map).

## Questions for the team

1. Is Dastkhat a fit for the catalog?
2. Do you prefer the three families submitted separately, as I proposed?
3. Is there anything you want changed in the sources or metadata before review?

I have signed the Google CLA. Thank you for your time.
