import logging
from datetime import datetime, timedelta
from typing import Dict, List

import arxiv

from config import Config
from paper_utils import (
    find_matching_keywords,
    generate_summary,
    keyword_aliases,
    truncate_text,
)

logger = logging.getLogger(__name__)


class ArxivFetcher:
    source_name = "arXiv"

    def __init__(self):
        self.client = arxiv.Client()
        self.keywords = Config.SEARCH_KEYWORDS

    def fetch_recent_papers(self, days_back: int = 1, max_results: int = 50) -> List[Dict]:
        """Fetch recent arXiv papers matching the configured terms and categories."""
        try:
            query_terms = []
            for keyword in self.keywords:
                query_terms.extend(keyword_aliases(keyword))
            keyword_query = " OR ".join([f'all:"{term}"' for term in query_terms])
            query = f"({keyword_query})"

            if Config.SEARCH_CATEGORIES:
                cat_query = " OR ".join([f"cat:{cat}" for cat in Config.SEARCH_CATEGORIES])
                query += f" AND ({cat_query})"

            if days_back > 0:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                date_range = f"[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
                query += f" AND submittedDate:{date_range}"

            logger.info("arXiv 搜索查询: %s", query)
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []
            for result in self.client.results(search):
                matched_kws = find_matching_keywords(
                    result.title, result.summary, self.keywords
                )
                if not matched_kws:
                    logger.info("跳过未在标题或摘要中严格命中主题的 arXiv 论文: %s", result.title[:60])
                    continue

                paper = {
                    "id": result.get_short_id(),
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "pdf_url": result.pdf_url,
                    "published": result.published.strftime("%Y-%m-%d %H:%M"),
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                    "arxiv_url": result.entry_id,
                    "article_url": result.entry_id,
                    "source": self.source_name,
                    "journal": "",
                    "doi": result.doi or "",
                    "matched_keywords": matched_kws,
                }
                papers.append(paper)
                logger.info("找到 arXiv 论文: %s", paper["title"][:60])

            logger.info("arXiv 共找到 %s 篇相关论文", len(papers))
            return papers
        except Exception as exc:
            logger.error("获取 arXiv 论文失败: %s", exc, exc_info=True)
            return []

    def generate_summary(self, paper: Dict) -> str:
        """Backward-compatible summary API."""
        return generate_summary(paper)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Backward-compatible text truncation API."""
        return truncate_text(text, max_length)
