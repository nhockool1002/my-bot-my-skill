---
name: Muse_Testcase_Triaging
description: Triage submitted test-case executions for the "Muse" (Meta) project across its per-country uTest test cycles (payments connectors like Stripe Link, Shop Pay, Shopping Catalog, chatbot booking flows, etc.). Unlike other uTest projects, Muse testers record their step-by-step evidence as short videos logged in a companion Google Sheet ("[Tester View] Muse - <Country>") rather than purely as uTest attachments, because the formal uTest test case doesn't list every granular step. This skill pulls each run's claim/submission status from uTest's own JSON API, locates the matching row in the Tester View sheet, downloads each step's video and runs an AI pre-review (frame sampling + local speech-to-text transcription) against that step's Expected Result text to suggest Pass/Fail with a confidence level, then — once the TTL confirms — approves the run in uTest, copies the verified result + video share link into the client-facing "[EXT] Muse - <Country>" sheet, updates the Tracking Sheet (status/device/bug ID), and flags $10 bonus eligibility (submission-to-triage time under 6 hours). Use this proactively whenever the user mentions "Muse triage", "Muse Meta", a platform.utest.com Muse test cycle, or asks to review/triage Muse test case videos — even if they don't name this skill directly.
---

# Muse Testcase Triaging

## What this skill is for

Muse test cycles (one per country/locale — Australia, Netherlands, Spain,
etc.) test a set of payment/booking connectors (Stripe Link, Shop Pay,
Shopping Catalog, chatbot table-booking, …) inside the Muse assistant. Each
connector's real test steps live in a companion Google Sheet, not fully in
the uTest test case itself, because a single connector can need 6–50
individual video steps — far more granular than uTest's own step UI
comfortably holds. So the pipeline spans two systems that must be kept in
sync by the TTL:

1. **uTest** — where testers claim slots and submit an overall Pass/Fail,
   and where the TTL gives the formal Approve/Reject recommendation.
2. **A per-country Google Sheet pair** — the **Tester View** sheet (every
   tester's raw video + notes + bug ID, one row per test case, columns per
   tester per platform) and the **External** sheet (the client-facing copy:
   same rows, but only the *verified* Pass results plus a video
   share-link column), connected by a **Tracking Sheet** that records final
   status/device/bug ID and bonus eligibility.

The actual triage judgment call — does this video really show the Expected
Result — cannot be made from JSON alone. This skill does an **AI pre-review**
of each video (frame sampling + a local transcription pass, see
`references/video_review_technique.md`) and gives you a confidence-scored
suggestion, but you (the TTL) make the final call before anything gets
written back to uTest or copied into the client-facing sheet. Treat every
suggestion as a draft, especially for foreign-language cycles or a video
with no clear verbal/visual confirmation.

## Inputs you need

1. **A uTest test cycle link** for the Muse country/cycle you're triaging —
   `https://platform.utest.com/testcycles/<cycleId>/testcases`.
2. **The Tester View sheet URL** for that same country — e.g.
   `[Tester View] Muse - AU`. Get it from the user, from the cycle's Monday.com
   board entry, or from a link inside the uTest test case's own instructions.
3. **The External sheet URL** (`[EXT] Muse - <Country>`) — same source.
4. **The Tracking Sheet URL** — same source; ask the user if it isn't
   reachable from the other two.
5. **A logged-in browser session** for both uTest and Google (the same
   Google account needs edit access to all three sheets).
6. **Confirmation of the bonus rule for this cycle** — default is $10 for a
   valid triage completed within 6 hours of submission (see
   `references/bonus_rules.md`), but this is a business rule that can change
   per cycle; ask if unsure rather than assuming.

If any of 2–4 is missing, ask the user for it before starting — there is no
API that links a uTest cycle to its Google Sheets automatically.

## Step 0 — Open everything and confirm access

Load the `built-in-browser` skill if you haven't this session. `navigate` to
the uTest test cycle's testcases URL and confirm you're logged in (same
pattern as the AuthorsFirst skills — if redirected to a
`prod-auth.cloud.applause.com` sign-in page, ask the user to sign in
themselves). Open the Tester View, External, and Tracking sheets in separate
tabs and confirm you have edit access (not just viewer) — you'll be writing
to the External and Tracking sheets later.

## Step 1 — Pull claim/submission status from uTest (API first)

Muse runs on the same uTest platform as every other project in this family,
so the exact same internal API applies — see
`AuthorsFirst Project/AuthorsFirst_Testcase_Triaging/references/api_reference.md`
for the full field reference; don't duplicate that discovery effort here.
The one call you need:

```js
const base = '/api/testruns/results?DisplayStart=0&iDisplayLength=1000&testCycleId=<cycleId>'
  + '&approvalStatusId%5B%5D=1&approvalStatusId%5B%5D=2&approvalStatusId%5B%5D=3&approvalStatusId%5B%5D=4&approvalStatusId%5B%5D=5&approvalStatusId%5B%5D=6'
  + '&testRunResultStatus%5B%5D=1&testRunResultStatus%5B%5D=2&testRunResultStatus%5B%5D=3&testRunResultStatus%5B%5D=4&testRunResultStatus%5B%5D=5'
  + '&testRunResultStatus%5B%5D=6&testRunResultStatus%5B%5D=7&testRunResultStatus%5B%5D=8&testRunResultStatus%5B%5D=9&testRunResultStatus%5B%5D=10&testRunResultStatus%5B%5D=11';
const res = await fetch(base, {credentials:'include'});
const rows = (await res.json()).data.data;
JSON.stringify(rows.map(r => ({testRunResultId: r.testRunResultId, testCaseName: r.testCaseName, tester: r.testerName, status: r.testRunResultStatusDescriptor.name, submitDate: r.submitDate, environmentDescription: r.environmentDescription})));
```

Skip `Unclaimed` and not-yet-submitted (`New`/`Started`) rows — nothing to
triage yet. Queue every `Passed`/`Failed` row. `submitDate` (epoch ms) is
what the bonus check in Step 8 is measured against — record it per run now.

## Step 2 — Find the matching row in the Tester View sheet

The Tester View sheet is organized **one row per test-case/connector step**,
with a block of columns per tester per platform (e.g. "iOS Result — what you
see (Priyanka Sharma)", "iOS Notes", "Android Result — what you see (tester
2)", …) rather than one row per uTest run. Match on tester name + platform
(iOS/Android) + connector/test case name from Step 1's queue. Each matched
cell set gives you, per step: the Pass/Fail the tester entered, their notes,
a bug ID if Failed/Blocked, and a video link (usually a Google Drive share
link pasted directly into the cell or an adjacent column).

If you can't find a tester's row (name spelled differently, sheet tab for
the wrong connector), say so explicitly rather than guessing — don't invent
a Pass/Fail for a step you couldn't locate.

## Step 3 — AI pre-review each step's video against its Expected Result

For each step with a video link:

1. Resolve the share link to a downloadable file (Google Drive: use the
   Drive connector if available, or the direct-download form of the share
   URL; uTest-hosted videos resolve the same way as any other uTest
   attachment — see the AuthorsFirst skill's attachment-resolution note).
2. Run the frame-sampling + transcription pass described in
   `references/video_review_technique.md` — this is the exact technique of
   extracting periodic frames with `ffmpeg` and transcribing any narration
   with the local `whisper-cli` model, then reading both against the step's
   `Expected result` column text (and `Precondition`/`Steps` columns if the
   sheet has them, matching the catalog structure seen in the External
   sheet's connector tabs).
3. Produce a **confidence-scored suggestion**: `Likely Pass`, `Likely Fail`,
   or `Unclear — needs human review`, with the specific frame timestamp or
   transcript line that drove the call. Never silently upgrade "Unclear" to
   a Pass/Fail — surface it.
4. For a foreign-language cycle, note in the suggestion if the transcript
   itself looks garbled or low-confidence (small local models struggle with
   non-English speech) — flag for the TTL to double check with Google
   Translate/Gemini per the cycle's own language, don't claim certainty you
   don't have.

This step produces **suggestions for the TTL to confirm**, not a final
verdict — present them clearly (step, suggestion, confidence, evidence
cited) and wait for the TTL's go-ahead before Step 4.

## Step 4 — TTL confirms, then write back

Once the TTL confirms a step's (or a whole run's) verdict:

- **If the run's steps all check out (Pass):**
  1. In uTest, open that run and apply the Approve recommendation
     (**Recommendation → Add → Approve → Save Recommendation** — same UI
     flow as every other uTest project; verify the page afterward shows
     `Pending Approval`, not just that the save button was clicked).
  2. In the External sheet's matching connector tab, copy the row's
     Pass results and notes from the Tester View sheet, and paste the
     **verified** video share link into its dedicated column — only after
     you've actually confirmed the video shows what it claims, never before.
- **If a step is Failed/Blocked:** confirm a bug ID is present (ask the
  tester for one if missing — this project's own convention, per the
  walkthrough, is that *every* Failed step needs a bug ID even in a run with
  40–50 steps). Don't copy a Failed row into the External sheet as if it
  were a client-facing Pass.

## Step 5 — Update the Tracking Sheet

For every triaged run, record: final status (Pending Approval / Information
Request / Pending Rejection), device/environment (from Step 1's
`environmentDescription`), and bug ID(s) if any. Match the Tracking Sheet's
existing column layout exactly — don't invent new columns.

## Step 6 — Bonus eligibility

See `references/bonus_rules.md` for the full rule and edge cases (blocked
testers, multi-session submissions). Default: compare Step 1's `submitDate`
against the triage completion time (now); if the gap is under 6 hours **and**
the result is valid, flag the tester for the $10 bonus in the Tracking
Sheet's bonus column. Always confirm this threshold with the user before
applying it, since it's a per-cycle business rule, not a platform constant.

## Step 7 — Always produce the bilingual output together

Same convention as every other project skill in this family:

1. **Triaged result table** (`| Tiếng Việt | English |` rows), one per run:
   tester, connector/test case, verdict, confidence of the AI pre-review,
   and what specifically was checked.
2. **Flag list** for anything the AI pre-review marked `Unclear` or
   low-confidence — these need the TTL's own eyes on the video before being
   treated as final, list them separately so they're not lost in the main
   table.
3. **Final summary for the TE Lead/TTL lead**, bilingual, grouping by
   verdict with counts, naming specific connectors/testers, and stating how
   many runs were approved + copied to the External sheet vs. still pending
   human video review vs. bonus-flagged.
