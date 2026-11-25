# Test cycle Overview — cycle #566836

Extracted 2026-11-25; re-fetch the live page
(`https://platform.utest.com/testcycles/566836/`) rather than trusting this to
stay current if you're working this cycle much later — announcements get
added over a cycle's life, same caveat as the sibling skill's own cached
overview for cycle #565506.

## Worked example — "FinServ - Reviewers (Citi Bank - AI Digital Assistant) - 11/23/2026 / Test Cycle"

> **In Scope:**
> Welcome to this test cycle for Citi Bank (AI Digital Assistant). We will be
> reviewing results from Citi Bank's AI-enabled virtual assistant.
> Location: United States.
> Peer Review - you will review the RECORDED responses captured by the
> tester. You don't need to have a Citi Bank account. You don't need to ask
> any questions/prompts. You just need to review the responses given by the
> AI and evaluate them.

> **Out of Scope:** Bugs. Do not report duplicated bugs. (Plus the standard
> boilerplate about social-sharing, emulators, beta OS, external websites,
> security/invasive testing, and off-list devices — same as every FinServ
> cycle, not specific to peer review.)

> **Issue Reporting Instructions:** No bugs — this is a pure
> review-and-rate cycle, like its sibling cycle #565506. Nothing in this
> skill's workflow ever involves filing a bug.

> **Team Contact Information (this cycle):** Test Team Lead — Nhut Nguyen.
> Test Engineer — Juliana Henrique (jhenrique@applausemail.com). Testing
> Services Manager — Iris Bentley (ibentley@applause.com).

## What this cycle's shape tells you

Each test case in this cycle is titled "AI - Peer Review", assigned to one
tester (the **reviewer**), whose "SLOT DESCRIPTION" names which *other*
tester's sheet they're reviewing (e.g. "Peer Review for Tester 10") and links
to that tester's Google Sheet (often via an obfuscated
`platform.utest.com/docs/...` redirect link). The step instructions on that
test case are the authoritative source for exactly which columns the reviewer
is responsible for — they've read, in this cycle:

> There is a link assigned to your Peer slot. Open the PEER REVIEW tab in
> your sheet. You CANNOT claim a peer slot of a test case you completed (you
> cannot review your own original submission). You will review the RECORDED
> responses captured by the tester — you don't need to ask the bot the same
> questions again. Your review is based on Columns E and F.
>
> Expected results: Columns I-Q are completed for all 3 rounds of questions.

The tester's **result attachment** on that same test case is the sheet's own
`.xlsx` export (e.g. `Tester_10_-_Citi_AI_-_Evaluation_Datasheet.xlsx`) — but
you don't need the attachment to do this skill's review; the live Google
Sheet is the same data and is what you should check, since it's the thing
the reviewer actually edited and what the TTL would open to re-verify a
complaint.
