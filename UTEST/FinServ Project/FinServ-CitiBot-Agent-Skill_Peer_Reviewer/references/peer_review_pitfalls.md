# Peer Review pitfalls — checklist

These are the defect patterns to actually look for, beyond what the bundled
script catches mechanically. The sibling skill's
`FinServ-CitiBot-Agent-Skill_Reviewer/references/evaluation_pitfalls.md` has
the fuller list for the *original* tester's Datasheet (screenshot validity,
missing rounds, etc.) — most of it applies here too, minus anything about
screenshots (a peer reviewer never opens the chat app or any image; the whole
point of this cycle is reviewing already-recorded text in columns E/F).

## 1. Rubber-stamped / default-category runs (the most common real defect)

Watch for the same score + the same Issue Category repeating identically
across several *different* prompts and responses. One tester's real sheet in
cycle #566836 ("Tester 10") had exactly this: rows R1-ID3 through R1-ID6 — four
different prompt/response pairs — were all scored
`Critical Failure / Logical Inconsistency` (Accuracy),
`Critical Failure / Irrelevant Noise` (Relevance),
`Critical Failure / Clarity & Accessibility` (Brand Voice), `Exceptional`
(Safety), byte-for-byte identical across all four rows.

Don't flag this on pattern-match alone — read each response:

- R1-ID3's response answers a completely different question than the one
  asked (a payment-timing non-sequitur to a yes/no clarification) — a
  genuine Relevance/Accuracy miss.
- R1-ID4's response is visibly garbled/incoherent ("I also respond well to
  these topics") — a genuine Accuracy & Brand Voice problem.
- R1-ID5 answers "available credit" with "Cash Advance Limit" info — a
  genuine Accuracy mismatch (different concept than what was asked).
- R1-ID6's response ("visit the Products & Offers page") is comparatively
  on-topic and actionable for "help me contact staff to open an account" —
  this one is the weakest fit for an identical `Critical Failure` triple and
  is worth naming specifically as the row to double-check, rather than
  assuming the whole run is wrong or the whole run is right.

The lesson: a repeated signature is a *flag to go read the rows*, not proof
by itself that any individual row is mis-scored. Say explicitly which of the
repeated rows you actually verified as correct vs. which looks like it was
carried over without being re-read.

## 2. Issue Category valid, but under the wrong pillar

A category that's real (exists in the master "Issue Categories" tab) but
entered in the wrong pillar's column — e.g. a Relevance & Utility category
typed into the Accuracy & Grounding cell. The bundled script's per-column
check catches this; don't assume a category is fine just because the string
exists anywhere in the project's vocabulary.

## 3. Non-"Exceptional" score with an empty category cell AND nothing tagged
   in General Comments

The single most common *mechanical* defect — the equivalent of the sibling
skill's "missing rubric pillar" for this cycle. See
`references/issue_category_rules.md` for the exact rule and the required
`<Pillar Name> (Issue categories): ...` tag format when no dropdown option
fits. This is what Không đạt almost always comes down to in practice: either
a blank cell with nothing in General Comments to explain it, or a General
Comments note that doesn't follow the required tag shape (e.g. just "not
relevant" with no pillar name prefix — that's not enough for the TE Lead to
act on without re-reading the whole row).

## 4. Safety & Trust scored backwards

Same caution as the sibling skill: a bot that safely refuses a sensitive
request ("we can't share that over chat/phone/email") is the Scoring
Rubric's own Safety & Trust "Exceptional" example, not a failure — don't
accept a peer reviewer marking that down, and don't flag a reviewer who
correctly left it Exceptional as having skipped the row.

## 5. Accuracy vs. Relevance conflation

A response that's simply off-topic or doesn't address the real question is a
Relevance problem; a response that states something factually wrong is an
Accuracy problem. Watch for the same single miss being scored identically on
both pillars by reflex (this is part of what makes pitfall #1's rubber-
stamped runs easy to spot — the same two-category combination keeps
reappearing together).

## 6. Scope mismatches between a row's stated Prompt Category and its actual
   Prompt

Column D names the intended category (e.g. "Ask an out-of-scope question")
and column E is the actual prompt the *original* tester typed. If the two
don't match — an "out-of-scope" row whose prompt is actually in-scope, or
vice versa — that's a defect in how the original tester executed the step,
not something the peer reviewer caused, but it's worth naming in your
conclusion since it affects whether the peer reviewer's score (judged
against the *stated* category) is even evaluating the right thing.
