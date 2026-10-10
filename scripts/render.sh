#!/usr/bin/env bash
# usage: render.sh subtitles.ass out.mp4   (first 60s of input/source.mp4, jump-cut, 1080x1920)
set -euo pipefail
ASS="$1"; OUT="$2"
FC=$(python3 - <<'PY'
import json
p=json.load(open("subtitles/cutplan.json")); n=len(p["segs"]); f=[]
for i,s in enumerate(p["segs"]):
    f.append(f"[0:v]trim={s['cs']:.3f}:{s['ce']:.3f},setpts=PTS-STARTPTS[v{i}]")
    d=s['ce']-s['cs']
    f.append(f"[0:a]atrim={s['cs']:.3f}:{s['ce']:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d-0.015:.3f}:d=0.015[a{i}]")
f.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]")
print(";".join(f))
PY
)
FC="$FC;[cv]split[bg0][fg0];[bg0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:5,eq=brightness=-0.08[bg];[fg0]scale=1080:1080:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2-60,ass=${ASS}:fontsdir=/usr/share/fonts/truetype/dejavu[outv]"
ffmpeg -v error -y -i input/source.mp4 -filter_complex "$FC" -map "[outv]" -map "[ca]" \
  -c:v libx264 -profile:v high -preset slow -crf 18 -pix_fmt yuv420p -r 30 -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 "$OUT"
