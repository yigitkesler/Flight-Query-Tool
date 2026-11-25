"""Reading CSV files into flight records and error messages."""

import csv
from pathlib import Path
from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()

    for path in paths:
        filename = Path(path).name

        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if line_number == 1:
                    continue

                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                fields = next(csv.reader([line]))
                error = validate_row(fields, airports)

                if error is None:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])

                    if key in seen:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if error is not None:
                    errors.append(
                        f"{filename}:{line_number}: {error} | {line.rstrip()}"
                    )

    return records, errors