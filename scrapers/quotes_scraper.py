from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class QuotesScraper(BaseScraper):
    source = "Quotes to Scrape"
    start_url = "https://quotes.toscrape.com/"

    def scrape(self) -> list[dict]:
        records: list[dict] = []
        for page_url, html in self.pages(self.start_url):
            soup = BeautifulSoup(html, "lxml")
            for quote in soup.select("div.quote"):
                record = self._parse_quote(quote, page_url)
                if record is not None:
                    records.append(record)
        return records

    def _parse_quote(self, quote, page_url: str) -> dict | None:
        text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        if text is None or author is None:
            return None
        author_link = author.find_next("a", href=True)
        author_url = (
            urljoin(page_url, author_link["href"])
            if author_link is not None
            else page_url
        )
        return {
            "source": self.source,
            "source_url": author_url,
            "name_or_title": text.get_text(),
            "category": None,
            "price_raw": None,
            "rating_raw": None,
            "author_raw": author.get_text(),
            "tags_raw": [tag.get_text() for tag in quote.select("a.tag")],
            "description": None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def next_url(self, current_url: str, html: str) -> str | None:
        soup = BeautifulSoup(html, "lxml")
        link = soup.select_one("li.next > a")
        return urljoin(current_url, link["href"]) if link and link.get("href") else None
