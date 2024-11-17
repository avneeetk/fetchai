import requests
import time
from config import SERPAPI_KEY, MAX_SEARCH_RESULTS, SEARCH_TIMEOUT, ERROR_MESSAGES

class SearchHandler:
    def __init__(self):
        self.api_key = SERPAPI_KEY
        self.last_request_time = 0
        self.min_request_interval = 1  

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
            
        self.last_request_time = time.time()

    def search(self, query_entity: str, prompt: str) -> dict:
        """
        Perform search for any entity type
        Args:
            query_entity: The entity to search for (could be company, person, product, etc.)
            prompt: The search prompt with {entity} placeholder
        """
        try:
            self._rate_limit()
            
            # Replace any placeholder with the actual entity
            query = prompt.replace("{entity}", query_entity)
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": MAX_SEARCH_RESULTS,
                "timeout": SEARCH_TIMEOUT
            }
            
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            
            result = response.json()
            search_results = result.get("organic_results", [])
            
            if not search_results:
                return {"status": "no_results", "data": []}
                
            return {"status": "success", "data": search_results}
            
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                return {"status": "error", "message": ERROR_MESSAGES["rate_limit"]}
            return {"status": "error", "message": f"Search error: {str(e)}"}
            
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    def batch_search(self, entities: list, prompt: str) -> dict:
        """
        Perform batch search for multiple entities
        Args:
            entities: List of entities to search for
            prompt: Search prompt with {entity} placeholder
        """
        results = {}
        for entity in entities:
            results[entity] = self.search(entity, prompt)
            time.sleep(self.min_request_interval)  # Basic rate limiting
                
        return results