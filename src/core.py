import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
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

from src.configs import SELENIUM_REMOTE_ENABLED, SELENIUM_CHROME_BASE_URL, COOKIE_FILE
from src.db.dao import ApiKeyDao
from src.manager.cookie_manager import CookieManager
from src.manager.progress_manager import ProgressManager


class APIKeyLeakageScanner:
    """
    Scan GitHub for available OpenAI API Keys
    """
    def __init__(self, website: dict):
        self.progress = ProgressManager()
        self.driver: webdriver.Chrome | None = None
        self.cookies: CookieManager | None = None

        self.candidate_urls = []
        self.website_name = website["name"]
        self.validator = website["validator"]()
        self.regexes: List[Pattern] = [re.compile(r) for r in website["regexes"]]

        for r in self.regexes:
            self.candidate_urls.append(f"https://github.com/search?q=(/{r.pattern}/)&type=code&ref=advsearch")

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

    def _process_url(self, url: str):
        """
        Process a search query url
        """
        if self.driver is None:
            raise ValueError("Driver is not initialized")

        self.driver.get(url)
        apis_found = []
        apis_found2 = []
        urls_need_expand = []

        while True: # Loop until all the pages are processed
            # If current webpage is reached the rate limit, then wait for 30 seconds
            if self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'You have exceeded a secondary rate limit')]"):
                for _ in tqdm(range(30), desc="⏳ Rate limit reached, waiting ..."):
                    time.sleep(1)
                self.driver.refresh()
                continue

            # Expand all the code
            elements = self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'more match')]")
            for element in elements:
                element.click()

            # find all elements with class name 'f4'
            codes = self.driver.find_elements(by=By.CLASS_NAME, value="code-list")
            for element in codes:
                apis = []
                # Check all regex for each code block
                for regex in self.regexes:
                    apis.extend(regex.findall(element.text))

                if len(apis) == 0:
                    # Need to show full code. (because the api key is too long)
                    # get the <a> tag
                    a_tag = element.find_element(by=By.XPATH, value=".//a")
                    urls_need_expand.append(a_tag.get_attribute("href"))

                ApiKeyDao.batch_add(self.website_name, apis)
                apis_found.extend(apis)

            rich.print(f"🌕 There are {len(urls_need_expand)} urls waiting to be expanded")

            try:
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                rich.print("    🔍 Clicking next page")
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next Page']")))
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                next_buttons[0].click()
            except Exception as _:
                rich.print("    ⚪️ No more pages")
                break


        # Handle the expand_urls
        for url in tqdm(urls_need_expand, desc="🔍 Expanding URLs ..."):
            if self.driver is None:
                raise ValueError("Driver is not initialized")

            self.driver.get(url)
            time.sleep(3) # TODO: find a better way to wait for the page to load

            retry = 0
            while retry <= 3:
                matches = []
                for regex in self.regexes:
                    matches.extend(regex.findall(self.driver.page_source))

                api_keys = list(set(matches))

                if len(api_keys) == 0:
                    rich.print(f"    ⚪️ No matches found in the expanded page, retrying [{retry}/3]...")
                    retry += 1
                    time.sleep(3)
                    continue

                new_apis = [api for api in api_keys if not ApiKeyDao.key_exists(self.website_name, api)]
                new_apis = list(set(new_apis))
                apis_found.extend(new_apis)
                ApiKeyDao.batch_add(self.website_name, new_apis)
                rich.print(f"    🟢 Found {len(api_keys)} api_keys in the expanded page, adding them to the list")
                for k in api_keys:
                    rich.print(f"        '{k}'")

                break

    def search(self):
        """
        Search for API keys, and save the results to the database
        """
        total = len(self.candidate_urls)
        pbar = tqdm(
            enumerate(self.candidate_urls),
            total=total,
            desc="🔍 Searching ...",
        )

        for idx, url in enumerate(self.candidate_urls):
            self._process_url(url)
            self.progress.save(idx, total)
            logging.debug("🔍 Finished %s", url)
            pbar.update()
        pbar.close()

    def valid_existed_keys(self):
        last_id = 0
        while True:
            keys = ApiKeyDao.get_all_keys(self.website_name, last_id=last_id)
            if not keys:
                break

            for key in tqdm(keys, desc="🔄 Updating existed keys ..."):
                result = self.validator.validate(key.api_key)
                ApiKeyDao.update_one(key.id, result)

            last_id = keys[-1].id


    def __del__(self):
        if hasattr(self, "driver") and self.driver is not None:
            self.driver.quit()