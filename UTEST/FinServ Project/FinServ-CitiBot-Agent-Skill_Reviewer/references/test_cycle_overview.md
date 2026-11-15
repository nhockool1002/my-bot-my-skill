# Test cycle Overview — what it is and why you need it

Every uTest test case belongs to a **Test Cycle** (the `<cycleId>` in
`platform.utest.com/testcycles/<cycleId>/testcases/<testcaseId>`). The cycle's
own Overview page — `https://platform.utest.com/testcycles/<cycleId>/`, i.e.
the same URL with the `/testcases/...` part stripped off — carries rules that
apply to *every* test case in it, and that you cannot get from the Datasheet
or the testcase page alone:

- The **Announcement** from the TTL, which is often the only place the actual
  scope constraint for that cycle's prompts is spelled out.
- **In Scope** / **Out of Scope** sections, which tell you what a tester was
  and wasn't supposed to do at all — separate from whether any individual
  response was scored correctly.
- **Team Contact Information** — the actual named TTL and TE for *this*
  cycle, which is who your "TE Lead" summary message should really be
  addressed to (the role names and people differ cycle to cycle; don't assume
  the name from a previous review carries over).

Fetch this page once per cycle (the first time you review any testcase from
it), read the Announcement / In Scope / Out of Scope / Team Contact sections
with `get_page_text`, and ignore the "Test Case Payouts", "Bug Payouts" and
"Your Specified Environments" sections — those are compensation and device-
matrix boilerplate with nothing relevant to reviewing a tester's evaluation.

## What this unlocks in your review

1. **Judge whether a Prompt was actually in-scope.** If the Overview says
   (as cycle 565506's does) "there is no standard set of questions; you must
   ensure that your questions fall within the defined scope—that is, they
   must relate to banking, finance, etc.", then a Datasheet row whose Prompt
   isn't actually about banking/finance at all is a real scope violation worth
   naming in your conclusion — separate from whatever score the row got.
   Conversely, a prompt that's deliberately absurd/unrelated for an
   "Ask an out-of-scope question" row is *correct by design*, not a
   violation — read the category label, not just the topic, before flagging
   this.

2. **Confirm whether this cycle reports bugs at all.** Cycle 565506's Overview
   says plainly: "OUT OF SCOPE: Bugs" / Issue Reporting Instructions: "No
   bugs." — this is a pure response-collection-and-rating cycle, not a
   functional-testing one. That's why nothing in this skill's workflow ever
   involves filing a bug: the entire deliverable is the Datasheet. If a future
   cycle's Overview *does* ask for bug reports, that changes what "complete"
   looks like for that cycle and you should say so rather than silently
   assuming this skill's usual scope.

3. **Address the TE Lead message to the right person.** Use the name/role the
   Overview's Team Contact Information actually gives for this cycle (TTL vs.
   TE vs. Testing Services Manager) instead of a generic "TE Lead" — it reads
   as more credible and makes it obvious who should act on it.

## Worked example — Test Cycle #565506 ("FinServ - Citi Bank (AI Digital Assistant)")

Extracted 2026-11-15; re-fetch the live page rather than trusting this to stay
current if you're working this same cycle much later — announcements get
added over a cycle's life.

> **Announcement from Nhut Nguyen (TTL):**
> "For this cycle, we will focus on testing/gathering feedback for the Citi
> Bank Chatbot - so you need to access your Citi Bank account or Citi Bank
> membership systems (which also use the Citi Bank Chatbot). Please note that
> there is no standard set of questions; you must ensure that your questions
> fall within the defined scope—that is, they must relate to banking,
> finance, etc."

> **In Scope:**
> Welcome to this test cycle for Citi Bank (AI Digital Assistant). We will be
> doing testing on the AI-enabled virtual assistant.
> Required Environment: iOS 15+, Android OS 10+. Location: United States.
> Bank: Citi Bank, personal banking customers, Citi-issued credit cards.
> In Scope: AI driven virtual financial assistant (Citi's chatbot) — claim a
> test case, follow instructions to ask questions and then rate the answers;
> "in scope" questions must be related to banking, finance, etc.

> **Out of Scope:**
> OUT OF SCOPE: Bugs. DO NOT REPORT duplicated bugs. Don't test social-sharing
> aspects unless test accounts are fully private/locked. No emulators, no
> beta OS, no website external to the application, no security/invasive
> testing, no devices outside the listed environments.

> **Issue Reporting Instructions:** "No bugs."

> **Team Contact Information (this cycle):** TTL — Nhut Nguyen. Test Engineer
> — Juliana Henrique (jhenrique@applausemail.com). Testing Services Manager —
> Iris Bentley (ibentley@applause.com).
