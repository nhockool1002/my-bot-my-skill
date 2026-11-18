---
name: Harvey_Weekly_Sync_Meeting_Sub_Creator
description: Generate Vietnamese-translated .srt subtitles for Harvey.ai weekly FN (Field/Functional) sync meeting recordings, plus a plain-language breakdown in chat of what each recording is demoing (feature name(s), what testers need to test, any caveat the speaker flags). Input is one or more local video files (the weekly sync recordings, e.g. "Applause & Harvey.AI - weekly FN sync - ... - Recording.mp4") given as file paths. Runs fully local — ffmpeg extracts audio, whisper.cpp (whisper-cli) transcribes English with word-level timestamps, a script re-chunks those into short subtitle-length cues, Claude translates each cue into natural Vietnamese while keeping Harvey product/feature names and UI labels in English per a glossary, then a script re-wraps and re-attaches timestamps into the final .srt. Output is one Vietnamese .srt per input video (named after the source video) plus the meeting-analysis write-up, delivered to the user. Use proactively whenever the user gives one or more Harvey weekly sync meeting recordings and asks for subtitles/sub, dịch sub, phụ đề tiếng Việt, or "cho biết video này test gì" — even without naming this skill.
---

# Harvey Weekly Sync Meeting — Subtitle Creator

## What this skill is for

Every week, someone on the Harvey.ai side records a short sync call
walking through what needs testing next ("weekly FN sync"). The TTL/testers
need two things out of each recording: a Vietnamese subtitle file they can
actually watch the recording with, and a quick written summary of what
feature(s) are being demoed and what to test — without having to sit
through the whole video first. This skill produces both, for one video or
a whole batch at once, and is meant to be reused every week as new
recordings come in (see `references/setup_requirements.md` for why the
heavier local model and persistent cache path matter for that).

This was built by generalizing a one-off manual run on two real Harvey
weekly sync recordings (2026-11-17) covering the Word add-in contract
review flow and the Outlook add-in meeting-scheduling flow — see
`references/meeting_analysis_template.md` for what a good write-up from
that run looked like.

## Inputs you need

1. **One or more local video file paths**, as given by the user (any
   format `ffmpeg` reads — `.mp4` is the common case here). Process every
   file given; don't go looking for other recordings in the same folder
   unless the user asks for that.
2. Nothing else — no API, no login, no attachment beyond the video files
   themselves. If the recording's audio is in a language other than
   English, ask the user before assuming — `transcribe.sh`'s language
   flag defaults to `en`.

## Step 0 — Confirm local tooling is ready

Check `ffmpeg`, `whisper-cli`, and the cached model per
`references/setup_requirements.md`. If `ffmpeg` or `whisper-cli` is
missing, try installing it (`brew install ffmpeg` / `brew install
whisper-cpp`) rather than giving up immediately, but tell the user what
you're installing. If install isn't possible, say so plainly — don't fall
back to a lower-quality substitute silently.

## Step 1 — Extract audio (per video)

```bash
bash scripts/extract_audio.sh "<video path>" "<work_dir>/<basename>.wav"
```

Use a scratch/temp work directory for intermediate files (wav/json/raw
srt) — only the final `.vi.srt` files and the chat write-up are the actual
deliverables.

## Step 2 — Transcribe with word-level timestamps (per video)

```bash
bash scripts/transcribe.sh "<work_dir>/<basename>.wav" "<work_dir>/<basename>"
```

This writes `<basename>.json` (word-level detail — what the next step
needs) and `<basename>.srt` (whisper's own long-cue version, reference
only, not the deliverable).

## Step 3 — Re-chunk into subtitle-length English cues (per video)

```bash
python3 scripts/chunk_subtitles.py "<work_dir>/<basename>.json" "<work_dir>/<basename>_en_chunked.srt"
```

Read the result. If you see obvious word-join artifacts (rare, but
whisper sometimes mis-tokenizes a name) fix them by eye before moving on
— don't translate a garbled source.

## Step 4 — Translate every cue to Vietnamese

Read `<basename>_en_chunked.srt` in full (for context) and
`references/glossary_do_not_translate.md` and
`references/subtitle_style_guide.md`. Then write
`<work_dir>/<basename>_vi_lines.txt`: **exactly one line per cue, in the
same order as the chunked SRT, no blank lines** — this is the part only
Claude does; nothing here is scriptable, since it needs real
comprehension of the demo to translate well and to apply the
do-not-translate glossary correctly.

## Step 5 — Assemble the final Vietnamese .srt (per video)

```bash
python3 scripts/assemble_vi_srt.py "<work_dir>/<basename>_en_chunked.srt" "<work_dir>/<basename>_vi_lines.txt" "<work_dir>/<original video basename>.vi.srt"
```

The script refuses to run on a line-count mismatch rather than silently
misaligning cues — if it does, re-check Step 4's output, don't force it.

## Step 6 — Write the meeting analysis

For each video, produce the write-up described in
`references/meeting_analysis_template.md` (feature name(s), what's being
tested per flow, any caveat/discrepancy the speaker calls out, any
scheduling/data-prerequisite note). Show this in the chat response itself
— it's as much the deliverable as the .srt file.

## Step 7 — Deliver

Send every `<original video basename>.vi.srt` file to the user (one per
input video), together with the Step 6 write-up for the whole batch.
Mention which local STT model/tooling was used and that translation was
done by Claude directly (not a machine-translate pass), so the user knows
to spot-check names/jargon rather than assuming a third-party MT quality
bar.

## Scaling to a batch of videos

Run Steps 1–5 per video independently (they don't depend on each other),
but do Step 6 after processing is done, covering the whole batch together
per `references/meeting_analysis_template.md`'s guidance on multi-video
batches (e.g. noting when two recordings are two halves of one sync).
