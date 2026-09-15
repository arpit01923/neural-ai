from services.research_service import build_research_report
from services.tools.search_tool import normalize_result_url


def test_normalize_result_url_adds_https_scheme_for_duckduckgo_redirect_links():
    normalized = normalize_result_url("//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage")

    assert normalized == "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage"


def test_build_research_report_returns_structured_response():
    sources = [
        {
            "title": "React overview",
            "url": "https://example.com/react",
            "content": "React remains a popular front-end library with a large ecosystem and strong developer experience.",
            "score": 0.92,
        },
        {
            "title": "Angular overview",
            "url": "https://example.com/angular",
            "content": "Angular remains an enterprise-focused framework with full platform tooling and strong typing support.",
            "score": 0.84,
        },
        {
            "title": "Angular overview duplicate",
            "url": "https://example.com/angular-duplicate",
            "content": "Angular remains an enterprise-focused framework with full platform tooling and strong typing support.",
            "score": 0.79,
        },
    ]

    report = build_research_report("Compare React vs Angular in 2026", sources)

    assert report["title"] == "Compare React vs Angular in 2026"
    assert report["summary"]
    assert len(report["key_points"]) >= 2
    assert len(report["sources"]) == 2
