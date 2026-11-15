# Triage heuristics — test-case run verdicts

Generalized principles for turning step-by-step evidence into a verdict.
Re-check specifics (what's in/out of scope, what counts as a purchase, etc.)
against the current cycle's own Overview every time — don't assume facts
from one cycle carry over to another.

## Pending Approval

Every instruction in every step was genuinely followed (not just "something
was filled in"), required evidence meets the stated minimum and — where you
opened it — actually shows the claimed action, any Failed step's linked bug
independently holds up as a real defect (Step 5 of SKILL.md), and nothing
contradicts the cycle's Overview rules. Still write a concrete summary citing
what you checked — "all 6 steps followed per instructions; step 4's required
screenshot confirmed; no bugs filed" is a valid, useful Pending Approval
summary, not just the label.

## Information Request

Use this when the submission is genuinely ambiguous — you cannot responsibly
call it either Approval or Rejection without the tester clarifying something:

- A step's `MINIMUM_REQUIRED_ATTACHMENTS` count isn't met, but the written
  `actualResult`/`comment` otherwise reads like the step was actually done —
  could be an upload that failed to attach, not necessarily fabrication.
- A `SURVEY_QUESTION` step has no retrievable answer via the API and the UI
  render doesn't clearly show one either — ask rather than assume it was
  skipped.
- A Failed step's linked bug hasn't been triaged yet (no
  `latestRecommendation`, status still `New`) — you can't yet tell whether
  the Fail is substantiated; say so and either wait or flag for the TTL to
  decide alongside the bug's own triage.
- The run's overall status and an individual step's status disagree in a way
  that isn't obviously explainable (e.g. overall `Passed` but
  `failedStepNumber` is set) — ask rather than guess which is authoritative.

## Pending Rejection

Use this when what was submitted doesn't hold up once actually checked:

- An attachment that's supposed to prove a step was clearly reused from
  another step/run (same file, unrelated claimed content), is a screenshot
  of something other than the app under test, or plainly contradicts the
  written `actualResult` — same "open every screenshot, never trust the
  filename" principle as the FinServ CitiBot reviewer skill.
- A required step was skipped entirely (blank `actualResult`, no attachment,
  no comment) while the run was still submitted as complete.
- The Overview's own out-of-scope rules were violated by what the tester
  actually did — e.g. a step's comment indicates a real purchase was
  completed in a round where the Overview says purchases are out of scope,
  or testing activity the Overview explicitly disclaims.
- A step marked Failed links a bug that was itself triaged DUP, OOS, or WAD
  by `AuthorsFirst_Issue_Triaging` (or by a TTL's existing
  `latestRecommendation` on that bug), **and** nothing else in the step's own
  evidence independently supports a real Fail — the Fail status isn't
  substantiated, and submitting it as a blocking failure without that backing
  is a real defect in the run, not merely the linked bug's problem.

## A note on survey/question steps

Don't penalize a run for an unanswered survey question until you've actually
tried both the API fields documented in `api_reference.md` *and* the
rendered UI — the answer not showing up in the JSON you happened to check is
not the same as the tester never answering it. When you genuinely can't find
it either way, that's an Information Request, not an automatic Rejection.

## A note on step status vs. instruction content

A step module's `INSTRUCTION`/`EXPECTED_RESULT` text is written once by the
TTL/TE and shared by every tester running that test case — it is not itself
evidence of anything about this particular submission. Only the step's own
`actualResult`, `comment`, and `attachments[]` (and the
`MINIMUM_REQUIRED_ATTACHMENTS` module's own `attachments[]`) tell you what
*this tester* actually did. Don't confuse the spec with the submission when
reading the JSON.
