#!/usr/bin/env python3
"""
Turn whisper.cpp's word-level JSON-full output into subtitle-friendly
English cues: short, readable lines timed off real word boundaries,
instead of whisper's own long auto-generated segments.

Usage:
    python3 chunk_subtitles.py <input_whisper.json> <output_en_chunked.srt>

Input is the *_ojf output of `whisper-cli ... -ojf -of <prefix>`, i.e.
"<prefix>.json" (NOT the plain .srt — this needs per-token timestamps).

See ../references/subtitle_style_guide.md for the segmentation rules this
implements (max line length, max duration, pause-based breaks, stray-chunk
merging) and why each threshold is set where it is.
"""
import json
import re
import sys


def load_words(json_path):
    d = json.load(open(json_path, encoding="utf-8"))
    words = []
    for seg in d["transcription"]:
        for tok in seg["tokens"]:
            text = tok["text"]
            if text.startswith("[_") or text.strip() == "":
                continue
            start_s = tok["offsets"]["from"] / 1000.0
            end_s = tok["offsets"]["to"] / 1000.0
            words.append((text, start_s, end_s))
    return words


def fmt_ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_chunks(words, max_chars=80, max_dur=6.5, max_gap=1.4, min_words_for_break=4):
    """Group whisper tokens into cues.

    A cue breaks on: a long pause (> max_gap, only once the cue already has
    a few words so we don't fragment on every little hesitation), a hard
    length/duration cap, or a sentence-ending punctuation mark. Tokens keep
    whisper's own leading-space convention, so within one cue we must NOT
    insert extra spaces (continuation sub-word tokens have none); across a
    flush/merge boundary a space is always correct, since flush only ever
    happens between whole words.
    """
    chunks = []
    cur = []
    cur_text = ""

    def flush():
        nonlocal cur, cur_text
        if cur:
            start = cur[0][1]
            end = cur[-1][2]
            text = cur_text.strip()
            if text and not re.fullmatch(r"[.,!?]+", text):
                chunks.append((start, end, text))
        cur = []
        cur_text = ""

    prev_end = None
    for text, start, end in words:
        gap = (start - prev_end) if prev_end is not None else 0
        tentative = cur_text + text
        enough_words = len(cur) >= min_words_for_break
        strong_break = prev_end is not None and gap > max_gap and enough_words
        too_long_chars = len(tentative.strip()) > max_chars
        too_long_dur = cur and (end - cur[0][1]) > max_dur
        ends_sentence = (
            prev_end is not None
            and enough_words
            and cur_text.rstrip()
            and cur_text.rstrip()[-1] in ".?!"
        )
        if cur and (strong_break or too_long_chars or too_long_dur or ends_sentence):
            flush()
        cur.append((text, start, end))
        cur_text += text
        prev_end = end
    flush()

    # Merge stray short chunks (artifacts of pause/length heuristics) into
    # the previous one. Chunks are always word-boundary text, so a plain
    # space join is always correct here.
    merged = []
    for start, end, text in chunks:
        is_stray = len(text.strip()) < 14 or (end - start) < 0.9
        fits = merged and len(merged[-1][2]) + len(text) < max_chars + 20
        if merged and is_stray and fits:
            ps, _, ptext = merged[-1]
            merged[-1] = (ps, end, ptext + " " + text)
        else:
            merged.append((start, end, text))
    return merged


def write_srt(chunks, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(chunks, 1):
            f.write(f"{i}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}\n\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    json_path, out_path = sys.argv[1], sys.argv[2]
    words = load_words(json_path)
    chunks = build_chunks(words)
    write_srt(chunks, out_path)
    print(f"{len(chunks)} cues written to {out_path}")
