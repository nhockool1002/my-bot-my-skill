# Subtitle segmentation & translation style

## Why re-chunk at all

Whisper's own auto-generated segments are built for the *model's*
convenience (often 15–30+ seconds, a full run-on sentence per cue) — fine
as a transcript, bad as a subtitle: a viewer can't read that much text
before it vanishes, and a long cue hides which specific words were spoken
when. `scripts/chunk_subtitles.py` re-cuts the word-level timestamps into
much shorter cues before anything gets translated.

## The cutting rules (as implemented)

A cue ends when any of these trigger, in order of priority:
1. **Hard length cap** — text would exceed ~80 characters.
2. **Hard duration cap** — cue would exceed ~6.5 seconds.
3. **Sentence-ending punctuation** (`.` `?` `!`) already seen, *and* the
   cue already has at least 4 words (so "Okay." doesn't become its own cue
   every time someone says it mid-sentence pause).
4. **A long pause** (> 1.4s gap to the next word), again only once the cue
   already has at least 4 words.

After the first pass, any stray very short chunk (< 14 characters or
< 0.9s — almost always a single trailing word split off by a pause, e.g.
"one." landing alone) gets merged back onto the previous cue rather than
flashing on screen by itself for a fraction of a second.

**Don't loosen the 4-word minimum or the pause threshold without checking
real output** — earlier, looser versions of this logic produced isolated
one-word cues ("seconds.", "reject", "one") that looked broken on screen.

## Translating each cue (Claude's job, not a script's)

- Read the **whole** English chunked transcript first, not cue-by-cue in
  isolation — a cue often ends mid-clause by design (see above), and you
  need the next cue's text to translate the current one naturally.
- One Vietnamese line **per English cue, in the same order, one line per
  cue in `vi_lines.txt`** — `assemble_vi_srt.py` will refuse to run if the
  line counts don't match, rather than silently misaligning timestamps.
  If a cue's translation doesn't read as a complete thought on its own,
  that's fine and expected (so is the English source) — don't artificially
  merge or split cues to "fix" it, since that breaks the 1:1 mapping back
  to `assemble_vi_srt.py`'s timestamps.
- Keep each Vietnamese line able to wrap to **two lines of ≤ 42
  characters** (`assemble_vi_srt.py`'s default) without losing words —
  i.e. don't write a Vietnamese line dramatically longer than its English
  source. If a cue's English source is already near the 80-char cap, aim
  for a Vietnamese line under roughly 80–85 characters too; it's fine if
  Vietnamese runs a little longer than English here and there, just not
  so much that it needs 3+ wrapped lines.
- Apply `glossary_do_not_translate.md` — product names, UI labels and
  technical nouns stay in English inside otherwise-Vietnamese sentences.
- Register: natural spoken Vietnamese for a work meeting (how a TTL or TE
  actually talks to colleagues), not stiff literal/formal translation —
  contractions and filler ("kiểu như", "đúng không?") are fine where the
  English has them ("like", "right?"), since these are live demo
  recordings full of verbal filler, not scripted prose.
- A long silence in the source (e.g. the speaker is clicking through the
  UI without narrating) produces one real cue spanning many seconds with
  little text — leave it as-is; don't invent words to fill the time, and
  don't force-split it into multiple empty-ish cues.

## Final wrap

`assemble_vi_srt.py` wraps each line to at most 2 lines of ≤ 42 characters
(`textwrap`, no mid-word breaks) and re-attaches the exact timestamps from
the English chunked SRT. If a translated line is so long it would need a
3rd line, that's a sign the cue needs re-splitting upstream — raise it
rather than letting the wrapper silently drop the overflow text (it keeps
only the first 2 wrapped lines).
