---
name: AuthorsFirst_Testcase_Triaging
description: Triage submitted test-case executions on uTest for the "Authors First" streaming-app project (iOS, iPadOS, Apple TV, Android, Web test cycles). Given a platform.utest.com test cycle URL, this skill logs in, pulls the cycle's Overview rules and its full test-case run list straight from uTest's own JSON API (falling back to the browser UI only if the API is unreachable), skips Unclaimed and not-yet-submitted (New/Started) runs, opens every submitted run's step-by-step instructions/expected results/actual evidence, and classifies each one into Pending Approval, Information Request, or Pending Rejection — always with a concrete per-step-cited summary, always with a ready-to-send bilingual (Vietnamese/English) message for anything needing more info or being rejected, and always with a final bilingual summary for the TE Lead. This is the sibling skill to AuthorsFirst_Issue_Triaging (same project, same API family) but reviews Test Cases instead of Issues. Use this proactively whenever the user pastes an Authors First test cycle or test-cases URL and asks to "triage testcases", "review submitted test cases", "chấm testcase", "duyệt testcase mới" — even if they don't explicitly ask for the summary messages or mention this skill by name.
---

# AuthorsFirst Testcase Triaging

## What this skill is for

Each Authors First test cycle is driven by test cases: a tester claims one,
works through a fixed sequence of steps (instructions, required screenshots/
video, sometimes survey questions), marks each step Pass/Fail, and submits
the whole run. Before a TTL can act on a batch of submissions, every one
needs a verdict: did the tester actually do what the step asked and back it
up with real evidence (→ Pending Approval), is something missing or
ambiguous that only the tester can clarify (→ Information Request), or does
the submission clearly fail to hold up once you look at what was actually
submitted (→ Pending Rejection)?

This is the sibling of `AuthorsFirst_Issue_Triaging` — same project, same
uTest API family, same "API first, verify evidence yourself, cite the Overview's
own rules" philosophy — but it reviews **test-case run submissions**
instead of **bug reports**. If both skills are relevant to the same cycle,
a Failed step on a test case is usually *because* of a bug the tester filed
on that step — cross-reference that bug's own triage verdict (Step 5) before
deciding whether the Failed status itself holds up.

## Inputs you need

1. A uTest test cycle link for an Authors First cycle — either form works:
   `https://platform.utest.com/testcycles/<cycleId>/` or
   `.../testcycles/<cycleId>/testcases`.
2. A logged-in tester session in the browser. If the user hasn't specified
   which runs to triage, default to every **submitted** run (`Passed` or
   `Failed` status — see Step 3); if they give specific test-case names or
   tester names, narrow to those.

No Excel/Datasheet is needed — everything comes from the test cycle itself.

## API-first, UI as fallback — read this before Step 1

Exactly like `AuthorsFirst_Issue_Triaging`: uTest's SPA is backed by a plain
JSON REST API under `/api/...`, callable with
`fetch(url, {credentials:'include'})` from the logged-in tab. **Always try
the API calls in Steps 1–4 first**; only fall back to driving the rendered
UI (the Test Cases tab's table, pagination, status filters) if a call 404s,
403s, or its shape no longer matches `references/api_reference.md` — this is
an internal API uTest can change without notice.

## Step 0 — Open the cycle and confirm login

Load the `built-in-browser` skill if you haven't already this session, then
`navigate` to the cycle's test cases URL
(`https://platform.utest.com/testcycles/<cycleId>/testcases`). If it
redirects to a `prod-auth.cloud.applause.com` sign-in page, tell the user and
ask them to sign in in the Browser pane — never guess or enter credentials
yourself. Dismiss the cookie-consent banner if it appears. Wait a couple of
seconds after navigation before reading anything — this is a client-rendered
app and content is empty for the first moment.

## Step 1 — Pull the cycle's Overview rules via API

Identical call to the Issue Triaging skill — reuse it if you've already
fetched it this session for the same cycle:

```js
const res = await fetch('/api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1', {credentials:'include'});
const d = (await res.json()).data;
JSON.stringify({inScope: d.inScope, outScope: d.outScope, issueReportingInstructions: d.issueReportingInstructions, teamContactInformation: d.teamContactInformation});
```

You need this for Step 6's scope checks (e.g. "purchases are out of scope
this round" directly affects whether a purchase test case that claims to
have completed a purchase is acceptable) and for addressing the TE Lead
summary to the real name. **Fallback:** `navigate` to
`https://platform.utest.com/testcycles/<cycleId>/` and read the Overview tab
with `get_page_text` if the API call fails.

## Step 2 — Pull the cycle's full test-case run list via API

```js
const base = '/api/testruns/results?DisplayStart=0&iDisplayLength=1000&testCycleId=<cycleId>'
  + '&approvalStatusId%5B%5D=1&approvalStatusId%5B%5D=2&approvalStatusId%5B%5D=3&approvalStatusId%5B%5D=4&approvalStatusId%5B%5D=5&approvalStatusId%5B%5D=6'
  + '&testRunResultStatus%5B%5D=1&testRunResultStatus%5B%5D=2&testRunResultStatus%5B%5D=3&testRunResultStatus%5B%5D=4&testRunResultStatus%5B%5D=5'
  + '&testRunResultStatus%5B%5D=6&testRunResultStatus%5B%5D=7&testRunResultStatus%5B%5D=8&testRunResultStatus%5B%5D=9&testRunResultStatus%5B%5D=10&testRunResultStatus%5B%5D=11';
const res = await fetch(base, {credentials:'include'});
const rows = (await res.json()).data.data;
JSON.stringify(rows.map(r => ({testRunResultId: r.testRunResultId, testCaseName: r.testCaseName, tester: r.testerName, status: r.testRunResultStatusDescriptor.name, approvalStatus: r.approvalStatusDescriptor.name, failedStepNumber: r.failedStepNumber, submitDate: r.submitDate, verificationBugId: r.verificationBugId})));
```

One call returns **every** test-case run tied to the cycle, whatever its
status. `testRunResultStatusDescriptor.name` is the field that matters most:
`New` (claimed, not started), `Started` (in progress), `Passed` / `Failed`
(submitted — these are the ones to triage), `Unclaimed` (returned/expired
without being worked — **always skip these**, per this skill's whole
purpose). Full field reference in `references/api_reference.md`.

## Step 3 — Build this run's triage queue

From Step 2's rows:
- **Skip** every row with `status === 'Unclaimed'` — explicitly out of scope
  for this skill.
- **Skip** `New` and `Started` — nothing has been submitted yet, there's
  nothing to triage. Note the count of these separately (useful context for
  the TE Lead summary — "N test cases still in progress") but don't treat
  them as needing a verdict.
- **Triage** every row with `status` in `Passed` or `Failed` — these are
  completed submissions. If the user gave specific test-case names, testers,
  or IDs, narrow to those instead of taking every Passed/Failed row.

## Step 4 — Pull full step-by-step detail per queued run

```js
const res = await fetch('/api/testruns/results/<testRunResultId>?markMessagesAsRead=false', {credentials:'include'});
const steps = (await res.json()).data.testRunResult.steps;
```

For each step, you get the tester's actual submission alongside the original
spec, in the same object:

- `testCaseStepModules[]` — the step's **spec**, authored once by the TTL/TE
  and identical for every tester: an `INSTRUCTION` module (`.instruction`,
  HTML), an `EXPECTED_RESULT` module (`.expectedResult`, HTML, sometimes with
  branching `.options[]`), a `MINIMUM_REQUIRED_ATTACHMENTS` module
  (`.minNumberOfAttachments` + its own `.attachments[]` — **this module
  already holds the tester's submitted attachments for that specific
  requirement**, so checking evidence is just comparing the two counts), and
  sometimes a `SURVEY_QUESTION` module (`.questionInfo.text` is the question;
  where exactly the tester's free-text answer is stored wasn't fully pinned
  down during development — check the step's own `comment`/`actualResult`
  fields first, and fall back to reading the rendered test-case-result page
  in the UI if the answer isn't visible in the JSON).
- Step-level fields are the tester's **submission**: `testRunResultStatusDescriptor.name`
  (this step's own Pass/Fail), `actualResult` (free text — for a Failed step
  this commonly embeds the linked bug as `"<bugId>\t<bug subject>"`),
  `comment`, `attachments[]` (general step evidence, each already carrying a
  usable `storageUrl`), `bugsCount`.

To actually view an attachment, resolve its `storageUrl`
(`https://platform.utest.com/services/links/v1/internal/<id>?.<ext>`) the
same way as any other uTest attachment: `navigate` to it and read
`location.href` after the redirect to get the real, curl-able S3 URL. Only
bother for steps where the written report is ambiguous or high-stakes (a
Failed step, a step with a linked bug, the final step) — reading every
attachment on every Passed step with a clear, consistent report is wasted
effort.

## Step 5 — Cross-check Failed steps against the linked bug's own triage

When a step's `actualResult` embeds a bug ID, that bug's own status matters
for whether the Failed step is legitimate:

- Fetch `GET /api/bugs/<bugId>` (same call `AuthorsFirst_Issue_Triaging`
  uses) and check its `latestRecommendation` or current `bugStatus`.
- If the bug holds up as a real, in-scope, non-duplicate defect (Pending
  Approval or already Approved) — the Failed step is legitimate; it reflects
  a genuine blocker the tester correctly caught.
- If the bug would be (or was) triaged as DUP, OOS, or WAD — the Failed
  status on this step is **not actually substantiated**. Say so explicitly;
  this is a real reason to lean Information Request (ask the tester to
  re-verify) or Pending Rejection (if the step's own evidence, independent of
  the bug, also doesn't hold up) rather than accepting the Fail at face
  value.

## Step 6 — Evaluate each submitted run

Work through every step of a queued run and check, same spirit as the
FinServ reviewer skill's "open every screenshot, never trust the filename":

1. **Did the tester actually do what the instruction asked?** Compare
   `actualResult`/`comment`/attachment content against the `INSTRUCTION`
   module's text — not just whether *something* was filled in.
2. **Is the evidence requirement met and real?** `MINIMUM_REQUIRED_ATTACHMENTS.attachments.length`
   should meet `.minNumberOfAttachments`; open the attachment itself when a
   step is ambiguous, Failed, or decisive for the verdict, and confirm it
   actually shows the claimed action — not a mismatched, reused, or
   irrelevant file.
3. **Does the Overview's scope apply here?** (Step 1) — e.g. a purchase test
   case whose steps/comments indicate an actual purchase was completed when
   the cycle's Overview says purchases are out of scope this round is a real
   problem, independent of whether the steps were otherwise followed
   correctly.
4. **Do Failed steps hold up?** Per Step 5.
5. **Is the overall `Passed`/`Failed` status consistent with what the steps
   actually show?** A run marked `Passed` with an attached screenshot that
   plainly contradicts the expected result (or a required step silently
   skipped) is not a clean Approval just because the tester marked it Passed.

See `references/triage_heuristics.md` for the full verdict criteria and the
patterns worth watching for (missing evidence, skipped steps, mismatched
evidence, unsubstantiated Fails).

## Step 7 — Classify every queued run

| Verdict | When |
|---|---|
| **Pending Approval** | Every step genuinely followed, required evidence present and (where checked) verified as real, any Failed step's linked bug independently holds up, nothing violates the cycle's Overview rules. |
| **Information Request** | Can't safely conclude either way yet — missing required attachment(s), an ambiguous/unanswered survey question, unclear whether a step was actually performed, or a Failed step whose linked bug's validity you can't yet confirm. Must ship with a ready-to-send message (Step 8). |
| **Pending Rejection** | Evidence clearly contradicts the claimed result, a required step was skipped or faked, an Overview out-of-scope rule was violated, or a Failed step's linked bug was itself triaged DUP/OOS/WAD with no other evidence supporting the Fail. |

Every run gets a concrete, step-cited summary — name the step number/name and
quote the specific instruction/evidence/Overview line that drove the
verdict. A bucket label with no reasoning is not acceptable output.

## Step 8 — Always produce the full bilingual output together

Every triage run ends with all three parts, every time:

1. **Triaged result table** (Vietnamese primary, English alongside) — one
   row per test-case run: tester, test case name, verdict, evidence-cited
   summary (cite step numbers).
2. **Message(s)** — one per run in Information Request or Pending Rejection,
   formatted per `references/message_templates.md`: a
   `| Tiếng Việt | English |` table, one row, the complete ready-to-send
   message text in each cell, citing the exact step and what's missing or
   wrong.
3. **Final TE Lead summary** — one consolidated bilingual message grouping
   results by verdict with counts and headline reasons, naming the specific
   test cases/testers; mention the still-in-progress (New/Started) count
   from Step 3 as context, not as something needing a verdict. Address it to
   the real TTL/TE name from Step 1's `teamContactInformation` when the
   context calls for naming someone.

Keep all three internally consistent — every claim in a message or the TE
Lead summary must trace back to a row in the triaged table.
