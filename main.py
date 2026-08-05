# main.py - GitHub Actions entry point
import logging
import os
import sys
from datetime import datetime

from arxiv_fetcher import ArxivFetcher
from config import Config
from email_sender import EmailSender


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ArxivDailyDigest:
    def __init__(self):
        self.fetcher = ArxivFetcher()
        self.email_sender = EmailSender()

    def run(self, test_mode=False):
        logger.info("=" * 60)
        logger.info(
            "Starting Arxiv paper digest task - %s",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        try:
            days_back = 0 if test_mode else Config.FETCH_DAYS
            papers = self.fetcher.fetch_recent_papers(days_back=days_back)

            summaries = []
            if papers:
                summaries = [self.fetcher.generate_summary(paper) for paper in papers]
                logger.info("Found %s matching papers", len(papers))
            else:
                logger.info("No matching papers found; sending an empty digest notice")

            success = self.email_sender.send_digest(papers, summaries)
            if not success:
                logger.error("Email sending failed")
                return False

            if papers:
                logger.info("Task completed; sent digest for %s papers", len(papers))
            else:
                logger.info("Task completed; sent empty digest notice")
            return True

        except Exception as exc:
            logger.exception("Task failed: %s", exc)
            return False
        finally:
            logger.info("=" * 60)

    def run_once(self, test_mode=False):
        logger.info("Starting single-run mode for GitHub Actions")
        success = self.run(test_mode=test_mode)
        logger.info("Single-run task finished")
        return success


def main():
    try:
        Config.validate()
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        logger.info("Please check the required environment variables and GitHub Secrets")
        return 1

    digest = ArxivDailyDigest()

    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("RUN_MODE") == "ci":
        logger.info("Detected CI/CD environment; using single-run mode")
        return 0 if digest.run_once(test_mode=False) else 1

    if Config.TEST_MODE:
        logger.info("Running local test mode")
        return 0 if digest.run(test_mode=True) else 1

    logger.info("Running one local digest task")
    return 0 if digest.run_once(test_mode=False) else 1


if __name__ == "__main__":
    sys.exit(main())
