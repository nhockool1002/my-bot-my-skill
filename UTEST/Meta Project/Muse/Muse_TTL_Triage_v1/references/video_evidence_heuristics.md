# Video evidence heuristics

## Frame-sampling density — scale with duration, never use a fixed count

A real incident: an H1/H2 ("Stripe Link entry" / "Browser handoff") video
was reviewed with 6 evenly-spaced frames across its full length. The actual
regional-block message only appeared in the final ~15 seconds of a
178-second video — the sparse sample missed it entirely, producing a false
"tester's evidence doesn't match what they reported" finding that was
drafted into a message to the tester before being caught and walked back.
On the same video reviewed again with denser sampling, the block was
clearly visible.

Use a duration-scaled frame count instead of a fixed number, e.g.:

```python
n = max(8, min(18, round(duration_seconds / 9)))
pad = min(2.0, duration_seconds * 0.03)
span = duration_seconds - 2 * pad
times = [pad + span * i / (n - 1) for i in range(n)]
```

Roughly: ~1 frame per 9 seconds, floored at 8 frames even for very short
clips, capped at 18 so a 3-minute video doesn't produce an unreviewable
pile. Extract with
`ffmpeg -y -ss <t> -i <file> -frames:v 1 -q:v 3-4 <out>.jpg` per timestamp,
and put the timestamp in the output filename (`<name>_f<NN>_t<SSS.S>.jpg`)
so whoever reads the frames can reason about ordering and gaps without
re-deriving it.

**When a scenario specifically hinges on a short-lived state change**
(a blocking message, an error toast, a status transition) and the sparse
pass doesn't clearly show it either way, re-extract that one video alone at
higher density before concluding anything — don't generalize "probably
fine" from a gap in coverage.

## Review against the actual Expected Result, not just tester self-report

Two different review questions exist, and the deeper one should be the
**default from the first pass**, not a follow-up requested later after the
shallow one already missed something:

- **Shallow / consistency check**: "does this video plausibly match what
  the tester wrote as Result/Issue?" This catches gross mismatches (wrong
  app, wrong scenario entirely) but will not catch anything the tester
  themselves failed to notice.
- **Deep / requirements audit**: "does this video actually satisfy the test
  case's own `Expected Result` text (both the shared localization
  requirement and the scenario's own functional requirement), independent
  of what the tester marked?" A real session only found a real, previously
  unreported localization bug (English text leaking into status chrome)
  after switching to this deeper check — the shallow pass had already
  cleared every affected scenario as "fine."

Pull the `Expected Result` / `Test Case Steps` columns from the sheet
alongside the Result/Issue columns before reviewing, and check both the
primary (shared, usually localization) and secondary (scenario-specific,
usually functional) criteria explicitly per scenario. A scenario the tester
marked Pass can still be worth flagging if the video shows a real violation
they missed; a scenario marked Fail for a known, already-filed issue (e.g.
a currency-formatting bug everyone already knows about) doesn't need to be
re-litigated as a "new finding" every time it recurs across scenarios or
test cases — name it once, move on.

## Verify root cause before any tester-facing message

If something looks wrong, the ambiguity is never resolved by messaging the
tester first. Check, in order:

1. The exact file(s) on uTest's own test-case attachment list (filenames,
   sizes — a size match against what you downloaded confirms you have the
   right file).
2. The tester's own entry in the Tester View sheet for that scenario (the
   literal Applause link hash they entered).

Only once both independently point to the same content is it safe to
conclude where a mismatch actually originates — it can be the TTL's own
earlier transcription error into the EXT sheet rather than the tester's
fault, and drafting an accusatory message before checking this wastes the
tester's time and the TTL's credibility. Delegate this cross-check instead
of skipping it under time pressure — it's a few extra fetches, not a few
extra hours.

## Reuse, don't re-review, identical evidence

Some scenarios intentionally reuse the exact same recording across
platform-specific test cases (the "I1 - iOS / Android / Web" scenario is a
standing example — it tests cross-platform browser behavior and legitimately
points at the same Applause hash regardless of which platform's test case
you're triaging). Before downloading, diff the hash against anything already
reviewed this session (or recorded as verified in a prior triage); if it
matches byte-for-byte, cite the earlier verification instead of repeating
the download-and-frame-review cycle.

Two files that are byte-identical in size *and* duration despite different
hashes/URLs (seen with two scenario videos in the same test case) is not
automatically an error either — open a handful of frames from each to
confirm it's a legitimate single combined recording serving both scenarios
(the standard "you may combine recordings for multiple test scenarios"
allowance) rather than a data-entry mistake, and say explicitly which it
turned out to be.
