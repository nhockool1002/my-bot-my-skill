#!/usr/bin/env bash
# Extract mono 16kHz PCM WAV from a video file, ready for whisper.cpp.
# Usage: extract_audio.sh <input_video> <output_wav>
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Usage: extract_audio.sh <input_video> <output_wav>" >&2
  exit 1
fi

IN="$1"
OUT="$2"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install it first (e.g. 'brew install ffmpeg')." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
ffmpeg -y -i "$IN" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$OUT"
