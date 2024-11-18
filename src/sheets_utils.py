"""
Google Sheets Interaction Utility

Provides a robust interface for interacting with Google Sheets:
- Handles OAuth2 authentication
- Reads sheet data into pandas DataFrames
- Extracts sheet IDs from URLs
- Provides error handling for sheet operations

Security and Error Handling Considerations:
- Uses service account credentials
- Validates sheet URLs and data ranges
- Implements comprehensive error logging
"""

import pandas as pd
import re
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os


class SheetsUtils:
    def __init__(self, credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
        """
        Initialize the SheetsUtils class with credentials from a JSON file.
        
        Args:
            credentials_path (str): Path to the credentials JSON file
        """
        self.credentials_path = credentials_path
        self.service = None
        self.init_service()
        
    def init_service(self) -> None:
        """Initialize the Google Sheets service with credentials from the JSON file."""
        try:
            credentials = self.create_google_credentials()
            self.service = build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            st.error(f"Failed to initialize Sheets API service: {str(e)}")
            self.service = None
            raise RuntimeError("Failed to initialize Google Sheets service. Check your credentials and try again.")

    def create_google_credentials(self) -> Credentials:
        """
        Create Google credentials from the JSON file.
        
        Returns:
            Credentials: Google OAuth2 credentials object
        """
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )
            return credentials
        except Exception as e:
            st.error(f"Error creating Google credentials: {str(e)}")
            raise RuntimeError("Failed to create Google credentials. Check your service account configuration.")

    def read_sheet(self, sheet_id: str, range_name: str) -> pd.DataFrame:
        """
    Retrieve and parse data from a specified Google Sheet.

    Args:
        sheet_id (str): Unique identifier for the Google Sheet
        range_name (str): Specific cell range to extract (e.g., "Sheet1!A1:D10")

    Returns:
        pd.DataFrame: Parsed sheet data with first row as headers

    Raises:
        RuntimeError: If sheet cannot be accessed or parsed
    """
        
        if not self.service:
            raise RuntimeError("Google Sheets API service is not initialized.")

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            if not values:
                raise RuntimeError(f"No data found in range {range_name}")
                
            if len(values) < 2:
                raise RuntimeError("Sheet must contain at least a header row and one data row")

            df = pd.DataFrame(values[1:], columns=values[0])
            df.columns = df.columns.str.strip()
            
            return df

        except Exception as e:
            st.error(f"Error reading from Google Sheet: {str(e)}")
            raise RuntimeError(f"Failed to read sheet: {str(e)}")

    @staticmethod
    def get_sheet_id_from_url(url: str) -> str:
        """
        Extract the Google Sheet ID from its URL.
        
        Args:
            url (str): The Google Sheet URL
            
        Returns:
            str: The extracted Sheet ID
            
        Raises:
            ValueError: If the URL is invalid
        """
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Google Sheets URL. Please check the URL format.")