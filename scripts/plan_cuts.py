"""Build jump-cut plan + caption groups from word timestamps (first 60s test)."""
import json, sys
GAP, PAD = 0.30, 0.07           # cut gaps longer than GAP, keep PAD of room around speech
DROP = {(17.6,17.84),(17.84,18.44),(18.5,18.7),   # "so yeah, but"
        (33.66,34.02),                              # "well,"
        (49.32,50.48)}                              # hesitant "and"
d = json.load(open("subtitles/transcript_words.json"))
words = [w for w in d["words"] if (w["s"], w["e"]) not in DROP and w["e"] <= 59.95]
# fix: the stretched "and" etc. use start only
segs = []
for w in words:
    if segs and w["s"] - segs[-1]["e"] <= GAP:
        segs[-1]["e"] = w["e"]; segs[-1]["words"].append(w)
    else:
        segs.append({"s": w["s"], "e": w["e"], "words": [w]})
t = 0.0
for sg in segs:
    sg["cs"] = max(0, sg["s"] - PAD); sg["ce"] = sg["e"] + PAD
    sg["off"] = t; t += sg["ce"] - sg["cs"]
for i in range(1, len(segs)):  # avoid overlap between neighbours
    pass
for sg in segs:
    for w in sg["words"]:
        w["ns"] = sg["off"] + w["s"] - sg["cs"]; w["ne"] = sg["off"] + w["e"] - sg["cs"]
        # a stretched word shouldn't linger on screen
        w["ne"] = min(w["ne"], w["ns"] + 0.6)
# caption groups: <=4 words / <=22 chars, break at punctuation, segment end
groups, cur = [], []
for sg in segs:
    for w in sg["words"]:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        if w["w"][-1] in ",.?!" and len(cur) >= 2 or len(cur) >= 4 or len(txt) >= 24 or w is sg["words"][-1]:
            groups.append(cur); cur = []
if cur: groups.append(cur)
json.dump({"segs":[{k:v for k,v in s.items() if k!="words"} for s in segs],
           "groups":[[{"w":w["w"],"ns":w["ns"],"ne":w["ne"]} for w in g] for g in groups],
           "total":t}, open("subtitles/cutplan.json","w"), indent=1, ensure_ascii=False)
print(f"{len(segs)} segments, total {t:.2f}s (from 60s)")
for i,g in enumerate(groups): print(i, round(g[0]["ns"],2), " ".join(w["w"] for w in g))
