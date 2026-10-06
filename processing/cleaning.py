from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value: object) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    return text.strip("\"'“”‘’ ") or None


def clean_price(value: object) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:[.,]\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value: object) -> int | None:
    for word in str(value or "").lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(value: object) -> str | None:
    if value is None:
        return None
    values: Iterable[object] = value if isinstance(value, (list, tuple, set)) else [value]
    tags = sorted({tag.lower() for item in values if (tag := clean_text(item))})
    return ";".join(tags) or None


def normalize_url(value: object, base_url: str | None = None) -> str | None:
    if value is None:
        return None
    url = urljoin(base_url or "", str(value).strip())
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else None


def clean_record(raw: dict) -> dict:
    is_quote = raw.get("source") == "Quotes to Scrape"
    return {
        "source": clean_text(raw.get("source")),
        "source_url": normalize_url(raw.get("source_url")),
        "name_or_title": strip_quotes(raw.get("name_or_title")) if is_quote else clean_text(raw.get("name_or_title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price_raw")),
        "rating": clean_rating(raw.get("rating_raw")),
        "author": clean_text(raw.get("author_raw")),
        "tags": clean_tags(raw.get("tags_raw")),
        "description": clean_text(raw.get("description")),
        "scraped_at": clean_text(raw.get("scraped_at")),
    }
