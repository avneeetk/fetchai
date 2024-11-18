"""
Configuration Management Module

This module handles environment variable loading and centralized configuration settings.
Key functionalities:
- Load API keys securely from .env file
- Define application-wide constants
- Centralize error message definitions
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
SERP_API_KEY = os.getenv("SERP_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Search Settings
MAX_SEARCH_RESULTS = 5
SEARCH_TIMEOUT = 30

# Error Messages
ERROR_MESSAGES = {
    "no_results": "No results found for this query.",
    "api_error": "An error occurred while accessing the API.",
    "invalid_file": "Please upload a valid CSV file.",
    "missing_column": "Please select a valid column for search.",
    "rate_limit": "Rate limit exceeded. Please try again later."
}