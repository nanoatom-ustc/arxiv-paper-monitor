from __future__ import annotations

from typing import Optional

import requests

from config import Config
from crossref_fetcher import CrossrefFetcher


class NatureFetcher(CrossrefFetcher):
    """Nature Portfolio journals registered under DOI prefix 10.1038."""

    source_name = "Nature"
    doi_prefix = "10.1038"
    venue_fallback = "Nature Portfolio journal"

    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__(session=session, journals=Config.NATURE_JOURNALS)

