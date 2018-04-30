import logging
from bs4 import BeautifulSoup

logging = logging.getLogger(__name__)


class ScrapingTemplate:
    def __init__(self, web_driver: object) -> None:
        self.driver = web_driver
        self.results = None

    def get_data(self) -> object:
        self._parse(soup=self._soup())

        logging.debug(self.results)
        return self.results

    def _soup(self) -> object:
        tree = self.driver.find_element_by_id("tab1")
        soup = BeautifulSoup(
            tree.get_attribute("innerHTML"),
            "html.parser")

        return soup

    def _parse(self, soup: object) -> None:
        parser = Parser(soup=soup, web_driver=self.driver)
        self.results = {
            "module": __name__,
            "parsed_results": parser.get_parsed_results()
        }


class Parser:
    def __init__(self, web_driver: object, soup: object) -> None:
        self.soup = soup
        self.driver = web_driver
        self.results = []

    def get_parsed_results(self) -> list:
        rows = self.soup.find_all("tr")
        self._parse_rows(rows)

        logging.debug(self.results)
        return self.results

    def _parse_rows(self, rows: list) -> None:
        entries = []

        for row in rows:
            columns = row.find_all("td")
            course = columns[0].a.text
            course_code = columns[0].span.text
            semester = columns[1].span.text
            grades = []

            for grade in columns[2].find_all("div"):
                grades.append(f"{grade.a.text}: {grade.span.text}")

            entries.append({
                "group": semester,
                "subgroup": course_code,
                "item": course,
                "values": grades
            })

        self._populate_results("final-grades", entries)

    def _populate_results(self, entity: str, entries: list) -> list:
        self.results.append({
            "entity": entity,
            "items": entries,
        })
