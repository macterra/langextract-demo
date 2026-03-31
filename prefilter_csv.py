import argparse
import csv
import re
import sys
from pathlib import Path


TEXT_COLUMNS = ("title", "ancestry_titles", "resolved_text")

# Keep this fairly strict: only pass rows with a strong chance of yielding
# a boring_type extraction, not just generic geotech activity words.
BORING_TYPE_PATTERNS = (
    r"\btest borings?\b",
    r"\bsoil borings?\b",
    r"\brock borings?\b",
    r"\bmonitoring well borings?\b",
    r"\bcone penetration tests?\b",
    r"\bcone penetration test soundings?\b",
    r"\bcpt soundings?\b",
    r"\bcpts?\b",
    r"\bsoundings?\b",
    r"\bborings?\b",
)

BORING_TYPE_REGEX = re.compile("|".join(BORING_TYPE_PATTERNS), re.IGNORECASE)


def build_text(row: dict[str, str]) -> str:
    return " ".join((row.get(column, "") or "") for column in TEXT_COLUMNS)


def is_survivor(row: dict[str, str]) -> bool:
    text = build_text(row)
    return bool(BORING_TYPE_REGEX.search(text))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print only CSV rows with a strong chance of containing a boring_type extraction."
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        return 1

    scanned = 0
    written = 0
    rejected = 0

    with csv_path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            scanned += 1

            if not is_survivor(row):
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
