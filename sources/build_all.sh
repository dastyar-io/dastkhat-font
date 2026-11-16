#!/bin/sh
# Rebuild every Dastkhat font from the UFO sources.
#   pip install fontmake fonttools brotli
#   sh sources/build_all.sh <output_dir>
# Output: <output_dir>/{Main,FaNum,NoEn}/<Family>/{Variable,TTF,Webfonts}
set -e
OUT="${1:?usage: build_all.sh <output_dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
VF="$OUT/_vf"
mkdir -p "$VF"
for fam in Dastkhat DastkhatDiamond DastkhatBar; do
  fontmake -m "$HERE/ufo/$fam/$fam.designspace" -o variable --output-dir "$VF" --no-production-names
done
python3 -I "$HERE/release_fonts.py" "$OUT" "$VF"
rm -rf "$VF"
