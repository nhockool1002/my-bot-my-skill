---
name: AuthorsFirst_Issue_Triaging
description: Triage newly-submitted bug reports (Issues) on uTest for the "Authors First" streaming-app project (iOS, iPadOS, Apple TV, Android, Web test cycles). Given a platform.utest.com test cycle URL, this skill logs in, pulls the cycle's Overview rules and its full Issues list straight from uTest's own JSON API (falling back to the browser UI only if the API is unreachable), cross-checks every new issue against the cycle's in-scope/out-of-scope rules and against every other issue in the cycle (including Known Issues) for real duplicates, and classifies each one into Pending Approval, Pending Rejection - DUP, Pending Rejection - OOS, Pending Rejection - WAD, or Info Requested — always with a concrete summary, always with a ready-to-send bilingual (Vietnamese/English) message for anything needing more info, and always with a final bilingual summary for the TE Lead. Use this proactively whenever the user pastes an Authors First test cycle or issues URL and asks to "triage issues", "review new issues", "chấm issue", "duyệt bug mới", or check issues for duplicates/OOS/WAD — even if they don't explicitly ask for the summary messages or mention this skill by name.
---

# AuthorsFirst Issue Triaging

## What this skill is for

Each Authors First test cycle collects bug reports ("Issues") from many testers in parallel. Before a Test Team Lead (TTL) can act on them, every new issue needs a verdict: is it a real, in-scope, non-duplicate defect (→ Pending Approval), or should it be rejected as a duplicate (DUP), out of scope (OOS), or expected/working-as-designed behavior (WAD)? Some reports are too ambiguous or self-contradictory to call either way and need the tester to clarify first (Info Requested).

Your job is to do that first pass of triage: read each new issue on its own merits, check it against the cycle's own stated rules (not generic assumptions), check it against every other issue already in the cycle (new, resolved, and Known Issues) for genuine duplication, and hand back a clear, evidence-cited verdict per issue plus the messages needed to act on it.

## Inputs you need

1. A uTest test cycle link for an Authors First cycle — either form works, since only the numeric cycle ID matters:
   `https://platform.utest.com/testcycles/<cycleId>/` or `.../testcycles/<cycleId>/issues`.
2. A logged-in tester session in the browser. If the user hasn't specified which issues to triage, default to every issue currently in status **New**; if they give specific IDs or a range, triage exactly those.

No Excel/Datasheet is needed for this skill — everything comes from the test cycle itself.

## API-first, UI as fallback — read this before Step 1

uTest's own single-page app is backed by a plain JSON REST API under `/api/...` on the same origin, callable with `fetch(url, {credentials:'include'})` from the logged-in tab exactly like the testruns API used for screenshot attachments in other uTest skills. **Always try the API calls in Steps 1–4 first.** Only fall back to driving the rendered UI (scraping with `get_page_text`, clicking "Include Known Issues" / "Include Resolved" checkboxes, paging through the Issues table) if an API call 404s, 403s, or comes back in a shape that doesn't match `references/api_reference.md` — uTest can change this API without notice, so don't assume it's permanent, just prefer it while it works.

## Step 0 — Open the cycle and confirm login

Load the `built-in-browser` skill if you haven't already this session, then `navigate` to the cycle's issues URL (`https://platform.utest.com/testcycles/<cycleId>/issues`). If it redirects to a `prod-auth.cloud.applause.com` sign-in page, tell the user and ask them to sign in in the Browser pane — never guess or enter credentials yourself. Dismiss the cookie-consent banner if it appears. Wait a couple of seconds after navigation before reading anything; this is a client-rendered app and content is empty for the first moment.

## Step 1 — Pull the cycle's Overview rules via API

```js
const res = await fetch('/api/testcycles/<cycleId>/details?testCycleInstructionTypeIds=1', {credentials:'include'});
const d = (await res.json()).data;
JSON.stringify({inScope: d.inScope, outScope: d.outScope, issueReportingInstructions: d.issueReportingInstructions, teamContactInformation: d.teamContactInformation, ttlInstructions: d.ttlInstructions});
```

The fields come back as HTML strings (the TTL's rich-text Overview editor) — read them as-is, the tags don't meaningfully obscure the content. This is everything Step 6's OOS/WAD judgment and Step 8's TE-Lead-addressing need: in-scope rules, explicit out-of-scope/do-not-report rules, required bug-report format, and the real TTL/TE/Testing Services Manager names for this cycle. Don't assume these from a previous cycle — every cycle's Overview is independent; re-fetch per cycle, not per issue.

**Fallback:** if this 404s, `navigate` to `https://platform.utest.com/testcycles/<cycleId>/` and read the Overview tab with `get_page_text` instead (Announcement, In Scope, Out of Scope, Issue Reporting Instructions, Team Contact Information — skip Payouts/Environments, they're not review-relevant).

## Step 2 — Pull the cycle's full issue list via API — this is both your queue and your duplicate corpus

```js
const res = await fetch('/api/bugs?DisplayStart=0&iDisplayLength=1000&includeKnownIssues=true&resolved=true&testCycleId=<cycleId>', {credentials:'include'});
const rows = (await res.json()).data.rows;
JSON.stringify(rows.map(r => ({id: r.id, subject: r.subject, status: r.bugStatusDescriptor.name, severity: r.bugSeverityDescriptor.name, type: r.bugTypeDescriptor.name, tester: r.testerName, isKnownIssue: r.isKnownIssue, expectedResult: r.expectedResult, result: r.result, testCaseOther: r.testCaseOther, createDate: r.createDate})));
```

One call returns **every** issue associated with the cycle — every status, resolved ones, and Known Issues imported from other cycles — in one shot, each with its title, tester, status, severity/type, and the actual Prompt/Expected/Actual-equivalent text (`testCaseOther` = reproduction steps, `expectedResult`, `result`). This single response is both:

- **Your triage queue**: filter to `status === 'New'` (or whatever statuses/IDs the user specified) to get the issues that actually need a verdict this run.
- **Your duplicate-detection corpus**: every other row, including `isKnownIssue: true` ones, is a candidate to check each queued issue against in Step 5 — no separate "Known Issues" fetch needed.

Full field reference (environments, recommendations, attachments, etc. — not all present on the list rows) is in `references/api_reference.md`.

**Fallback:** if blocked, drive the UI instead: on the Issues tab, check **Include Known Issues** and **Include Resolved**, set page size to 500, and scrape with `get_page_text` across pages (watch for client-side state — a stale tab can silently keep an old filtered view; open a fresh tab if counts look wrong).

## Step 3 — Build this run's triage queue

From Step 2's rows, take the ones to triage: by default every row with `status === 'New'`; if the user gave explicit IDs or a range, use exactly those (regardless of current status, if they want a re-check). Sort by `id` unless the user asked otherwise.

## Step 4 — Pull full detail per queued issue

```js
const res = await fetch('/api/bugs/<issueId>', {credentials:'include'});
const d = (await res.json()).data;
```

Key fields beyond what the list gave you:
- `environments[]` — each entry has `.environmentGroupTypeDescriptor.name` (e.g. `"Mobile Device"` vs `"Claimed Direct Environment"`/Set-Top-Box) and `.description` (e.g. `"Apple iPhone 13 Pro Max - iOS 18.3.1, Telenor - Native"`). Compare this against the title's stated platform and against what `actionPerformed` actually describes doing — a mismatch here (title says Apple TV, every step says "on iPhone") is a real, recurring reporting defect, not a feature of multi-device testing; see `references/triage_heuristics.md`.
- `latestRecommendation` — if non-null, a **human TTL has already triaged this issue**: `bugReproducibleDefDescriptor.name`, `bugInScopeDefDescriptor.name`, `duplicate` (bool), `duplicateBugId`, `valid`, `fixWorthinessLevelDescriptor.name`, `comment`. Treat this as authoritative — report what it says rather than re-deriving a verdict from scratch, unless you have concrete evidence contradicting it.
- `attachments[]` — `{fileName, id}` only (no URL). To actually view one, resolve it exactly like the FinServ skill's attachment step: `navigate` to `https://platform.utest.com/services/links/v1/internal/<attachmentId>?.<ext>` and read `location.href` after the redirect — same mechanism as testrun screenshots, just a different source id. Only bother for issues where the written report is genuinely ambiguous and a screenshot/video would settle it; most triage calls don't need this.
- `messages[]` (separate call: `GET /api/bugs/<issueId>/messages?includeDeleted=false`) — check this **before** drafting an Info Request message in Step 7: if a message already asked the tester the same question, don't send a duplicate one, note that it's pending a reply instead.

## Step 5 — Check for real duplicates (not the UI's fuzzy hint)

**Important lesson, worth remembering for every cycle:** the uTest UI shows a "Do not report duplicates — these N issues look similar" box on every issue page. This is a loose title/keyword matcher, not a duplicate verdict. On a real Authors First cycle, every single one of these warnings (across more than ten issues, several flagging 10+ "similar" issues) turned out to share nothing but a topic keyword ("Apple TV", "Playback", "Create account") — zero were genuine duplicates. Never mark an issue DUP because the UI flagged it as similar; always do your own check:

1. Build your candidate set from Step 2's full `rows[]` — same subject-area keywords, same `bugTypeId`, and especially any row with `isKnownIssue: true`.
2. For each candidate, read its `subject` + `expectedResult` + `result` + `testCaseOther` side-by-side with the issue you're triaging.
3. Only call it DUP when the **underlying defect is the same** — same trigger, same broken behavior — not merely the same feature area. "Apple TV Search shows no results despite results existing" and "Apple TV Search field never receives focus" are both about Apple TV Search and are **not** duplicates of each other.
4. When you do find a real duplicate, cite the exact other issue ID and quote the matching detail; if it matched a Known Issue, say so explicitly — that's a stronger/different signal than a same-cycle duplicate.

Full method and a worked real-example table (showing exactly why a dozen "similar" warnings were all false positives) is in `references/duplicate_detection.md`.

## Step 6 — Decide OOS / WAD against the cycle's own Overview (Step 1), not generic assumptions

- **OOS**: the issue falls under a rule this cycle's Overview explicitly names as out of scope or "do not report" (a disclaimed UI quirk, a feature explicitly out of scope this round, a testing method the cycle forbids). Cite the exact Overview sentence.
- **WAD**: the reported behavior is explicitly called out in the Overview as *expected*, not a defect (e.g., a shared test account logging other users out after N logins, bookmark/progress drifting on a shared account) — or is self-evidently an intentional product decision, not a bug. Cite the rule or the reasoning.
- **Reporting-quality flag (not automatically OOS/WAD, but worth naming)**: title/platform says one device while `actionPerformed` describes a different one; `expectedResult`/`result` appear swapped (Expected describes the broken behavior instead of the correct one); a `customFields` "Platform" value contradicts the `environments[]` description. These came up repeatedly in real review — see `references/triage_heuristics.md` for the full list and how to phrase the ask.
- **Device/OS not on the cycle's listed-environments table**: do **not** auto-reject for this alone. Observed TTL behavior on this project approves issues from devices never listed in the environments table; treat it as informational context, not disqualifying, unless the Overview explicitly restricts testing to listed devices only.

## Step 7 — Classify every queued issue

| Verdict | When |
|---|---|
| **Pending Approval** | In scope, reproducible, not a duplicate — may still carry a reporting-quality note. |
| **Pending Rejection - DUP** | Step 5 found a genuine duplicate; cite the other issue ID. |
| **Pending Rejection - OOS** | Violates a named Overview out-of-scope/do-not-report rule; cite it. |
| **Pending Rejection - WAD** | Matches explicitly-expected behavior from the Overview, or is self-evidently intentional; cite the rule/reasoning. |
| **Info Requested** | Can't safely conclude any of the above yet — contradictory or incomplete report. Must ship with a ready-to-send message (Step 8) and a check of Step 4's `messages[]` so you don't duplicate an existing ask. |

Every issue gets a concrete, evidence-cited summary — quote the specific `result`/`expectedResult`/`testCaseOther` line or Overview sentence that drove the verdict. A bucket label with no reasoning is not acceptable output.

## Step 8 — Always produce the full bilingual output together

Every triage run ends with all three parts, every time — never just the table:

1. **Triaged result table** (Vietnamese primary language for this project, English alongside) — one row per issue: ID, short title, verdict, evidence-cited summary.
2. **Info Request message(s)** — one per issue in that bucket, formatted per `references/message_templates.md`: a `| Tiếng Việt | English |` table, one row, the complete ready-to-send message text in each cell (no greeting/"Dear"), citing the exact contradiction/missing item and what correction is needed.
3. **Final TE Lead summary** — one consolidated bilingual message (same table format) grouping results by verdict bucket with counts and headline reasons per group, naming specific issue IDs; a compression of the table, not a fresh analysis. Address it to the real TTL/TE name from Step 1's `teamContactInformation` if the context calls for naming someone, not a generic "TE Lead".

Keep all three internally consistent — every claim in an Info Request or the TE Lead summary must trace back to a row in the triaged table.
