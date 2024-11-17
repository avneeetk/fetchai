from groq import Groq
from config import GROQ_API_KEY, ERROR_MESSAGES

class LLMHandler:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama3-8b-8192"

    def extract_information(self, search_results: dict, extraction_prompt: str) -> dict:
        """
        Extract information from search results using LLM
        Args:
            search_results: Dictionary containing search results
            extraction_prompt: Prompt for information extraction
        """
        try:
            if search_results["status"] != "success":
                return {"status": "error", "message": search_results.get("message", "Search failed")}

            # Combine all search snippets into one text
            search_text = " ".join([
                result.get('snippet', '') for result in search_results["data"]
            ])

            # Create a clear prompt for the LLM
            system_prompt = """
            You are an AI assistant that extracts specific information from search results.
            Only extract the exact information requested. If the information is not found,
            say "Information not found." Be concise and accurate.
            """

            # Get response from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{extraction_prompt}\n\nSearch Results:\n{search_text}"}
                ],
                temperature=0.5,
                max_tokens=100
            )

            extracted_info = response.choices[0].message.content.strip()
            
            return {
                "status": "success",
                "data": extracted_info
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"LLM processing error: {str(e)}"
            }

    def batch_extract(self, search_results_batch: dict, extraction_prompt: str) -> dict:
        """
        Process batch of search results
        Args:
            search_results_batch: Dictionary of search results for multiple entities
            extraction_prompt: Prompt for information extraction
        """
        results = {}
        for entity, search_result in search_results_batch.items():
            results[entity] = self.extract_information(search_result, extraction_prompt)
        
        return results
