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

    def upload_multiple(self, items: list) -> None:
        """Uploads a list of items to a temporary data storage. 

        Internally uses the :meth:`upload` method on every item provided
        in the list. ::

            my_final_grades = {
                'entity': 'final-grades',
                'items: [...]
            }

            entities = {}
            for i in range(0, 15):
                entities.append({
                    'entity': 'iterations-for-analysis'
                    'items': [
                        'group': 'Just a for loop',
                        'item': 'A single iteration',
                        'values': [i, i+1, i+2]    
                    ]    
                })

            entities = entities.append(my_final_grades)
            data.upload_multiple(entities)


        :param items: items in an **entity-compatible** format.
        """
        for item in items:
            self.upload(item)

    def upload(self, item: dict) -> None:
        """Uploads a given item to a temporary data storage.

        The :meth:`upload` method works on dictionaries structured as
        **entities**.

        Learn more about entities here: :ref:`CustomEntity`. ::

            data.upload({
                'entity': 'example-entity-type',
                'items': [...]
            })

        :param item: item in an **entity-compatible** format.
        """
        self._data.append(item)

    def analyze(self) -> None:
        """Analyzes the data stored in the temporary storage and passes 
        the results to the notifications' dispatcher."""
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
        """Returns a filename based on the data's **entity-type**. ::

            >>> grades = {
            ...     "entity": "final-grades",
            ...     "items": []
            ... }

            >>> course_results = {
            ...     "entity": "course-results-tree",
            ...     "items": [
            ...         {
            ...             "group": "28-INF-S-DOLI",
            ...             "subgroup": "Logic for Computer Science",
            ...             "hierarchy": "/Exam",
            ...             "item": "Results",
            ...             "values": ["104.5 pkt"]
            ...         }
            ...     ]
            ... }

            >>> data._get_filename(grades)
            'data/final-grades.json'
            >>> data._get_filename(course_results)
            'data/courses/28-inf-s-doli.json'


        :returns: filename of the json file for a given entity."""
        filename = "data/exception.json"

        if "entity" in data:
            if data["entity"] == "final-grades":
                filename = "data/final-grades.json"

            elif data["entity"] == "course-results-tree":
                group = data["items"][0]["group"].lower()
                filename = "data/courses/{}.json".format(group)

        return filename

    def _load(self, filename: str) -> dict:
        """Loads the data from a specified JSON file.

        :param filename: name of the JSON file to load the data from.
        :returns: an entity retrieved from a file.
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

    def _save(self, filename: str, data: dict) -> None:
        """Saves the data to a specified JSON file.

        :param filename: name of the JSON file to save the data to.
        :param data: data to store.
        """
        logging.info("Saving entity to '{}'".format(filename))
        with open(filename, 'w') as working_file:
            json.dump(data, working_file)

    def _analyze_single(self, entity: dict) -> None:
        filename = self._get_filename(entity)
        old = self._load(filename)

        self._compare(old, entity)

        self._save(filename, entity)

    def _same_item(self, old: dict, new: dict) -> bool:
        """Checks whether a given new item carries the same identifiers 
        as the old one. ::

            >>> rectangle = {
            ...     "group": "Shapes",
            ...     "subgroup": "Two-dimensional",
            ...     "item": "A rectangle",
            ...     "values": [10, 20]
            ... }

            >>> new_rectangle = {
            ...     "group": "Shapes",
            ...     "subgroup": "Two-dimensional",
            ...     "item": "A rectangle",
            ...     "values": [30, 50]
            ... }

            >>> square = {
            ...     "group": "Shapes",
            ...     "subgroup": "Two-dimensional",
            ...     "item": "A square",
            ...     "values": [10, 10]
            ... }

            >>> data._same_item(rectangle, square)
            False
            >>> data._same_item(rectangle, new_rectangle)
            True

        :param old: an element from the list of items of an old entity.
        :param new: an element from the list of items of a new entity.
        """
        results = []
        identifiers = ["group", "subgroup", "item"]

        if "hierarchy" in new:
            identifiers.append("hierarchy")

        for identifier in identifiers:
            results.append(old[identifier] == new[identifier])

        return (False not in results)

    def _compare_items(self, old: list, new: list,
                       append_if_missing: bool = False) -> list:
        """Compares two lists of items.

        :param old: items from an old entity.
        :param new: items from a new entity.
        :param append_if_missing: whether the item should be added to the 
            final results if it is present in :attr:`new` but missing in 
            :attr:`old`.
        :returns: items that share the same identifiers but with updated
            values.
        """
        results = []

        for item_new in new:
            present_in_both = False
            
            for index, item_old in enumerate(old):
                if self._same_item(item_old, item_new):
                    present_in_both = True
                    if item_old["values"] != item_new["values"]:
                        entry = copy.copy(item_new)
                        entry["old_values"] = item_old["values"]
                        results.append(entry)
                        logging.debug(
                            "Detected change: {}".format(entry))
                        break

            if append_if_missing and not present_in_both:
                results.append(item_new)
                logging.debug("New item found: {}".format(item_new))

        return results

    def _compare(self, old: dict, new: dict) -> None:
        """Compares two entities between eachother.

        :param old: locally stored entity.
        :param new: newly retrieved entity.
        """
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
