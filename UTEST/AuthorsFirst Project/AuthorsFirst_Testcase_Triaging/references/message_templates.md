# Message templates

Same convention as the sibling `AuthorsFirst_Issue_Triaging` skill: every
triage run ends with the triaged table plus ready-to-send messages, each as a
Markdown table with a Vietnamese column and an English column, full
ready-to-send prose per cell (no greeting/"Dear"), no bullet fragments to
assemble later. Every claim names the test case, the tester, and the specific
step number/field that drove the finding.

## Message to the tester — one per run needing Information Request or facing Pending Rejection

Check the run's existing messages (`numberOfMessages`/`unreadMessages` from
the list call, or the detail call's `messages[]`) before drafting — don't
re-ask something already sent and awaiting a reply.

Structure: one sentence naming the test case and tester and that it needs
more information or has an issue before it can be approved; then the specific
step(s) and what's missing/wrong, quoting the instruction or expected result
where useful; then the concrete action needed from the tester; one short
closing line.

```markdown
## Tin nhắn — Gửi Tester <Name> (Test Case "<name>", Run #<testRunResultId>)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese message text> | <full English message text> |
```

## Final TE Lead summary — one per triage run, covering every submitted test case

Always a compression of the triaged table, never a fresh re-analysis. Address
it using the real TTL/TE name from the cycle's `teamContactInformation` when
the context calls for naming someone specific.

Structure:
- First line: which cycle, how many runs were triaged (and how many were
  skipped as Unclaimed, and how many are still New/Started as context), plus
  the headline breakdown (e.g. "X Pending Approval, Y Information Request, Z
  Pending Rejection").
- One short paragraph per non-empty verdict bucket, grouping related runs
  when there are many, always naming the specific test case + tester for
  each.
- Call out anything a human should double-check themselves (a run marked
  Information Request because a survey answer genuinely couldn't be located,
  a Failed step whose linked bug is still untriaged, a Pending Rejection tied
  to a scope violation worth the TTL's own read).
- Last line: what's needed next (e.g. "messages have been sent to the N
  testers in Information Request; the Pending Rejection runs are ready for
  the TTL's final call").

```markdown
## Summary — Gửi <TTL/TE name> (Test Cycle #<cycleId>)

| Tiếng Việt | English |
|---|---|
| <full Vietnamese summary text> | <full English summary text> |
```
