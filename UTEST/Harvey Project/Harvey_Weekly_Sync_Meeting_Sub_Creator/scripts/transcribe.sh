#!/usr/bin/env bash
# Transcribe a WAV file with whisper.cpp (whisper-cli), with word-level
# timestamps (-ojf = output JSON, full detail) plus a raw .srt for reference.
# Downloads the ggml-small.bin model once into a persistent cache dir if
# it isn't there yet, so repeat runs (many meetings) never re-download it.
#
# Usage: transcribe.sh <input_wav> <output_prefix> [model_path] [language]
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: transcribe.sh <input_wav> <output_prefix> [model_path] [language]" >&2
  exit 1
fi

WAV="$1"
OUT_PREFIX="$2"
MODEL="${3:-$HOME/.cache/whisper-cpp/models/ggml-small.bin}"
LANG="${4:-en}"

if ! command -v whisper-cli >/dev/null 2>&1; then
  echo "whisper-cli not found. Install whisper.cpp first (e.g. 'brew install whisper-cpp')." >&2
  exit 1
fi

if [ ! -f "$MODEL" ]; then
  echo "Model not found at $MODEL — downloading ggml-small.bin (~480MB, one-time)..." >&2
  mkdir -p "$(dirname "$MODEL")"
  curl -L --fail -o "$MODEL" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
fi

mkdir -p "$(dirname "$OUT_PREFIX")"
whisper-cli -m "$MODEL" -f "$WAV" -l "$LANG" -osrt -ojf -of "$OUT_PREFIX" --max-len 0
