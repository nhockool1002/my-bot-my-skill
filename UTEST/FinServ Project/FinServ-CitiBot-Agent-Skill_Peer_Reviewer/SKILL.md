---
name: FinServ-CitiBot-Agent-Skill_Peer_Reviewer
description: Audit a peer reviewer's work on the uTest "FinServ - Reviewers (Citi Bank - AI Digital Assistant)" test cycle — the cycle where one tester reviews another tester's RECORDED Citi Bot chat responses (no screenshots, no live chatbot access needed) and fills in the "Peer Review" tab of that other tester's "<Tester Name> - Citi AI - Evaluation Datasheet" Google Sheet. Given a link to that Google Sheet (and/or the uTest testcase URL for the peer-review slot), this skill fetches the live "Peer Review" tab plus the sheet's own "Issue Categories" and "Scoring Rubric" tabs, checks every row across all 3 rounds for: missing rubric scores, an Issue Category that isn't actually a valid option for that pillar, a non-"Exceptional" score with neither a valid Issue Category nor a "<Pillar> (Issue categories): <proposed category>" tag appended in General Comments (the project's required fallback when no dropdown option fits), and rubber-stamped/default-category runs where the identical score+category pattern repeats across different prompts. Produces a clear Đạt/Không đạt (Pass/Fail) verdict citing exact rows, and — whenever it's Không đạt — a ready-to-send bilingual (Vietnamese/English) message asking the peer reviewer to fix it, plus a bilingual TE Lead summary. Use this proactively whenever the user pastes a Google Sheet link to a "Peer Review" tab, a uTest testcycle/testcase URL for this "FinServ - Reviewers" cycle, or asks to "chấm peer review", "duyệt peer review", "review Peer Review sheet" — even if they don't explicitly ask for the messages or mention this skill by name. Sibling skill to FinServ-CitiBot-Agent-Skill_Reviewer (which audits the *original* tester's Datasheet + screenshots instead of a peer reviewer's Peer Review tab) — never confuse the two inputs.
---

# FinServ CitiBot Agent — Peer Review Sheet Auditor

## What this skill is for

In the "FinServ - Reviewers (Citi Bank - AI Digital Assistant)" test cycle, each
test case assigns a tester to **peer-review** another tester's already-recorded
Citi Bot conversation — the peer reviewer does not need a Citi Bank account and
does not ask the bot anything. Per the uTest step instructions, their review is
"based on Columns E and F" (the original tester's Prompt and Response, already
filled in) and they must complete columns I–Q — the same 4-pillar rubric
(Accuracy & Grounding, Relevance & Utility, Brand Voice & UX, Safety & Trust),
an Issue Category per pillar, and General Comments — for all 3 rounds (24 rows),
but in the **"Peer Review" tab** of that tester's Google Sheet, not the
"Datasheet" tab.

Your job is to check whether the peer reviewer actually did this correctly —
not to re-judge the bot's response quality from scratch (that's a judgment
call the project leaves to the reviewer), but to verify the *mechanics* the
project requires are followed: every row scored, every non-"Exceptional" score
backed by either a valid Issue Category or a properly-tagged custom one, and
no sign that the reviewer rubber-stamped the same verdict down several rows
without actually reading each one.

## Inputs you need

1. **A link to the tester's Google Sheet**, e.g.
   `https://docs.google.com/spreadsheets/d/<sheetId>/edit?gid=<gid>#gid=<gid>`
   — this is the thing you're actually reviewing. The user may give you this
   directly, or it may be reachable from the uTest testcase's "SLOT
   DESCRIPTION" (see below).
2. **Optional: the uTest testcase URL** for the peer-review slot, shape
   `https://platform.utest.com/testcycles/<cycleId>/testcases/<testcaseId>`.
   Not required to do the review itself, but useful for:
   - Confirming which tester is being peer-reviewed (the "SLOT DESCRIPTION"
     names them, e.g. "Peer Review for Tester 10") and finding the sheet link
     if the user only gave you the testcase.
   - Step 0's cycle rules and the real TTL/TE names for the TE Lead message.
   If the user gives you a `platform.utest.com/docs/...` obfuscated link from
   the slot description, `navigate` to it in the browser — it redirects to
   the real Google Sheet URL.

## Step 0 — Learn this test cycle's own rules (once per cycle)

Fetch `https://platform.utest.com/testcycles/<cycleId>/` (Overview, no
`/testcases/...` suffix) with `get_page_text` and read Announcement / In
Scope / Out of Scope / Team Contact Information. Read
`references/test_cycle_overview.md` for the cached extract from cycle
#566836 and reuse it if you're still working that same cycle later in this
conversation — but re-fetch for a cycle you haven't already read this
session, since announcements and contact names can change.

The key things this cycle's Overview establishes: no Citi Bank account or bot
access is needed (you're reviewing *recorded* responses only), no bugs are
reported in this cycle, and the TTL/TE/Testing Services Manager names to
address your TE Lead message to.

## Step 1 — Open the Google Sheet and get to the "Peer Review" tab

Load the `built-in-browser` skill if you haven't already this session, then
`navigate` to the sheet URL. If the sheet is shared "Anyone with the link" it
loads with no sign-in needed (you may still see a logged-out "Đăng nhập"
button in the corner — that's fine, ignore it). If it instead shows a request
to sign in before the grid renders, **tell the user the sheet needs login and
ask them to sign in in the Browser pane** — do not attempt to guess or enter
credentials yourself. Once the grid is visible, click the "Peer Review" tab at
the bottom (use `find` for "Peer Review" then `computer` click) — the page
URL's `gid=` updates to that tab's id.

Google Sheets renders its grid on a canvas, so `get_page_text` does not return
cell values — don't rely on it for the data itself (a screenshot is fine for a
quick visual sanity check, e.g. confirming the right tab is open).

## Step 2 — Dump and check the data

Prefer the bundled script over hand-reading the grid — it fetches the sheet's
public CSV export directly (`gviz/tq`, no Drive API auth needed) and runs the
whole mechanical check in one pass:

```bash
python3 scripts/dump_peer_review.py "<sheet_id>" --check
```

`<sheet_id>` is the long id in the sheet's URL
(`.../spreadsheets/d/<sheet_id>/edit...`), not the full URL. This prints every
defect it finds — missing rubric scores, an Issue Category that isn't a valid
option for its pillar (cross-checked live against that sheet's own "Issue
Categories" tab, not a hardcoded list — definitions can drift between
copies), a non-"Exceptional" score with no valid category **and** no
"`<Pillar> (Issue categories): ...`" tag in General Comments, and any run of
3+ consecutive rows sharing an identical non-Exceptional score+category
signature (the rubber-stamping signal — see
`references/peer_review_pitfalls.md`) — then a final `Đạt`/`Không đạt`
verdict line.

**If the script errors with an HTML page / sign-in message**: the sheet isn't
publicly viewable. Fall back to reading the "Peer Review" and "Issue
Categories" tabs by hand from the signed-in browser tab (`computer` scroll +
`zoom`/screenshot, or re-run the same CSV fetch via `javascript_tool` against
the logged-in tab — `fetch('https://docs.google.com/spreadsheets/d/<id>/gviz/tq?tqx=out:csv&sheet=Peer%20Review', {credentials:'include'})` — which carries the
session cookie the plain script request doesn't have).

Run the same script with `--sheet "Issue Categories"` or without `--check` if
you need to eyeball the raw tabs yourself; `--dump` prints every row's Prompt/
Response/scores/categories/comments for manual spot-checking.

## Step 3 — Read the flagged rows yourself before writing the verdict

The script finds mechanical defects; it does not judge whether a score is
*substantively* right. For every row the script flags — and a handful of
others picked at random to sanity-check — open the actual Prompt/Response
text (the dump already prints it) and confirm the flag is real, not a false
positive:

- A **rubber-stamping run** the script catches might still be a coincidence
  (several consecutive responses that genuinely share the same real defect).
  Read each flagged row's Response and judge whether the *reused* category
  actually fits each individual row, or whether it was clearly copy-pasted
  without re-reading (see the worked example in
  `references/peer_review_pitfalls.md` — rows R1-ID3 through R1-ID6 of
  cycle #566836's "Tester 10" sheet are a real instance of this: four
  different prompts/responses scored with the byte-identical
  Critical-Failure/category triple, at least one of which — ID6, a
  reasonably on-topic response — does not obviously warrant the same
  verdict as the others).
- Cross-check any score against the sheet's own `Scoring Rubric` tab wording,
  not general intuition — same caution as the sibling Reviewer skill: a bot
  that safely declines a PII request is the rubric's own Safety & Trust
  "Exceptional" example, not a failure.
- Confirm an Issue Category is attached to the *right* pillar — e.g.
  "Irrelevant Noise" is a Relevance & Utility category; seeing it under
  Accuracy & Grounding would itself be a defect the script's validity check
  should also have caught (cross-check both agree).

Read `references/issue_category_rules.md` for the full Pillar → valid
Issue Category mapping and the exact append-to-General-Comments format this
project requires when no option fits.

## Step 4 — Always produce the verdict, and the messages when it's Không đạt

Write your reply as:

1. **Verdict**: one line, `Đạt` or `Không đạt`, right up front.
2. **Findings**, each citing the exact row (`R<round>-ID<id>`) — every
   mechanical defect from Step 2's script output that you confirmed in Step 3,
   plus anything you caught by hand that the script couldn't (e.g. a score
   that's substantively wrong against the Scoring Rubric even though its
   Issue Category was technically valid).
3. **If Không đạt** — two messages, in the bilingual markdown-table format
   from `references/message_templates.md`: one to the peer-review tester
   asking them to fix the specific rows (never a vague "please review
   again"), one summarizing for the TE Lead (name from Step 0). If Đạt, a
   short approval note is still worth sending — see the same reference for
   that case.

Keep the messages consistent with the findings — every point in the
tester-facing message should trace to something you actually cited in the
findings, and the TE Lead message is a compressed version of the same thing,
not a fresh analysis.
