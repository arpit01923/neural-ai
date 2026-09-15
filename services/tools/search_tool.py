import re
from html import unescape
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def normalize_result_url(url: str) -> str:
    stripped = url.strip()
    if not stripped:
        return stripped

    if stripped.startswith("//"):
        stripped = f"https:{stripped}"

    parsed = urlparse(stripped)
    if parsed.netloc.endswith("duckduckgo.com"):
        if parsed.path.startswith("/l/"):
            params = parse_qs(parsed.query)
            if "uddg" in params and params["uddg"]:
                return normalize_result_url(unquote(params["uddg"][0]))
        return ""

    if not parsed.scheme:
        return f"https://{stripped}"

    return stripped


def _strip_tags(raw_html: str) -> str:
    clean = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<style.*?</style>", " ", clean, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def search_web(query: str, max_results: int = 5) -> list[dict[str, object]]:
    """Search the web and return top results with normalized URLs."""
    encoded_query = quote_plus(query.strip())
    responses = [
        requests.get(
            f"https://lite.duckduckgo.com/lite/?q={encoded_query}",
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        ),
        requests.get(
            f"https://duckduckgo.com/html/?q={encoded_query}",
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        ),
    ]

    results: list[dict[str, object]] = []
    for response in responses:
        try:
            response.raise_for_status()
        except requests.HTTPError:
            continue

        match_blocks = re.findall(
            r"<a[^>]+class=['\"]result-link['\"][^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
            response.text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if not match_blocks:
            match_blocks = re.findall(
                r"<a[^>]+class=['\"]result__a['\"][^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
                response.text,
                flags=re.DOTALL | re.IGNORECASE,
            )

        for index, match in enumerate(match_blocks[:max_results], start=1):
            url = match[0]
            title_html = match[1] if len(match) > 1 else ""
            snippet_html = match[2] if len(match) > 2 else ""
            normalized_url = normalize_result_url(url)
            if not normalized_url:
                continue

            title = _strip_tags(title_html)
            snippet = _strip_tags(snippet_html)
            if not title:
                title = normalized_url
            results.append(
                {
                    "title": title,
                    "url": normalized_url,
                    "content": snippet or "No excerpt available.",
                    "score": round(max(0.45, 0.95 - (index * 0.08)), 2),
                }
            )

        if results:
            break

    print(f"Search results for query '{query}': {len(results)}")
    return results


def fetch_page_text(url: str) -> str:
    """Fetch a page and return a compact text body for summarization."""
    normalized_url = normalize_result_url(url)
    if not normalized_url:
        return ""

    try:
        response = requests.get(normalized_url, headers={"User-Agent": USER_AGENT}, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    return _strip_tags(response.text)[:4000]
