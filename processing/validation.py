from __future__ import annotations

import math
from numbers import Real
from urllib.parse import urlparse

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record: dict) -> list[str]:
    problems: list[str] = []
    if record.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")
    if not record.get("name_or_title"):
        problems.append("missing_name")
    parsed_url = urlparse(str(record.get("source_url") or ""))
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        problems.append("invalid_url")
    price = record.get("price")
    if price is not None and (
        isinstance(price, bool)
        or not isinstance(price, Real)
        or not math.isfinite(float(price))
        or price < 0
    ):
        problems.append("invalid_price")
    rating = record.get("rating")
    if rating is not None and (isinstance(rating, bool) or rating not in {1, 2, 3, 4, 5}):
        problems.append("invalid_rating")
    return problems
