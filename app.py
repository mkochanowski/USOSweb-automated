import os
import yaml
import logging
import logging.config
import coloredlogs
from os.path import join, dirname
from dotenv import load_dotenv
from authentication import Authentication, Credentials
from data import DataController
from web_driver import SeleniumDriver
from notifications import Dispatcher
from scraper import Scraper


def load_environmental_variables() -> None:
    if os.path.isfile('.env'):
        dotenv_path = join(
            dirname(__file__), '.env')
        load_dotenv(dotenv_path)

def load_logging_setup(debug_mode: bool) -> None:
    with open('logging.yaml', 'r') as stream:
        config = yaml.load(stream)

    logging.config.dictConfig(config)
    
    log_level = 'INFO'
    if debug_mode:
        log_level = 'DEBUG'

    coloredlogs.install(
        fmt=config["formatters"]["simple"]["format"],
        level=log_level)

    selenium_logger = 'selenium.webdriver.remote.remote_connection'
    selenium_logger = logging.getLogger(selenium_logger)
    selenium_logger.setLevel(logging.ERROR)


def main() -> None:
    load_environmental_variables()
    
    load_logging_setup(
        debug_mode=os.environ['USOS_SCRAPER_DEBUG_MODE'])

    web_driver = SeleniumDriver(
        headless=os.environ['USOS_SCRAPER_WEBDRIVER_HEADLESS']).get_instance()

    credentials = Credentials(
        username=os.environ['USOS_SETTINGS_USERNAME'],
        password=os.environ['USOS_SETTINGS_PASSWORD'])

    authentication = Authentication(
        credentials=credentials,
        root_url=os.environ['USOS_SCRAPER_ROOT_URL'],
        web_driver=web_driver)

    notifications_dispatcher = Dispatcher(
        channels=os.environ['USOS_NOTIFICATIONS_STREAMS'],
        enable=os.environ['USOS_NOTIFICATIONS_ENABLE'])

    data = DataController(
        dispatcher=notifications_dispatcher
    )

    scraper = Scraper(
        root_url=os.environ['USOS_SCRAPER_ROOT_URL'],
        destinations=os.environ['USOS_SCRAPER_DESTINATIONS'],
        authentication=authentication,
        data_controller=data,
        web_driver=web_driver)

    scraper.run()
    data.analyze()


if __name__ == "__main__":
    main()