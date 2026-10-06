from __future__ import annotations

import logging
import time
from typing import Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self, delay: float = 0.5, timeout: float = 15.0) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MultiSourceScraper/1.0 (educational project)"}
        )
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url: str) -> requests.Response | None:
        try:
            logger.info("Requesting %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None
        finally:
            time.sleep(self.delay)

    def pages(self, start_url: str) -> Iterator[tuple[str, str]]:
        url = start_url
        page_number = 1
        while url:
            logger.info("Processing page %d: %s", page_number, url)
            response = self.fetch(url)
            if response is None:
                break
            yield url, response.text
            url = self.next_url(url, response.text)
            page_number += 1

    def next_url(self, current_url: str, html: str) -> str | None:
        raise NotImplementedError
