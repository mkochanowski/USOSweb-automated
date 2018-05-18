import os
import logging
import importlib
from os.path import join, exists

logging = logging.getLogger(__name__)


class Scraper:
    """Navigates the interface and scrapes the data.
    
    :param root_url: a root url for the USOSweb interface.
    :param destinations: 
    :param authentication: an instance of 
        :class:`usos.authentication.Authentication` for accessing 
        protected data.
    :param data_controller: a controller for storing and analysing 
        scraped data.
    :param web_driver: a Selenium web driver instance for navigating.
    """
    def __init__(self, root_url: str, destinations: str,
                 authentication: object, data_controller: object,
                 web_driver: object) -> None:
        self.root_url = root_url
        self.destinations = destinations.split(" ")
        self.visited = []
        self.authentication = authentication
        self.data_controller = data_controller
        self.driver = web_driver

    def run(self) -> None:
        """Runs the process of iterating through provided destinations."""
        logging.info("Launching the scraper")

        for destination in self.destinations:
            self.go_to(destination)

        self.quit()

    def quit(self) -> None:
        """Terminates the scraper."""
        logging.info("Terminating the scraper")

        self.driver.quit()

    def go_to(self, destination: str) -> None:
        """Navigates to the provided destination.
        
        :param destination: a part of the url that will be used to match 
            the ScrapingTemplate.
        """
        logging.info("Going to the destination: '{}'".format(
            destination))
        destination = self._normalize_destination_url(destination)
        self.visited.append(destination)

        if self.authentication.is_authenticated():
            self.driver.get(''.join([self.root_url, destination]))
            self._perform(destination)

    def _process_results(self, data: dict) -> None:
        """Processes data returned from ScrapingTemplates.
        
        If the data includes these keys:
        ``new_destinations`` - adds new destinations to the scraper queue.
        ``parsed_results`` - uploads the data for later analysis.
        :param data: data passed from a ScrapingTemplate.
        """
        logging.info("Processing results initialized")
        logging.debug("Data: {}".format(data))

        if data is not None:
            if "new_destinations" in data:
                logging.info("New destinations detected in the data"
                             + "package")
                self._process_results_destinations(
                    data["new_destinations"])

            if "parsed_results" in data:
                logging.info("Results detected in the data package")
                self._process_results_parsed(data["parsed_results"])

    def _process_results_destinations(self, data: list) -> None:
        """Adds new, unvisited destinations to the scraper queue from the 
        ScrapingTemplate results.
        
        :param data: destinations excluded from results dict.
        """
        for link in data:
            link = self._normalize_destination_url(link)

            if link in self.visited:
                logging.info(
                    "'{}' has already been visited".format(link))
            else:
                logging.info(
                    "Adding '{}' to the scraping queue".format(link))
                self.destinations.append(link)

    def _process_results_parsed(self, data: list) -> None:
        """Uploads parsed results to the data controller.
        
        :param data: entites sent from a ScrapingTemplate.
        """

        if len(data) == 1:
            self.data_controller.upload(data[0])
        else:
            self.data_controller.upload_multiple(data)

    def _normalize_destination_url(self, destination: str) -> str:
        """Translates url into a scraper-compatible destination.
        
        :param destination: a full url inside of a USOSweb application.
        :returns: a destination.
        """
        if destination.startswith("http"):
            if destination.startswith(self.root_url):
                new_destination = destination[len(self.root_url):]
                logging.debug(
                    "Destination '{}' normalized into '{}'".format(
                        destination, new_destination))
                destination = new_destination
            else:
                logging.error("Normalizing url '{}'".format(destination)
                              + " has failed: no rule has been set")
        return destination

    def _perform(self, destination: str) -> None:
        """Performs the scraping and parsing of a given destination.

        :param destination: scraper-compatible destination path.
        """
        logging.info(
            "Performing the scraping of '{}'".format(destination))

        scraping_template = self._detect(destination)
        data = None

        if scraping_template is not None:
            try:
                data = scraping_template.get_data()
                self._process_results(data)
            except:
                logging.exception("Execution of a ScrapingTemplate has failed")
        
        logging.debug("Retrieved data: {}".format(data))


    def _detect(self, destination: str) -> object:
        """Detects the template to import based on a given destination. 
        
        :param destination: scraper-compatible destination path.
        :returns: an imported ScrapingTemplate.
        """
        destination = destination.replace("/", "-")
        parameter = destination.find("&")

        if parameter >= 0:
            destination = destination[:parameter]

        module = ".".join(["templates", "scraping", destination])
        logging.debug("Looking for '{}' class".format(destination))

        return self._import(module=module)

    def _import(self, module: str) -> object:
        """Provides a requested ScrapingTemplate.
        
        :param module: a name of ScrapingTemplate to import.
        :returns: an imported ScrapingTemplate.
        """
        spec = importlib.util.find_spec(module)

        if spec is None:
            logging.error("'{}' template not found".format(module))

            return None
        else:
            logging.info("'{}' template file found".format(module))
            imported = importlib.import_module(module)

            logging.debug(
                imported.ScrapingTemplate(web_driver=self.driver))
            return imported.ScrapingTemplate(web_driver=self.driver)
