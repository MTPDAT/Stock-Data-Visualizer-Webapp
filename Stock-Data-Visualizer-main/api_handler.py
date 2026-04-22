import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv


load_dotenv()


ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
'''"H0XQD306IFOZECWX"'''
def get_api_key():
    api_key = "H0XQD306IFOZECWX"
    if not api_key:
        print("API key not found in environment variables.")
        return None
    return api_key

def get_function_map():
    return {
        "intraday": "TIME_SERIES_INTRADAY",
        "daily": "TIME_SERIES_DAILY",
        "weekly": "TIME_SERIES_WEEKLY",
        "monthly": "TIME_SERIES_MONTHLY"
    }

def get_output_key_map():
    return {
        "intraday": "Time Series (5min)",
        "daily": "Time Series (Daily)",
        "weekly": "Weekly Time Series",
        "monthly": "Monthly Time Series"
    }

def get_time_series_name_map():
    return {
        "intraday": "Intraday",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly"
    }