import logging
from typing import List

# Import internal Reaplex modules
from src.search.advanced_search import AdvancedSearcher

logger = logging.getLogger(__name__)


class AgentTools:
    """
    Bridge between the Agent/Brain and the Reaplex Body (Search, etc).
    """

    @staticmethod
    async def discover_urls(queries: List[str]) -> List[str]:
        """
        Run searches for each query and return a unique list of found URLs.
        """
        unique_urls = set()
        async with AdvancedSearcher(headless=False, engine="google") as searcher:
            for q in queries:
                print(f"[TOOL] Searching for: {q}")

                html = await searcher.search(q)
                if not html:
                    continue

                # We need to extract URLs from this SERP HTML.
                from src.search.serpapi_formatter import SerpAPIFormatter

                formatter = SerpAPIFormatter(q)
                data = formatter.format(html)

                links = data.get("all_result_links", [])
                for link in links:
                    unique_urls.add(link)

        return list(unique_urls)
