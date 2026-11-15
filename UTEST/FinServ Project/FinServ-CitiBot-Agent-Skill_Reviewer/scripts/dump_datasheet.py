#!/usr/bin/env python3
"""Dump a 'Citi AI - Evaluation Datasheet' style xlsx for the FinServ CitiBot
review skill, so Claude doesn't have to hand-write openpyxl code for every
test case.

The template always has an A..V (22 column) 'Datasheet' tab with one header
row, one instructions row, then up to 24 data rows (R=round 1-3, ID=1-8), and
separate 'Issue Categories' / 'Scoring' / 'Scoring Rubric' reference tabs.

Usage:
  python3 dump_datasheet.py "<path to .xlsx>"
  python3 dump_datasheet.py "<path to .xlsx>" --completeness
  python3 dump_datasheet.py "<path to .xlsx>" --all-tabs
  python3 dump_datasheet.py "<path to .xlsx>" --sheet "Peer Review"
"""
import argparse
import sys

import openpyxl

MAIN_COLUMNS = 22  # columns A..V in this template

# 1-indexed column numbers of the 4 rubric-score columns in the Datasheet tab.
RUBRIC_COLUMNS = {
    9: "Accuracy & Grounding",
    11: "Relevance & Utility",
    13: "Brand Voice & UX",
    15: "Safety & Trust",
}


def dump_sheet(ws, max_col=MAIN_COLUMNS, first_data_row=3):
    headers = [ws.cell(row=1, column=c).value for c in range(1, max_col + 1)]
    for r in range(first_data_row, ws.max_row + 1):
        vals = [ws.cell(row=r, column=c).value for c in range(1, max_col + 1)]
        if all(v in (None, "") for v in vals):
            continue
        print(f"--- ROW {r} ---")
        for h, v in zip(headers, vals):
            if v not in (None, ""):
                print(f"{h}: {v}")
        print()


def dump_flat(ws):
    for row in ws.iter_rows(values_only=True):
        vals = [v for v in row if v not in (None, "")]
        if vals:
            print(vals)


def check_completeness(ws, first_data_row=3):
    """Flag any row that has an ID but is missing one of the 4 rubric columns.

    This is the single most common defect found across past reviews: a tester
    scores Accuracy, decides it's fine, and never fills in Relevance / Brand
    Voice / Safety for that row at all.
    """
    any_missing = False
    for r in range(first_data_row, ws.max_row + 1):
        id_val = ws.cell(row=r, column=3).value  # column C = ID
        if id_val in (None, ""):
            continue
        missing = [
            name
            for col, name in RUBRIC_COLUMNS.items()
            if ws.cell(row=r, column=col).value in (None, "")
        ]
        if missing:
            any_missing = True
            round_val = ws.cell(row=r, column=2).value  # column B = R
            print(f"Row {r} (R={round_val}, ID={id_val}): MISSING -> {', '.join(missing)}")
    if not any_missing:
        print("All scored rows have all 4 rubric pillars filled in.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("xlsx_path")
    ap.add_argument("--sheet", default="Datasheet", help="Tab to dump row-by-row (default: Datasheet)")
    ap.add_argument(
        "--completeness",
        action="store_true",
        help="Also report which rows are missing one of the 4 rubric-score columns",
    )
    ap.add_argument(
        "--all-tabs",
        action="store_true",
        help="Also dump 'Issue Categories', 'Scoring Rubric' and 'Scoring' tabs for reference",
    )
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx_path, data_only=True)
    print("Sheets found:", wb.sheetnames)
    print()

    if args.sheet not in wb.sheetnames:
        print(f"Sheet '{args.sheet}' not found in this workbook.", file=sys.stderr)
        sys.exit(1)

    print(f"===== {args.sheet} =====")
    dump_sheet(wb[args.sheet])

    if args.completeness and args.sheet == "Datasheet":
        print("===== Rubric completeness check =====")
        check_completeness(wb[args.sheet])
        print()

    if args.all_tabs:
        for name in ("Issue Categories", "Scoring Rubric", "Scoring"):
            if name in wb.sheetnames:
                print(f"\n===== {name} =====")
                dump_flat(wb[name])


if __name__ == "__main__":
    main()
