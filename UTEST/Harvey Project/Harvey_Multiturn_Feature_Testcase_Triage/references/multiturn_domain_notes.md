# Harvey Multiturn — domain notes

Captured from three sources while building this skill: the "Dogfooding
contract space multi turn" test-plan PDF (dated 2026-10-28), the live Test
Cycle #565709 Overview tab / API (`Harvey AI - Feature (Main) - Multiturn -
Web - 11/13/2026`, status Locked as of 2026-11-17), and a weekly FN sync
recording between Applause and Harvey (2026-10-27). **Treat this file as a
snapshot, not a source of truth** — always re-read the live cycle's own
Overview/known-issues text (Step 2 of SKILL.md) for the cycle actually being
triaged; the feature and its known bugs evolve cycle to cycle, and a
behavior listed as "known" here may be fixed, or a new one may exist, by the
time you're triaging.

## Feature under test

Contract Space multi-turn: a new agreement creates one Space; a later
version of the same agreement, submitted through intake, appends to that
same Space instead of creating a duplicate. The same Space is then used for
Documents (version history), Compare, Review, Ask Harvey, Repair (choosing
a primary contract on a legacy/ambiguous Space), and Merge (combining two
duplicate Spaces on the same client matter).

From the FN sync recording: the version-tracking UI shows a `Latest` badge
and version numbers (V1, V2, …); a new matching version submitted through
intake is auto-matched to the right Space and logged as the next version,
kicking off a new review that follows the existing assignment/routing rules
(no routing differences expected for multi-turn itself at the time of that
sync). The "Ask Harvey" trimmed composer was, as of that sync, expected to
be **informational/read-oriented** (summarize, answer questions, search) —
not yet a confirmed way to edit or reorganize Space documents through chat;
the in-scope list below treats Vault write operations through chat as
explicitly unavailable, consistent with that.

## In Scope (cycle #565709 Overview, verify against the live cycle each time)

- Intake (email `contracts@main.email.harvey.engineering`, and Vault): a new
  agreement creates one Space; a later version appends to that Space only
  when the sender can access it.
- Documents: history, upload, markup, move, and remove keep one correct
  version list.
- Compare and review: Word versions can be compared; review uses the
  selected version and supporting files.
- Ask Harvey: the trimmed composer answers from the current Space; a
  follow-up stays in the same conversation.
- Repair: "Choose the primary contract" turns the selected chain(s) into one
  primary history.
- Merge: two Spaces on the same client matter become one history; the
  source is retired.
- Access and refresh: only the right role can see/change the Space; a
  reload shows the same versions once.
- In-scope components: Assistant, Vault, Contract Intelligence, Playbook.

## Out of Scope

- Any Harvey feature other than Contract Space.
- Creating, assigning, completing, or reopening tasks — including a task
  assigned to Harvey.
- Multi-turn **agent conversation** (distinct from the Contract Space
  multi-turn version history that *is* in scope — don't conflate the two
  when reading a test case title).
- External integrations that are not connected.
- The backfill case, until the sample and its expected values are named.
- Any Beta OS.

## Known issues as of cycle #565709 (Pass/Fail criteria — re-verify against the live cycle)

These are pre-declared: when the described behavior is what you see, the
correct *result* is **Pass**, and no new bug should be filed. A Fail
submitted against one of these, or a new bug filed for one, is itself a
defect in the submission (→ Pending Rejection, per `triage_heuristics.md`).

1. **Manual Upload doesn't use the intake agent yet.** Pass when the Space,
   contract, context, and assignee are right and no second Space is
   created. Fail only when those fields are wrong or a second Space is
   created. (Per-case note seen verbatim on at least one slot description:
   *"A missing review on manual Upload is a known bug: Pass, and do not
   file it."*)
2. **Matching is still partly in review.** A continuation can miss, append
   to the wrong Space, or look like a duplicate — Pass on that match. Fail
   only when original versions disappear or the page fails for another
   reason.
3. **A file added from the composer stays off Documents until reload.**
   Pass when it's missing before reload and present after exactly one
   reload. Fail when still missing after reload, or reload creates a second
   copy.
4. **Some realtime updates are missing** (a second tab can stay stale until
   reload). Pass when the tabs agree after one reload. Fail when they still
   disagree after reload, or a version appears twice.
5. **Some Activity entries are missing.** Pass when this upload has no
   Activity entry. Fail only when the same upload is logged more than once.

The PDF's own "Known Bugs" list (dated 2026-10-28, pre-dates the cycle) is
the same five items in shorter form, plus a sixth not carried into the
cycle's formal known-issues list: *"Adding a contract file using composer
doesn't update FE properly till reload"* — effectively the same behavior as
known issue 3 above, described from the composer side; if a run's Fail
describes this and doesn't match issue 3's own Pass criteria, treat it as
ambiguous (Info Requested) rather than assuming which framing governs.

## Bug-reference convention observed on this cycle

TTLs Dilip Kumar and Urszula Witkowska have each asked testers (on run
#12527406) to "+1 the issue <bugId> and attach video recording/screenshot
showing the actual result to the reported issue" rather than file a new bug
for a repeat occurrence. When a Failed step's `actualResult` only contains a
bug number with no description, that's consistent with this convention
**but incomplete on its own** — confirm (via `messages[]`, `bugsCount`, or
`stepLinkedBugs`) that the +1 and evidence attachment actually happened
before treating the run as complete; if unconfirmed, it's an Info Request
candidate (see `triage_heuristics.md`).

## Environment / evidence requirements (from Issue Reporting Instructions)

- Screenshots mandatory for all bugs.
- MP4 video mandatory for all Functional and Performance bugs, high
  quality, under 5 minutes, focused only on the bug and the steps to
  reproduce it.
- Performance bugs specifically need the video recorded with DevTools
  Network tab open (API request/response times visible).
- If a bug is already reported, the correct tester action is to +1 the
  existing report, not file a near-duplicate.
