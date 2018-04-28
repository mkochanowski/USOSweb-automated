import logging
from bs4 import BeautifulSoup

logging = logging.getLogger(__name__)


class ScrapingTemplate:
    def __init__(self, web_driver: object) -> None:
        self.driver = web_driver
        self.results = None

    def get_data(self) -> object:
        self._parse(soup=self._soup())

        return self.results

    def _soup(self) -> object:
        tree = self.driver.find_element_by_id("drzewo")
        soup = BeautifulSoup(
            tree.get_attribute("innerHTML"),
            "html.parser")
    
        return soup

    def _parse(self, soup: object) -> None:
        self.results = {
            "module": __name__
        }
