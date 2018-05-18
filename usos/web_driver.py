import os
import logging
from selenium import webdriver
from datetime import datetime

logging = logging.getLogger(__name__)


class SeleniumDriver:
    """Provides a layer of abstraction to obtain a preconfigured object 
        of a Selenium-compatible web driver.
        
        :param headless: whether the driver should run in headless mode
        :param config: set of config variables to tweak the behaviour of
            the web driver"""

    def __init__(self, headless: bool, config: dict = {}) -> None:
        self.headless = headless
        self.config = config
        self._driver = None

    def reset(self) -> None:
        """Resets the instance of a web driver to ``None``. 
        
        This method might prove useful while switching between 
        different web drivers.
        """
        logging.info("Resetting the webdriver instance")
        logging.debug("Headless? {} Config: {}".format(
            self.headless, self.config))
        
        if self._driver:
            self.quit()

        self._driver = None

    def get_instance(self) -> object:
        """Returns an instance of selected web driver.
        
        Changing the implementation of this method will allow you to 
        integrate different web drivers and replace *Chrome* (the 
        default) with *Firefox*, *PhantomJS* or something else.
        
        To find out more, read :ref:`CustomWebDriver`.

        :returns: by default - an object of ChromeDriver. Can be 
            extended.
        """
        self.reset()

        # if self.headless:
        #     self._driver_phantomjs()
        # else:
        #     self._driver_chrome()

        self._driver_chrome()

        return self._driver

    def exception_take_screenshot(self, codename: str) -> None:
        """Takes a screenshot of web driver's current viewport.
        
        This method can be utilized as a tool for troubleshooting
        non-trivial errors with parsing. ::

            def perform-login-example(self, usr: str, pwd: str) -> object:
                try:
                    ...
                    return get_user_instance(usr, pwd)
                except:
                    driver.exception_take_screenshot("perform-login")
                    logging.exception("Could not retrieve user instance")

        :param codename: name of the exception/event that will be added
            to the image's filename
        """
        logging.info("Initializing taking screenshot from webdriver")

        now = datetime.datetime.today()
        date = now.strftime('%d-%m-%y')
        filename = "exception-{}-{}.png".format(date, codename)

        self._driver.save_screenshot("data/screenshots/" + filename)

        logging.info("Screenshot taken for `{}` as {}".format(
            codename, filename))

    def quit(self) -> None:
        """Forces the web driver to terminate."""
        logging.info("Forcing the webdriver to quit")

        self._driver.quit()

    def _driver_phantomjs(self) -> None:
        """Adds PhantomJS WebDriver support."""
        logging.info("Creating new PhantomJS Driver")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        driver_path = dir_path + '/../phantomjs'
        driver = webdriver.PhantomJS(executable_path=driver_path)
        driver.set_window_size(1120, 550)

        self._driver = driver

    def _driver_chrome(self) -> None:
        """Adds ChromeDriver support."""
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
