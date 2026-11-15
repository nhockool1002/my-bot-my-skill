# uTest Issues/Overview API reference

Discovered by inspecting the network traffic of the Authors First Issues tab and
issue detail pages (test cycle #565607) while logged in. All calls are plain
`fetch(url, {credentials:'include'})` against the same origin as the open tab
(`platform.utest.com`) — the tester's existing browser session cookie is what
authenticates them, there is no separate API key. This is the same mechanism
other uTest skills use for the `testruns` attachment API; nothing here needs a
new login flow.

uTest can change or remove this API without notice — it is the app's own
internal API, not a published/versioned public one. If any call in this file
stops matching (404, 403, or a reshaped response), fall back to the UI steps
described in SKILL.md and don't assume the rest of this file is still accurate
either; re-discover via the browser's network tab if needed.

## Cycle Overview

```
GET /api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1
```

Response: `{ data: { ...,  inScope, outScope, issueReportingInstructions,
teamContactInformation, ttlInstructions, productDescription, name, ... } }`.
The scope/instructions fields are HTML strings (the TTL's rich-text editor
output) — read them directly, the markup doesn't meaningfully obscure content.

## Full issue list for a cycle

```
GET /api/bugs?DisplayStart=0&iDisplayLength=1000&includeKnownIssues=true&resolved=true&testCycleId=<cycleId>
```

Response: `{ data: { rows: [...], totalResults, sessionId } }`. `rows` is
**every** issue tied to the cycle regardless of status, including resolved
ones and Known Issues pulled in from other cycles (`isKnownIssue: true`) —
one call replaces paging through the UI and toggling its "Include Known
Issues"/"Include Resolved" checkboxes (which are also known to not reliably
refresh the rendered list — see SKILL.md's UI-fallback note).

Key fields per row:

| Field | Meaning |
|---|---|
| `id` | Issue ID (matches the URL) |
| `subject` | Title |
| `testerName` | Reporter |
| `bugStatusDescriptor.name` | e.g. `New`, `Pending Approval`, `Info Requested`, `Approved`, `Rejected` |
| `bugSeverityDescriptor.name` | Low/Medium/High/Critical |
| `bugTypeDescriptor.name` | Functional/Visual/Content/Crash/Performance |
| `expectedResult` | Tester's stated expected result |
| `result` | Tester's stated actual result |
| `testCaseOther` | Reproduction steps ("Action Performed") |
| `isKnownIssue` | `true` if this row is a Known Issue (possibly from another cycle) |
| `createDate` / `lastChangeDate` | Epoch ms |
| `customFields[]` | `{fieldName, displayValue}` — includes the free-text "Platform" field testers fill in, which can disagree with the structured environment (see triage_heuristics.md) |
| `recommendations` / `latestRecommendation` | Often empty/null on the list call — fetch the single-issue detail for the authoritative one |

## Single issue detail

```
GET /api/bugs/<issueId>
```

Response: `{ data: { ...full object... } }`. Everything from the list row
plus:

- `environments[]` — one entry per environment group attached to the issue.
  Each has `.environmentGroupTypeDescriptor.name` (e.g. `"Mobile Device"`,
  `"Claimed Direct Environment"` for a Set-Top-Box/TV, `"Set Top Boxes &
  Streaming Devices"`) and a human `.description` (e.g. `"Apple iPhone 13 Pro
  Max - iOS 18.3.1, Telenor - Native (No mobile browser)"`). A playback/cast
  issue can legitimately carry two paired environment groups (phone +
  TV/streaming box) when the tester's account has both claimed — that's
  normal for dual-device test cases, not itself a defect. What *is* worth
  flagging is when the **title and `actionPerformed` steps only ever
  reference one of the paired devices**, while the title names the other.
- `attachments[]` — `{fileName, id}` only, no direct URL. Resolve via
  `https://platform.utest.com/services/links/v1/internal/<id>?.<ext>` and read
  `location.href` after the redirect (same mechanism as the testruns
  attachment API).
- `latestRecommendation` — null until a human (usually the TTL) has recorded
  a judgment on this issue. When present:
  `{ bugReproducibleDefDescriptor: {name}, bugInScopeDefDescriptor: {name},
  duplicate: bool, duplicateBugId, valid: bool,
  fixWorthinessLevelDescriptor: {name}, comment, userName, createDate }`.
  Treat a non-null recommendation as authoritative unless you have concrete
  evidence contradicting it.

## Reproductions and messages for an issue

```
GET /api/bugs/<issueId>/reproductions
GET /api/bugs/<issueId>/messages?includeDeleted=false
```

`reproductions.data` is the list of other testers' "+1 Confirm Issue" entries.
`messages.data` is the chat thread on the issue (`{id, createdOn, message,
userName, userRole, createDate}`) — always check this before drafting a new
Info Request so you don't re-ask something already sent and awaiting a reply.

## Attachment resolution (shared with other uTest skills)

```
navigate -> https://platform.utest.com/services/links/v1/internal/<attachmentId>?.<ext>
javascript_exec -> location.href
```

Resolves to a presigned `https://utest-dl.s3-accelerate.amazonaws.com/...` URL
good for ~24h (`X-Amz-Expires`), downloadable directly with `curl` with no
further auth needed.

## What there is *not* an API for

No endpoint was found for the UI's "these N issues look similar" duplicate
hints on an issue detail page — that box appears to be a client-side,
title/keyword-based comparison the SPA computes itself from data it already
has, not a separate server call. Don't go looking for it; instead do your own
comparison using the full `rows[]` from the bugs-list call (see
`references/duplicate_detection.md`) — it's more reliable anyway.
