# Message templates

Every triage run ends with the triaged table plus two kinds of ready-to-send
message, each as a Markdown table with a Vietnamese column and an English
column — this project's standard format, since messages get copy-pasted
straight out of either column with no further editing. Write complete,
ready-to-send prose in each cell, not bullet fragments to assemble later.

Tone: direct, specific, no filler, no "Dear ..." greeting. Every claim names
the issue ID and quotes or closely paraphrases the exact field/text that
drove the finding — never a vague "this seems off."

## Info Request message — one per issue needing clarification

Used for every issue classified **Info Requested**. Before drafting, check
that issue's `/api/bugs/<id>/messages` (see `references/api_reference.md`) —
if a message already asked the same question and is awaiting a reply, don't
send a duplicate; note in the triaged table that a request is already
pending instead.

Structure: one sentence naming the issue and that it needs more information
before it can be processed; then the specific contradiction/missing item
with the exact quoted fields; then the concrete question(s) the tester needs
to answer or correction(s) needed; one short closing line.

```markdown
## Tin nhắn — Gửi Tester <Name> (Issue #<id>)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese message text> | <full English message text> |
```

## Final TE Lead summary — one per triage run, covering every issue

Always a compression of the triaged table, never a fresh re-analysis. Address
it using the real TTL/TE name from the cycle's `teamContactInformation`
(Step 1) when the context calls for naming someone specific, not a generic
"TE Lead" placeholder.

Structure:
- First line: which cycle, how many issues were triaged, and the headline
  breakdown (e.g. "X Pending Approval, Y DUP, Z OOS, W WAD, V Info
  Requested").
- One short paragraph per non-empty verdict bucket, grouping related issues
  rather than listing all of them individually when there are many, but
  always naming the specific issue IDs in each group.
- Call out anything a human should double-check themselves (an issue the
  skill marked Info Requested because it genuinely couldn't tell, an existing
  `latestRecommendation` it deferred to, a Known Issue match it's confident
  about).
- Last line: what's needed from the TE Lead next, if anything (e.g. "the N
  Info Requested issues now have messages sent to testers; everything else
  is ready to action as triaged above").

```markdown
## Summary — Gửi <TTL/TE name> (Test Cycle #<cycleId>)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese summary text> | <full English summary text> |
```

## Worked example (Info Request, trimmed)

| Tiếng Việt | English |
|---|---|
| Issue #7314306 "Apple TV - Playback - Resume Playback starts the episode from the beginning" cần bổ sung thông tin trước khi duyệt. Title và Platform đều ghi Apple TV, nhưng toàn bộ 6 bước trong Action Performed lại mô tả thao tác trên iPhone — không có bước nào thao tác bằng Apple TV remote. Nhờ bạn xác nhận lại nền tảng thực tế đã test và chỉnh sửa Title/Platform hoặc các bước cho khớp. | Issue #7314306 "Apple TV - Playback - Resume Playback starts the episode from the beginning" needs more information before it can be approved. The Title and Platform are both set to Apple TV, but all 6 steps in Action Performed describe actions on an iPhone — none involve the Apple TV remote. Please confirm which platform was actually tested and correct either the Title/Platform or the steps to match. |
