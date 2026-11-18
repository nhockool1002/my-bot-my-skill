# Message templates

Same convention as the sibling `AuthorsFirst_Testcase_Triaging` skill: every
triage run ends with the triaged table plus ready-to-send messages, each as
a Markdown table with a Vietnamese column and an English column, full
ready-to-send prose per cell (no greeting/"Dear" needed — this platform's
own message thread already shows sender/recipient), no bullet fragments to
assemble later. Every message names the test case, the run ID, and the
specific step(s) that drove the finding — never a vague "please check your
work".

These are **drafts for the TTL (Nhut Nguyen) to review and send himself**
from the uTest Messages tab on that run. This skill never posts a message or
changes an Approval status on its own.

## IR (Info Request) message — one per run needing Info Requested or facing Pending Rejection

Check `messages[]` first — don't re-ask something already sent and awaiting
a reply; if a prior ask got a "Done" reply without enough detail, the new
message should ask for the specific missing confirmation instead of
repeating the original ask verbatim.

Structure: one sentence naming the test case and run ID and that it needs
more information before it can be approved; then the specific step(s) and
what's missing/unclear, quoting the instruction or known-issue rule where
useful; then the concrete action needed from the tester; one short closing
line.

```markdown
## Tin nhắn IR — Gửi Tester <Name> (Test Case "<name>", Run #<testRunResultId>)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese message text> | <full English message text> |
```

## Batch summary — one per triage batch, covering every run in that batch

Always a compression of the triaged table, never a fresh re-analysis.

Structure:
- First line: how many runs were triaged in this batch, plus the headline
  breakdown (e.g. "2 Pending Approval, 2 Info Requested, 1 Pending
  Rejection").
- One short line per run, naming the test case + tester + run ID + verdict.
- Last line: what's needed next (e.g. "IR messages drafted above for runs
  #X and #Y — review the Vietnamese/English wording before sending from
  each run's Messages tab").

```markdown
## Tóm tắt triage — <N> test case(s)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese summary text> | <full English summary text> |
```
