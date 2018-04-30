import json
import copy
import os.path
import logging
import hashlib

logging = logging.getLogger(__name__)


class DataController:
    def __init__(self, dispatcher: object) -> None:
        self.dispatcher = dispatcher
        self.results = []
        self._data = []

    def upload(self, item: object) -> None:
        self._data.append(item)

    def analyze(self) -> None:
        logging.info("Analyzing initialized")
        for entity in self._data:
            if ("items" in entity and entity["items"]):
                self._analyze_single(entity=entity)

        self._save("data/compared.json", self.results)
        self.dispatcher.send(self.results)

    def _get_filename(self, data: dict) -> str:
        filename = "data/exception.json"

        if "entity" in data:
            if data["entity"] == "final-grades":
                filename = "data/final-grades.json"

            elif data["entity"] == "course-results-tree":
                group = data["items"][0]["group"].lower()
                filename = f"data/courses/{group}.json"

        return filename

    def _load(self, filename: str) -> dict:
        logging.info(f"Loading entity from '{filename}'")
        data = []
        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as working_file:
                    data = json.load(working_file)
                    logging.info(f"'{filename}' - json fetched correctly")
            except IOError:
                logging.exception("File could not be opened")
            except:
                logging.exception(
                    f"'{filename}' - fetching json failed for some reasone")

        return data

    def _save(self, filename: str, entity: dict) -> None:
        logging.info(f"Saving entity to '{filename}'")
        with open(filename, 'w') as working_file:
            json.dump(entity, working_file)

    def _analyze_single(self, entity: dict) -> None:
        filename = self._get_filename(entity)
        old = self._load(filename)

        self._compare(old, entity)

        self._save(filename, entity)

    def _same_item(self, old: list, new: list) -> bool:
        results = []
        identifiers = ["group", "subgroup", "item"]

        if "hierarchy" in new:
            identifiers.append("hierarchy")

        for identifier in identifiers:
            results.append(old[identifier] == new[identifier])

        return (False not in results)

    def _compare_items(self, old: list, new: list) -> list:
        results = []
        for item_new in new:
            for index, item_old in enumerate(old):
                if (self._same_item(item_old, item_new)
                        and item_old["values"] != item_new["values"]):
                    entry = copy.copy(item_new)
                    entry["old_values"] = item_old["values"]
                    results.append(entry)
                    logging.debug(f"Detected change: {entry}")
                    break
                elif index == len(old) - 1:
                    results.append(item_new)
                    logging.debug(f"New item found: {item_new}")

        return results

    def _compare(self, old: list, new: list) -> None:
        if ("entity" in old
                and "entity" in new
                and old["entity"] == new["entity"]):
            entity_name = new["entity"]
            logging.info(f"Comparing results of entity '{entity_name}'")
            self.results.append({
                "entity": new["entity"],
                "items": self._compare_items(
                    old["items"], new["items"]),
            })
        elif ("entity" not in old and "entity" in new):
            self.results.append(new)
        else:
            logging.info(f"old: {old}\nnew: {new}")
            logging.error("Entity passed for comparison with incorrect type")
