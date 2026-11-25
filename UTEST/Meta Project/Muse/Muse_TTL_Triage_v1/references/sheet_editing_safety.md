# Editing shared Google Sheets safely via browser automation

Two real incidents happened during triage sessions: one wrong-column data
entry (see `sheet_conventions.md`) and one near-total-data-loss when a
single cell edit on a Tracking Sheet accidentally selected and deleted an
entire sheet's worth of data. Both are avoidable with the rules below.

## Default to TSV + manual paste for anything bulk

Typing 30 rows x 4 columns directly into a shared sheet cell-by-cell via
`computer` actions is slow, consumes a huge number of tool calls, is nearly
impossible to visually verify in real time, and is exactly the kind of
repetitive mechanical task where a stray scroll or a misdirected click goes
unnoticed until it's already landed.

Instead:
1. Build the data as a local TSV file (`Result`, `Video`, `Date`, `Note` —
   or whatever the target's column order is — one row per scenario, same
   row order as the sheet) from the Tester View source.
2. Send the file to the user.
3. Select the exact destination range in the Browser pane (Name Box ->
   `<Col>2:<Col+3><lastRow>`) so it's visually obvious where to paste.
4. Tell the user to paste it themselves.

This is dramatically safer (the person who can see their own clipboard and
the target cell does the actual write), trivially diffable (they can see
exactly what's about to land before committing), and sidesteps every
problem below. Reserve direct `computer` cell editing for one-off things: a
single header rename, one dropdown pick, one free-text override.

## When direct cell editing is unavoidable

- **Navigate with the Name Box, not blind clicking.** Click the Name Box
  (top-left, labeled `A1` by default), type the exact cell reference
  (`I11`), press Return. Confirm the resulting screenshot shows that exact
  reference in the Name Box / formula bar before acting — a click that
  lands on a stale coordinate (because the sheet auto-scrolled, or another
  person is interacting with the same Browser pane concurrently) will
  silently target the wrong cell otherwise.
- **A single `left_click` on a cell does not reliably enter edit mode** in
  a Google Sheets Table — the first keystroke can be lost or land as a
  fresh selection instead of inserting text. Use `double_click` on the
  target cell to explicitly enter edit mode before typing.
- **For a dropdown-validated cell**, click once to select, click again (or
  click the dropdown arrow) to open the options list, and click the exact
  option. If scrolling within the dropdown's own list is needed, scroll
  inside the dropdown's bounding box, not the sheet behind it.
- **Verify every write with a fresh CSV-export fetch, not a screenshot.**
  Screenshots can be stale or can be mid-render if the sheet is scrolling;
  the `gviz/tq?...&tqx=out:csv` fetch (same technique as reading Tester
  View data) is the only way to know for certain what's actually stored.
  Do this after every meaningful write, not just at the end of a batch.

## Never use Cmd+A inside a cell-edit box to select-and-replace text

**This caused a real near-total-data-loss incident.** The intent was: enter
edit mode on one cell, select all of that cell's existing text, and replace
it with a corrected value. `Cmd+A` while focus was ambiguous (the edit box
had just been entered via double-click, but focus hadn't unambiguously
landed inside the text field) instead selected the **entire sheet grid**
(the Name Box showed `A1:L31`). The very next keystroke was `Delete` —
which wiped every header and every data row across the whole visible Table.
It was caught immediately from the resulting blank-header screenshot and
reverted with a single `Cmd+Z`, with a follow-up CSV-fetch confirming full
recovery, but it should never have been attempted this way.

To replace an existing cell's text safely instead:
- `triple_click` directly on the cell's rendered text (not just inside its
  bounding box) to select the existing content for overwrite, then type the
  replacement directly — don't press `Cmd+A` as a separate step.
- If a correction attempt produces visibly wrong concatenated text (e.g.
  `"Apple iPhone 15iPhone 15 Pro - iOS 27.2.1"`), stop immediately, press
  `Escape`, and restart the edit from a clean double-click rather than
  trying to patch the damage in place.
- After any text-replacement edit, always re-fetch the row via CSV export
  and confirm the exact string before moving to the next cell — don't chain
  multiple risky edits before checking the first one landed correctly.

## Headers and sheet-wide Find & Replace

Scope every Find & Replace to the exact header range (`H1:K1`, not "All
sheets" / "This sheet") when renaming a column-block header — the same
placeholder text (`"Tester 1"`, `"Tester 2"`) appears in multiple unrelated
column blocks on the same sheet, and a sheet-wide replace renames all of
them at once. Always check the "Replaced N instances" count against the
expected number of header cells (usually exactly 4) before closing the
dialog.
