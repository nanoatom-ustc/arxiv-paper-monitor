from __future__ import annotations

from typing import Optional

import requests

from config import Config
from crossref_fetcher import CrossrefFetcher


class ScienceFetcher(CrossrefFetcher):
    """Science/AAAS journals registered under DOI prefix 10.1126."""

    source_name = "Science"
    doi_prefix = "10.1126"
    venue_fallback = "Science/AAAS journal"

    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__(session=session, journals=Config.SCIENCE_JOURNALS)

