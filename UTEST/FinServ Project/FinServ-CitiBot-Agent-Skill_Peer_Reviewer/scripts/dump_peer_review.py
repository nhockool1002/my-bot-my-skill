#!/usr/bin/env python3
"""Dump and validate the 'Peer Review' tab of a 'Citi AI - Evaluation Datasheet'
Google Sheet for the FinServ CitiBot Peer Reviewer skill.

Works directly against the live Google Sheet over HTTP (no Drive API auth
needed) via the public `gviz/tq` CSV export endpoint, so it only works on
sheets shared "Anyone with the link can view" (or better). If the sheet
needs sign-in, this script will get back an HTML login page instead of CSV
and will say so -- fall back to having the user sign in in the browser pane
and reading the tabs from there instead.

Usage:
  python3 dump_peer_review.py "<sheet_id>"
  python3 dump_peer_review.py "<sheet_id>" --check
  python3 dump_peer_review.py "<sheet_id>" --sheet "Datasheet" --check

The --check report is the whole point of this script: it flags, for every
scored row, whether a non-"Exceptional" pillar score has either (a) a valid
Issue Category selected for that pillar, or (b) a matching
"<Pillar> (Issue categories): ..." tag appended in General Comments -- the
project's own rule for when no dropdown option fits. A row failing both is a
real defect the tester must fix before this sheet can be approved.
"""
import argparse
import csv
import io
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

GVIZ_URL = "https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet}"

MAIN_COLUMNS = 22  # columns A..V

# 0-indexed column numbers of the 4 rubric-score / issue-category column pairs.
PILLARS = [
    ("Accuracy & Grounding", 8, 9),
    ("Relevance & Utility", 10, 11),
    ("Brand Voice & UX", 12, 13),
    ("Safety & Trust", 14, 15),
]
GENERAL_COMMENTS_COL = 16
ID_COL = 2
ROUND_COL = 1

VALID_ROUND_IDS = {(r, i) for r in (1, 2, 3) for i in range(1, 9)}


def fetch_csv(sheet_id, sheet_name):
    url = GVIZ_URL.format(sheet_id=sheet_id, sheet=urllib.parse.quote(sheet_name))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} fetching '{sheet_name}' -- sheet may need sign-in or the tab "
              f"name doesn't match. Ask the user to open it in the browser pane instead.",
              file=sys.stderr)
        sys.exit(1)
    if raw.lstrip().startswith("<"):
        print(f"Got an HTML page back instead of CSV for '{sheet_name}' -- this sheet is not "
              f"publicly viewable. Ask the user to sign in to the Google Sheet in the browser "
              f"pane, then read the tabs from there instead of this script.", file=sys.stderr)
        sys.exit(1)
    return raw


def parse_rows(raw_csv):
    """Return (round_num, row) for every real data row.

    The number of header rows this template's gviz export produces has been
    observed to vary (the merged-banner row and the field-name row can come
    back as one combined CSV row or two), so a data row is identified
    structurally -- its ID column (C) is a bare integer 1-8 -- rather than by
    assuming a fixed number of rows to skip. The Round column (B) is merged
    down the sheet (only the first row of each round carries a value), so it
    must be forward-filled across ALL rows, including header rows, before
    filtering down to data rows -- otherwise every row after the first in a
    round loses its round number.

    One real sheet (cycle #566836, Tester 2's "Peer Review" tab) had its R1-ID6
    ID cell accidentally blanked out even though that row's Prompt Category /
    Prompt / Response / all I-Q scoring was filled in normally -- a data-entry
    slip in the original tester's columns (A-D), not something the peer
    reviewer touched. Relying on the ID cell alone made that real, fully-
    reviewed row invisible (misreported as an entirely missing row, and its
    own missing-category defect went unflagged as a result). So: track the
    row's position within its 8-row round block, and if the ID cell doesn't
    parse as 1-8 but the Prompt Category cell (D) is non-empty, recover the ID
    from that position instead of dropping the row.
    """
    reader = csv.reader(io.StringIO(raw_csv))
    rows = list(reader)
    out = []
    round_num = None
    position = 0
    for row in rows:
        round_cell = (row[ROUND_COL] if len(row) > ROUND_COL else "").strip()
        if re.fullmatch(r"[1-3]", round_cell):
            round_num = int(round_cell)
            position = 0
        if round_num is None:
            continue
        id_cell = (row[ID_COL] if len(row) > ID_COL else "").strip()
        prompt_cat_cell = (row[3] if len(row) > 3 else "").strip()
        if re.fullmatch(r"[1-8]", id_cell):
            position = int(id_cell)
            out.append((round_num, row))
        elif prompt_cat_cell and position < 8:
            position += 1
            recovered = list(row) + [""] * (ID_COL + 1 - len(row))
            recovered[ID_COL] = str(position)
            out.append((round_num, recovered))
    return out


def load_issue_categories(sheet_id, sheet_name="Issue Categories"):
    raw = fetch_csv(sheet_id, sheet_name)
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)[1:]  # skip header
    by_pillar = {}
    current_pillar = None
    for row in rows:
        if len(row) < 2:
            continue
        pillar, category = row[0].strip(), row[1].strip()
        if pillar:
            current_pillar = pillar
        if current_pillar and category:
            by_pillar.setdefault(current_pillar, set()).add(category)
    return by_pillar


def split_categories(cell):
    """Issue-category cells can hold more than one selection (the column header
    says "select all relevant reasons"). Split on commas/newlines/semicolons."""
    return [c.strip() for c in re.split(r"[,;\n]", cell) if c.strip()]


def dump_flat(rows, max_col=MAIN_COLUMNS):
    for i, (round_num, row) in enumerate(rows):
        vals = (row + [""] * max_col)[:max_col]
        id_val = vals[ID_COL]
        print(f"--- R{round_num}-ID{id_val} ---")
        print(f"Prompt Category: {vals[3]}")
        print(f"Prompt: {vals[4][:200]}")
        print(f"Response: {vals[5][:200]}")
        for name, score_col, cat_col in PILLARS:
            print(f"{name}: {vals[score_col]!r}  Issue Category: {vals[cat_col]!r}")
        print(f"General Comments: {vals[GENERAL_COMMENTS_COL][:300]}")
        print()


def check(rows, issue_categories, max_col=MAIN_COLUMNS):
    seen = set()
    problems = []
    prev_signature = None
    run_start = None
    run_len = 0
    run_label = None

    for round_num, row in rows:
        vals = (row + [""] * max_col)[:max_col]
        id_val = vals[ID_COL]
        id_num = int(id_val)
        row_label = f"R{round_num}-ID{id_val}"
        if (round_num, id_num) in seen:
            problems.append(f"{row_label}: duplicate row -- check for a copy-paste error.")
        seen.add((round_num, id_num))

        general_comments = vals[GENERAL_COMMENTS_COL]
        signature = []
        for name, score_col, cat_col in PILLARS:
            score = vals[score_col].strip()
            cat_cell = vals[cat_col].strip()
            signature.append((score, cat_cell))

            if not score:
                problems.append(f"{row_label}: MISSING {name} rubric score.")
                continue

            if score == "Exceptional":
                continue

            if cat_cell:
                selected = split_categories(cat_cell)
                valid = issue_categories.get(name, set())
                invalid = [c for c in selected if c not in valid]
                if invalid:
                    problems.append(
                        f"{row_label}: {name} Issue Category "
                        f"{invalid} is not one of this pillar's valid options {sorted(valid)}."
                    )
            else:
                tag_re = re.compile(re.escape(name) + r"\s*\(Issue categories?\)\s*:", re.IGNORECASE)
                if not tag_re.search(general_comments):
                    problems.append(
                        f"{row_label}: {name} scored '{score}' but has "
                        f"no Issue Category selected AND no '{name} (Issue categories): ...' tag "
                        f"in General Comments -- tester must either pick a valid option or append "
                        f"that tag with their own proposed category."
                    )

        # Only "all Exceptional" is a common, legitimate pattern across many rows -- that's
        # just the bot doing well repeatedly. A repeated signature that contains a non-
        # Exceptional score is the real rubber-stamping / default-category-syndrome signal
        # (same failure, same category, picked without re-reading each new prompt/response).
        sig_tuple = tuple(signature)
        sig_has_defect = any(score != "Exceptional" for score, _ in signature)
        if sig_tuple == prev_signature and sig_has_defect:
            run_len += 1
        else:
            if run_len >= 3:
                problems.append(
                    f"{run_label} .. {row_label} (previous row): identical 4-pillar "
                    f"score+category pattern {prev_signature} repeated {run_len} rows in a row "
                    f"across different prompts/responses -- looks like a rubber-stamped / "
                    f"default-category pass rather than an independent per-row judgment. "
                    f"Verify each row individually."
                )
            prev_signature = sig_tuple if sig_has_defect else None
            run_label = row_label
            run_len = 1
    if run_len >= 3:
        problems.append(
            f"{run_label} .. {row_label} (last row): identical 4-pillar score+category pattern "
            f"{prev_signature} repeated {run_len} rows in a row across different "
            f"prompts/responses -- looks like a rubber-stamped / default-category pass rather "
            f"than an independent per-row judgment. Verify each row individually."
        )

    missing_rounds_ids = sorted(VALID_ROUND_IDS - seen)
    if missing_rounds_ids:
        problems.append(f"Missing rows entirely for (Round, ID): {missing_rounds_ids}")

    if not problems:
        print("No completeness or Issue Category defects found -- all 24 rows present, all "
              "scored pillars have either a valid category or a properly tagged General "
              "Comments entry.")
    else:
        for p in problems:
            print("- " + p)
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet_id", help="The Google Sheet ID (the long id in its URL, not the full URL)")
    ap.add_argument("--sheet", default="Peer Review", help="Tab to dump/check (default: 'Peer Review')")
    ap.add_argument("--check", action="store_true", help="Run the completeness / Issue Category validity report")
    ap.add_argument("--dump", action="store_true", help="Print every scored row (default if --check not given)")
    args = ap.parse_args()

    raw = fetch_csv(args.sheet_id, args.sheet)
    rows = parse_rows(raw)

    if args.check:
        print(f"===== {args.sheet}: completeness / Issue Category check =====")
        issue_categories = load_issue_categories(args.sheet_id)
        problems = check(rows, issue_categories)
        print()
        print(f"Verdict: {'KHÔNG ĐẠT / FAIL' if problems else 'ĐẠT / PASS'} "
              f"({len(problems)} issue(s) found)")

    if args.dump or not args.check:
        print(f"\n===== {args.sheet}: row dump =====")
        dump_flat(rows)


if __name__ == "__main__":
    main()
