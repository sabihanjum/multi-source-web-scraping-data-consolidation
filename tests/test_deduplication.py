from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_spacing_and_punctuation():
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example Book Title"},
        {"source": "Books to Scrape", "name_or_title": "  example   book-title "},
        {"source": "Books to Scrape", "name_or_title": "Different Book"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 2
    assert len(duplicates) == 1


def test_quote_duplicates_use_author_and_first_fifty_characters():
    records = [
        {"source": "Quotes to Scrape", "author": "A. Author", "name_or_title": "Same quote"},
        {"source": "Quotes to Scrape", "author": "a author", "name_or_title": " SAME QUOTE!"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
