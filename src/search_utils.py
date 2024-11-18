"""
Search Handling Module

Provides flexible search capabilities:
- Interfaces with SerpAPI for web searches
- Implements rate limiting to prevent API abuse
- Supports batch and individual entity searches
- Standardizes search result processing

Performance and Reliability Features:
- Configurable search parameters
- Timeout and result limit management
- Comprehensive error handling
"""

import requests
import time
from config import SERP_API_KEY
import logging
from config import MAX_SEARCH_RESULTS, SEARCH_TIMEOUT
class SearchHandler:
    def __init__(self, api_key=SERP_API_KEY, search_engine="google", min_request_interval=1):
        self.api_key = api_key
        self.search_engine = search_engine
        self.min_request_interval = min_request_interval
        self.last_request_time = 0

    def _rate_limit(self):
        """
    Implement adaptive rate limiting:
    - Prevent overwhelming external APIs
    - Ensure consistent, respectful API usage
    - Dynamically adjust request intervals
    """
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def search(self, query_entity: str, prompt: str) -> dict:
        """
        Perform search for any entity type.
        Args:
            query_entity: The entity to search for (could be company, person, product, etc.)
            prompt: The search prompt with {entity} placeholder.
        """
        try:
            self._rate_limit()

            # Replace any placeholder with the actual entity
            query = prompt.replace("{entity}", query_entity)

            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": self.search_engine,
                "num": MAX_SEARCH_RESULTS,
                "timeout": SEARCH_TIMEOUT
            }

            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()

            result = response.json()
            search_results = result.get("organic_results", [])  # Ensure this is a list

            if not isinstance(search_results, list):  # Validate response
                logging.error("Unexpected structure for search results")
                return {"status": "error", "data": [], "message": "Invalid search results format"}

            return {"status": "success", "data": search_results}

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            return {"status": "error", "message": f"Search error: {str(e)}"}

        except Exception as e:
            logging.error(f"Unexpected search error: {e}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    def batch_search(self, entities, prompt):
        """
        Perform searches for multiple entities using the same prompt.
        
        Args: 
            entities (list): List of entities to search for.
            prompt (str): Search query template with a placeholder {entity}.
        
        Returns:
            dict: A dictionary of search results for each entity.
        """
        return {entity: self.search(entity, prompt) for entity in entities}
