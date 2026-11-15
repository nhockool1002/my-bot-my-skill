# Duplicate detection — don't trust the UI's "similar issues" box

## Why this file exists

On a real Authors First cycle (#565607), every issue detail page showed a
"Do not report duplicates — these N issues look similar" warning, with N
ranging from 1 to 17. When each one was actually opened and compared
side-by-side against the issue it was attached to, **zero were genuine
duplicates** — every single match was two different bugs that happened to
share a topic keyword in the title. If this skill ever marks an issue DUP
based on that box alone, it will systematically over-reject good bugs. Do the
comparison yourself every time.

## Worked example — none of these were duplicates

| Issue being triaged | UI flagged as "similar" | Why it's actually a different bug |
|---|---|---|
| Apple TV — Search field does not receive focus | Apple TV — Search — "Sorry, no results found" shown despite results existing | One is an input/focus bug (can't type at all); the other is a results-rendering bug after a successful search. Different trigger, different broken behavior. |
| iOS — Playback — Closed captions disappear towards the end of a video | iOS — AirPlay — Duplicate closed captions displayed when switching AirPlay device | One is CC vanishing over time during normal playback; the other is CC duplicating only when switching AirPlay targets. Different trigger. |
| Apple TV — Resume Playback starts from the beginning | Apple TV — Trailer will not be shown in resume section | One is about the saved position being wrong; the other is about an item missing from a list entirely. Different symptom, different feature. |
| iPadOS — Shared link missing when sharing a title via the Share sheet | iOS — Share — Unable to launch app when tapping a shared link | One is about the *sender's* share action producing no link; the other is about the *recipient's* tap not opening the app. Opposite ends of the flow. |
| iPhone — Cast to Chromecast/Google Hub not playing | iPhone — Screen Mirroring — app shows a black screen on launch while mirroring | Both involve a second screen, but one is the app's own in-app Cast feature failing, the other is an OS-level mirroring interaction. Different mechanism entirely. |

The pattern: the UI's matcher keys off shared nouns ("Apple TV", "Search",
"Share", "Playback", "Resume") with no regard for what the bug actually *is*.

## The method to use instead

1. Pull the cycle's full issue list once (`references/api_reference.md`'s
   `/api/bugs?...` call) — this is your comparison corpus, already including
   resolved issues and `isKnownIssue: true` rows from other cycles.
2. Narrow candidates cheaply first: same `bugTypeId`, overlapping
   device/screen keyword in `subject`, and every `isKnownIssue: true` row
   regardless of keyword match (a Known Issue is worth a closer look even on
   a weaker title match, since it represents an already-confirmed recurring
   problem).
3. For every candidate that survives that filter, actually read
   `expectedResult` + `result` + `testCaseOther` side-by-side with the issue
   being triaged. Ask: is this the *same underlying defect* — same trigger,
   same broken behavior — or just the same general area of the app?
4. Only conclude DUP when you can name the specific matching issue ID and
   quote the overlapping detail (the same trigger steps, the same described
   failure). "Both are about Apple TV Search" is not sufficient; "both
   report that tapping the search field never shows a cursor or accepts
   input" is.
5. If the match came from an `isKnownIssue: true` row, say so explicitly in
   the summary — a Known Issue duplicate is a stronger, cycle-independent
   signal and worth naming differently from an ordinary same-cycle dup.
6. If nothing in the corpus is a genuine match, say so plainly — "checked
   against N same-area issues incl. known issues, none share the same
   underlying defect" is a valid, useful line in the per-issue summary, not
   something to skip because nothing was found.

If a `latestRecommendation` on the issue detail already has `duplicate: true`
with a `duplicateBugId`, that's a human TTL's own prior determination — defer
to it and cite it rather than re-running this whole process, unless you have
new evidence that specifically contradicts it.
