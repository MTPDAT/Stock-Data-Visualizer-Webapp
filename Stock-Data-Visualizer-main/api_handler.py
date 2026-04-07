import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv


load_dotenv()


ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

def get_api_key():
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        print("API key not found.")
        return None
    return api_key

def get_function_map():
    return {
        "1": "TIME_SERIES_INTRADAY",
        "2": "TIME_SERIES_DAILY",
        "3": "TIME_SERIES_WEEKLY",
        "4": "TIME_SERIES_MONTHLY"
    }

def get_output_key_map():
    return {
        "1": "Time Series (5min)",
        "2": "Time Series (Daily)",
        "3": "Weekly Time Series",
        "4": "Monthly Time Series"
    }

def get_time_series_name_map():
    return {
        "1": "Intraday",
        "2": "Daily",
        "3": "Weekly",
        "4": "Monthly"
    }