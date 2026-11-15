# Triage heuristics — OOS, WAD, and reporting-quality patterns

These are generalized from real findings on an Authors First cycle (#565607).
Apply the *principle*, not the specific example — always re-check against the
current cycle's own Overview (Step 1) rather than assuming these exact facts
carry over.

## Out of scope (OOS)

An issue is OOS when it falls under something the cycle's own Overview names
as out of scope or "do not report" — never from a generic assumption about
what a streaming app "should" test. Typical categories seen in this project's
Overviews:

- A UI quirk the Overview explicitly disclaims (e.g. "the back button here
  leads to our marketing site, don't report it").
- A whole feature area marked out of scope for the round (e.g. "all purchases
  are out of scope this round").
- A testing method the Overview forbids outright (security/invasive testing,
  Beta OS, external websites unrelated to the app, social-sharing tests on
  non-private/non-locked test accounts).
- A device/browser genuinely outside what the cycle supports at all (not
  merely "not on the sample list" — see the environment note below).

Cite the exact sentence from Step 1's `outScope`/`issueReportingInstructions`
when calling OOS. A vague "this doesn't feel in scope" is not sufficient.

## Works as designed (WAD)

WAD applies when the reported behavior is the *product's intended behavior*,
not a defect — either because the Overview says so explicitly, or because the
behavior is self-evidently intentional once you read the actual mechanism.
Seen in this project:

- A shared test account logging other testers out once more than N users are
  logged in simultaneously — the Overview calls this expected for a shared
  account, not a session-management bug.
- Playback position / bookmark drifting unexpectedly on a shared account —
  again explicitly named as expected given concurrent shared use.

Don't invent WAD reasoning that isn't grounded in the Overview or in a clearly
intentional design choice visible in the report itself (e.g. a confirmation
dialog that is supposed to require two taps). If you're not sure something is
intentional, it isn't WAD — it's either Pending Approval or Info Requested.

## Reporting-quality flags (not themselves OOS/WAD, but block a clean Approval)

These don't invalidate the underlying defect, but they mean you can't approve
"as is" without asking the tester to fix the report first:

- **Title/platform vs. repro-steps mismatch**: the title and the structured
  "Platform" field say one device, but every numbered action in
  `actionPerformed` describes operating a *different* device, with no step
  referencing the named one's actual input method (e.g. title says Apple TV,
  but every step says "on iPhone" with no Apple TV remote action at all).
  This is a common copy-paste artifact when a tester reuses a template from a
  different test case. Ask which device it was actually tested on, and ask
  for the title/platform or the steps to be corrected to match.
- **Expected/Actual fields swapped or duplicated**: `expectedResult`
  describes the *broken* behavior instead of the *correct* one, and `result`
  just repeats it — instead of Expected describing what should happen and
  Actual describing what did. The underlying bug claim may still be real;
  ask for the two fields to be rewritten correctly, per the Overview's own
  "no one-liners, clear repro" requirement.
- **Free-text "Platform" custom field contradicts the structured
  environment**: e.g. `customFields` says `"Platform": "Fire TV"` while the
  actual `environments[]` entry and the title both say Apple TV. Usually a
  copy-paste leftover from reporting a similar bug on a different device
  cycle; flag for correction.

## Environment/device not on the cycle's listed table — informational only

The Overview usually ships a long table of "your specified environments."
**Do not auto-reject or down-weight an issue solely because the exact device/
OS combination isn't literally in that table.** Observed TTL behavior on this
project explicitly approved issues reported from devices never listed there
(e.g. an iPhone 12, an iPhone 7) — the table is a sampling guide for staffing
the cycle, not a strict allowlist the TTL actually enforces at triage time.
Only treat a device as disqualifying when the Overview explicitly restricts
testing to the listed devices only, or the device is a category the Overview
names as forbidden outright (Beta OS, emulators, etc.).

## When none of the above apply

If an issue is in scope, isn't a duplicate (per
`references/duplicate_detection.md`), isn't WAD, and has no reporting-quality
problem serious enough to block approval, it's **Pending Approval** — say so
plainly, and still give a one- or two-line summary of what the bug is and why
it holds up, citing the repro/expected/actual text. A valid issue still needs
a summary, not just a bucket label.
