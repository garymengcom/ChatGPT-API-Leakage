"""
This module is used to store the configurations.
"""
import os
import re
from pathlib import Path

from src.validator.serpapi_validator import SerpApiValidator

TMP_DIR = Path(__file__).parent.parent.joinpath("tmp")
LOG_DIR = TMP_DIR.joinpath("logs")
COOKIE_FILE = TMP_DIR.joinpath("cookies.pkl")

DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:12345678@localhost:3306/api_key_hub?charset=utf8mb4")

SELENIUM_REMOTE_ENABLED = os.getenv("SELENIUM_REMOTE_ENABLED", "False").lower() == "true"
SELENIUM_CHROME_BASE_URL = os.getenv("SELENIUM_CHROME_BASE_URL", "http://192.168.1.110:4444")

WEBSITES = [
    {
        "name": "serpapi",
        "regexes": [
            "SERPAPI_KEY\s*=\s*os\.getenv\(['\"]SERPAPI_KEY['\"],\s['\"](\w{64})['\"]",
            "SERPAPI_KEY\s*=\s*['\"]?(\w{64})['\"]?",
            "SERPAPI_API_KEY\s*=\s*os\.getenv\(['\"]SERPAPI_API_KEY['\"],\s['\"](\w{64})['\"]",
            "SERPAPI_API_KEY\s*=\s*['\"]?(\w{64})['\"]?",
        ],
        "validator": SerpApiValidator
    }
]
