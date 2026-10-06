from __future__ import annotations

import hashlib
import re


def _normalized(value: object) -> str:
    return " ".join(re.sub(r"[^\w\s]+", " ", str(value or "").lower()).split())


def make_fingerprint(record: dict) -> str:
    source = record.get("source")
    if source == "Books to Scrape":
        key = f"{source} {record.get('name_or_title')}"
    else:
        quote = _normalized(record.get("name_or_title"))[:50]
        key = f"{source} {record.get('author')} {quote}"
    return hashlib.sha256(_normalized(key).encode("utf-8")).hexdigest()


def find_duplicates(records: list[dict]) -> tuple[list[dict], list[dict]]:
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates: list[dict] = []
    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)
    return unique, duplicates
