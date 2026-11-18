---
name: Harvey_Multiturn_Feature_Testcase_Triage
description: Triage submitted test-case executions on uTest for the Harvey.ai "Contract Space — multi-turn, repair, and merge" feature (test cycle family "Harvey AI - Feature (Main) - Multiturn - Web", e.g. cycle #565709). Input is one or more platform.utest.com test-case run links (`.../testcycles/<cycleId>/testcases/<testRunResultId>`) pasted by the user — never a whole cycle unless the user explicitly asks to triage "all" or "the whole cycle". For each given run this skill pulls the run's full step-by-step detail straight from uTest's own JSON API (falling back to the browser UI only if the API is unreachable), checks it against this feature's own known-issues list (both the cycle Overview's list and the per-test-case "known bug: Pass, do not file" notes baked into several slot descriptions), classifies it into Pending Approval, Info Requested, or Pending Rejection with a concrete step-cited summary, and — whenever a run needs the tester to update, clarify, or add something — drafts a ready-to-send IR (Information Request) message as a bilingual Vietnamese/English table for the TTL to compare before sending (never sends it). Never changes the Approval status or sends the message itself; always stops and hands the TTL the verdict + message to review and act on manually. Use proactively whenever the user pastes one or more Harvey Multiturn test-case links and asks to "triage testcase", "duyệt testcase", "chấm testcase", "review these test cases" — even without naming this skill.
---

# Harvey Multiturn Feature — Testcase Triage

## What this skill is for

Harvey AI's Contract Space multi-turn feature (intake → new negotiation
turn, Documents/version history, Compare & Review, Ask Harvey, Repair a
legacy primary chain, Merge duplicate Spaces) is tested on uTest through
test cases claimed and run by Test Engineers (TEs): Dilip Kumar, Urszula
Witkowska, Kevin Schumacher, Aman Ali, plus other testers such as Hai Vu Anh
and Paul Xu. The TTL for this cycle family is Nhut Nguyen. A tester claims a
case, works a fixed sequence of steps (instructions + expected result +
required screenshots/video), marks each step Pass/Fail, and submits. Before
the TTL acts on a submission it needs a verdict: did the tester genuinely do
what the step asked, is the attached evidence real and sufficient, does a
Fail actually hold up once you check it against this feature's own known
bugs, and does the overall result match what the steps show?

This is modeled on the sibling `AuthorsFirst_Testcase_Triaging` skill — same
uTest API family, same "API first, verify evidence yourself, cite the
specific step" philosophy — adapted for Harvey Multiturn's own domain rules
in `references/multiturn_domain_notes.md`.

## Inputs you need

1. **One or more test-case run links**, as pasted by the user, in the form
   `https://platform.utest.com/testcycles/<cycleId>/testcases/<testRunResultId>`.
   The user may paste a single link or several in one message — triage every
   one given. **Do not go fetch or triage anything beyond what was pasted.**
   In particular, never pull and triage a cycle's full test-case list unless
   the user explicitly asks for "all test cases" / "toàn bộ testcase" /
   "cả cycle" for a given cycle.
2. A logged-in TTL session in the browser (the built-in browser skill's
   persistent session). If the session isn't logged in, say so and ask the
   user to sign in — never guess or enter credentials yourself.

If a link's `testRunResultId` can't be resolved (bad link, wrong cycle
family, 404), say so for that specific link and continue with the rest
rather than aborting the whole batch.

## API-first, UI as fallback

uTest's SPA is backed by a plain JSON REST API under `/api/...`, callable
with `fetch(url, {credentials:'include'})` from the logged-in tab — verified
working against Harvey cycle #565709 during this skill's development.
**Always try the API calls below first**; only fall back to driving the
rendered UI (`get_page_text` on the test case's Description/Messages/History
tabs) if a call 404s, 403s, or its shape no longer matches
`references/api_reference.md` — this is an internal API uTest can change
without notice. Full endpoint/field reference, shared with the AuthorsFirst
skill family, lives in `references/api_reference.md`.

## Step 0 — Open the browser and confirm login

Load the `built-in-browser` skill if you haven't already this session. Pick
any one of the given links and `navigate` there to confirm the session is
logged in (the page should render the cycle name and TTL status, not a
sign-in page). If it redirects to a sign-in page, tell the user and ask them
to sign in in the Browser pane. Wait a couple of seconds after navigation —
this is a client-rendered app and content is empty for the first moment.

## Step 1 — Extract cycle + run IDs from each given link

Parse `cycleId` and `testRunResultId` out of each pasted URL. Group by
`cycleId` (usually all links share one cycle, but don't assume it).

## Step 2 — Pull each cycle's Overview + known-issues text once

For each distinct `cycleId` in the batch:

```js
const res = await fetch(`/api/testcycles/${cycleId}/details?testCycleInstructionTypeIds=1`, {credentials:'include'});
const d = (await res.json()).data;
```

Read `d.inScope`, `d.outScope`, `d.issueReportingInstructions`,
`d.teamContactInformation` (HTML strings). The cycle's **Known issues**
list — behaviors that must be marked Pass, not Fail, and must not get a new
bug filed — is embedded as plain text/HTML within `inScope` (or
`specialInstruction` if `inScope` doesn't have it); it is not a separate
API field. Cross-check whatever you find here against
`references/multiturn_domain_notes.md`, which has the known-issues list
captured as of this skill's authoring — the live cycle is authoritative if
the two disagree (the feature evolves cycle to cycle). **Fallback:**
`navigate` to `https://platform.utest.com/testcycles/<cycleId>/` and read
the Overview tab with `get_page_text`.

## Step 3 — Pull full step detail for each given run

```js
const res = await fetch(`/api/testruns/results/${testRunResultId}?markMessagesAsRead=false`, {credentials:'include'});
const { testRunResult, testCase, messages } = (await res.json()).data;
```

Field reference in `references/api_reference.md`. Two Harvey-specific things
to always check on top of the generic shape:

- **`testRunResult.slotDescription` / `testCaseDescription`** often embeds a
  per-case known-bug instruction directly in its own text, e.g. *"A missing
  review on manual Upload is a known bug: Pass, and do not file it."* Read
  this field's full text for every run — it can override what you'd
  otherwise conclude from a Fail, and it is specific to that test case, not
  just the cycle-wide list from Step 2.
- **`actualResult`** on a Failed step frequently names an existing bug ID
  with little or no description (sometimes literally just the bug number,
  e.g. `"7313862"`). Per this cycle's own messaging pattern (see history on
  run #12527406), the expected tester behavior is: **+1 the existing bug
  report and attach the video/screenshot evidence to that bug**, not file a
  duplicate. A bare bug-ID actual result with no readable description is a
  real candidate for an Info Request asking the tester to confirm the +1 and
  evidence were attached to the bug itself (check whether `bugsCount`/
  `stepLinkedBugs` on that step already shows it before assuming it's
  missing).

Check `messages` (and `numberOfMessages`/`unreadMessages` from the list
call, if you also fetched one) before drafting anything — if a TTL already
asked this tester for the same thing and the tester replied "Done", don't
re-ask; verify what they say they did instead.

## Step 4 — Evaluate against Harvey Multiturn's own domain rules

Work through every step of each run:

1. **Did the tester actually do what the instruction asked?** Compare
   `actualResult`/`comment`/attachments against the step's `INSTRUCTION` and
   `EXPECTED_RESULT` modules — not just whether something was filled in.
2. **Is the required evidence present and real?**
   `MINIMUM_REQUIRED_ATTACHMENTS.attachments.length` should meet
   `.minNumberOfAttachments`. Screenshots are mandatory for every bug;
   MP4 (under 5 minutes) is required for Functional/Performance bugs per
   this cycle's Issue Reporting Instructions — a Failed step citing a new
   bug with only a screenshot and no video (or vice versa, where video is
   required) is incomplete. Open the attachment when a step is ambiguous,
   Failed, or decisive, and confirm it actually shows the claimed Harvey UI
   action — not a mismatched or irrelevant file.
3. **Does a Failed step match a known issue?** Check both Step 2's
   cycle-wide Known Issues list and the per-case text from Step 3. If it
   matches, the correct result is **Pass**, no new bug — a Fail here is
   itself the defect in the submission, not a legitimate finding. See
   `references/multiturn_domain_notes.md` for the specific known-issue
   patterns and their Pass/Fail criteria as last captured.
4. **Does scope apply?** Out of Scope for this feature family includes: any
   Harvey feature other than Contract Space, task creation/assignment/
   completion/reopening (including a task assigned to Harvey), multi-turn
   *agent conversation* (as opposed to the Contract Space multi-turn version
   history under test), unconnected external integrations, the backfill
   case until named, and any Beta OS. A run exercising out-of-scope behavior
   isn't a clean Approval regardless of how well the steps were executed.
5. **Is the overall Passed/Failed status consistent with what the steps
   show?** An overall Pass with a step whose evidence plainly contradicts
   the expected result, or a required step silently skipped, is not a clean
   Approval just because the tester marked it Passed.

Full verdict criteria and judgment patterns in
`references/triage_heuristics.md` (shared logic with the AuthorsFirst
skill — written generically, applies here unchanged).

## Step 5 — Classify each run

| Verdict | When |
|---|---|
| **Pending Approval** | Every step genuinely followed, evidence meets the stated minimum and (where opened) verified as real, any Failed step is either a genuine new defect with correct evidence or correctly matches a known issue and was marked Pass, nothing violates scope. |
| **Info Requested** | Genuinely ambiguous — missing required attachment that otherwise reads like the step was done, a Failed step citing a bare bug ID with no confirmation the bug itself got the +1/evidence, unclear whether a known-issue match applies, or overall status disagrees with step status in a way that isn't self-explanatory. Ship with a drafted message (Step 6). |
| **Pending Rejection** | Evidence clearly contradicts the claimed result or is reused/irrelevant, a required step was skipped outright, a Fail clearly matches a known issue (per Step 4.3) and should have been Pass with no new bug, or an out-of-scope action was performed and reported as if in-scope. |

Every run gets a concrete, step-cited summary — name the step number/name
and quote the specific instruction, known-issue line, or scope rule that
drove the verdict. A bucket label alone is not acceptable output.

## Step 6 — Produce the triage output

For every batch, produce all of the following together, every time:

1. **Triaged result table** — one row per run: tester, test case name, run
   ID, verdict, evidence-cited summary (cite step numbers and, where
   relevant, the known-issue/scope rule applied).
2. **IR / rejection message(s)** — one per run in Info Requested or Pending
   Rejection, per `references/message_templates.md`: a
   `| Tiếng Việt | English |` table with the full ready-to-send message in
   each cell, naming the test case, run ID, step(s), and the concrete action
   needed from the tester. **Draft only — never send it and never change the
   run's Approval status yourself.** These are handed to the user so they
   can compare the Vietnamese and English wording before sending.
3. **Short batch summary** — one line per verdict bucket with counts, so the
   user can see the whole batch's outcome at a glance.

Keep all three internally consistent — every claim in a message must trace
back to a row in the triaged table.
