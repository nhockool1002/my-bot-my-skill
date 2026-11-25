---
name: Muse_TTL_Triage_v2_25_Nov
description: Full end-to-end TTL workflow for the Muse (Meta) in-market testing project on uTest — not just evidence triage, but the whole job a Muse TTL does, cycle by cycle, as walked through live in the 2026-11-24 TTL onboarding call (Monday.com board navigation, Meta account sourcing + allow listing, the Tester Sheet / External Sheet / Meta Tracking Sheet trio with its now-automatic hourly sync, the $10/$20 bonus rules, and the Management-tool "Slotting" procedure for assigning testers to sheet columns). Use this whenever the user pastes a Muse/platform.utest.com link or Monday.com board link and asks to "triage", "duyệt", "chấm", "slot a tester", "allowlist", "check the tracking sheet", or otherwise work a Muse cycle — even without naming this skill. This is the v2 update (25 Nov 2026) of Muse_TTL_Triage; see `../Muse_TTL_Triage_v1/` for the prior version's deep evidence-verification hard rules (frame-sampling density, EXT column-guessing safety), which still apply and are referenced from here rather than duplicated.
---

# Muse TTL Triage — v2 (25 Nov 2026)

## What changed from v1

[[Muse_TTL_Triage_v1]] (`../Muse_TTL_Triage_v1/`) covered cycle discovery,
allowlisting and the Connector-vs-Browser Pass/Fail rule in its README, and
went deep on evidence-review mechanics (Steps 4-6: pulling Tester View
evidence, reviewing video, publishing to EXT/Tracking) in its SKILL.md. This
v2 is built from a **live TTL onboarding call recorded 2026-11-24** (not
reconstructed after the fact) given by a TTL ~3 weeks into the project,
followed live by several other TTLs asking real questions — so it's heavier
on *mechanics TTLs actually get stuck on* than v1 was: the Management-tool
"Slotting" procedure (not covered in v1 at all), the exact Tracking Sheet
flow-naming convention, and a handful of real edge cases from the Q&A.

**Source material:** a ~90-minute screen-share recording (YouTube, private,
auto-dubbed to Vietnamese — the transcript below is read off the Vietnamese
audio track) plus a companion English Gemini meeting-notes summary of the
same call. Both describe the same session; cross-check between them where
one is ambiguous. **One transcription quirk to flag:** the Vietnamese audio
consistently renders the project's name as "News" where context makes clear
it means **Muse** (e.g. "News Local Connector" = "Muse Local Connector") —
auto-dub mishearing, not a different project. Treat exact sheet/column/tab
names below as a map to confirm against the real documents on your actual
cycle, not a guaranteed schema — this is explicitly how the presenter
themselves framed it ("treat this as a starting point, ask on Slack if
something's changed").

## 1. Finding your cycle (Monday.com board)

Each Muse cycle (one per country/locale) is a row on a Monday.com board.
Filter the board by **Person** and select your own name to find which
cycle(s) you're assigned — usually one or two. That row links out to the
sheets everything else in this skill works from:

- **ITW / tester platform link** — the `platform.utest.com` link for that
  cycle, used for claiming/triaging test cases and for Approve actions.
- **Tester Sheet** — where testers log their own results.
- **TTL Sheet** (bundles the **Meta Tracking Sheet**) — where the TTL
  records the final outcome per test case.
- **External ("EXT") Sheet** — the client-facing sheet.
- **Meta Allow Listing Sheet** / **Meta Account Sourcing Sheet** — pre-cycle
  tester-account onboarding (see §3).

You're not confined to only your assigned cycle — a TE may ask you to help
on another active cycle if its workload is heavier; that's normal, follow
the TE's redirect when it happens. Keep to **one Slack thread per cycle per
day** (don't open a second thread for a cycle that already has one today),
and CC the cycle's primary TE, support TE, and any other TTLs working it so
people don't duplicate a thread that already exists.

## 2. The Tester Sheet → External Sheet → Tracking Sheet trio

See `references/sheet_conventions_v2.md` for the full column-by-column
detail. The short version:

- **Tester Sheet** — testers fill in their own `Pass`/`Fail`/`Partial`/
  `Blocked` result, notes, and (for `Fail`) an **Issue ID** (the cell goes
  red if left blank on a Failed row). Comments are required on **Failed**
  rows, optional on **Passed** rows. Some rows are pre-marked
  `removed by Meta` / `Meta` — that's expected scope-reduction, not a
  defect; just counter-check it, don't chase it as a bug.
- **External Sheet** — **results now auto-sync from the Tester Sheet
  roughly every hour** (this is no longer a TTL copy-paste job — if you see
  this as manual work, you're on a stale process). The TTL's own job on
  this sheet is only: (a) confirm the auto-synced result actually matches
  what's in the Tester Sheet, (b) attach the **video link** for that step —
  tester platform → External Sheet video-link transfer is **not**
  automatic and is required for **every** step, passed or failed, and
  (c) once both are right, mark that row **`Validated`**.
- **Meta Tracking Sheet** — one row per test case run: test case ID, tester
  name, country (separate tabs per region — UK, and then EMEA / APAC
  tabs), result, approval status (`Pending Approval` / `Info Request`),
  device used, the `Flow` field (naming convention below), and — if
  Failed — the bug ID.

### Flow naming convention (Tracking Sheet)

`<Project> <Sheet tab name> <Feature> <test case number or range>` — e.g.
for a row on the "UK browser partners in market" tab, feature "JD Sports",
single test case 4: project prefix (read aloud as "News", i.e. **Muse**) +
`UK browser partners in market` + `JD Sports` + `4`. For a range of test
cases sharing one flow, write the range (e.g. `1-15`), not a list. **Confirm
the exact separator/format against neighboring rows already on your
cycle's Tracking Sheet** — the call demonstrated the four components but
didn't spell out punctuation, and v1's own Tracking Sheet examples
(`Connector Shopping Catalog`, `Stripe Link`, `Shop Pay`) look like just the
feature name alone, so this 4-part form may be specific to Local-Connector-
style cycles rather than universal — don't overwrite an existing row's Flow
value to "fix" it into this format without checking first.

### Bonus rules

$10 if a test case is completed within **6 hours of the tester claiming
it**; $20 for test cases run during a flagged **weekend priority cycle**,
if completed within the cycle's own stated window. Both are announced on
Slack/the platform when active — don't infer eligibility without a live
announcement for anything beyond the standing $10/6h rule. **Flexibility on
IR back-and-forth:** if a tester's *first* submission after claiming came
in within 6 hours, they stay bonus-eligible even if a later Info Request
round-trip pushes the *final* validated time past 6 hours — human error in
one step isn't supposed to cost them the bonus. If genuinely unsure on a
specific case, ask on Slack (CC the TE Lead) rather than guessing either
way.

### Two things that trip people up — flag both for every IR you send

1. **Upload the video link for already-correct steps immediately** — don't
   wait for a tester to fix the one bad step before pushing any of the good
   ones to External. If steps 1-6 are correct and only step 7 needs an IR,
   validate and attach video for 1-6 **now**. This means a different TTL
   coming on shift later only has to deal with the one outstanding step
   instead of re-reviewing the whole test case from scratch.
2. **Flip the row's status from `Validated` back to `Info Request` (or
   `Pending`) when you send an IR**, not just when you first review it —
   `Validated` **locks** the tester's cells, so if the row is still marked
   `Validated` the tester literally cannot edit it to act on your IR. See
   [[project-muse-utest]] for the full `Review Status` value set and lock
   behavior this was first documented against.

## 3. Meta account sourcing & allow listing (pre-activation)

Before a cycle goes `Active` it sits `Pending Activation` while tester
accounts are collected:

1. Testers claim a **participation slot** and submit an allow-listing form
   (iOS: TestFlight email + Muse/News account email; Android: Google/Play
   Store email + Muse account email).
2. Submitted data auto-populates the **Meta Account Sourcing Sheet**.
3. The TTL copies each tester's row from there into the **Meta Allow
   Listing Sheet**, under the correct country section, marks that row
   **`Yes`**, and **highlights the row green** once copied. Leave
   `Account type` blank if the sheet doesn't ask you to fill it.
4. Per [[project-muse-utest]] / v1's README, confirmed entries then move on
   to the client-facing **Applause Allowlisting Sheet** once the client
   itself confirms them — this call didn't re-demo that final hop, so
   treat it as still accurate from v1 rather than superseded.

Full step-by-step in `references/account_sourcing_and_allowlisting.md`.

## 4. Slotting a tester onto the Tester Sheet (Management tool)

New in this call — not covered by v1 at all. Because many testers work the
same Tester Sheet tab, an un-slotted sheet makes it hard to tell who filled
which column. When a tester claims a test case (or messages asking which
column to use), assign them a specific column via the **Slotting** tab and
the **M tool** (Management tool) menu:

1. On the **Slotting** tab, find the sheet-tab/feature's existing slot
   ranges and pick an **open** column (e.g. `Android 1` vs `Android 2` vs
   `Android 3`) with no one already assigned to the tester's test case
   number.
2. If the open slot currently covers a wider range than just this tester's
   case(s) (e.g. a block covering cases 1-11 but this tester only has case
   4), you need to **split** it down to just their case(s) first — select
   the row, open **M tool → Split**, and split down to the range *before*
   theirs, then **M tool → Split a slot in row** again on the remainder to
   isolate exactly their case number(s). Each split runs a script — wait
   for the "Running script" indicator to clear before doing anything else
   to that row.
3. Once split, copy the tester's name and test case ID into the new row —
   the sheet auto-fills a formula-driven link straight to that test case.
   The corresponding column on the Tester Sheet (e.g. `Android 1`) picks up
   the tester's name automatically after a short propagation delay — don't
   assume it failed just because it hasn't updated within a few seconds.
4. Message the tester (platform chat) once slotted: confirm which column
   is theirs and ask them to start at their earliest convenience.

**When to slot:** proactively when you have spare time and a test case is
still unclaimed/unstarted, but realistically **most slotting happens
reactively** — either while you're already triaging a test case, or the
moment a tester messages asking which column to use. This is normal; the
presenter was explicit that trying to slot 100% proactively during a
high-volume cycle isn't realistic. Check the platform chat frequently
(every 15-60 minutes if you can) specifically so these requests don't sit
unanswered. A test case that's filled in but was never pre-slotted is not a
problem — split and backfill the tester's name during triage itself.

Full step-by-step (with the exact menu path) in
`references/tester_slotting.md`.

## 5. Edge cases from the Q&A

- **A row shows `Validated` on the Tester Sheet but the test case still
  isn't Approved on uTest, and you didn't validate it yourself.** Don't
  just re-validate or second-guess it. Check the sheet's own **edit
  history** on that cell to see which TTL touched it and when; if it's
  still ambiguous, ask on the cycle's Slack thread (CC the TE / other
  TTLs) rather than guessing or silently overriding someone else's work.
- **A tab name on the tester platform doesn't match any Tester Sheet tab
  name.** Confirmed real for **Local Connectors UK** specifically (covers
  easyJet, H&M, M&S, Just Park) — the platform may show a cycle-level
  label like "PO UK regional retail" where the actual Tester Sheet tab is
  "Local Connectors UK". Every *other* sheet type's tab name matches the
  platform's naming exactly — this mismatch is a known one-off, not a
  sign you're in the wrong sheet generally.
- **A client adds a new test case directly on the External sheet, but it
  doesn't show up on the Tester Sheet.** TTLs don't have permission to add
  new test-case slots to the Tester Sheet — only TEs do. Flag it to the TE
  rather than trying to add the row yourself.
- **How long should triage take?** No fixed number — a single-step test
  case and a 15-scenario flow are not comparable. Report your actual time
  honestly; the TE Lead's own stated bar is just "reasonable," not a fixed
  SLA.

## Carried forward from v1 — still apply

The engineering-safety practices below came from real incidents on this
project's sheets and are independent of which workflow version is current.
See `../Muse_TTL_Triage_v1/references/` for the full text; copies also live
in this skill's own `references/` so v2 is self-contained:

- **Frame-sampling density must scale with video duration**, never a fixed
  frame count — `references/video_evidence_heuristics.md`.
- **Never guess a column block on a shared sheet; never bulk-type directly
  into one; never `Cmd+A` inside a cell-edit box** —
  `references/sheet_editing_safety.md`.
- Draft any tester- or TE-facing message as a bilingual
  `| Tiếng Việt | English |` table and let the TTL send it themselves —
  these skills never send a message or change an approval status on their
  own initiative.
