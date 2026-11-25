---
name: Muse_TTL_Triage
description: TTL triage workflow for the Muse (Meta) in-market testing project on uTest — exploratory cycles with 30-scenario Test Cases per connector/platform (A1-J4), evidence living in a companion "Tester View" Google Sheet (one video per scenario, sometimes several scenarios sharing one combined recording) rather than in uTest's own test-case UI. Given a uTest test-case URL, this skill identifies the tester/platform/scope, pulls the real source-of-truth evidence from the Tester View sheet, downloads and visually reviews every video against the test case's own Expected Result criteria (not just against what the tester self-reported), reports findings before touching any shared sheet, and — once directed — safely republishes the verified data into the client-facing EXT sheet and the TTL Tracking Sheet. Use this proactively whenever the user pastes a Muse test-cycle or test-case platform.utest.com link and asks to "check evidence", "triage testcase", "kiểm tra evidence", "bắt đầu luồng Muse triage" — even if they don't name this skill directly. This skill was hardened after real triage sessions surfaced a false-positive evidence mismatch (fixed by denser frame sampling), a wrong-column data entry on the EXT sheet, and a near-total-data-loss incident while editing a Tracking Sheet cell — read "Hard rules" before doing anything destructive.
---

# Muse TTL Triage

## What this skill is for

Each Muse cycle is one country/locale. A tester claims a test case for one
platform (Mac App / Web / iOS / Android) and works through up to 30 numbered
scenarios (Case IDs A1-A5, B1-B5, C1-C4, D1-D3, E1-E3, F1, G1-G2, H1-H2, I1,
J1-J4) defined in a shared results sheet, not in uTest's own step UI. uTest's
test-case page only shows the coarse Pass/Fail/Pending status and the raw
attachment list; the real per-scenario Result/Video/Date/Issue evidence lives
in a **"Tester View" Google Sheet**, one wide tab per connector/feature with
a repeated 4-column block (`Result`, `Notes - what you saw` [actually the
video link], `Date`, `Issue ID`) per platform x per tester. The TTL's job is
to watch that evidence against the test case's own `Expected Result` text —
not just rubber-stamp what the tester self-reported — then publish the
verified rows to the client-facing **EXT sheet** and record the outcome in
the **Tracking Sheet**.

See `../README.md` in this folder for the full 6-step onboarding-level
picture (cycle discovery on Monday.com, allowlisting, and the Connector-vs-
Browser Pass/Fail rule) — that covers the parts of the job this skill
doesn't exercise directly. This SKILL.md starts from "I have a uTest
test-case link" (README Step 3 onward) and goes deep on Steps 4-6, which is
where real triage sessions actually spend their time and where the mistakes
below were made and fixed.

## Hard rules — read before doing anything

These came from real incidents in actual triage sessions. They are not
optional style preferences.

1. **Never write tester-facing evidence findings before verifying the root
   cause.** If a video's content looks wrong (wrong app, wrong scenario,
   missing expected message), check the raw source **and** the uTest test
   case's own attachment list **before** drafting any message that implies
   the tester made a mistake — your own transcription could be the actual
   error. See `references/video_evidence_heuristics.md`.
2. **Never conclude "mismatch" from a sparse frame sample.** A real incident:
   6 evenly-spaced frames missed a blocking message that only appeared in
   the last ~15 seconds of a 178-second video, producing a false "tester is
   wrong" finding that was walked back later. Frame density must scale with
   video duration — see `references/video_evidence_heuristics.md` for the
   formula and the default review depth (check against actual Expected
   Result text, not just tester self-report, from the first pass).
3. **Never guess which column group on the EXT sheet a tester's data
   belongs to.** EXT sheets have repeated per-platform x per-tester column
   blocks that look identical at a glance; a real incident put an entire
   test case's data into the wrong tester's column group, silently clobbering
   nothing-visible until caught days later. Always fetch and print the
   header row programmatically and confirm the exact column index with the
   user before writing. See `references/sheet_conventions.md`.
4. **Never bulk-type scenario data directly into a shared Sheet via
   browser automation.** Generate a TSV and have the TTL paste it themselves
   — this is dramatically safer, trivially diffable, and avoids exactly the
   wrong-column and Cmd+A incidents below. Reserve direct cell editing for
   one-off things (a header rename, a single dropdown pick), always via Name
   Box navigation plus a CSV-fetch verification afterward, **never** `Cmd+A`
   inside a cell-edit box (a real incident: it selected the *entire sheet*
   instead of the cell's text and a follow-up Delete wiped the whole Table —
   caught and undone, but avoidable). See `references/sheet_editing_safety.md`.
5. **Always fill every Tracking Sheet column**, not just Result and
   Approval_Status — `acc collection status`, `Device`, `Flow`, and `Bug ID`
   are equally required and were missed in an early pass. See
   `references/sheet_conventions.md` for the full checklist.

## Step 1 — Identify the test case

`navigate` to the uTest test-case URL
(`https://platform.utest.com/testcycles/<cycleId>/testcases/<testCaseId>`)
and read: tester name, platform/environment (Mac App / Web / iOS / Android —
this decides which EXT column block and Tester View column block you need),
`RESULTS` (tester's own overall verdict) and `STATUS` (uTest's own
Pending/Pending Approval state), and the raw attachment filenames for a
sanity cross-check later (filenames follow `Muse_TC_<N>_<Platform>...mp4`
where `<N>` maps 1:1 in sequence onto Case IDs A1, A2, A3, ... — but a
missing TC number usually means it's folded into a neighboring combined
recording, not missing evidence).

## Step 2 — Pull the real evidence from the Tester View sheet

The Tester View Google Sheet (linked from the cycle Overview's "Test Case
Instructions" as "IT Result sheet" or similar) is the **source of truth** —
not the EXT sheet, and not your own prior transcription of it. Fetch it from
a `docs.google.com` tab (same-origin requirement) with the CSV-export trick:

```js
const r = await fetch('https://docs.google.com/spreadsheets/d/<ID>/gviz/tq?gid=<gid>&tqx=out:csv', {credentials:'include'});
const t = await r.text();
```

Parse with a quote-aware CSV parser (many cells contain embedded newlines —
naive `.split('\n')` undercounts rows). Locate the tester's column block by
searching the header row for their name (name order/formatting is
inconsistent sheet-to-sheet — try both `"First Last"` and `"Last First"`,
and check for the platform label too, e.g. `"iOS - Result\n(Troshina Anna)"`).
Extract, per scenario: Result, Video link(s), Date, Issue/Note. Several
scenarios legitimately share one combined recording (same Applause link
hash appearing under 2-3 Case IDs) — this is allowed per the recording
instructions and is not itself a defect; flag it only if the *content*
doesn't plausibly cover all the scenarios pointing at it.

## Step 3 — Download and review every video

Bulk-download with `curl -sL` on the raw `platform.applause.com/services/
links/v1/external/<hash>` URLs (a plain GET succeeds directly, no browser
navigation needed; `curl -sIL` HEAD requests 403 — always use GET). Dedupe
by hash before downloading — shared/combined-recording scenarios don't need
a second download.

Extract frames with `ffmpeg -ss <t> -frames:v 1` at a density that scales
with duration (not a fixed frame count) — see
`references/video_evidence_heuristics.md` for the exact formula and for why
the review should check against the test case's actual `Expected Result`
localization + functional criteria from the first pass, not merely whether
the video is consistent with what the tester self-reported. Delegate the
actual frame-by-frame reading to a fork/subagent when reviewing many videos
in one pass — this is a large, repetitive visual task that doesn't need to
live in your main context, and the forked report is what the TTL actually
reads.

Reuse already-downloaded/verified videos across test cases when the exact
same Applause hash reappears (common for scenarios like "I1 - iOS/Android/
Web" that intentionally reuse the same browser-flow recording across
platform-specific test cases) — don't re-download or re-review something
byte-identical to what you already confirmed.

## Step 4 — Report findings before touching any shared sheet

Always report what you found — confirmed-correct scenarios, anything
uncertain (say exactly what's missing to resolve it, don't guess), and
anything that looks wrong — **before** writing anything to the EXT sheet or
Tracking Sheet, and before drafting any tester-facing message. Let the TTL
decide next steps (dig deeper, message the tester, accept as-is, proceed to
publish). Never auto-send a tester-facing message — draft it as a bilingual
`| Tiếng Việt | English |` table per this project's established convention
and let the TTL send it themselves.

## Step 5 — Publish verified data to the EXT sheet

**Official process (per TE Lead, 2026-11-19) — follow this, not the legacy
manual-copy approach below:**

1. In the **Tester View** sheet, once triage is complete for a scenario, set
   that tester/platform slot's **`Review Status`** column to `Validated`.
   This is what actually marks the row as TTL-reviewed — it is a real
   column (one per platform x tester-slot block, next to `Issue ID`), not a
   free-text note.
2. Marking a row `Validated` is expected to **auto-populate** the
   corresponding row into the client-facing **EXT Results sheet** — the TTL
   does not manually copy Result/Notes/Date/Issue data across anymore where
   this auto-populate is in place. Go to the EXT sheet afterward and
   **confirm** the validated results actually populated correctly (don't
   just trust that marking Validated was enough — verify with a CSV fetch,
   per Hard rule 4).
3. **Add Video Evidence** yourself: the auto-populate does not appear to
   carry the video link automatically, so explicitly add the corresponding
   video link to each result's own `Video` column in the EXT sheet (now a
   separate 5th column per block — see `references/sheet_conventions.md`
   for the current 5-column layout, which differs from the one this skill
   originally described).

This instruction arrived after this skill was first written and after
several triage sessions had already published rows the legacy way (manual
TSV-paste of Result/Video/Date/Note straight into EXT, with a TTL-renamed
header claiming the slot). **Do not go back and "fix" or reconcile rows
published the legacy way unless the TTL explicitly asks** — leave prior
work as-is and apply the Review-Status-driven process going forward. The
underlying sheets were also restructured around when this instruction
arrived (generic `(Tester 1)/(Tester 2)/(Tester 3)` slot labels came back
instead of TTL-renamed `"<Name> - <test case ID>"` headers, and a
`Scenario Key`/`Scope` pair of columns appeared before the per-platform
blocks) — re-verify the exact current column layout with a header fetch
every time rather than trusting what a past session recorded, even from
this same file.

**Legacy manual-copy approach (fallback only, e.g. if `Review Status` /
auto-populate isn't present on a given sheet yet):** confirm the exact
target column block first (Hard rule 3), generate a TSV (`Result`, `Video`,
`Date`, `Note` — one row per scenario, in the sheet's existing row order)
from the Tester View source data, send it to the user, and select the exact
target range in the Browser pane so they paste it themselves (Hard rule 4).
If a column header is still a generic placeholder, confirm with the TTL
which slot to claim before renaming it. Verify the final state with a fresh
CSV fetch either way, never by trusting a screenshot alone — concurrent TTL
interaction in the same Browser pane can make a screenshot stale mid-task.

## Step 6 — Update the Tracking Sheet

Find (or add, if claiming a new test case) the row for this `TC ID` under
the cycle's own tab, then fill **every** column per
`references/sheet_conventions.md`'s checklist — `acc collection status`,
`Result`, `Approval_Status`, `Device`, `Flow`, `Bug ID` — matching the
convention of neighboring rows. If the Device dropdown has no exact match
for the tester's real device, override it with the exact free-text value
(don't silently settle for the closest generic option) — see Hard rule 4 for
*how* to safely overwrite dropdown-validated cell text without triggering a
whole-sheet selection. Then apply the bonus-eligibility check from the
README's Step 6 (6-hour clock from claim to valid completed result, or from
blocker resolution if the tester was blocked by something outside their
control).
