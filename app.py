import os
import yaml
import logging
import logging.config
import coloredlogs
from os.path import join, dirname
from dotenv import load_dotenv
from usos.authentication import Authentication, Credentials
from usos.data import DataController
from usos.web_driver import SeleniumDriver
from usos.notifications import Dispatcher
from usos.scraper import Scraper


def load_environmental_variables(file) -> bool:
    """Populates the environment with variables from a .env file.
    
    :param file: path to the file with environmental variables.
    :returns: ``True`` if variables have been successfuly loaded.
    """
    if os.path.isfile(file):
        dotenv_path = join(
            dirname(__file__), file)
        load_dotenv(dotenv_path)
        return True
    else:
        logging.error("Oops! Did you forget to setup your .env file? "
                      + "You can use the included .env.sample as a "
                      + "starting point for your configuration.")
        return False

def check_required_dirs() -> bool:
    """Checks whether the required directories were created."""
    required = ["data", "logs"]
    for directory in required:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return True

def load_logging_setup(debug_mode: bool) -> None:
    """Initializes the logging configuration with pretty-printing for 
    console users.
    
    This method does not replace the configuration of the logging.yaml 
    file.

    :param debug_mode: whether to include DEBUG statements in the 
        console output.
    """
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
    """Runs the scraper with configuration fetched from the .env file."""
    load_logging_setup(
        debug_mode=(os.environ['USOS_SCRAPER_DEBUG_MODE'] == "True"))

    web_driver = SeleniumDriver(
        headless=(os.environ['USOS_SCRAPER_WEBDRIVER_HEADLESS'] == "True"))
    web_driver = web_driver.get_instance()

    credentials = Credentials(
        username=os.environ['USOS_SETTINGS_USERNAME'],
        password=os.environ['USOS_SETTINGS_PASSWORD'])

    authentication = Authentication(
        credentials=credentials,
        root_url=os.environ['USOS_SCRAPER_ROOT_URL'],
        web_driver=web_driver)

    notifications_dispatcher = Dispatcher(
        channels=os.environ['USOS_NOTIFICATIONS_STREAMS'],
        enable=(os.environ['USOS_NOTIFICATIONS_ENABLE'] == "True"),
        config_file=os.environ['USOS_NOTIFICATIONS_CONFIG_FILE'])

    data = DataController(
        dispatcher=notifications_dispatcher)

    scraper = Scraper(
        root_url=os.environ['USOS_SCRAPER_ROOT_URL'],
        destinations=os.environ['USOS_SCRAPER_DESTINATIONS'],
        authentication=authentication,
        data_controller=data,
        web_driver=web_driver)

    scraper.run()
    data.analyze()


if __name__ == "__main__":
    if load_environmental_variables('.env') and check_required_dirs():
        main()
