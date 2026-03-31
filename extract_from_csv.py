import argparse
import csv
import json
import sys
from pathlib import Path

from boring_extraction import extract_context_keys
from boring_extraction import filter_context_keys
from prefilter_csv import is_survivor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run boring extraction on survivor rows from a CSV and print JSONL results."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="staging_phase_I_20260330_192757.csv",
        help="Path to the source CSV file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of survivor rows to extract.",
    )
    return parser.parse_args()


def build_output_row(row: dict[str, str], normalized_records) -> dict:
    return {
        "report_id": row.get("report_id"),
        "system_label_name": row.get("system_label_name"),
        "ancestry_titles": row.get("ancestry_titles"),
        "title": row.get("title"),
        "filename": row.get("filename"),
        "resolved_text": row.get("resolved_text"),
        "normalized_records": [
            record.model_dump(exclude_none=True) for record in normalized_records
        ],
    }


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        return 1

    scanned = 0
    survivors = 0
    pattern_regex = filter_context_keys()

    with csv_path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            scanned += 1
            if not is_survivor(row, pattern_regex=pattern_regex):
                continue

            text = row.get("resolved_text", "")
            if not text.strip():
                continue

            normalized_records = extract_context_keys(text, show_progress=False)
            print(
                json.dumps(
                    build_output_row(row, normalized_records),
                    ensure_ascii=True,
                )
            )

            survivors += 1
            if args.limit is not None and survivors >= args.limit:
                break

    print(
        (
            f"extract stats: scanned={scanned}, extracted={survivors}, "
            f"limit_hit={str(args.limit is not None and survivors >= args.limit).lower()}"
        ),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
