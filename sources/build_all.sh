#!/bin/sh
# Rebuild every Dastkhat font from the UFO sources.
#   pip install fontmake fonttools brotli
#   sh sources/build_all.sh <output_dir>
# Output: <output_dir>/{Main,FaNum,NoEn}/<Family>/{Variable,TTF,Webfonts}
# (DastkhatMono is Main only). Its UFOs are derived from Dastkhat by make_mono.py.
# DastkhatRound's UFOs are derived from DastkhatDots by round_corners.py.
# plus the Arabic-only cut of Dastkhat (release_arabic.py): Main, ArNum and NoEn builds of DastkhatArabic.
set -e
OUT="${1:?usage: build_all.sh <output_dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
VF="$OUT/_vf"
mkdir -p "$VF"
for fam in Dastkhat DastkhatDiamond DastkhatBar DastkhatDots DastkhatBarDots DastkhatRound DastkhatMono; do
  fontmake -m "$HERE/ufo/$fam/$fam.designspace" -o variable --output-dir "$VF" --no-production-names
done
python3 -I "$HERE/release_fonts.py" "$OUT" "$VF"
python3 -I "$HERE/release_arabic.py" "$OUT" "$VF/Dastkhat-VF.ttf"
rm -rf "$VF"
