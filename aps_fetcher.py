from __future__ import annotations

from typing import Optional

import requests

from config import Config
from crossref_fetcher import CrossrefFetcher


class APSFetcher(CrossrefFetcher):
    """APS journals registered under DOI prefix 10.1103."""

    source_name = "APS"
    doi_prefix = "10.1103"
    venue_fallback = "APS journal"

    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__(
            session=session,
            journals=Config.APS_JOURNALS,
            excluded_journals=Config.APS_EXCLUDE_JOURNALS,
        )

