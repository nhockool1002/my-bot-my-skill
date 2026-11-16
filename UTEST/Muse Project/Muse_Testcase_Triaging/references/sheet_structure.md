# Observed Google Sheet structures

Captured from screen-share frames of the TTL onboarding walkthrough this
skill was built from — **not yet verified against a live sheet**. Treat
every column name here as a best guess to confirm on first use, not a fixed
schema. If a real sheet doesn't match, trust the real sheet and update this
file rather than forcing the data to fit.

## Applause Allowlisting Sheet (pre-activation, not directly handled by this
skill's steps, but useful context for why a tester's uTest claim might be
blocked)

Columns observed: Tester Name, Country, Meta Platform tested (iPhone/
Android App), Allowlist process, TF mail (TestFlight email), GPlay email,
Email will be used for Muse, QA, Permission Status, Comments/Notes from
Meta.

Flow: tester's form response → a separate **Meta Allowlisting Sheet** (after
TTL cross-checks evidence/screenshot) → this Applause sheet (after the
client/Meta confirms) → this is the sheet the client reads to know who's
onboarded.

## Tester View sheet (`[Tester View] Muse - <Country>`)

One row per test-case/connector step, **not** one row per tester — instead
there's a repeating block of columns per tester per platform:
`<Platform> Result - what you see (<Tester Name>)`,
`<Platform> Notes - what you see (<Tester Name>)`, repeated for each tester
who ran that step, for both iOS and Android.

Likely also has, per the External sheet's connector tabs (below): Connector,
Test case title, Expected result, Error category. Tabs are per connector:
"Connector Stripe Link", "Connector Shop Pay", "Connector Shopping Catalog",
etc.

Video evidence is pasted as a share link, either directly in the Notes cell
or an adjacent column — confirm which on first use, it may vary by sheet.

## External sheet (`[EXT] Muse - <Country>`)

Client-facing. Tabs observed: "Connector Stripe Link", "Connector Shop Pay",
"Connector Shopping Catalog", "AU connectors (in-market)", "Connector Global
PO (full)" — tab names vary by country/scope. Columns observed on the
catalog-style tabs: `#`, Connector, Test case title, Precondition, Steps,
Expected result, Error category.

Per the walkthrough, after triage the TTL adds the **same** Pass results
columns as the Tester View sheet, **plus one additional column**: the
verified video share link. That is the one structural difference between
Tester View (internal, raw) and External (client-facing, verified) —
confirm the exact column position on first use.

## Tracking Sheet

Referenced by name in the walkthrough but not shown on screen in enough
detail to document its columns here. Expect at minimum: test case / run
identifier, final status, device/environment, bug ID, bonus-eligibility
flag. Read the real sheet's header row before writing anything to it — do
not assume this list is complete or in the right order.

## Monday.com board

Used for: TTL-to-cycle assignment (find your name in a column to know which
cycle(s) you're responsible for), and as one place to find the Tester View
sheet link for a given cycle if it's not linked from the uTest test case
itself. Not yet integrated into this skill's steps — ask the user for the
direct sheet links if the Monday board isn't accessible.
