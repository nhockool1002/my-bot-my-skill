#!/usr/bin/env python3
"""
Assemble the final Vietnamese .srt by pairing the timestamps of the
English chunked SRT (from chunk_subtitles.py) with a plain-text file of
Vietnamese translations — one line per cue, same order, no blank lines.

The translation itself is NOT done by this script. Claude writes
vi_lines.txt by hand (or has it written), following
../references/glossary_do_not_translate.md so product/technical terms
stay in English. This script only does the mechanical part: line-count
validation, word-wrapping to <= 2 short lines per cue, and re-attaching
the original timestamps.

Usage:
    python3 assemble_vi_srt.py <en_chunked.srt> <vi_lines.txt> <output_vi.srt> [wrap_width]
"""
import re
import sys
import textwrap


def parse_timestamps(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"\n\n+", text.strip())
    ts = []
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) < 2:
            continue
        m = re.match(r"(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)", lines[1])
        if m:
            ts.append((m.group(1), m.group(2)))
    return ts


def wrap_vi(text, width=42):
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    if not lines:
        return text
    return "\n".join(lines[:2])


def write_srt(ts_list, vi_list, out_path, width):
    if len(ts_list) != len(vi_list):
        sys.exit(
            f"Line-count mismatch: {len(ts_list)} cues in the English chunked "
            f"SRT but {len(vi_list)} lines in the Vietnamese text file. "
            "Every cue needs exactly one line, in the same order — fix "
            "vi_lines.txt and re-run (do not guess an alignment)."
        )
    with open(out_path, "w", encoding="utf-8") as f:
        for i, ((start, end), text) in enumerate(zip(ts_list, vi_list), 1):
            f.write(f"{i}\n{start} --> {end}\n{wrap_vi(text, width)}\n\n")
    print(f"Wrote {len(ts_list)} cues to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print(__doc__)
        sys.exit(1)
    en_srt, vi_txt, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    width = int(sys.argv[4]) if len(sys.argv) == 5 else 42
    ts_list = parse_timestamps(en_srt)
    vi_list = open(vi_txt, encoding="utf-8").read().splitlines()
    write_srt(ts_list, vi_list, out_path, width)
