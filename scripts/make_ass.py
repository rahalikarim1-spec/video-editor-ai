"""Generate word-by-word TikTok-style ASS captions. usage: make_ass.py en|fr out.ass"""
import json, re, sys
lang, out = sys.argv[1], sys.argv[2]
plan = json.load(open("subtitles/cutplan.json")); groups = plan["groups"]; total = plan["total"]
fr = json.load(open("subtitles/french_groups.json"))
KEY = {"en": {"crash","nürburgring","google","penalty","thousands","500","daily","extreme","incidents","crashes","opinion","blame","video","footage","license"},
       "fr": {"accident","nürburgring","google","sanction","milliers","500","jours","extrêmes","incidents","accidents","avis","responsable","images","licence"}}[lang]
FONT = "DejaVu Sans"
def ts(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{FONT},78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,300,1
[Events]
Format: Layer,Start,End,Name,Style,MarginL,MarginR,MarginV,Effect,Text
"""
WHITE, YELLOW, GREEN = r"{\c&HFFFFFF&}", r"{\c&H00E5FF&}", r"{\c&H5CFF3C&}"   # BGR
ev = []
for gi, g in enumerate(groups):
    gs = g[0]["ns"]; ge = g[-1]["ne"]
    nxt = groups[gi+1][0]["ns"] if gi+1 < len(groups) else total
    ge = min(max(ge, gs+0.3), nxt - 0.02) if nxt - ge < 0.35 else ge + 0.15
    if lang == "en":
        toks = [(re.sub(r"[^\w']", "", w["w"]).lower(), w["w"].upper(), w["ns"]) for w in g]
    else:
        ws = fr[gi].split(); wts = [len(x)+1 for x in ws]; tot = sum(wts); acc = 0; toks = []
        for x, wt in zip(ws, wts):
            toks.append((re.sub(r"[^\w']", "", x).lower(), x.upper(), gs + (ge-gs)*acc/tot)); acc += wt
    for i, (key, txt, st) in enumerate(toks):
        en = toks[i+1][2] if i+1 < len(toks) else ge
        parts = []
        for j, (k2, t2, _) in enumerate(toks):
            base = GREEN if k2 in KEY else WHITE
            parts.append((YELLOW if j == i else base) + (r"{\fscx112\fscy112}" if j == i else r"{\fscx100\fscy100}") + t2)
        ev.append(f"Dialogue: 0,{ts(st)},{ts(max(en, st+0.05))},,Cap,0,0,0,,{' '.join(parts)}")
open(out, "w").write(hdr + "\n".join(ev) + "\n")
print(out, len(ev), "events")
