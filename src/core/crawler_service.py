import logging
import re
import time
from typing import Pattern, List
from urllib.parse import urljoin
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import rich
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from bs4 import BeautifulSoup

from src.core.configs import SELENIUM_REMOTE_ENABLED, SELENIUM_CHROME_BASE_URL, COOKIE_FILE
from src.db.dao import ApiKeyDao
from src.manager.cookie_manager import CookieManager
from src.manager.progress_manager import ProgressManager
from src.core.models import UrlRegex


class APIKeyLeakageScanner:
    def __init__(self, website: dict):
        self.progress = ProgressManager()
        self.driver: webdriver.Chrome | None = None
        self.cookies: CookieManager | None = None

        self.candidate_urls = []
        self.website_name = website["name"]
        self.validator = website["validator"]()
        self.regexes: List[Pattern] = [re.compile(r, re.IGNORECASE) for r in website["regexes"]]
        self.url_regexes: List[UrlRegex] = [
            UrlRegex(regex=r, url=f"https://github.com/search?q=(/{r.pattern}/)&type=code&ref=advsearch")
            for r in self.regexes
        ]

    def login_to_github(self):
        """
        Login to GitHub
        """
        rich.print("🌍 Opening Chrome ...")

        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")

        if SELENIUM_REMOTE_ENABLED:
            self.driver = webdriver.Remote(urljoin(SELENIUM_CHROME_BASE_URL, '/wd/hub'), options=options)
        else:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.implicitly_wait(3)

        self.cookies = CookieManager(self.driver)
        self.driver.get("https://github.com/login")

        if not COOKIE_FILE.exists():
            rich.print("🤗 No cookies found, please login to GitHub first")
            input("Press Enter after you logged in [Enter]? ")
            self.cookies.save()
        else:
            rich.print("🍪 Cookies found, loading cookies")
            self.cookies.load()

        self.cookies.verify_user_login()

    def _process_url(self, url_regex: UrlRegex):
        """
        Process a search query url
        """
        if self.driver is None:
            raise ValueError("Driver is not initialized")

        self.driver.get(url_regex.url)

        while True:  # Loop until all the pages are processed
            # If current webpage is reached the rate limit, then wait for 30 seconds
            if self.driver.find_elements(by=By.XPATH,
                                         value="//*[contains(text(), 'You have exceeded a secondary rate limit')]"):
                for _ in tqdm(range(30), desc="⏳ Rate limit reached, waiting ..."):
                    time.sleep(1)
                self.driver.refresh()
                continue

            # Expand all the code
            elements = self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'more match')]")
            for element in elements:
                element.click()

            api_keys = self.get_keys_from_code_list(self.driver.page_source, url_regex.regex)

            ApiKeyDao.batch_add(self.website_name, api_keys)
            logging.info("🔑 Found and added [%d] keys", len(api_keys))

            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next Page']")))
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                next_buttons[0].click()
            except Exception as _:
                logging.info("    ⚪️ No more pages")
                break

    def search(self):
        for url_regex in self.url_regexes:
            self._process_url(url_regex)
            logging.info("🔍 Finished %s", url_regex.url)

    @staticmethod
    def get_keys_from_code_list(html_source: str, regex: Pattern) -> list[str]:
        soup = BeautifulSoup(html_source, 'html.parser')

        # remote line numbers
        for element in soup.find_all(class_="blob-num"):
            element.clear()

        codes = soup.find_all(class_="code-list")

        api_keys = []
        for code in codes:
            text = code.get_text(separator=" ")
            keys = regex.findall(text)
            api_keys.extend(keys)

        return list(set(api_keys))


    def __del__(self):
        if hasattr(self, "driver") and self.driver is not None:
            self.driver.quit()
