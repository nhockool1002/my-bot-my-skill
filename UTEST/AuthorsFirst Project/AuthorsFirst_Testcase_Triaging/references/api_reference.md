# uTest Test Case run API reference

Discovered the same way as the sibling `AuthorsFirst_Issue_Triaging` skill's
API reference: inspecting network traffic of the Test Cases tab and a
test-case run's detail view while logged in, on Authors First test cycle
#565607. Same auth model — `fetch(url, {credentials:'include'})` against the
open tab's own origin, no separate key. uTest can change this internal API
without notice; fall back to the UI steps in SKILL.md if anything here stops
matching.

## Full test-case run list for a cycle

```
GET /api/testruns/results?DisplayStart=0&iDisplayLength=1000&testCycleId=<cycleId>
    &approvalStatusId[]=1&approvalStatusId[]=2&approvalStatusId[]=3&approvalStatusId[]=4&approvalStatusId[]=5&approvalStatusId[]=6
    &testRunResultStatus[]=1&testRunResultStatus[]=2&testRunResultStatus[]=3&testRunResultStatus[]=4&testRunResultStatus[]=5
    &testRunResultStatus[]=6&testRunResultStatus[]=7&testRunResultStatus[]=8&testRunResultStatus[]=9&testRunResultStatus[]=10&testRunResultStatus[]=11
```

(The long `approvalStatusId[]`/`testRunResultStatus[]` repetition is just
"include every value of this filter" — copy it as-is; the UI sends the same
thing when no filter is narrowed.)

Response shape: `{ data: { totalItems, data: [...] } }` — note this is
`.data.data`, not `.data.rows` like the sibling bugs-list API. Each row key
fields:

| Field | Meaning |
|---|---|
| `testRunResultId` | The run's own ID — this is the ID in the testcase URL (`/testcases/<testRunResultId>` as referenced from a linked bug) and what Step 4's detail call takes. |
| `testCaseId` / `testCaseName` | Which test case template this run is of |
| `testerName` | Who ran it (can be `null` on some rows in list form — the detail call always has it) |
| `testRunResultStatusDescriptor.name` | **The field to filter the triage queue on**: `New`, `Started`, `Passed`, `Failed`, `Unclaimed` |
| `approvalStatusDescriptor.name` | TTL's own approval verdict if already set (`Pending` on every row observed on an in-progress cycle — approval happens after triage, not before) |
| `failedStepNumber` | Which step caused an overall Fail, if any |
| `submitDate` / `createDate` | Epoch ms |
| `verificationBugId` | Set if a bug was linked for verification purposes |
| `environmentDescription` | Device/OS string, same format as the bugs API. **This is the TESTER's own registered device profile (what hardware/software they have on file), NOT necessarily what this specific run was assigned to test** — see the warning below. |
| `numberOfMessages` / `unreadMessages` | Existing chat on this run — check before sending a new Info Request |

## `environmentDescription` vs `slotDescription` — do not confuse these

**This caused a real false-positive during cycle #566112 triage (2026-11-19) and
must not happen again.** The detail call (`GET /api/testruns/results/<id>`)
returns BOTH fields on `testRunResult`, and they answer different questions:

- `environmentDescription` — the tester's own registered device/browser
  combination (their hardware profile on file with uTest). It can list a
  completely different platform than what this particular run was actually
  supposed to be tested on.
- `slotDescription` (HTML string, e.g. `"<p>Mac/Firefox - Previous
  purchase</p>..."`) — **this is the actual, authoritative requirement for
  THIS run/slot.** It's what the tester claimed and is the thing their
  submitted evidence should be judged against.

A run's `slotDescription` can name a platform entirely different from its
`environmentDescription` (e.g. `environmentDescription` says "iPhone 17 Pro
Max / Apple TV 4K" while `slotDescription` says "Mac/Firefox") — this is
normal, not a red flag. **Always pull and read `slotDescription` before
judging whether a step's evidence "matches the wrong device."** Fetch it the
same way as any other `testRunResult` field in Step 4's detail call — it's
right there on the object, no extra request needed. Judging device-match
off `environmentDescription` alone produced an incorrect "evidence doesn't
match declared environment, recommend Pending Rejection" verdict on a run
that was actually completely correct once `slotDescription` was checked.

## Full step detail for one run

```
GET /api/testruns/results/<testRunResultId>?markMessagesAsRead=false
```

Response: `{ data: { testRunResult: { steps: [...], ... }, testCase, attachments, messages, ... } }` —
this is the **same endpoint the FinServ CitiBot reviewer skill uses** to pull
screenshots, just read more fully here for its step structure.

Each entry in `testRunResult.steps[]`:

- `stepNumber`, `testCaseStepName`
- `testRunResultStatusDescriptor.name` — this **step's own** Pass/Fail (the
  run's overall status can differ from any one step's)
- `actualResult` — free text; for a Failed step this commonly contains the
  linked bug as `"<bugId>\t<bug subject>"`, tab-separated
- `comment`, `bugsCount`
- `attachments[]` — `{fileName, fileSize, fileType, id, storageUrl}` — unlike
  the bugs API, **`storageUrl` is already given**
  (`https://platform.utest.com/services/links/v1/internal/<id>?.<ext>`); you
  still need to resolve it through a logged-in browser redirect
  (`navigate` + read `location.href`) to get the actual downloadable S3 URL,
  same mechanism as every other uTest attachment.
- `testCaseStepModules[]` — the step's authored spec, shared by every tester
  who runs this test case (not tester-specific, except where noted):
  - `INSTRUCTION` — `.instruction` (HTML)
  - `EXPECTED_RESULT` — `.expectedResult` (HTML), optionally `.options[]`
    for branching
  - `MINIMUM_REQUIRED_ATTACHMENTS` — `.minNumberOfAttachments` (int) and its
    own `.attachments[]`, which **does** hold this specific tester's
    submitted files for this requirement (same `storageUrl` shape as above)
  - `SURVEY_QUESTION` — `.questionInfo.text` is the question,
    `.questionInfo.questionTypeValue` (e.g. `FreeText`) and
    `.questionInfo.options[]` describe the answer shape. **Where the
    tester's actual answer value is stored was not conclusively found**
    during development — it did not appear in the module's own `options[]`
    (those looked like the question's static definition, not a response) or
    in an obvious `answer`/`response` field. Check the step's `comment` and
    `actualResult` first; if neither has it, treat the answer as unverified
    via API and read the rendered test-case-result page in the UI instead
    (`get_page_text` on `https://platform.utest.com/testcycles/<cycleId>/testcases/<testRunResultId>`
    or equivalent) before concluding an answer is missing.

## Bug cross-reference (shared with AuthorsFirst_Issue_Triaging)

```
GET /api/bugs/<bugId>
```

Use this when a Failed step's `actualResult` names a bug ID, to check whether
that bug's own `latestRecommendation`/status holds up — see SKILL.md Step 5.
Full field reference already documented in the sibling skill's
`AuthorsFirst_Issue_Triaging/references/api_reference.md`; don't duplicate
discovery effort, just reuse that file's knowledge if both skills are loaded
in the same session.

## Saving a TTL "Recommendation" (safe — distinct from Approve/Reject)

See SKILL.md's Hard Rule section for when this is and isn't appropriate to
call. Discovered 2026-11-19 on cycle #566112.

```
POST /api/testruns/results/<testRunResultId>/recommendation
Headers: Content-Type: application/json, X-XSRF-TOKEN: <value of the XSRF-TOKEN cookie>
Body: {"approvalStatusId": 4, "comment": ""}
```

Requires the CSRF header or the call 403s ("Invalid CSRF Token"); read it
from `document.cookie`'s `XSRF-TOKEN` entry (URL-decode it) in the logged-in
tab. Needs a `credentials:'include'` fetch like every other call here.

Response on success: `200 {"data": <new recommendation id>}`.

`approvalStatusId: 4` is confirmed to produce
`approvalStatusDescriptor: {id: 4, name: "Pending Approval"}` on the run —
**not** `{id: 2, name: "Approved"}`, which is what the real "Approve" button
on the Test Cases tab sets. `{id: 1, name: "Pending"}` is the default,
untouched state before anything (TTL recommendation or TE action) has
happened. The Reject side of the Recommendation dialog was not indepedently
captured/confirmed — don't assume its `approvalStatusId` without checking,
if it's ever needed.

A 409 with `testcase.result.recommendation.must.be.pending.approval.or.rejection`
means the call's shape or the run's current state doesn't qualify — reproduce
the payload above exactly (this error showed up when guessing a different
field name/value before the real payload was captured via a network-request
intercept of the genuine UI flow).

## Cycle Overview

Identical to the sibling skill — see its `api_reference.md` for the full
field list. In short:
`GET /api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1` →
`data.{inScope, outScope, issueReportingInstructions, teamContactInformation}`.
