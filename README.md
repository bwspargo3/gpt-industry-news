# Actuarial Intelligence Digest

A robust, automated pipeline for tracking life and annuity market developments, regulatory updates, and emerging industry trends.

## Data Pipeline Architecture
The intelligence digest has transitioned to a professional, API-first data ingestion model to ensure high availability and data integrity[span_1](start_span)[span_1](end_span).

*   **API Integration**: Replaced legacy `BeautifulSoup` HTML scrapers with the **NewsAPI** `/everything` endpoint. This shift eliminates 404 errors, prevents bot-blocking, and ensures structured JSON ingestion[span_2](start_span)[span_2](end_span).
*   **Direct RSS Feeds**: Added direct, open-access RSS wire support for real-time updates from core trade presses and regulatory bodies[span_3](start_span)[span_3](end_span).
*   **Pipeline Efficiency**: The codebase is now leaner, natively parsing structured data and utilizing GitHub Actions to manage environment secrets securely (e.g., `NEWSAPI_KEY`)[span_4](start_span)[span_4](end_span).
*   **Legacy Cleanup**: Custom HTML scraping functions have been deprecated in favor of robust, environment-variable-driven API queries[span_5](start_span)[span_5](end_span).

## Requirements
To run the digest, install the necessary dependencies:

```bash
pip install -r requirements.txt
