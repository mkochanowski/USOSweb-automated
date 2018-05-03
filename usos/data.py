import json
import copy
import os.path
import logging
import hashlib

logging = logging.getLogger(__name__)


class DataController:
    """Stores and performs analysis of collected data.
    
    ::
    
        from usos.data import DataController
        from usos.notifications import Dispatcher

        my_dispatcher = Dispatcher(
            channels="Email SMS WebPush MessengerPigeon",
            enable=True,
            config_file="notifications.json")

        data = DataController(dispatcher=my_dispatcher)
        
        single_entry = {
            'entity': 'example-entity-type',
            'items': [...]
        }

        data.upload(single_entry)        
        ...
        data.analyze()
    
    :param dispatcher: instance of :class:`usos.notifications.Dispatcher` 
        responsible for providing the notifications via available 
        channels.
    """
    def __init__(self, dispatcher: object) -> None:
        self.dispatcher = dispatcher
        self.results = []
        self._data = []

    def upload(self, item: dict) -> None:
        """Uploads a given item to a data temporary storage.

        ::

            data.upload({
                'entity': 'example-entity-type',
                'items': [...]
            })

        :param item: item that will be uploaded to the temporary storage.
        """
        self._data.append(item)

    def analyze(self) -> None:
        """Analyzes the data stored in temporary storage and passes the 
        results onto the notifications' dispatcher."""
        logging.info("Initializing the analysis")
        for entity in self._data:
            if ("items" in entity and entity["items"]):
                self._analyze_single(entity=entity)

        # self._save("data/compared.json", self.results)
        if self.results:
            logging.info("Changes detected, passing onto dispatcher")
            self.dispatcher.send(self.results)
        else:
            logging.info("No changes have been detected")

    def _get_filename(self, data: dict) -> str:
        """Returns a filename based on the data's **entity-type**."""
        filename = "data/exception.json"

        if "entity" in data:
            if data["entity"] == "final-grades":
                filename = "data/final-grades.json"

            elif data["entity"] == "course-results-tree":
                group = data["items"][0]["group"].lower()
                filename = "data/courses/{}.json".format(group)

        return filename

    def _load(self, filename: str) -> dict:
        """Loads the data from a specified json file.

        :param filename: name of the json file to load the data from
        """
        logging.info("Loading entity from '{}'".format(filename))
        data = []

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as working_file:
                    data = json.load(working_file)
                    logging.info("'{}'".format(filename)
                                 + "- json has been fetched correctly")
            except IOError:
                logging.exception("File could not be opened")
            except:
                logging.exception("'{}'".format(filename)
                                  + "- fetching json has failed "
                                  + "for an unknown reason")

        return data

    def _save(self, filename: str, entity: dict) -> None:
        """Saves the data to a specified json file.
         
        :param filename: name of the json file to save the data to
        :param entity: entity items to store
        """
        logging.info("Saving entity to '{}'".format(filename))
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
                    logging.debug("Detected change: {}".format(entry))
                    break

                # elif index == len(old) - 1:
                #     results.append(item_new)
                #     logging.debug(f"New item found: {item_new}")

        return results

    def _compare(self, old: list, new: list) -> None:
        if ("entity" in old and
                "entity" in new and
                old["entity"] == new["entity"]):

            entity_name = new["entity"]
            logging.info("Comparing results of entity "
                         + "'{}'".format(entity_name))
            entry = {
                "entity": new["entity"],
                "items": self._compare_items(
                    old["items"], new["items"]),
            }

            if entry["items"]:
                self.results.append(entry)

        elif ("entity" not in old
              and "entity" in new):

            if "items" in new and new["items"]:
                self.results.append(new)
        else:
            logging.debug("Old: {}\nNew: {}".format(old, new))
            logging.error("Entity passed for comparison with "
                          + "incorrect type")
