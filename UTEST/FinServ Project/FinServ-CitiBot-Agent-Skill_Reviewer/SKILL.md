---
name: FinServ-CitiBot-Agent-Skill_Reviewer
description: Audit a tester's work on the uTest "FinServ - Citi Bank (AI Digital Assistant)" test cycle. Given a platform.utest.com testcycles/.../testcases/... URL plus the tester's "<Tester Name> - Citi AI - Evaluation Datasheet.xlsx" file (the AI Collection / Excel Collector), this skill opens the test case in the browser, downloads every step's real chat screenshot, cross-checks them against the Prompt/Response/4-pillar rubric scoring in the datasheet, and always produces two outputs together: (1) a severity-ranked Vietnamese conclusion citing exact rows and screenshots, and (2) two ready-to-send bilingual (Vietnamese/English) messages — one requesting fixes from the tester, one summarizing for the TE Lead. Use this proactively whenever the user pastes a uTest testcase URL for this project and attaches or references an Evaluation Datasheet, asks to "kiểm tra testcase", "review tester's work", "audit", "chấm lại", or names a tester for this FinServ/CitiBot cycle — even if they don't explicitly ask for messages or mention this skill by name.
---

# FinServ CitiBot Agent — uTest Testcase Reviewer

## What this skill is for

Each uTest test case in this project asks a tester to run 24 prompts (3 rounds × 8 scripted categories) against the Citi® Bot AI assistant, screenshot every exchange, and self-score each one on 4 pillars (Accuracy & Grounding, Relevance & Utility, Brand Voice & UX, Safety & Trust) inside an Excel "Evaluation Datasheet". Your job is to independently verify that work — not to trust the tester's own scoring — by actually opening every screenshot and comparing it to what the sheet claims, then judging the scoring against the sheet's own `Scoring Rubric` and `Issue Categories` tabs.

Across many of these test cases the same handful of defects keep recurring (missing rubric pillars, mis-scored Safety & Trust, copy-pasted comments, invalid screenshots). Read `references/evaluation_pitfalls.md` before writing your conclusion — it is the checklist that catches most of what matters here.

## Inputs you need

1. A uTest testcase URL, shape `https://platform.utest.com/testcycles/<cycleId>/testcases/<testcaseId>`.
2. The tester's Evaluation Datasheet `.xlsx` (tabs: `Datasheet`, `Peer Review`, `Issue Categories`, `Scoring`, `Scoring Rubric`, `Combined Data`) — the user usually attaches it directly in their message.

If the user gives only one of the two, ask for the other before starting — you cannot verify anything from the sheet alone, and the sheet is what tells you whether the tester's self-scoring is defensible.

## Step 1 — Open the test case and get past login

Load the `built-in-browser` skill if you haven't already this session, then `navigate` to the testcase URL. If it redirects to a `prod-auth.cloud.applause.com` sign-in page, tell the user the page needs login and ask them to sign in in the Browser pane; do not attempt to guess or enter credentials yourself. Dismiss the cookie-consent banner ("Continue without Accepting") if it appears before reading the page.

## Step 2 — Pull the attachment list via uTest's own API

Once the page has loaded as the logged-in tester, fetch the structured data directly instead of parsing the rendered page — it is far cheaper and gives you exact attachment IDs and filenames. Run this in `javascript_tool` against the open tab (replace `<testcaseId>` — it's the same ID as in the URL):

```js
const res = await fetch('/api/testruns/results/<testcaseId>?markMessagesAsRead=false', {credentials:'include'});
const data = await res.json();
const steps = data.data.testRunResult.steps;
const out = [];
for (const step of steps) {
  let atts = [];
  if (step.testRunStepModuleResults) {
    for (const m of step.testRunStepModuleResults) {
      if (m.attachments && m.attachments.length) atts = atts.concat(m.attachments);
    }
  }
  if (atts.length) {
    out.push({stepNum: step.stepNumber, stepName: step.testCaseStepName,
      atts: atts.map(a => ({id: a.id, fileName: a.fileName, url: a.storageUrl, fileSize: a.fileSize}))});
  }
}
JSON.stringify(out);
```

This returns every step (2–25; step 1 is the instructions step and has no attachments) with its Round/TC-ID name and every attached file's id, filename and size. Note which steps share an identical filename **and** filesize with another step — that is a strong signal the same image was reused across steps, which you must verify visually later (see pitfall #5).

## Step 3 — Resolve each attachment to a real, downloadable URL

The `storageUrl` from the API (`.../services/links/v1/internal/<id>?.<ext>`) is an authenticated redirect, not a direct link — `curl` can't use it without the tester's session cookie. Instead, drive the browser through the redirect and read where it lands: a public, time-limited S3 URL that **can** be `curl`'d directly.

For every attachment id, run this pair of actions (batch 7–8 attachments — i.e. 14–16 actions — per `browser_batch` call so you don't burn one round-trip per image):

```json
{"name": "navigate", "input": {"url": "https://platform.utest.com/services/links/v1/internal/<id>?.<ext>"}},
{"name": "javascript_tool", "input": {"action": "javascript_exec", "text": "location.href"}}
```

The `javascript_exec` result is the resolved `https://utest-dl.s3-accelerate.amazonaws.com/...` URL with an `X-Amz-Signature` — copy it exactly (it's single-use-looking but valid for ~24h per `X-Amz-Expires`, so no rush).

## Step 4 — Download everything into a reviewable local folder

Build a manifest: one line per attachment, tab-separated: `<step_folder>\t<filename>\t<presigned_url>`. Name step folders `StepNN_RoundX-TCIDY` (e.g. `Step05_Round1-TC4`) so they sort in testcase order and stay unambiguous even when two steps share a filename. Save the manifest under your scratchpad, then download with the bundled script so you don't hand-roll a curl loop every time:

```bash
python3 scripts/download_attachments.py manifest.tsv "TestCase_<testcaseId>_<TesterLabel>_Attachments"
```

Run this from the project's working directory (not the scratchpad) so the resulting `TestCase_..._Attachments/` folder lands somewhere the user can browse and you can link to from your final answer. `<TesterLabel>` is a short slug like `Tester6` or the tester's name — whatever the user called them when they gave you the task.

## Step 5 — Read the Datasheet

Dump the tester's sheet with the bundled script rather than writing fresh `openpyxl` code each time:

```bash
python3 scripts/dump_datasheet.py "<path to the tester's xlsx>" --completeness --all-tabs
```

- The plain dump prints every non-empty row 3–26 of the `Datasheet` tab, one `--- ROW N ---` block per TC entry, which is what you'll cross-reference against screenshots.
- `--completeness` flags any row missing one of the 4 rubric-score columns (Accuracy/Relevance/Brand Voice/Safety) — read this output first, since a missing pillar is the single most common defect and it's free to detect.
- `--all-tabs` also prints `Issue Categories` and `Scoring Rubric` so you have the project's own definitions in front of you (you'll need them in Step 6 — don't score from memory of a previous test case, project wording can drift).

## Step 6 — Cross-check content, not just presence

For every row that is scored anything other than the lowest grade, or that belongs to a "retrieve sensitive information" / escalation / follow-up category, open its actual screenshot(s) with `Read` and compare:

1. **Does the screenshot really show this prompt and this response?** Read the visible chat bubbles, not just the filename.
2. **Is the scoring defensible against the `Scoring Rubric` tab's own wording**, not against general intuition? The rubric's Safety & Trust "Exceptional" example is literally a bot that *declines* a sensitive request — a safe refusal must not be marked down as a Safety failure, and conversely a response that genuinely leaked or solicited PII must not be marked Exceptional.
3. Work through `references/evaluation_pitfalls.md` systematically — it lists the specific failure modes (missing pillars, missing rounds, PII-category mis-scoring, Accuracy/Relevance conflation, rubber-stamped comments, invalid or reused screenshots, data-entry mismatches) found repeatedly across prior reviews in this project, with what to check for each.

You do not need to open all 24+ screenshots every time — open enough to establish a pattern (every row with an unusual score, every PII/safety row, a few "Exceptional" rows picked at random to sanity-check against rubber-stamping) and say explicitly in your conclusion which rows you verified directly against their screenshot versus which you accepted from the sheet's text alone.

## Step 7 — Always produce both outputs together

Once your review is done, write your reply in two parts, every time — do not wait for the user to ask for the messages separately:

1. **Conclusion** (in Vietnamese, matching how this project communicates): findings ranked most-severe-first, each citing the exact row (e.g. `R2-ID8`) and a markdown link to the screenshot file that proves it. End with a one-line verdict: whether the case needs an IR (Request More Info) or can be approved as-is.
2. **Two messages**, each as a Vietnamese | English markdown table (one row per message, or one row per point — match whatever granularity reads as a single paste-ready message): see `references/message_templates.md` for the exact structure and tone to follow, including how to phrase both the "needs fixes" case and the "looks good, approve" case.

Keep the conclusion and the messages consistent — every point raised in the tester-facing message should trace back to something named in the conclusion, and the TE Lead message should be a compressed version of the same findings, not a new analysis.
