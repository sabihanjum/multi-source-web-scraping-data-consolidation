from processing.cleaning import clean_price, clean_rating, clean_tags, clean_text, strip_quotes


def test_clean_text_collapses_whitespace():
    assert clean_text("  Hello\xa0\n  World ") == "Hello World"


def test_clean_price_and_rating():
    assert clean_price("£51.77") == 51.77
    assert clean_rating("star-rating Three") == 3


def test_quote_and_tags_are_normalized():
    assert strip_quotes("“ A useful quote ”") == "A useful quote"
    assert clean_tags(["Python", " web ", "python"]) == "python;web"
