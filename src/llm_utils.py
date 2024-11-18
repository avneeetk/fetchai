from groq import Groq
from config import GROQ_API_KEY, ERROR_MESSAGES
import logging

class LLMHandler:
    def __init__(self):
        self.client = Groq(api_key="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")
        self.model = "llama3-8b-8192"

    def extract_information(self, search_results: dict, extraction_prompt: str) -> dict:
        """
        Extract information from search results using LLM.
        Args:
            search_results: Dictionary containing search results.
            extraction_prompt: Prompt for information extraction.
        """
        try:
            # Check if search was successful
            if search_results["status"] != "success" or not search_results.get("data"):
                return {"status": "error", "message": "No valid search results to process."}

            # Combine snippets from search results
            search_text = " ".join([
                result.get('snippet', '') for result in search_results["data"]
            ]).strip()

            if not search_text:
                return {"status": "error", "message": "No relevant search snippets found."}

            # Prepare LLM prompt
            system_prompt = """
            You are an AI assistant that extracts specific information from search results.
            Only extract the exact information requested. If the information is not found,
            say "Information not found." Be concise and accurate.
            """

            user_prompt = f"{extraction_prompt}\n\nSearch Results:\n{search_text}"

            # Call the LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )

            # Validate LLM response
            if not response or not response.choices:
                return {"status": "error", "message": "LLM did not return a valid response."}

            extracted_info = response.choices[0].message.content.strip()

            # Check if the response contains relevant data
            if not extracted_info or extracted_info.lower() == "information not found.":
                return {"status": "error", "message": "No relevant data extracted by LLM."}

            return {
                "status": "success",
                "data": extracted_info
            }

        except Exception as e:
            logging.error(f"LLMHandler Error: {str(e)}")
            return {"status": "error", "message": f"LLM processing error: {str(e)}"}

    def batch_extract(self, search_results_batch: dict, extraction_prompt: str) -> dict:
        """
        Process batch of search results.
        Args:
            search_results_batch: Dictionary of search results for multiple entities.
            extraction_prompt: Prompt for information extraction.
        """
        results = {}
        for entity, search_result in search_results_batch.items():
            results[entity] = self.extract_information(search_result, extraction_prompt)
        return results
