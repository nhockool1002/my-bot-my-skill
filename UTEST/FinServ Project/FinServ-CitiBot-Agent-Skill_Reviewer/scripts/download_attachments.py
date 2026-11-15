#!/usr/bin/env python3
"""Download uTest attachment screenshots resolved during the FinServ CitiBot
review workflow (see SKILL.md Step 3 for how the manifest is produced).

Manifest format: tab-separated, one line per file, no header:
  <step_folder>\t<filename>\t<presigned_url>

Example line:
  Step05_Round1-TC4\tIMG_1330.png\thttps://utest-dl.s3-accelerate.amazonaws.com/...

Usage:
  python3 download_attachments.py manifest.tsv "TestCase_12345_Tester6_Attachments"
"""
import os
import sys
import urllib.request


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    manifest_path, base_dir = sys.argv[1], sys.argv[2]
    ok, fail = 0, 0

    with open(manifest_path, encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                print(f"Skipping malformed manifest line {line_num}: {line[:80]!r}", file=sys.stderr)
                continue
            folder, filename, url = parts
            dest_dir = os.path.join(base_dir, folder)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            try:
                urllib.request.urlretrieve(url, dest_path)
                print(f"OK: {folder}/{filename}")
                ok += 1
            except Exception as exc:  # noqa: BLE001 - want to keep going and report at the end
                print(f"FAIL: {folder}/{filename} ({exc})", file=sys.stderr)
                fail += 1

    print(f"\nDownloaded {ok} file(s), {fail} failure(s), into {base_dir!r}.")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
