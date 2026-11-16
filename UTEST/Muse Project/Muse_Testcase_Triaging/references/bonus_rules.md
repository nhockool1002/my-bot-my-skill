# Bonus eligibility

Per the TTL onboarding walkthrough this skill was built from. Treat the
numbers here as the **default observed in that walkthrough**, not a
platform constant — always confirm with the user before applying this to a
specific cycle, since bonus rules are a client/business decision that can
change cycle to cycle.

## Default rule

- $10 bonus for a test completed **with a valid result** **within 6 hours**
  of the tester's submission.
- "Valid result" means the run's own triage verdict holds up — don't flag
  bonus eligibility for a run you haven't actually triaged yet, and don't
  flag it for a run that ends up Pending Rejection.
- Compare the run's `submitDate` (from the uTest API, Step 1 of SKILL.md)
  against the moment you actually complete that run's triage — not against
  when the tester *started* the test case, and not against when you merely
  opened it.

## Blocked testers

If a tester hit a genuine blocker outside their control (e.g. the test
cycle itself had an issue, a shared account was logged out by another
tester, an allowlist step wasn't done yet) and this delayed their
completion, the 6-hour clock is **not** measured from their original
submission — it restarts from when the TTL/TE informed them the blocker was
fixed. The walkthrough is explicit that a tester who hits a blocker is
still entitled to the bonus; don't penalize them for a delay they didn't
cause. If it's ambiguous whether a delay was the tester's fault or a real
blocker, say so and ask rather than guessing either way — the walkthrough
itself frames this as a judgment call ("so that's basically is guess by
guess... if you think they are entitled for the bonus, please add it").

## Where to record it

Add the bonus flag to the Tracking Sheet's existing bonus column (Step 5 of
SKILL.md) — don't invent a new column. If the sheet has no such column yet,
ask the user before adding one.
