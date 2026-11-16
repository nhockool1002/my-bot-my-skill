# Message templates

Same bilingual convention as every other skill in this project family: a
`| Tiếng Việt | English |` Markdown table, one row, full ready-to-send prose
per cell, no greeting/"Dear". Every claim names the connector, test case
step number, and tester.

## Per-run triage summary row

```markdown
| Tiếng Việt | English |
|---|---|
| <connector/test case, tester, verdict, which steps were AI pre-reviewed vs needing human review, and why> | <same in English> |
```

## Flag for human video review (AI pre-review was Unclear or low-confidence)

```markdown
## Cần TTL tự xem video — <Connector> / <Test case> (Tester: <name>)

| Tiếng Việt | English |
|---|---|
| Step <n> chưa thể kết luận tự động: <lý do — transcript không rõ, frame không bắt được khoảnh khắc quyết định, v.v.>. Vui lòng tự xem video tại <link> và đối chiếu với Expected Result: "<quoted text>". | Step <n> could not be auto-concluded: <reason — unclear transcript, frames missed the decisive moment, etc.>. Please review the video yourself at <link> against the Expected Result: "<quoted text>". |
```

## Final summary for the TTL/TE Lead

```markdown
## Summary — Gửi <TTL/TE name> (Muse - <Country>, Cycle #<cycleId>)

| Tiếng Việt | English |
|---|---|
| <counts by verdict, which runs were approved in uTest + copied to External, which are still pending human video review, which were bonus-flagged, any sheet-access or missing-link issues encountered> | <same in English> |
```
