import logging
from bs4 import BeautifulSoup

logging = logging.getLogger(__name__)


class ScrapingTemplate:
    """Scrapes the specific type of page by using predefined
    set of actions."""
    def __init__(self, web_driver: object) -> None:
        self.driver = web_driver
        self.results = None

    def get_data(self) -> object:
        """Returns scraped and parsed data."""
        self._parse(soup=self._soup())

        logging.debug(self.results)
        return self.results

    def _soup(self) -> object:
        """Generates a soup object out of a specific element
        provided by the web driver."""
        tree = self.driver.find_element_by_id("lista")
        soup = BeautifulSoup(
            tree.get_attribute("innerHTML"),
            "html.parser")
    
        return soup

    def _parse(self, soup: object) -> None:
        """Initializes parsing of the innerHTML."""
        parser = Parser(soup=soup, web_driver=self.driver)
        self.results = {
            "module": __name__,
            "new_destinations": parser.get_destinations()
        }

class Parser:
    """Parses the provided HTML with BeautifulSoup."""
    def __init__(self, web_driver: object, soup: object) -> None:
        self.soup = soup
        self.driver = web_driver

    def get_destinations(self) -> list:
        """Returns the results back to the ScrapingTemplate."""
        links = self.driver.find_elements_by_class_name("fwdlink")
        destinations = []
        for link in links:
            destinations.append(link.get_attribute("href"))

        return destinations