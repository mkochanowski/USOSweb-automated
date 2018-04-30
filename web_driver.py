import os
import logging
from typing import Dict
from selenium import webdriver
from datetime import datetime

logging = logging.getLogger(__name__)


class SeleniumDriver:
    def __init__(self, headless: bool, config: Dict = {}) -> None:
        self.headless = headless
        self.config = config
        self._driver = None

    def reset(self) -> None:
        logging.info("Resetting the webdriver instance")
        logging.debug(f"Headless? {self.headless}\n"
                      + f"Config: {self.config}")
        self._driver = None

    def get_instance(self) -> object:
        self.reset()

        # if self.headless:
        #     self._driver_phantomjs()
        # else:
        #     self._driver_chrome()

        self._driver_chrome()

        return self._driver

    def exception_take_screenshot(self, codename: str) -> None:
        logging.info("Initializing taking screenshot from webdriver")

        now = datetime.datetime.today()
        date: str = now.strftime('%d-%m-%y')
        filename: str = f"exception-{date}-{codename}.png"

        self._driver.save_screenshot("data/screenshots/" + filename)

        logging.info(f"Screenshot taken for `{codename}` as {filename}")

    def quit(self) -> None:
        logging.info("Forcing the webdriver to quit")

        self._driver.quit()

    def _driver_phantomjs(self) -> None:
        logging.info("Creating new PhantomJS Driver")

        dir_path: str = os.path.dirname(os.path.realpath(__file__))
        driver_path: str = dir_path + '/phantomjs'
        driver = webdriver.PhantomJS(executable_path=driver_path)
        driver.set_window_size(1120, 550)

        self._driver = driver

    def _driver_chrome(self) -> None:
        logging.info("Creating new Chrome Driver")

        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=5")
        options.add_argument("--disable-extensions")
        if self.headless:
            options.add_argument("headless")
        options.add_argument(
            "user-data-dir=data/chrome_profile")
        driver = webdriver.Chrome(chrome_options=options)

        self._driver = driver
