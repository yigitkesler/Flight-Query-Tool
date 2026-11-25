"""Flight schedule parser and query tool."""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB030"
FIRST_NAME = "Yigit"
LAST_NAME = "Kesler"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i")
    source.add_argument("-d")
    source.add_argument("-j")

    parser.add_argument("-a")
    parser.add_argument("-o")
    parser.add_argument("-q")
    parser.add_argument("-r", default=".")

    try:
        args = parser.parse_args(argv)

        if args.j is None and args.a is None:
            parser.error("-a is required with -i or -d")

        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")

    except SystemExit as error:
        return error.code

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j is not None:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list):
                raise ValueError("Invalid database format")

            if not all(isinstance(record, dict) for record in db):
                raise ValueError("Invalid database format")

        else:
            output = Path(args.o if args.o is not None else "db.json")
            log_path = output.parent / "errors.log"

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            airports = load_airports(args.a)

            if args.i is not None:
                paths = [args.i]
            else:
                paths = sorted(
                    str(path)
                    for path in Path(args.d).iterdir()
                    if path.is_file() and path.name.endswith(".csv")
                )

                if not paths:
                    raise ValueError("No CSV files found")

            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            with open(output, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        if args.q is not None:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if isinstance(queries, list):
                if not all(isinstance(q, dict) for q in queries):
                    raise ValueError("Invalid query format")
            elif not isinstance(queries, dict):
                raise ValueError("Invalid query format")

            results = run_queries(db, queries)

            time = datetime.now().strftime("%Y%m%d_%H%M")
            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{time}.json"
            )

            response_path = Path(args.r) / filename

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=2)

        return 0

    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())