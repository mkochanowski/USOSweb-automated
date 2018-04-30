import copy
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
        tree = self.driver.find_element_by_id("layout-c22a")
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
        self._group = None
        self._subgroup = None
        self._tree_entries = []

    def get_parsed_results(self) -> list:
        self._parse_groups(self.soup)
        tree = self.soup.find("div", {"id": "drzewo"})
        tree = tree.find("div", id=True, recursive=False)
        self._parse_tree(tree)

        logging.debug(self.results)
        return self.results

    def _parse_groups(self, soup: object) -> None:
        rows = soup.h1.find_all("span")
        course = rows[0].a.text
        course_code = rows[0].span.text
        semester = rows[1].text

        self._group = course_code
        self._subgroup = course

    def _parse_single_table_title(self, table: object) -> str:
        table = table.find("tr")
        columns = table.find_all("td")
        
        return columns[1].contents[0].strip()

    def _strip_cell(self, cell: str) -> str:
        cell = cell.replace("\n", " ")
        cell = " ".join(cell.split())
        return cell

    def _parse_single_table(self, table: object,
                            hierarchy: str) -> dict:
        table = table.find("tr")
        columns = table.find_all("td")
        title = columns[1].contents[0].strip()
        grade = self._strip_cell(columns[2].text)
        values = [grade]
        
        if (len(columns) > 3 
                and "pokaż szczegóły" not in columns[3].text):
            values.append(self._strip_cell(columns[3].text))

        self._tree_entries.append({
            "group": self._group,
            "subgroup": self._subgroup,
            "hierarchy": hierarchy[2:],
            "item": title,
            "values": values
        })

    def _parse_subtree_recursively(self, tree: object,
                                   hierarchy: str) -> dict:
        tables = tree.find_all("table", recursive=False)
        titles = []
        for table in tables:
            titles.append(self._parse_single_table_title(table))
            self._parse_single_table(table, hierarchy)

        subtrees = tree.find_all("div", id=True, recursive=False)
        for index, subtree in enumerate(subtrees):
            expanded_hierarchy = "{}/{}".format(
                hierarchy, titles[index])
            self._parse_subtree_recursively(
                subtree, expanded_hierarchy)

    def _parse_tree(self, tree: object) -> None:
        self._parse_subtree_recursively(tree, ".")

        self._populate_results("course-results-tree", self._tree_entries)

    def _populate_results(self, entity: str, entries: list) -> list:
        self.results.append({
            "entity": entity,
            "items": entries,
        })
