import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def classify(payload: Dict[str, Any]) -> str:
    """
    Classifies a job payload into one of three types: 'html', 'browser', or 'skip'.

    Classification is based on:
    - Explicit instructions in payload (render_js flag)
    - File extensions to skip
    - Heuristic domains for JS-heavy/browser-driven sites
    - Defaults to static HTML processing

    Args:
        payload (Dict[str, Any]): The job payload. Must contain 'url'.

    Returns:
        str: One of 'html', 'browser', or 'skip'.
    """
    url = payload.get("url", "")
    if not url:
        logger.warning("Classifier: Payload missing 'url' key. Skipping job.")
        return "skip"

    url_lower = url.lower()

    # Rule 1: Explicit render_js flag
    if payload.get("render_js") is True:
        logger.debug(f"Classifier: {url} -> browser (render_js=True)")
        return "browser"

    # Rule 2: Skip non-HTML or binary resources
    skip_extensions = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".exe")
    if url_lower.endswith(skip_extensions):
        logger.info(f"Classifier: {url} -> skip (excluded extension)")
        return "skip"

    # Rule 3: Heuristic domains that require JS/browser
    browser_domains = [
        "twitter.com",
        "instagram.com",
        "facebook.com",
        "tiktok.com",
        "youtube.com",
    ]
    for domain in browser_domains:
        if domain in url_lower:
            logger.debug(f"Classifier: {url} -> browser (matched domain {domain})")
            return "browser"

    # Default: static HTML
    logger.debug(f"Classifier: {url} -> html (default)")
    return "html"
