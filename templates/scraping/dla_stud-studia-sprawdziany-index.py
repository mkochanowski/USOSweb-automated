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
        tree = self.driver.find_element_by_id("lista")
        soup = BeautifulSoup(
            tree.get_attribute("innerHTML"),
            "html.parser")
    
        return soup

    def _parse(self, soup: object) -> None:
        parser = Parser(soup=soup, web_driver=self.driver)
        self.results = {
            "module": __name__,
            "new_destinations": parser.get_destinations()
        }

class Parser:
    def __init__(self, web_driver: object, soup: object) -> None:
        self.soup = soup
        self.driver = web_driver

    def get_destinations(self) -> list:
        links = self.driver.find_elements_by_class_name("fwdlink")
        destinations = []
        for link in links:
            destinations.append(link.get_attribute("href"))

        return destinations