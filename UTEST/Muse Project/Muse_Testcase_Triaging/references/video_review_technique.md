# AI pre-review of step videos

Developed and verified by running it directly on a real recording (the TTL
onboarding walkthrough this skill was built from) — `ffmpeg` and the local
`whisper-cli` model both worked out of the box on this machine, so this is a
proven technique, not a theoretical one. The goal is a fast, good-enough
first pass, not a replacement for the TTL's own eyes.

## Why this exists

A Muse test case can have 15–50 individual step videos per tester. Watching
every one end-to-end is the single biggest time cost in the whole triage
flow (the walkthrough calls this out directly: "it's actually quite an easy
triage, just that there's a lot of videos"). Sampling frames + transcribing
any narration gets you most of the way to a verdict in a few seconds per
video instead of minutes.

## Pipeline

1. **Get the video file locally.** Resolve the share link to a real,
   downloadable URL first (Google Drive share links need the direct-download
   form or the Drive connector; uTest-hosted attachments resolve via the
   same `/services/links/v1/internal/<id>` redirect used elsewhere in this
   project family). Save to a scratch directory — never reuse a shared
   project directory for downloaded video, per the usual untrusted-download
   hygiene.

2. **Extract periodic frames** with `ffmpeg`, scaled down for fast reading:
   ```bash
   ffmpeg -y -i input.mp4 -vf "fps=1/N,scale=960:-1" frames/frame_%03d.png
   ```
   Pick `N` (seconds between frames) based on the video's own length — for a
   short single-step clip (10–60s) use `N=2` to `N=5`; for a longer combined
   clip (several steps merged into one video, per the walkthrough's note
   that "some tester combine together... into one") use `N=15` to `N=30` and
   expect to need a second, denser pass around the moment that matters once
   you've found it from the sparse pass.

3. **Transcribe any narration/on-screen dialogue** with the local
   `whisper.cpp` model (`whisper-cli`), if the step involves the tester
   speaking to the Muse chatbot or any audio cue worth checking:
   ```bash
   ffmpeg -y -i input.mp4 -ar 16000 -ac 1 -vn audio.wav
   whisper-cli -m <path-to-ggml-model>.bin -f audio.wav -otxt -of transcript -l en
   ```
   Use `-l <lang>` for a cycle in a known non-English locale rather than
   `en`, when the model supports it — forcing the wrong language degrades
   the transcript badly. If you don't know the local model's path, ask the
   user or search the machine for a `ggml-*.bin` file before assuming none
   exists.

4. **Read a handful of frames** (Read tool, images) spanning the video's
   start/middle/end at minimum, plus any frame right around a transcript
   line that sounds decisive, and compare what you see against the step's
   `Expected result` text (and `Precondition`/`Steps` if present).

5. **Score your confidence honestly**:
   - `Likely Pass` — the sampled frames and/or transcript clearly show the
     expected outcome (e.g. the right screen state, a confirmation message,
     the exact UI element named in Expected Result).
   - `Likely Fail` — frames/transcript clearly show something that
     contradicts the Expected Result (error state, wrong screen, missing
     element).
   - `Unclear — needs human review` — the sampled frames don't land on the
     decisive moment, the transcript is too garbled to trust (common for
     small local models on accented or non-English speech), or the step's
     pass/fail hinges on something frame-sampling genuinely can't catch
     (fine visual detail, subtle text, precise timing). **This is a valid,
     expected outcome for a meaningful fraction of videos — don't force a
     Pass/Fail call you don't have evidence for.**

## What this does NOT replace

- The TTL's own confirmation before anything gets written back to uTest or
  copied into the client-facing External sheet (Step 4 of SKILL.md).
- Careful review of anything flagged `Unclear`, any high-stakes step (the
  one evidence that makes or breaks a whole run), or any foreign-language
  cycle where transcript quality is inherently shaky.
- The actual "is this video share-linked correctly and watchable by the
  client" check — confirm the link works before pasting it into the
  External sheet, a pre-review pass on your own download doesn't verify
  that.
