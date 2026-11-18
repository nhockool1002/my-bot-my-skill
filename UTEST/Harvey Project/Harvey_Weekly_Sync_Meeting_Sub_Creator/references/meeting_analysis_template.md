# Meeting analysis write-up — template

For **every** video processed, show this in chat (in Vietnamese) alongside
delivering the .srt file — the transcript alone isn't the deliverable, the
point is the user can tell at a glance what next week's testing covers
without watching the recording.

```markdown
### Video "<original filename>" (~<duration>) — <one-line theme>

- **Tên chức năng / feature đang test:** <feature name(s), in English per
  the glossary — e.g. "Assistant Thread", "Contract Intelligence">
- **Luồng test 1 — <short name>:** <what the presenter demos, what the
  tester should verify, any known caveat or discrepancy called out live>
- **Luồng test 2 — <short name>:** <...> (as many luồng as the video
  actually shows — don't force exactly two)
- **Lưu ý / rủi ro:** <anything the speaker flags as fragile, a known bug,
  a timing dependency (e.g. "auto-open takes up to 10s"), or something
  that needs seed data / account setup before testers can start>
```

## What makes a good analysis vs. a thin one

- Name the **actual feature/button/flow**, not a vague paraphrase — "test
  nút Create Invite và việc invite card hiện đúng attendee/agenda" beats
  "test tính năng lịch".
- Carry over any **explicit discrepancy or caveat** the speaker states
  (e.g. "136 cards on web vs. 58+86 on Word — expected, not a bug") — this
  is exactly the kind of thing a tester needs to know *not* to file as a
  bug.
- If the speaker gives **process/scheduling context** (no pressure this
  week, syncing with someone else next week, data/account prerequisites),
  include it as a short separate note — it changes what the TTL/testers
  should actually do this week, even though it's not a test step itself.
- If multiple videos in one batch are **two halves of the same sync**
  (e.g. one covers the Word flow, another the Outlook flow), say so
  explicitly rather than presenting them as unrelated.

## After the per-video sections

Close with a short combined summary line if more than one video was
processed — total features covered, anything that applies across all of
them (e.g. "cả 2 video đều cần tester có sẵn seed data trong account
Outlook trước khi bắt đầu").
