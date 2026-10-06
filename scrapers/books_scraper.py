from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class BooksScraper(BaseScraper):
    source = "Books to Scrape"
    start_url = "https://books.toscrape.com/"

    def scrape(self) -> list[dict]:
        records: list[dict] = []
        for page_url, html in self.pages(self.start_url):
            soup = BeautifulSoup(html, "lxml")
            for article in soup.select("article.product_pod"):
                record = self._parse_book(article, page_url)
                if record is not None:
                    records.append(record)
        return records

    def _parse_book(self, article, page_url: str) -> dict | None:
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        if link is None:
            return None
        href = link.get("href")
        if not href:
            return None
        return {
            "source": self.source,
            "source_url": urljoin(page_url, href),
            "name_or_title": link.get("title") or link.get_text(),
            "category": None,
            "price_raw": price.get_text() if price else None,
            "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            "author_raw": None,
            "tags_raw": None,
            "description": None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def next_url(self, current_url: str, html: str) -> str | None:
        soup = BeautifulSoup(html, "lxml")
        link = soup.select_one("li.next > a")
        return urljoin(current_url, link["href"]) if link and link.get("href") else None
