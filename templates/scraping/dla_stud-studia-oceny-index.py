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
        tree = self.driver.find_element_by_id("tab1")
        soup = BeautifulSoup(
            tree.get_attribute("innerHTML"),
            "html.parser")

        return soup

    def _parse(self, soup: object) -> None:
        """Initializes parsing of the innerHTML."""
        parser = Parser(soup=soup, web_driver=self.driver)
        self.results = {
            "module": __name__,
            "parsed_results": parser.get_parsed_results()
        }


class Parser:
    """Parses the provided HTML with BeautifulSoup."""
    def __init__(self, web_driver: object, soup: object) -> None:
        self.soup = soup
        self.driver = web_driver
        self.results = []

    def get_parsed_results(self) -> list:
        """Returns the results back to the ScrapingTemplate."""
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
                grade_title = grade.a.text if grade.a else "(brak)"
                grade_value = grade.span.text if grade.span else "(brak)"
                grades.append(
                    "{}: {}".format(grade_title, grade_value))

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
