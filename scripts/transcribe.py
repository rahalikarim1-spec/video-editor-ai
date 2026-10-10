import sys, json
from faster_whisper import WhisperModel
wav, out, size = sys.argv[1], sys.argv[2], sys.argv[3]
m = WhisperModel(size, device="cpu", compute_type="int8", download_root="temp/models")
segs, info = m.transcribe(wav, word_timestamps=True, vad_filter=False, beam_size=5)
res = {"language": info.language, "prob": info.language_probability, "words": []}
for s in segs:
    for w in s.words:
        res["words"].append({"w": w.word.strip(), "s": round(w.start,3), "e": round(w.end,3)})
json.dump(res, open(out,"w"), ensure_ascii=False, indent=1)
print(info.language, info.language_probability, len(res["words"]))
