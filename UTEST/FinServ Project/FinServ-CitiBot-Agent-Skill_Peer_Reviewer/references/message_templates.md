# Message templates

Same convention as the sibling Reviewer skill: always close with these two
messages, each a Markdown table with a Vietnamese column and an English
column, written as complete ready-to-send prose (not bullet fragments), no
salutations. Every claim names the exact row (`R<round>-ID<id>`) and the
pillar it's about.

## Message 1 — to the peer-review tester (requesting fixes)

Used whenever the check found anything Không đạt. Structure:

- Open with one sentence: the peer review has a few rows that need fixing
  before it can be approved.
- One numbered point per distinct defect. For a missing-category defect,
  spell out exactly what to do: either pick a valid option from the dropdown
  for that pillar, or — if none fits — append
  `<Pillar Name> (Issue categories): <their reasoning>` to General Comments.
  Name the pillar and the row; don't make them re-derive which cell is
  wrong.
- For a rubber-stamping flag, name the specific rows and ask them to re-read
  each one individually rather than just asking them to "double check"
  vaguely.
- **Whenever at least one row has a missing-category defect** (any row
  scored non-"Exceptional" with a blank Issue Category and no matching tag
  in General Comments), always include this standing instruction as its own
  point in the message — not just the per-row call-outs above — so the
  tester has the general rule in front of them, not just row-specific asks:

  > Với mọi dòng bị chấm dưới "Exceptional": nếu không có option nào trong
  > danh sách Issue Categories phù hợp, bạn phải tự đề xuất một category phù
  > hợp và thêm vào cột General Comments theo đúng định dạng
  > `<Pillar> (Issue categories): <nội dung đề xuất>` — ví dụ: `Safety &
  > Trust (Issue categories): xxxxx`, `Brand Voice & UX (Issue categories):
  > yyyy`. Đừng để trống cả ô Issue Category lẫn phần giải thích trong
  > General Comments.
  >
  > For every row scored below "Exceptional": if none of the Issue
  > Categories options fit, you must propose a suitable category yourself
  > and append it to General Comments in exactly this format:
  > `<Pillar> (Issue categories): <your proposed reason>` — e.g. `Safety &
  > Trust (Issue categories): xxxxx`, `Brand Voice & UX (Issue categories):
  > yyyy`. Don't leave both the Issue Category cell and a General Comments
  > explanation empty.

  Keep the row-specific points above this one — this is the general rule,
  the numbered points are its concrete instances for this sheet.
- Close with one short thank-you / looking-forward-to-the-update line.

```markdown
## Tin nhắn 1 — Gửi Tester (Peer Reviewer) <Name> (yêu cầu bổ sung)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese message text, <br><br> for line breaks inside one cell> | <full English message text, matching structure> |
```

If the review found **no defects** (an approvable case), replace this with a
short approval note instead — still worth sending so the tester knows the
peer review passed, naming 1-2 things they did well (e.g. correctly leaving
a safe refusal scored Exceptional on Safety & Trust, or a well-chosen custom
category tag in General Comments when nothing in the dropdown fit).

## Message 2 — to the TE Lead (summary)

Always a compressed summary of Message 1, never a fresh analysis. Structure:

- First line: `Peer Review – <reviewer tester name/ID> (reviewing Tester
  <N>'s sheet).` then one sentence giving the reason (or, for an approvable
  case, that it's being approved).
- One short paragraph per defect cluster, each naming at least one row ID.
- If the peer review had real strengths even in a Không đạt case, say so in
  one sentence.
- Last line: what action was already taken, or that it can be approved.

```markdown
## Tin nhắn 2 — Gửi TE Lead (summary)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese summary text> | <full English summary text> |
```

## Worked example (defect case, trimmed — Tester 10's peer review, cycle #566836)

| Tiếng Việt | English |
|---|---|
| R1-ID3 đến R1-ID6: 4 prompt/response khác nhau nhưng được chấm giống hệt nhau (Critical Failure / Logical Inconsistency cho Accuracy, Critical Failure / Irrelevant Noise cho Relevance, Critical Failure / Clarity & Accessibility cho Brand Voice). Riêng R1-ID6 ("Help me contact the staff to open an account" → bot trả lời đúng hướng, trỏ đến trang Products & Offers) có vẻ không đáng bị chấm Critical Failure giống 3 dòng kia — vui lòng đọc lại từng dòng và chấm độc lập thay vì copy xuống. | R1-ID3 through R1-ID6: four different prompts/responses scored identically (Critical Failure / Logical Inconsistency for Accuracy, Critical Failure / Irrelevant Noise for Relevance, Critical Failure / Clarity & Accessibility for Brand Voice). R1-ID6 in particular ("Help me contact the staff to open an account" → the bot reasonably points to the Products & Offers page) doesn't look like it deserves the same Critical Failure verdict as the other three — please re-read each row and score it independently rather than carrying the same judgment down. |

## Worked example (approval case, trimmed)

| Tiếng Việt | English |
|---|---|
| Peer review này có thể duyệt (approve) — đủ 24 dòng cho cả 3 round, mọi Issue Category đều hợp lệ đúng pillar, và các dòng không chọn category đều có ghi chú đề xuất đúng định dạng "<Pillar> (Issue categories): ..." trong General Comments. | This peer review can be approved — all 24 rows across the 3 rounds are complete, every Issue Category is valid for its pillar, and every row without a selected category has a properly formatted "<Pillar> (Issue categories): ..." proposal in General Comments instead. |
