"""
This module is used to store the configurations.
"""
import os
import re
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.joinpath("tmp").joinpath("logs")

SELENIUM_REMOTE_ENABLED = os.getenv("SELENIUM_REMOTE_ENABLED", "False").lower() == "true"
SELENIUM_CHROME_BASE_URL = os.getenv("SELENIUM_CHROME_BASE_URL", "http://192.168.1.110:4444")

# https://github.com/github-linguist/linguist/blob/main/lib/linguist/languages.yml
LANGUAGES = [
    "Dotenv",
    "Text",
    "JavaScript",
    "Python",
    "TypeScript",
    "Dockerfile",
    "Markdown",
    '"Jupyter Notebook"',
    "Shell",
    "Java",
    "Go",
    "C%2B%2B",
    "PHP",
    "Ruby",
    "C%23",
    "Swift",
    "Rust",
    "Kotlin",
    "Perl",
    "Scala",
]

# regex, have_many_results, result_too_lang
REGEX_LIST = [
    (re.compile(r"sk-proj-[A-Za-z0-9-_]{74}T3BlbkFJ[A-Za-z0-9-_]{73}A"), True, True),  # Named Project API Key (no matter normal or restricted)
    (re.compile(r"sk-proj-[A-Za-z0-9-_]{58}T3BlbkFJ[A-Za-z0-9-_]{58}"), True, True),  # Old Project API Key
    (re.compile(r"sk-svcacct-[A-Za-z0-9-_]+T3BlbkFJ[A-Za-z0-9-_]+"), False, False),  # Service Account Key
    (re.compile(r"sk-proj-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}"), True, False),
    (re.compile(r"sk-[a-zA-Z0-9]{48}"), True, False),  # Deprecated by OpenAI
]
