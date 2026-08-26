from __future__ import annotations

import logging
import html
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

from config import Config
from paper_utils import generate_summary

logger = logging.getLogger(__name__)


class APSFetcher:
    """Fetch APS journal articles through Crossref's public API.

    APS registers its journal content under DOI prefix 10.1103. Crossref therefore
    provides broad APS coverage without scraping individual journal sites or
    requiring an API key.
    """

    source_name = "APS"
    api_url = "https://api.crossref.org/prefixes/10.1103/works"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.keywords = Config.SEARCH_KEYWORDS
        self.journals = Config.APS_JOURNALS

    def fetch_recent_papers(self, days_back: int = 1, max_results: int = 50) -> List[Dict]:
        if max_results <= 0:
            return []

        papers_by_doi = {}
        rows = min(max(max_results, 20), 100)
        for keyword in self.keywords:
            try:
                for item in self._fetch_keyword(keyword, days_back, rows):
                    paper = self._normalise_item(item, keyword)
                    if paper and self._journal_allowed(paper["journal"]):
                        existing = papers_by_doi.get(paper["doi"])
                        if existing:
                            existing["matched_keywords"] = sorted(
                                set(existing["matched_keywords"] + paper["matched_keywords"])
                            )
                        else:
                            papers_by_doi[paper["doi"]] = paper
            except requests.RequestException as exc:
                logger.warning("APS/Crossref 查询失败（关键词 %s）: %s", keyword, exc)
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("APS/Crossref 响应解析失败（关键词 %s）: %s", keyword, exc)

        papers = sorted(papers_by_doi.values(), key=lambda paper: paper["published"], reverse=True)
        result = papers[:max_results]
        logger.info("APS 共找到 %s 篇相关论文", len(result))
        return result

    def _fetch_keyword(self, keyword: str, days_back: int, rows: int) -> List[dict]:
        filters = ["type:journal-article"]
        if days_back > 0:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            filters.extend([
                f"from-pub-date:{start_date.isoformat()}",
                f"until-pub-date:{end_date.isoformat()}",
            ])

        params = {
            "query.bibliographic": keyword,
            "filter": ",".join(filters),
            "rows": rows,
            "sort": "published",
            "order": "desc",
        }
        headers = {"User-Agent": self._user_agent()}
        response = self.session.get(self.api_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["message"]["items"]

    def _normalise_item(self, item: dict, queried_keyword: str) -> Optional[Dict]:
        doi = (item.get("DOI") or "").strip()
        title = " ".join(item.get("title") or []).strip()
        if not doi or not title:
            return None

        journal = " ".join(item.get("container-title") or []).strip()
        abstract = self._clean_abstract(item.get("abstract", ""))
        authors = [self._author_name(author) for author in item.get("author", [])]
        authors = [author for author in authors if author]
        published = self._published_date(item)
        article_url = item.get("URL") or f"https://doi.org/{doi}"
        pdf_url = self._pdf_url(item)

        searchable = " ".join(
            [title, abstract, journal, " ".join(authors), " ".join(item.get("subject") or [])]
        ).lower()
        matched = [kw.strip() for kw in self.keywords if kw.strip().lower() in searchable]

        return {
            "id": doi,
            "doi": doi,
            "title": title,
            "authors": authors,
            "abstract": abstract or "Crossref 未提供摘要，请通过文章链接查看。",
            "pdf_url": pdf_url,
            "published": published,
            "primary_category": journal or "APS journal",
            "categories": item.get("subject") or [],
            "arxiv_url": article_url,
            "article_url": article_url,
            "source": self.source_name,
            "journal": journal or "APS journal",
            "matched_keywords": matched or [queried_keyword.strip()],
        }

    def _journal_allowed(self, journal: str) -> bool:
        if not self.journals:
            return True
        normalised = re.sub(r"[^a-z0-9]", "", journal.lower())
        acronym = "".join(
            word[0] for word in re.findall(r"[a-z0-9]+", journal.lower()) if word
        )
        return any(
            (
                re.sub(r"[^a-z0-9]", "", configured.lower()) in normalised
                or re.sub(r"[^a-z0-9]", "", configured.lower()) == acronym
            )
            for configured in self.journals
        )

    @staticmethod
    def _clean_abstract(value: str) -> str:
        if not value:
            return ""
        without_tags = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()

    @staticmethod
    def _author_name(author: dict) -> str:
        if author.get("name"):
            return author["name"].strip()
        return " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()

    @staticmethod
    def _published_date(item: dict) -> str:
        for key in ("published-online", "published-print", "published", "created"):
            date_parts = item.get(key, {}).get("date-parts", [])
            if date_parts and date_parts[0]:
                parts = list(date_parts[0]) + [1, 1]
                return f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d} 00:00"
        return ""

    @staticmethod
    def _pdf_url(item: dict) -> str:
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                return link.get("URL", "")
        return ""

    @staticmethod
    def generate_summary(paper: Dict) -> str:
        return generate_summary(paper)

    @staticmethod
    def _user_agent() -> str:
        contact = f"; mailto:{Config.CROSSREF_MAILTO}" if Config.CROSSREF_MAILTO else ""
        return f"arxiv-paper-monitor/2.0 ({contact.lstrip('; ')})" if contact else "arxiv-paper-monitor/2.0"

