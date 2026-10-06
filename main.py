from __future__ import annotations

import csv
import json
import logging
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_COLUMNS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]
SOURCES = ("Books to Scrape", "Quotes to Scrape")
logger = logging.getLogger(__name__)


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8")
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def write_outputs(records: list[dict], report: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / "final_dataset.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows({column: record.get(column) for column in CSV_COLUMNS} for record in records)
    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def run() -> None:
    configure_logging()
    started_at = datetime.now(timezone.utc)
    started_clock = time.perf_counter()
    raw_by_source: dict[str, list[dict]] = defaultdict(list)

    for scraper in (BooksScraper(), QuotesScraper()):
        try:
            raw_by_source[scraper.source].extend(scraper.scrape())
        except Exception:
            logger.exception("Unexpected failure while scraping %s", scraper.source)

    cleaned_records: list[dict] = []
    rejected_by_source: dict[str, Counter[str]] = defaultdict(Counter)
    cleaned_counts = {source: 0 for source in SOURCES}
    for source, raw_records in raw_by_source.items():
        for raw_record in raw_records:
            try:
                record = clean_record(raw_record)
                cleaned_counts[source] += 1
            except (TypeError, ValueError, AttributeError) as exc:
                rejected_by_source[source]["cleaning_error"] += 1
                logger.warning("Rejected %s during cleaning: %s", source, exc)
                continue
            problems = validate_record(record)
            if problems:
                for problem in problems:
                    rejected_by_source[source][problem] += 1
                logger.warning("Rejected record from %s: %s", source, ", ".join(problems))
                continue
            cleaned_records.append(record)

    unique_records, duplicate_records = find_duplicates(cleaned_records)
    duplicate_counts = Counter(record["source"] for record in duplicate_records)
    finished_at = datetime.now(timezone.utc)
    report = {
        "run": {
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_seconds": round(time.perf_counter() - started_clock, 3),
        },
        "per_source": {
            source: {
                "scraped": len(raw_by_source.get(source, [])),
                "cleaned": cleaned_counts[source],
                "rejected": sum(rejected_by_source[source].values()),
                "rejected_by_reason": dict(sorted(rejected_by_source[source].items())),
                "duplicates": duplicate_counts[source],
            }
            for source in SOURCES
        },
        "duplicates_detected": len(duplicate_records),
        "final_record_count": len(unique_records),
    }
    write_outputs(unique_records, report)
    logger.info("Wrote %d final records", len(unique_records))


if __name__ == "__main__":
    run()
