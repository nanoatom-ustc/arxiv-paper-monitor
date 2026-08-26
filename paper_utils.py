from typing import Dict


def truncate_text(text: str, max_length: int) -> str:
    text = (text or "").replace("\n", " ")
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated


def generate_summary(paper: Dict) -> str:
    abstract = paper.get("abstract", "")
    authors = paper.get("authors", [])
    source = paper.get("source", "arXiv")
    venue = paper.get("journal") or paper.get("primary_category") or "未知"
    article_url = paper.get("article_url") or paper.get("arxiv_url") or paper.get("pdf_url", "")

    summary_lines = [
        "=" * 60,
        f"📄 标题: {paper.get('title', '')}",
        "",
        f"👥 作者: {', '.join(authors[:3])}{' 等' if len(authors) > 3 else ''}",
        f"📅 发布时间: {paper.get('published', '')}",
        f"🗂️ 来源: {source} | 期刊/分类: {venue}",
        f"🏷️ 命中关键词: {', '.join(paper.get('matched_keywords', ['未知']))}",
        "",
        "📝 摘要:",
        truncate_text(abstract, 800) + ("..." if len(abstract) > 800 else ""),
        "",
        "🔗 链接:",
        f"文章: {article_url}",
    ]
    if paper.get("pdf_url"):
        summary_lines.append(f"PDF: {paper['pdf_url']}")
    summary_lines.extend(["=" * 60, ""])
    return "\n".join(summary_lines)

