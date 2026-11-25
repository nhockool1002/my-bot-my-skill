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

## Official publishing process (per TE Lead, 2026-11-19)

Both the Tester View and the EXT sheet got restructured around when this
instruction arrived — **don't trust a column layout recorded in this file
or from a past session; re-fetch the header row every time.** As of
2026-11-19 the layout is:

- **Tester View**, per platform x tester-slot block: `Result`,
  `Notes - what you saw` (the video link), `Date`, `Issue ID`, **`Review
  Status`** (new — this is the column the TTL sets to `Validated` once
  triage is done for that row).
- **EXT sheet**, per platform x tester-slot block: `Result`, `Notes - what
  you saw`, `Date`, `Issue ID`, **`Video`** (new — a separate last column;
  previously the video link lived inside `Notes`, it's now its own field).
- Slot header labels are back to auto-generated generic form
  (`(Tester 1)` / `(Tester 2)` / `(Tester 3)`, sometimes with a
  machine-generated prefix like `"#1: <Name>"` or `"#3: unassigned, N
  result(s) entered - name the tester on Slotting"`) rather than the
  TTL-renamed `"<Name> - <test case ID>"` form described elsewhere in this
  file — that renaming convention predates this restructure and may no
  longer be how slots are claimed. Confirm with the TTL before renaming
  anything now.
- A `Scenario Key` / `Scope` column pair now sits between `Expected Result`
  and the first platform block on the Tester View.

The TE Lead's stated process, in order:

1. Finish triage for a row, then set that row's own `Review Status` to
   `Validated` in the **Tester View**.
2. This should **auto-populate** the row into the **EXT Results sheet** —
   go confirm it actually landed correctly (CSV-fetch verify, don't just
   trust the instruction happened).
3. **Add the video evidence link** to the EXT sheet's own `Video` column
   yourself — this part is not automatic.

Do not fall back to the legacy manual-TSV-into-EXT approach (below) unless
`Review Status` / auto-populate genuinely isn't present on the sheet you're
working with. See `SKILL.md` Step 5 for the full instruction. Prior rows
published the legacy way are not something to go back and fix on your own
initiative — leave them, apply the new process going forward.

## `Review Status` — the full set of values (per TE Lead Slack update, 2026-11-25)

The `Review Status` column takes exactly these values — don't invent others:

| Value | Meaning | Side effect |
|---|---|---|
| `Pending` | Default state, not yet reviewed by the TTL | none |
| `Info Request` | TTL needs the tester to clarify/fix something before it can be validated | none (cells stay editable for the tester) |
| `Validated` | Results are correct and ready — **video link still needs to be added on EXT by the TTL**, this doesn't happen automatically | **Locks** the tester's result cells for that row (intentional — so results/counts can't change after being counted) |
| `Removed from Scope` | Meta removed this execution from scope | Turns the row's `Result` to `N/A` and **protects**/locks it |

**Important interaction:** if you set a row back to `Info Request` or
`Pending` *after* it was `Validated`, the previously-locked cells
**unprotect again for the tester within a few seconds** — i.e. reverting
the status re-opens editing for the tester. Only do this deliberately (e.g.
genuinely re-opening a row because something was wrong with a prior
validation) — don't toggle status back and forth casually, since it
changes who can edit the row.

## EXT sheet: identifying the right column block (legacy context)

Historically the EXT sheet repeated a 4-column block
(`<Platform> - Result`, `<Platform> Video`, `<Platform> - Date`,
`<Platform> Note & Issue ID`) once per platform **x** per tester slot
(commonly 2 tester slots per platform: `Tester 1`/`Tester 2`, or a real name
if already claimed) — see the section above for the current 5-column layout
and the TE Lead's official publishing process, which supersedes manually
identifying and writing into this block except as a fallback. The general
hazard below still applies regardless of which layout is live: columns for
different platforms and different tester slots are visually identical at a
glance when scrolled sideways through a 40+ column sheet — **this is
exactly what caused a real incident** where an entire test case's 30 rows
of data were typed into the wrong tester's column block and went unnoticed
for days.

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

## Claiming a column slot (legacy — confirm this still applies before doing it)

The sheets were restructured on 2026-11-19 (see "Official publishing
process" above) and slot headers reverted to an auto-generated generic
form, sometimes with a machine-filled name prefix already — this may mean
slots are no longer meant to be manually claimed by renaming at all, e.g.
if slotting now happens elsewhere (uTest, a Monday.com board) and just
flows into the sheet's own generated labels. **Confirm with the TTL that
manual renaming is still wanted before doing it.** If it is:

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

## Publishing data: TSV + manual paste (legacy fallback only)

Only relevant when `Review Status` / auto-populate isn't available (see
"Official publishing process" above, which is the default now). See
`sheet_editing_safety.md` for the full reasoning and the exact mechanics.
In short: build the TSV from Tester View data, send it to the user as a
file, and select the destination range in the Browser pane so they paste it
themselves. Prefer this over direct typing for anything more than a couple
of cells, same safety reasoning as always.

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
