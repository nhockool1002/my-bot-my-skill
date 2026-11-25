# Tester slotting via the Management tool ("M tool")

New procedure from the 2026-11-24 call — not covered by v1. Purpose: when
many testers share one Tester Sheet tab, slotting makes it unambiguous
which column belongs to which tester, so results don't get mixed up and
testers don't waste time guessing which column is theirs.

## When to slot

- **Proactively**, if you have spare time and see a test case that's
  unclaimed/unstarted and currently open (no one else assigned to that
  exact case number range yet).
- **Reactively** — in practice, most slotting happens either (a) while
  you're already triaging a test case and notice it was never slotted, or
  (b) the moment a tester messages on platform chat asking which column to
  use. Both are completely normal; don't treat reactive slotting as behind
  schedule. Check chat often enough that these requests don't sit — every
  15-60 minutes if your workload allows it.
- If a tester already filled in a column without being pre-slotted, that's
  fine — just split and backfill their name into the Slotting tab during
  triage; no need to have caught it beforehand.

## Step by step

1. Identify the tester's **sheet tab** (e.g. "UK browser partners in
   market"), **feature** (e.g. "JD Sports"), and **test case number** (e.g.
   `4`).
2. Open the **Slotting** tab and find that sheet-tab/feature's row(s).
   Existing rows cover *ranges* of test-case numbers (e.g. one row covering
   cases 1-11). Check which device/platform column (`Android 1` /
   `Android 2` / `Android 3`, etc.) is **already assigned** across that
   range by checking the Tester Sheet's corresponding column — don't assign
   a column that's already claimed by someone else for an overlapping case
   number.
3. If the existing range is wider than just this tester's case(s), **split
   it down**:
   - Select the row, open the **M tool** menu in the toolbar, choose
     **Split**.
   - First split off the range **before** the tester's case number (e.g.
     cases 1-3, if the tester is doing case 4 out of a 1-11 block).
   - Wait for the **"Running script"** indicator to clear before doing
     anything else to that row — splitting runs a script, not an instant
     formula.
   - Then select the remaining range and use **M tool → Split a slot in
     row**, entering just the tester's own case number(s) (e.g. `4`) to
     isolate a row containing only their case(s). Wait for the script
     again.
4. Once isolated, enter the tester's **name** and **test case ID** into the
   new row. The sheet has a pre-built formula that auto-generates a direct
   link to that test case from the ID — you don't need to build the link
   yourself.
5. Give it a short propagation delay (a refresh may still show "Open slot"
   for a bit) — the corresponding Tester Sheet column (e.g. `Android 1`)
   picks up the tester's name automatically once it catches up. Don't
   assume the slotting failed just because it hasn't updated within a few
   seconds of your edit.
6. Message the tester on the platform: confirm which column is theirs and
   ask them to start at their earliest convenience.

## Tracking claim/unclaim churn

Testers occasionally claim a slot and later unclaim it. In practice, most
testers who claim a slot do complete it, so this isn't usually a problem in
practice. If a tester fills in results on the Tester Sheet before you
managed to pre-slot them, that's fine — split and backfill their name
during triage rather than treating it as an error. When there are multiple
identical-looking slots for the same device (e.g. three iOS columns), the
Slotting tab plus checking chat frequently is the real mitigation — there
isn't a fully-proactive way to prevent every moment of tester confusion
during a high-volume cycle, and that's an accepted tradeoff, not a process
gap to fix on your own.
