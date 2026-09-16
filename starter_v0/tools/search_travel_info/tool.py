from __future__ import annotations

import os
import re
from typing import Any


MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")


ALLOWED_CATEGORIES = {
    "general",
    "attraction",
    "food",
    "hotel",
    "transport",
    "event",
}


def search_travel_info(
    query: str,
    destination: str = "",
    category: str = "general",
    max_results: int = 5,
) -> dict[str, Any]:
    """
    Search current travel information using OpenAI's web search tool.

    Args:
        query: What the user wants to know.
        destination: City, region, or country related to the request.
        category: general, attraction, food, hotel, transport, or event.
        max_results: Number of web results, from 1 to 10.

    Returns:
        Structured travel search results for the chatbot.
    """

    query = query.strip()
    destination = destination.strip()
    category = category.strip().lower()

    if not query:
        return {
            "error": "missing_query",
            "message": "A search query is required.",
        }

    if category not in ALLOWED_CATEGORIES:
        return {
            "error": "invalid_category",
            "message": (
                f"Unsupported category '{category}'. "
                f"Use one of: {sorted(ALLOWED_CATEGORIES)}"
            ),
        }

    max_results = max(1, min(int(max_results), 10))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "error": "missing_api_key",
            "message": "OPENAI_API_KEY is not configured.",
        }

    # Add travel context so the web search looks specifically for travel information.
    search_parts = [query]

    if destination:
        search_parts.append(f"in {destination}")

    search_query = " ".join(search_parts)

    try:
        from openai import OpenAI
    except ImportError as exc:
        return {
            "error": "missing_dependency",
            "message": f"Install the openai package first: {exc}",
        }

    base_url = os.getenv("BASE_API_URL") or None
    model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.responses.create(
            model=model,
            input=search_query,
            tools=[{"type": "web_search"}],
        )
    except Exception as exc:
        return {
            "error": "openai_web_search_failed",
            "message": str(exc),
        }

    results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            for annotation in getattr(content, "annotations", None) or []:
                if getattr(annotation, "type", None) != "url_citation":
                    continue
                url = getattr(annotation, "url", None)
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                results.append({"title": getattr(annotation, "title", None), "url": url})
                if len(results) >= max_results:
                    break

    answer = getattr(response, "output_text", None)

    # Some gateways/models cite sources as inline markdown links instead of
    # structured annotations. Fall back to parsing those so `results` is
    # still populated with real sources from this response.
    if not results and answer:
        for title, url in MARKDOWN_LINK_PATTERN.findall(answer):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            results.append({"title": title, "url": url})
            if len(results) >= max_results:
                break

    return {
        "query": query,
        "search_query": search_query,
        "destination": destination or None,
        "category": category,
        "answer": answer,
        "results": results,
        "result_count": len(results),
    }
