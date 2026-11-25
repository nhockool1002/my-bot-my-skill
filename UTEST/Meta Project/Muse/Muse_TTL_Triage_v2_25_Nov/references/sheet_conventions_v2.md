# Sheet conventions v2 — Tester Sheet, External Sheet, Meta Tracking Sheet

As demonstrated live in the 2026-11-24 onboarding call. Column names below
are what was shown on screen during that call — re-fetch the actual header
row on your own cycle's sheets before writing anything; these sheets have
been restructured more than once on this project (see
[[project-muse-utest]]).

## Tester Sheet

Testers fill this in directly. Per test-case row:

- **Result** — `Pass` / `Fail` / `Partial` / `Blocked`. See
  [[project-muse-utest]] for the full Pay-or-OK `Partial` rule and the
  distinction between `Partial` (site reached but became inaccessible
  mid-flow — it *was* tested) and `Blocked` (step never attempted at all).
- **Issue ID** — required when Result is `Fail`. The cell highlights red if
  left blank on a Failed row. Not required when Passed.
- **Comments/notes** — required on **Failed** rows (explain what went
  wrong); optional on **Passed** rows — don't chase a tester for notes on a
  clean pass.
- Rows marked **`removed by Meta`** (sometimes repeated as just `Meta`,
  `Meta`, `Meta` down a column) mean the client pulled that execution from
  scope. Counter-check it's genuinely marked that way by the client's own
  process, but don't treat it as a defect to chase.

Testers do **not** add video links here — video links are an External
Sheet / TTL-only field (see below).

## External ("EXT") Sheet

- **Auto-sync**: whatever a tester fills on the Tester Sheet (Result,
  Issue ID, Notes) propagates to the External Sheet automatically,
  roughly **once per hour**. This replaced an older fully-manual
  copy/paste process — if you're copying Result/Notes/Date by hand onto
  this sheet, confirm you're not on a stale process before continuing.
- **What's still manual, every single time:** attaching the **video
  link** for that step. This is required for every step regardless of
  Pass or Fail — pull it from the tester platform and paste it into the
  External Sheet's video column yourself.
- **Marking `Validated`**: once you've confirmed the auto-synced result is
  correct *and* the video link is attached, mark the row `Validated`. This
  is the real TTL review checkpoint on this sheet.
- **Partial-completion IRs**: if only some steps of a multi-step test case
  need an Info Request, validate + attach video for the already-correct
  steps right away rather than holding all of them until the IR'd step is
  fixed — see SKILL.md §2 for why (saves the next TTL from re-reviewing
  everything from scratch).
- **Unlocking for tester edits**: a `Validated` row **locks** the tester's
  cells. If you're sending an IR on a row that's currently `Validated`,
  change the status back to `Info Request`/`Pending` first — otherwise the
  tester literally can't edit it to respond. See [[project-muse-utest]] for
  the full lock-behavior writeup.

## Meta Tracking Sheet

One row per test case run. Columns demonstrated on the call:

| Column | What goes there |
|---|---|
| Test case ID | The uTest test case ID |
| Tester name | Matching their uTest/platform display name |
| Country | Separate tabs per region — this call showed a UK tab plus EMEA and APAC tabs |
| Result | Passed / Failed, the overall outcome |
| Approval status | `Pending Approval` once ready, `Info Request` if waiting on the tester |
| Device used | The tester's actual device |
| Flow | See the naming convention in SKILL.md §2 |
| Bug ID | Filled only if Result is Failed |
| Bonus | $10 / $20 flag — see SKILL.md §2's bonus rules |

Cross-check against v1's `sheet_conventions.md` Tracking Sheet checklist
(`acc collection status`, which this call didn't explicitly re-demo) before
assuming either list is complete on its own — the two were recorded from
different sessions and may both be capturing a true subset.
