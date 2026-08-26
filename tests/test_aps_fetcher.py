import unittest
from unittest.mock import patch

from aps_fetcher import APSFetcher


class FakeResponse:
    def __init__(self, items):
        self.items = items

    def raise_for_status(self):
        return None

    def json(self):
        return {"message": {"items": self.items}}


class FakeSession:
    def __init__(self, items):
        self.items = items
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.items)


APS_ITEM = {
    "DOI": "10.1103/PhysRevLett.123.456",
    "title": ["Integrated photonics with trapped atoms"],
    "container-title": ["Physical Review Letters"],
    "abstract": "<jats:p>An <b>integrated photonics</b> result.</jats:p>",
    "author": [{"given": "Ada", "family": "Lovelace"}],
    "published-online": {"date-parts": [[2026, 8, 25]]},
    "URL": "https://doi.org/10.1103/PhysRevLett.123.456",
    "link": [{"content-type": "application/pdf", "URL": "https://example.test/paper.pdf"}],
    "subject": ["Physics"],
}


class APSFetcherTests(unittest.TestCase):
    @patch("aps_fetcher.Config.SEARCH_KEYWORDS", ["integrated photonics", "trapped atoms"])
    @patch("aps_fetcher.Config.APS_JOURNALS", [])
    def test_fetch_normalises_and_deduplicates_crossref_results(self):
        session = FakeSession([APS_ITEM])
        fetcher = APSFetcher(session=session)

        papers = fetcher.fetch_recent_papers(days_back=2, max_results=10)

        self.assertEqual(len(papers), 1)
        paper = papers[0]
        self.assertEqual(paper["source"], "APS")
        self.assertEqual(paper["journal"], "Physical Review Letters")
        self.assertEqual(paper["authors"], ["Ada Lovelace"])
        self.assertEqual(paper["pdf_url"], "https://example.test/paper.pdf")
        self.assertNotIn("<jats:p>", paper["abstract"])
        self.assertEqual(
            set(paper["matched_keywords"]), {"integrated photonics", "trapped atoms"}
        )
        self.assertEqual(len(session.calls), 2)
        self.assertIn("type:journal-article", session.calls[0][1]["params"]["filter"])
        self.assertIn("from-pub-date:", session.calls[0][1]["params"]["filter"])

    @patch("aps_fetcher.Config.SEARCH_KEYWORDS", ["integrated photonics"])
    @patch("aps_fetcher.Config.APS_JOURNALS", ["PRA"])
    def test_journal_filter_excludes_nonmatching_journal(self):
        fetcher = APSFetcher(session=FakeSession([APS_ITEM]))
        self.assertEqual(fetcher.fetch_recent_papers(days_back=1, max_results=10), [])

    @patch("aps_fetcher.Config.SEARCH_KEYWORDS", ["integrated photonics"])
    @patch("aps_fetcher.Config.APS_JOURNALS", ["PRL"])
    def test_journal_filter_accepts_common_acronym(self):
        fetcher = APSFetcher(session=FakeSession([APS_ITEM]))
        self.assertEqual(len(fetcher.fetch_recent_papers(days_back=1, max_results=10)), 1)


if __name__ == "__main__":
    unittest.main()

