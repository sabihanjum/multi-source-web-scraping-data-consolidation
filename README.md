# Multi-Source Web Scraping & Data Consolidation

A Python 3.10-3.12 ETL pipeline for Books to Scrape and Quotes to Scrape. Run the complete job with one command:

```text
python main.py
```

## Setup

Create and activate a virtual environment, then install the pinned dependencies:

```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

The project uses Requests for HTTP, BeautifulSoup with lxml for parsing, and pytest for offline tests.

## Scraping design

`BooksScraper` starts at `https://books.toscrape.com/`; `QuotesScraper` starts at `https://quotes.toscrape.com/`. Each scraper selects records from the current page, finds `li.next > a`, resolves its relative `href` with `urljoin`, and repeats until there is no next link. Page counts are never hard-coded.

The shared HTTP helper sets a descriptive User-Agent, a timeout, retries temporary HTTP statuses (429, 500, 502, 503, 504), logs failures, and pauses 0.5 seconds between requests. A failed source does not prevent the other source from running.

Observed selectors are `article.product_pod`, `h3 > a`, `p.price_color`, and `p.star-rating` for books; `div.quote`, `span.text`, `small.author`, `a.tag`, and `li.next > a` for quotes.

## Common data model

The CSV columns are `source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `tags`, `description`, and `scraped_at`. Fields that do not exist at a source are empty. `source_url` is the book detail URL for books and the author page URL, or quote page URL if the author link is unavailable, for quotes.

Book category and description are left empty because the listing page does not expose them; the pipeline does not issue an extra request per book or invent values.

## Processing

Cleaning collapses whitespace and non-breaking spaces, strips quote marks, converts pound prices to floats, maps word ratings to integers 1-5, lowercases and sorts tags, and rejects URLs without an HTTP(S) scheme and host.

Validation requires a known source, a non-empty name/title, a valid URL, a non-negative numeric price when present, and a rating from 1 to 5 when present. Rejected records are logged and counted by reason.

Deduplication hashes normalized identifying fields. Books use `source + title`; quotes use `source + author + first 50 characters of quote text`. Lowercase conversion, punctuation removal, and whitespace collapsing make equivalent formatting match. Duplicate records are dropped and counted.

## Outputs

- `output/final_dataset.csv`: unique, valid records from both sources.
- `output/summary_report.json`: scrape, clean, rejection, duplicate, final-count, and timing metrics per source and overall.
- `logs/scraper.log`: timestamped requests, page progress, warnings, and errors.

## Free Render deployment

Render's free tier does not support Cron Jobs. The included `render.yaml` therefore defines a free Web Service using `web_service.py`. The service starts the scraper in the background and exposes a small health response on Render's assigned port. Free services may sleep or restart, so this is suitable for a demonstration run rather than reliable scheduled execution. The local command remains `python main.py`.

Run offline tests with:

```text
pytest -q
```

## Assumptions and limitations

The practice sites are server-rendered HTML and require no browser automation. Network availability is required for `main.py`. A page that still fails after retries stops that source, while the other source continues. The reported `cleaned` count is the number successfully transformed before validation; rejected counts are reported separately.

## AI usage

AI assistance was used for initial structure, selector review, edge-case suggestions, and test cases. See `AI_USAGE.md` for the review and verification record.
