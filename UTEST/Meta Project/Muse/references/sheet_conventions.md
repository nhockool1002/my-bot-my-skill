# Sheet conventions — EXT sheet, Tester View, Tracking Sheet

Muse cycles run on three separate Google Sheets with different audiences and
different trust levels. Don't confuse them.

| Sheet | Audience | Trust level |
|---|---|---|
| **Tester View** | Testers write into it; TTL reads from it | **Source of truth** for raw evidence — a tester's own original entry |
| **EXT sheet** | Client reads it | A TTL-curated *copy* of verified Tester View rows — never assume it's correct just because it was filled in before; re-derive from Tester View if in doubt |
| **Tracking Sheet** | TTL/TE internal | Per-cycle tab (`"<Country> - Cycle #<cycleId>"`), one row per test-case run, drives bonus payout |

If the EXT sheet and the Tester View ever disagree and you didn't make the
edit yourself, treat the Tester View as correct and re-derive the EXT row —
don't assume the EXT sheet was updated more recently just because it's the
"final" destination.

## EXT sheet: identifying the right column block

The EXT sheet repeats a 4-column block
(`<Platform> - Result`, `<Platform> Video`, `<Platform> - Date`,
`<Platform> Note & Issue ID`) once per platform **x** per tester slot
(commonly 2 tester slots per platform: `Tester 1`/`Tester 2`, or a real name
if already claimed). Columns for different platforms and different tester
slots are visually identical at a glance when scrolled sideways through a
40+ column sheet — **this is exactly what caused a real incident** where an
entire test case's 30 rows of data were typed into the wrong tester's
column block and went unnoticed for days.

Before writing anything:

```js
const header = rows[0];
header.forEach((h, i) => { if (/* match platform/tester text */) console.log(i, h); });
```

Print the exact column index (and convert to a letter: `A=0, B=1, ...
Z=25, AA=26, AB=27, ...`) and confirm it against what's already in column 0
(`Case ID`) for a couple of rows before trusting it. If two tester slots for
the same platform are both still generic (`Tester 1`/`Tester 2`) and neither
is obviously the one you're working on, **ask the TTL** which slot to use —
never guess, even when one "seems" more likely. A different person's
in-progress data (e.g. another TTL actively filling the sibling slot) is a
real scenario, not a hypothetical.

## Claiming a column slot

Once the TTL confirms which slot is theirs, rename the generic header
(`"Tester 1"` / `"Tester 2"`) to `"<Tester full name> - <uTest test case
ID>"`, matching the convention already used by platform blocks that have
been claimed before. Do this with Find & Replace **scoped to the exact
header row range** (e.g. `H1:K1`), never "All sheets" or "This sheet" —
the literal string `"Tester 1"` or `"Tester 2"` appears in multiple
unrelated column blocks (iOS, Android, Web, Mac App all have their own
Tester-1/2 slots) and a sheet-wide replace will silently rename all of
them. Confirm the "Replaced N instances" count matches the 4 columns in the
header row (exactly 4, not more) before moving on.

## Publishing data: TSV + manual paste, not direct typing

See `sheet_editing_safety.md` for the full reasoning and the exact
mechanics. In short: build the 4-column TSV from Tester View data, send it
to the user as a file, and select the destination range
(`<Col>2:<Col+3><lastDataRow>`) in the Browser pane so they paste it
themselves. This is the default for anything more than a couple of cells.

## Tracking Sheet: the full column checklist

An early pass filled only `Result` and `Approval_Status`, missing the rest
— caught and fixed later, but should be done right the first time. Every
new or updated Tracking Sheet row needs **all** of:

| Column | What goes there |
|---|---|
| `TC ID` | The uTest test case ID |
| `Tester` | Full tester name, matching their uTest display name |
| `Country` | Locale/country for this cycle |
| `TTL Notes` | The platform/environment label (`iOS`, `Android`, `Web`, `Mac App`, ...) |
| `acc collection status` | `Account credentials have been Allowlisted` once confirmed (match the exact dropdown value used by neighboring rows) |
| `Result` | `Passed` / `Failed` / `Blocked` — the test case's own overall result |
| `Approval_Status` | `Pending Approval` once evidence is verified and ready for the TTL's own Approve action on uTest; `Info Requested` if still waiting on the tester |
| `Device` | The specific device/OS the tester used. If the dropdown has no exact match (seen: no "iPhone 15 Pro" option, only generic "iPhone 15"), **override with the exact free-text value** rather than settling for the closest generic option — see `sheet_editing_safety.md` for how to do this without triggering a whole-sheet selection |
| `Flow` | The connector/feature under test (e.g. `Connector Shopping Catalog`, `Stripe Link`, `Shop Pay`) |
| `Bug ID` | Every distinct Issue/Bug ID number the tester reported across this test case's scenarios, comma-separated, numbers only (no `"Issue ID #"` prefix — match the format already used by neighboring rows) |

After every column is filled, apply the bonus-eligibility check: a $10
bonus flag if the result is valid and was completed within 6 hours of the
tester's claim (or within 6 hours of a blocker being resolved, if the
tester was blocked by something outside their control).
