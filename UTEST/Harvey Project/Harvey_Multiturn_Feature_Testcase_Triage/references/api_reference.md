# uTest Test Case run API reference — Harvey Multiturn

Same internal API family as `AuthorsFirst_Testcase_Triaging/references/api_reference.md`.
Re-verified working against Harvey cycle #565709 during this skill's
development (not just assumed from the sibling skill) — `fetch(url,
{credentials:'include'})` against the open tab's own origin, no separate
key. uTest can change this internal API without notice; fall back to the UI
steps in SKILL.md if anything here stops matching.

## One run's full step detail (the main call this skill uses)

```
GET /api/testruns/results/<testRunResultId>?markMessagesAsRead=false
```

Response: `{ data: { testRunResult: {...}, testCase: {...}, attachments: [...], messages: [...], ... } }`.

`testRunResult` top-level fields worth reading beyond the obvious
(`testRunResultStatusDescriptor.name`, `approvalStatusDescriptor.name`,
`testerLocator.name`, `environmentDescription`, `buildVersion`,
`submitDate`):

- `slotDescription` — HTML, this test case's own description as shown to
  the tester. **For Harvey Multiturn this routinely embeds a per-case known-
  bug note**, e.g. `"A missing review on manual Upload is a known bug: Pass,
  and do not file it."` — read it in full every time, don't skip past it.
- `testCaseDescription` — usually identical text to `slotDescription`.
- `failedStepNumber` — which step caused an overall Fail, if any; check this
  against the steps array for consistency (Step 4.5 of SKILL.md).
- `verificationBugId` — set if a bug was linked for verification purposes.

`testRunResult.steps[]`, each entry:

- `stepNumber`, `testCaseStepName`
- `testRunResultStatusDescriptor.name` — this **step's own** Pass/Fail (can
  differ from the run's overall status)
- `actualResult` — free text. For a Failed step this is commonly either a
  short description with an embedded bug reference (e.g. `"#7313862:
  Multiturn - Markup changed while offline is saved after reconnect"`) or,
  on some submissions, **just the bare bug number with no description**
  (e.g. `"7313862"`) — treat the latter as a real gap worth an Info Request,
  not as equivalent to the former.
- `comment` — free text, sometimes notes a limitation the tester hit (e.g.
  "There is no way to stop removing the file after approve deleting.") that
  can mean the step didn't actually exercise the scenario the instruction
  asked for, even though it's marked Pass.
- `bugsCount`, `stepLinkedBugs` — check before assuming a bug wasn't linked
  to this step.
- `attachments[]` — `{fileName, fileSize, fileType, id, storageUrl}`;
  `storageUrl` is already given
  (`https://platform.utest.com/services/links/v1/internal/<id>?.<ext>`), but
  still needs resolving through a logged-in browser redirect (`navigate` +
  read `location.href`) to get the real S3 URL.
- `testCaseStepModules[]` — the step's authored spec, identical for every
  tester running this test case:
  - `INSTRUCTION` — `.instruction` (HTML)
  - `EXPECTED_RESULT` — `.expectedResult` (HTML)
  - `MINIMUM_REQUIRED_ATTACHMENTS` — `.minNumberOfAttachments` (int) and its
    own `.attachments[]`, which holds this specific tester's submitted files
    for that requirement (compare counts, open files when the step is
    decisive).

`messages[]` — existing chat on this run. Harvey TTLs (Dilip Kumar, Urszula
Witkowska) have a visible pattern on this cycle of asking the tester to "+1
the issue and attach video recording/screenshot to the reported issue" —
check whether that already happened (and whether the tester replied "Done")
before drafting a duplicate ask.

## Full test-case run list for a cycle (only if the user asks for a whole cycle)

```
GET /api/testruns/results?DisplayStart=0&iDisplayLength=1000&testCycleId=<cycleId>
    &approvalStatusId[]=1&approvalStatusId[]=2&approvalStatusId[]=3&approvalStatusId[]=4&approvalStatusId[]=5&approvalStatusId[]=6
    &testRunResultStatus[]=1&testRunResultStatus[]=2&testRunResultStatus[]=3&testRunResultStatus[]=4&testRunResultStatus[]=5
    &testRunResultStatus[]=6&testRunResultStatus[]=7&testRunResultStatus[]=8&testRunResultStatus[]=9&testRunResultStatus[]=10&testRunResultStatus[]=11
```

Response shape: `{ data: { totalItems, data: [...] } }` (`.data.data`).
Confirmed against cycle #565709 (`totalItems: 117`). Use `testCaseId` as
the key field. `testerName` is `null` on list rows even though the detail
call always has it (`testerLocator.name`). Per SKILL.md, only pull this list
when the user explicitly asks to triage a whole cycle rather than specific
links.

## Cycle Overview / known issues / scope

```
GET /api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1
```

`data.{inScope, outScope, issueReportingInstructions, teamContactInformation,
testCaseInstructions, setupInstructions}` — all HTML strings. There is no
separate `knownIssues` field; the Known Issues list is embedded as part of
`inScope` (confirmed against cycle #565709 via both this API call and the
rendered Overview tab).

## Bug cross-reference

```
GET /api/bugs/<bugId>
```

Use when a Failed step's `actualResult` names a bug ID, to check the bug's
own `latestRecommendation`/status. Not yet exercised against a Harvey bug
during this skill's development — same shape as the AuthorsFirst sibling
skill's `api_reference.md` is the working assumption; verify the response
shape the first time you use it on this cycle family and update this note
if it differs.
