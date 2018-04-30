import json
import os.path
import logging
import hashlib

logging = logging.getLogger(__name__)


class DataController:
    def __init__(self, dispatcher: object) -> None:
        self.dispatcher = dispatcher
        self._data = []
        self.results = []

    def upload(self, item: object) -> None:
        self._data.append(item)

    def analyze(self) -> None:
        logging.info("Analyzing initialized")
        for entity in self._data:
            if ("items" in entity and entity["items"]):
                self._analyze_single(entity=entity)

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
        logging.info(f"Loading entity to '{filename}'")
        data = []
        if os.path.isfile(filename): 
            try:
                with open(filename, 'r') as working_file:  
                    current_data = json.load(working_file)
                    logging.info(f"'{filename}' - json fetched correctly")
            except IOError:
                logging.exception("File could not be opened")
            except:
                logging.exception(f"'{filename}' - fetching json failed for some reasone")

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

    def _compare(self, old: list, new: list) -> list:
        logging.info("Comparing results")
