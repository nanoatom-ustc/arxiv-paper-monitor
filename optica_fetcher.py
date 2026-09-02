from __future__ import annotations

from typing import Optional

import requests

from config import Config
from crossref_fetcher import CrossrefFetcher


class OpticaFetcher(CrossrefFetcher):
    """Optica Publishing Group journals registered under DOI prefix 10.1364."""

    source_name = "Optica"
    doi_prefix = "10.1364"
    venue_fallback = "Optica Publishing Group journal"

    def __init__(self, session: Optional[requests.Session] = None):
        super().__init__(session=session, journals=Config.OPTICA_JOURNALS)
