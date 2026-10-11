#!/bin/sh
# Loudness-master the Remotion render for social: -14 LUFS, -1.5 dBTP, video stream copied as-is.
set -e
IN="${1:-out/tubedrop-promo.mp4}"
OUT="${2:-out/tubedrop-promo-final.mp4}"
STATS=$(ffmpeg -hide_banner -nostats -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$STATS" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -hide_banner -v error -y -i "$IN" -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,alimiter=limit=0.82:level=false,aresample=48000" \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
echo "mastered → $OUT"
