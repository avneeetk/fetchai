import pandas as pd
import re
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class SheetsUtils:
    def __init__(self, creds: Credentials):
        self.service = build('sheets', 'v4', credentials=creds)

    def read_sheet(self, sheet_id: str, range_name: str) -> pd.DataFrame:
        """Read data from Google Sheet"""
        try:
            if not self.service:
                return pd.DataFrame()

            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            if not values or len(values) < 2:
                return pd.DataFrame()  # No data or header

            # Convert to DataFrame
            return pd.DataFrame(values[1:], columns=values[0])

        except Exception as e:
            logging.error(f"Error reading from Google Sheet: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_sheet_id_from_url(url: str) -> str:
        """Extract the sheet ID from the Google Sheets URL"""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid Google Sheets URL")