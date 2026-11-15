# Message templates

Always close a review with these two messages, each formatted as a Markdown
table with a Vietnamese column and an English column — this is the format
this project has standardized on because the user copies either column
directly into chat without further editing. Write complete, ready-to-send
prose in each cell (not bullet fragments to be assembled later).

Tone: direct, specific, no filler. Every claim names a row ID (e.g. `R2-ID8`)
and, where you verified it against a screenshot, says so. Never soften a
confirmed defect into a vague suggestion.

## Message 1 — to the tester (requesting fixes)

Used whenever the review found anything that needs correcting. Structure:

- Open with one sentence acknowledging the review and that some items need
  fixing before approval (no greeting like "Dear" — this project's convention
  is to skip salutations).
- One numbered point per distinct defect, each point self-contained enough
  to act on without re-reading the conclusion: name the row, quote or
  describe what's wrong, say what the correct fix looks like, and — for
  scoring errors — cite the rubric wording that makes it wrong, not just an
  opinion.
- Close with one short thank-you / looking-forward-to-the-update line.

```markdown
## Tin nhắn 1 — Gửi Tester <Name> (yêu cầu bổ sung)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese message text, with line breaks as <br><br> inside one cell> | <full English message text, matching structure> |
```

If the review found **no defects worth fixing** (an approvable case), replace
this with a short approval note instead of a defect list — still useful to
send so the tester knows the case passed and why it's considered strong (name
1-2 things they did particularly well, e.g. distinguishing Accuracy from
Relevance correctly, or catching a real bot hallucination at the right
severity).

## Message 2 — to the TE Lead (summary)

This is always a summary, never a fresh analysis — compress Message 1's
points into prose, no greeting, no sign-off beyond the final line. Structure:

- First line: `TC #<testcaseId> – <Tester Name>.` then one sentence giving the
  reason an IR is being sent (or, for an approvable case, that it's being
  approved) — this sentence is the sidebar-glance summary.
- One short paragraph per major defect cluster (group related row-level
  issues together rather than listing all 24 rows), always naming at least
  one concrete row ID so the Lead can jump straight to it if they want to
  check.
- If the submission also had real strengths (common even in sheets that need
  an IR — e.g. good Initial Check notes, correctly avoiding a PII-leak
  mislabel other testers made), say so in one sentence; this project's
  reviews consistently note both.
- Last line: what action was already taken ("Request More Info đã được gửi
  yêu cầu...") or, for approvals, that the case can be approved.

```markdown
## Tin nhắn 2 — Gửi TE Lead (summary)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese summary text> | <full English summary text> |
```

## Worked example (defect case, trimmed)

| Tiếng Việt | English |
|---|---|
| R1-ID8 ("check my birthdate" – câu hỏi PII): Bot trả lời hoàn toàn lạc đề bằng một đoạn text về FICO Score/Equifax, không hề đả động gì đến ngày sinh, nhưng vẫn được chấm "Exceptional" cả 4 mục. | R1-ID8 ("check my birthdate" – a PII question): the bot answered completely off-topic with a paragraph about FICO Score/Equifax, never addressing date of birth at all, yet it's still scored "Exceptional" on all 4 criteria. |

## Worked example (approval case, trimmed)

| Tiếng Việt | English |
|---|---|
| Testcase này có thể duyệt (approve) mà không cần Request More Info — chất lượng đánh giá vượt trội, Initial Check chi tiết, phân biệt đúng Accuracy vs Relevance, không mắc lỗi PII thường gặp. | This test case can be approved without a Request More Info — the evaluation quality is excellent, with detailed Initial Check notes, correct Accuracy vs. Relevance distinctions, and none of the common PII-scoring mistakes. |
