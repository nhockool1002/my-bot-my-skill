# Triage heuristics — test-case run verdicts

Generalized principles for turning step-by-step evidence into a verdict for
a Harvey Multiturn run. Re-check specifics (which behaviors are currently
"known issues", what's in/out of scope) against the current cycle's own
Overview and `multiturn_domain_notes.md` every time — the feature changes
cycle to cycle, and a note captured for one cycle may be stale for the next.

## Pending Approval

Every instruction in every step was genuinely followed (not just "something
was filled in"), required evidence meets the stated minimum and — where you
opened it — actually shows the claimed Harvey UI action, any Failed step is
either a genuine new defect backed by real evidence or a correct match to a
known issue marked Pass, and nothing violates scope. Still write a concrete
summary citing what you checked — "steps 1–2 followed per instructions, 4
attachments present and opened; step 2's Fail matches the known
offline-markup-save issue and was correctly left as Fail with bug #7313862
linked" is a valid Pending Approval summary even though step 2 is a Fail —
the Fail itself was correctly handled.

## Info Requested

Use when the submission is genuinely ambiguous — you cannot responsibly call
it either Approval or Rejection without the tester clarifying something:

- A step's `MINIMUM_REQUIRED_ATTACHMENTS` count isn't met, but the written
  `actualResult`/`comment` otherwise reads like the step was actually done —
  could be an upload that failed to attach, not necessarily fabrication.
- A Failed step's `actualResult` is a bare bug ID with no description and no
  visible confirmation (via `messages[]`, `bugsCount`, or `stepLinkedBugs`)
  that the tester +1'd the bug and attached evidence to it, per this cycle's
  own TTL-to-tester convention.
- A step's `comment` suggests the tester couldn't actually exercise the
  scenario the instruction describes (e.g. "there is no way to make the
  removal fail") yet the step is marked Pass — ask how they produced the
  required condition before accepting the Pass at face value.
- You can't confidently tell whether a Fail matches a known issue or is a
  genuine new defect from the evidence given — ask for the missing detail
  (exact steps, which version/field, a clearer screenshot) rather than
  guessing either way.
- The run's overall status and an individual step's status disagree in a way
  that isn't obviously explainable.
- **Before drafting**, check `messages[]` — if this exact point was already
  raised by a TTL and the tester replied "Done" without enough detail to
  confirm it, the message should ask for the specific missing confirmation,
  not repeat the original ask verbatim.

## Pending Rejection

Use when what was submitted doesn't hold up once actually checked:

- An attachment that's supposed to prove a step was clearly reused, is a
  screenshot of something other than Harvey, or plainly contradicts the
  written `actualResult` — open every screenshot, never trust the filename
  alone.
- A required step was skipped entirely (blank `actualResult`, no attachment,
  no comment) while the run was still submitted as complete.
- A Fail clearly matches a cycle known issue (per `multiturn_domain_notes.md`
  or the live Overview) and should have been marked Pass with no new bug —
  submitting it as a blocking Fail is itself the defect in the run.
- The tester's own actions, per their steps/comments, fall outside this
  feature's scope (e.g. testing multi-turn *agent conversation* rather than
  Contract Space version history, or a Beta OS environment) and were
  reported as if in-scope.

## A note on step status vs. instruction content

A step module's `INSTRUCTION`/`EXPECTED_RESULT` text is authored once and
shared by every tester running that test case — it is not itself evidence of
anything about this particular submission. Only the step's own
`actualResult`, `comment`, and `attachments[]` tell you what *this tester*
actually did. Don't confuse the spec with the submission when reading the
JSON.

## A note on known-issue matches

A Fail matching a known issue is not automatically wrong to report — the
cycle's own instructions are explicit that the correct *result* is Pass, not
that the behavior shouldn't be tested at all. The triage question is always
"does the submitted *result* (Pass/Fail) match what the known-issue rule
says it should be", not "did something break" in the abstract.
