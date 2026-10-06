from processing.validation import validate_record


def valid_book():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/book_1/index.html",
        "name_or_title": "A Book",
        "price": 10.5,
        "rating": 4,
    }


def test_valid_record_has_no_problems():
    assert validate_record(valid_book()) == []


def test_invalid_record_returns_all_reasons():
    record = valid_book() | {
        "source": "Unknown",
        "source_url": "not-a-url",
        "name_or_title": "",
        "price": -1,
        "rating": 6,
    }
    assert validate_record(record) == [
        "unknown_source",
        "missing_name",
        "invalid_url",
        "invalid_price",
        "invalid_rating",
    ]
