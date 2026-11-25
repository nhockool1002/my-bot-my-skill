# Meta account sourcing & allow listing (pre-activation)

A cycle sits in `Pending Activation` on the Monday.com board until enough
tester accounts are collected and allow-listed. This is the flow that gets
it there.

## 1. Participation slots + the allow-listing form

Testers claim a **participation slot** (one per platform they intend to
test — Android, iOS, Web, Mac App; the same tester can claim more than one
platform's slot at once, that's expected, not a conflict) and fill in a
form with the account details needed for the client to allow-list them:

- **iOS**: TestFlight email + the email used for their Muse/News account.
- **Android**: Google/Play Store email + the email used for their
  Muse/News account.

## 2. Meta Account Sourcing Sheet

Submitted form data auto-populates this sheet — nothing to do here except
reference it as the source for step 3.

## 3. Meta Allow Listing Sheet

For each new row on the Account Sourcing Sheet:

1. Find (or confirm) the correct **country section** on the Allow Listing
   Sheet.
2. Copy the tester's row across — email(s), platform, any other filled
   field. Leave `Account type` blank unless the sheet explicitly asks for
   it.
3. Mark the row **`Yes`** in its status column.
4. **Highlight the whole row green** once copied, so the next person
   scanning the sheet can see at a glance which rows are done. (If you
   notice earlier rows that were copied but never highlighted, that's a
   previous TTL's oversight, not something you need to go back and fix on
   your own initiative — just keep the convention going forward.)

## 4. Applause Allowlisting Sheet (next hop, per v1 / project memory)

Per [[reference-mybotmyskill-repo]] / v1's README, once the client
confirms entries from the Meta Allow Listing Sheet, they move on to the
client-facing **Applause Allowlisting Sheet**, which is what the client
reads to know who's officially onboarded. The 2026-11-24 call didn't
re-demonstrate this specific hop — treat it as still accurate rather than
superseded, but confirm with the TE if a cycle behaves differently.
