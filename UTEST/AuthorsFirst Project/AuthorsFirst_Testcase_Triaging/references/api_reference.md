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
| `environmentDescription` | Device/OS string, same format as the bugs API |
| `numberOfMessages` / `unreadMessages` | Existing chat on this run — check before sending a new Info Request |

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

## Cycle Overview

Identical to the sibling skill — see its `api_reference.md` for the full
field list. In short:
`GET /api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1` →
`data.{inScope, outScope, issueReportingInstructions, teamContactInformation}`.
