import logging
import os
import pickle
import sys
from selenium.common import UnableToSetCookieException
from selenium.webdriver.common.by import By

from src.core.configs import COOKIE_FILE


class CookieManager:
    def __init__(self, driver):
        self.driver = driver

    def save(self):
        cookies = self.driver.get_cookies()
        with open(COOKIE_FILE, "wb") as file:
            pickle.dump(cookies, file)
            logging.info("🍪 Cookies saved")

    def load(self):
        try:
            with open(COOKIE_FILE, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except UnableToSetCookieException:
                        logging.debug("🟡 Warning, unable to set a cookie %s", cookie)
        except (EOFError, pickle.UnpicklingError):
            if os.path.exists(COOKIE_FILE):
                os.remove(COOKIE_FILE)
            logging.error("🔴 Error, unable to load cookies, invalid cookies has been removed, please restart.")

    def verify_user_login(self):
        """
        Test if the user is really logged in
        """
        logging.info("🤗 Redirecting ...")
        self.driver.get("https://github.com/")

        if self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'Sign in')]"):
            if os.path.exists(COOKIE_FILE):
                os.remove(COOKIE_FILE)
            logging.error("🔴 Error, you are not logged in, please restart and try again.")
            sys.exit(1)
        return True

