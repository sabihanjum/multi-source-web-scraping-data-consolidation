# AI Usage

## Tool

GitHub Copilot was used as a coding assistant in VS Code.

## Uses

- Turned the assignment requirements into a small package structure.
- Suggested a shared Requests session with retries and a polite delay.
- Reviewed the CSS selectors and dynamic next-link pagination approach.
- Suggested pure cleaning, validation, fingerprinting, and offline test boundaries.
- Drafted README sections and summary-report fields.

## Representative prompts

- "Build a Python ETL pipeline with separate Books to Scrape and Quotes to Scrape classes that follow each site's next link."
- "Review this cleaning and validation design for missing values, invalid URLs, numeric prices, and ratings from one to five."
- "Add pytest tests proving duplicate detection ignores case, spacing, and punctuation."

## Human review and changes

The generated design was reviewed against the assignment before use. The final implementation keeps book category and description empty rather than making extra detail-page requests, uses the author URL for quote `source_url`, and treats failed sources independently. Validation explicitly rejects booleans as numeric prices or ratings, and summary counts separate validation reasons from duplicate counts.

## Verification

Offline tests cover whitespace, quote marks, prices, ratings, tags, validation reasons, and duplicate normalization. The complete pipeline is intended to be verified with `python main.py` from an environment created using `requirements.txt`; live results depend on network access and the current practice-site responses.
