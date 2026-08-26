import os

try:
    from dotenv import load_dotenv
except ImportError:  # Environment variables still work when python-dotenv is unavailable.
    def load_dotenv():
        return False

load_dotenv()


def _csv_env(name, default=""):
    value = os.getenv(name, default)
    return [item.strip().strip('"').strip("'") for item in value.split(",") if item.strip()]


class Config:
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

    FETCH_DAYS = int(os.getenv("FETCH_DAYS", 1))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", 50))

    SEARCH_KEYWORDS = _csv_env("SEARCH_KEYWORDS") or [
        "Rydberg atom",
        "magneto-optical trap",
        "optical tweezers",
        "nanophotonics",
    ]

    # Keep arXiv enabled and add APS by default. Existing deployments can restore
    # arXiv-only behavior with SEARCH_SOURCES=arxiv.
    SEARCH_SOURCES = [source.lower() for source in _csv_env("SEARCH_SOURCES", "arxiv,aps")]
    SEARCH_CATEGORIES = _csv_env("SEARCH_CATEGORIES")

    # Optional APS journal title/abbreviation filter, e.g. "Physical Review A,PRL".
    # An empty value covers all APS journal articles registered under DOI prefix 10.1103.
    APS_JOURNALS = _csv_env("APS_JOURNALS")
    CROSSREF_MAILTO = os.getenv("CROSSREF_MAILTO", "").strip()

    SCHEDULE_TIME = "09:00"
    TEST_MODE = False
    LOG_FILE = "logs/paper_digest.log"

    @classmethod
    def validate(cls):
        if not cls.EMAIL_SENDER or not cls.EMAIL_PASSWORD or not cls.RECIPIENT_EMAIL:
            raise ValueError("邮箱配置不完整，请检查 .env 文件或 GitHub Secrets")

        supported_sources = {"arxiv", "aps"}
        unknown_sources = set(cls.SEARCH_SOURCES) - supported_sources
        if unknown_sources:
            raise ValueError(f"不支持的数据源: {', '.join(sorted(unknown_sources))}")
        if not cls.SEARCH_SOURCES:
            raise ValueError("SEARCH_SOURCES 至少需要包含 arxiv 或 aps")
        return True

