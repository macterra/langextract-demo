import argparse
import csv
import re
import sys
from pathlib import Path

TEXT_COLUMNS = ("title", "ancestry_titles", "resolved_text")


def build_text(row: dict[str, str]) -> str:
    return " ".join((row.get(column, "") or "") for column in TEXT_COLUMNS)


def compile_pattern_regex(
    patterns: tuple[str, ...],
) -> re.Pattern[str]:
    return re.compile("|".join(patterns), re.IGNORECASE)


def is_survivor(
    row: dict[str, str],
    *,
    patterns: tuple[str, ...],
    pattern_regex: re.Pattern[str] | None = None,
) -> bool:
    text = build_text(row)
    if pattern_regex is None:
        pattern_regex = compile_pattern_regex(patterns)
    return bool(pattern_regex.search(text))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print only CSV rows that match the configured filter patterns."
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
        help="Maximum number of survivor rows to print.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Regex pattern to match against the combined row text. Repeat to provide multiple patterns.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)
    patterns = tuple(args.pattern)

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        return 1
    if not patterns:
        print("At least one --pattern is required.", file=sys.stderr)
        return 1

    scanned = 0
    written = 0
    rejected = 0
    pattern_regex = compile_pattern_regex(patterns)

    with csv_path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            scanned += 1

            if not is_survivor(row, patterns=patterns, pattern_regex=pattern_regex):
                rejected += 1
                continue

            writer.writerow(row)
            written += 1

            if args.limit is not None and written >= args.limit:
                break

    limit_hit = args.limit is not None and written >= args.limit
    print(
        (
            f"prefilter stats: scanned={scanned}, survivors={written}, "
            f"rejected={rejected}, limit_hit={str(limit_hit).lower()}"
        ),
        file=sys.stderr,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
