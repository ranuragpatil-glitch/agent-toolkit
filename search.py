# search.py
from ddgs import DDGS
from config import MAX_SEARCH_RESULTS


def web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> dict:
    """DDGS se web search karo. Returns {ok, results}."""
    try:
        results = list(DDGS().text(query, max_results=max_results))
        simplified = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
        return {"ok": True, "results": simplified}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def fetch_page(url: str, timeout: int = 15000) -> dict:
    """
    Playwright se page fetch karo (JS-rendered bhi).
    Note: Sirf tab use karo jab snippet kaafi na ho.
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            content = page.inner_text("body")
            browser.close()
        return {"ok": True, "content": content[:5000]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}