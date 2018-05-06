Extending the functionality
===========================

Scraping
--------

Writing ScrapingTemplates
~~~~~~~~~~~~~~~~~~~~~~~~~

A ``ScrapingTemplate`` is a set of rules that is predefined for a specific page.

| Let's say the url we want to scrape is:
| ``https://usosweb.uni.wroc.pl/kontroler.php?_action=dla_stud/studia/sprawdziany/pokaz&wez_id=33693``

In this example, a ``ROOT_URL`` is ``https://usosweb.uni.wroc.pl/kontroler.php?_action=`` and the destination:  ``dla_stud/studia/sprawdziany/pokaz``. 

The path of the template is going to be ``templates/scraping/dla_stud-studia-sprawdziany-pokaz.py`` (just replace the slashes with dashes).

This is how a minimal template looks like:

.. code-block:: python

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
            """Returns the scraped and parsed data."""
            self._parse(soup=self._soup())

            logging.debug(self.results)
            return self.results

        def _soup(self) -> object:
            """Generates a soup object out of a specific element
            provided by the web driver.""" 
            driver_html = self.driver.find_element_by_id("container")

            soup = BeautifulSoup(
                driver_html.get_attribute("innerHTML"),
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

            ... # does parsing magic

            return self.results

The only requirement for the ``ScrapingTemplate`` is to implement the ``get_data()`` method so that it returns a dictionary with a ``module`` key, such as:

.. code-block:: python

    {
        "module": __name__,
        "new_destinations": [ ... ],
        "parsed_results": [ ... ]
    }

**Available keys:**

| ``new_destinations`` - URLs to pass back to the scraper for building up the queue of crawling.
| ``parsed_results`` - data saved in a form of a list of entities. 

.. _CustomWebDriver:

Using custom web drivers
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the `Scraper <https://docs.kochanow.ski/usos/api.html#module-usos.scraper>`_ 
class uses ``ChromeDriver`` to automate the browser.

You can add more drivers in  ``usos/web_driver.py``. Here is an example of a custom driver:

.. code-block:: python

    def _driver_phantomjs(self) -> None:
        """Adds PhantomJS WebDriver support."""
        logging.info("Creating new PhantomJS Driver")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        driver_path = dir_path + '/phantomjs'
        driver = webdriver.PhantomJS(executable_path=driver_path)
        driver.set_window_size(1120, 550)

        self._driver = driver 

| Important: your method should set the ``self._driver`` attribute to point to the instance of the driver.
| Now, you can add additional logic to how the drivers are chosen. 
| Let's say, we want the ``PhantomJS`` driver to launch only in debug mode, and ``ChromeDriver`` on our production server.
| 

.. code-block:: python

    def get_instance(self) -> object:
        """Returns an instance of the selected web driver."""
        self.reset()

        if self.config["MY_DEBUG_MODE"]:
             self._driver_phantomjs()
        else:
             self._driver_chrome()

        return self._driver


.. _CustomEntity:

Defining new entities
~~~~~~~~~~~~~~~~~~~~~

.. warning::

    | The current implementation of an **Entity** will be replaced in the future by an independant data structure.
    | Honestly, operating on dictionaries instead of a dedicated class feels a little weird for such an important element.

| An ``Entity`` is a dictionary structure that contains two keys: ``entity`` and ``items``.
| Think about it not only as a data type, but also as an abstraction tak defines its *purpose*.

For example:  

.. code-block:: json

    {
        "entity": "course-results-tree",
        "items": [
            {
                "group": "28-INF-S-DOLI",
                "subgroup": "Logic for Computer Science",
                "hierarchy": "Exams",
                "item": "Final Exam",
                "values": ["85.0 pts", "Editor: John Doe"]
            }, {
                "group": "28-INF-S-DOLI",
                "subgroup": "Logic for Computer Science",
                "hierarchy": "Class/Tests",
                "item": "Test no. 3",
                "values": ["15.0 pts", "Editor: Jane Doe"]
            }
        ]
    }

.. hint::
    
    Entity ``course-results-tree`` defines not only what it stores in the ``items`` key, but also how to process the data - the defined behaviour is to compare the supplied items with existing data to search for changes.

1. If you want to introduce a new entity, start with a ScrapingTemplate. This is the very first step of a lifecycle of an entity.
2. Add custom behaviour for the specific entity you're implementing. Check and if needed, expand methods ``_get_filename()`` and ``analyze()`` of the ``usos.data.DataController`` class.
3. Update your rendering templates to support this type of entity.
4. Great! You now have a new type of entity that supports custom behaviour.

Notifications
-------------

.. _CustomNotificationsTemplates:

Writing message templates
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This package comes with `Jinja2 <http://jinja.pocoo.org/>`_ as a default templating engine.

| Everybody loves Jinja2. That's why it is used as a default templating engine for this project.
| You can add your own templates by putting them into the ``templates/notifications/`` directory.

To learn more about writing templates in Jinja2, check out the `documentation <http://jinja.pocoo.org/>`_.

.. _CustomNotificationsStreams:

Implementing additional Streams (channels)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Streams are defined in ``usos/notifications.py``. To add your own channel, just subclass ``Notification`` and implement two private methods: 
``_render()`` and ``_send()``. 

The Dispatcher class automatically sets the ``self.data`` and ``self.config`` attributes that supply results from the DataController as well as channel-specific key variables from ``notifications_config.json`` file.


.. important::

    The final template should be saved in the ``self._rendered_template`` attribute.

.. code-block:: python

    def _render(self) -> None:
        env = Environment(loader=FileSystemLoader('templates/notifications'))
        template = env.get_template('WebRequest.html')

        self._rendered_template = template.render(data=self.data)

Your ``_send()`` method should return a boolean indicating whether the notification has been sent successfuly or not.

.. code-block:: python

    def _send(self) -> bool:
        data = {
            'API_KEY': self.config["API_KEY"], 
            'MESSAGE': self._rendered_template
        }
        request = requests.post(API_URL, data=data)
        return (request.status_code == 200)

Here's another example of a custom stream: ``PaperMail``. 

.. code-block:: python

    class PaperMail(Notification):
        def _render(self) -> None:
            letter: str = "Hey, {name}! "
                            + "{message} "
                            + "Take care, {author}."  
            
            letter = letter.format(
                name=data["recipient"], 
                message=data["message"],
                author=data["sender"])
            
            self._rendered_template = letter

        def _send(self) -> bool:
            put_in_a_mailbox(self._rendered_template)
            return True

Now it can be used as a channel on it's own:

.. code-block:: python

    dispatcher = Dispatcher(
        channels="PaperMail",
        enable=True,
        config_file="mailbox_coordinates.json")

    my_message = {
        "recipient": "Kate",
        "message": "I'm getting a divorce.",
        "sender": "Anthony"
    }

    dispatcher.send(my_message)
