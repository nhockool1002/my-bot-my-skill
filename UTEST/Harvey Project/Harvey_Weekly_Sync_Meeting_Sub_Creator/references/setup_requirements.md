# Local tooling this skill needs

Everything runs **fully local and offline-capable** (no paid STT API, no
cloud transcription service) — only `ffmpeg` and `whisper.cpp` plus a
one-time model download.

## Required

- **ffmpeg / ffprobe** — audio extraction and duration checks.
  `brew install ffmpeg` (macOS). Check with `which ffmpeg ffprobe`.
- **whisper.cpp's `whisper-cli`** — local speech-to-text with word-level
  timestamps. `brew install whisper-cpp`. Check with `which whisper-cli`.
- **A ggml Whisper model**, cached once and reused for every future
  meeting: `$HOME/.cache/whisper-cpp/models/ggml-small.bin` (~480 MB).
  `scripts/transcribe.sh` downloads it automatically the first time it's
  missing, from
  `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin`.
  **Do not re-download it per video** — it's meant to live in that cache
  path across sessions, not in a scratch/temp directory that gets cleared.

Check all three before starting a batch:

```bash
which ffmpeg ffprobe whisper-cli
ls -la "$HOME/.cache/whisper-cpp/models/ggml-small.bin" 2>/dev/null || echo "model will be downloaded on first transcribe"
```

## Why "small" and not "tiny" or "medium"

- `tiny`/`base` mis-hear product names and jargon far more often (tested:
  "Assistant Thread" → "Assistant Th read flow", "counterparty" →
  "counterpart y", "136" → "13 6") — too unreliable for a QA meeting full
  of feature names and numbers.
- `medium`/`large` are meaningfully more accurate but 3–6 GB and much
  slower on CPU; for a ~5–10 minute weekly sync recording, `small` already
  gets product/feature names right in practice and finishes in well under
  a minute. Only step up to `medium` if a specific recording's transcript
  comes out noticeably garbled (heavy accents, bad audio, overlapping
  speakers) — pass its path as `transcribe.sh`'s third argument.

## If ffmpeg or whisper-cli truly cannot be installed

Tell the user directly rather than silently producing a lower-quality
result some other way (e.g. piping through an online auto-translate
tool) — this skill's whole value is an accurate, locally-verifiable
transcript that Claude then translates itself with full context.
