"""Flight database queries."""

import math
from validator import parse_datetime


def valid_query(query):
    if not isinstance(query, dict):
        return False

    record_keys = (
        "flight_id", "origin", "destination",
        "departure_datetime", "arrival_datetime", "price"
    )

    allowed_keys = record_keys + (
        "min_price", "sort_by", "order", "limit"
    )

    for key, value in query.items():
        if key not in allowed_keys:
            return False

        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return False

        elif key in ("departure_datetime", "arrival_datetime"):
            if not isinstance(value, str):
                return False
            if parse_datetime(value) is None:
                return False

        elif key in ("price", "min_price"):
            if type(value) not in (int, float):
                return False
            if isinstance(value, float) and not math.isfinite(value):
                return False

        elif key == "sort_by":
            if value not in record_keys:
                return False

        elif key == "order":
            if value not in ("asc", "desc"):
                return False
            if "sort_by" not in query:
                return False

        elif key == "limit":
            if type(value) is not int or value < 0:
                return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not valid_query(query):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": []
        }

    matches = []

    for flight in db:
        match = True

        for key, value in query.items():
            if key in ("flight_id", "origin", "destination"):
                if flight[key] != value:
                    match = False

            elif key == "departure_datetime":
                if flight[key] < value:
                    match = False

            elif key == "arrival_datetime":
                if flight[key] > value:
                    match = False

            elif key == "price":
                if flight["price"] > value:
                    match = False

            elif key == "min_price":
                if flight["price"] < value:
                    match = False

        if match:
            matches.append(flight)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=descending
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]