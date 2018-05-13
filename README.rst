USOSweb Automated - with Python!
################################

.. image:: https://www.travis-ci.com/mkochanowski/USOSweb-automated.svg?token=mjTA3RTxEXwwcJqa4ige&branch=master
    :target: https://www.travis-ci.com/mkochanowski/USOSweb-automated
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/mkochanowski/USOSweb-automated/blob/master/LICENSE.md
.. image:: https://img.shields.io/badge/python-3.3%2C%203.4%2C%203.5%2C%203.6-blue.svg
    :target: #getting-started

.. contents:: \

.. section-numbering::

The project
===========

This package provides functionality to automate tasks on the USOSweb Interface.

| It also adds support for the most needed and requested feature of all time - notifications!
| Setup takes only **5 minutes** and extending the script's functionality is a child's play.  
|
| The app uses ``Selenium`` for navigating the interface and ``BeautifulSoup4`` for parsing in the ScrapingTemplates.

Getting started
===============
1.  A good place to start is to clone the repository:

.. code-block:: bash

    git clone https://github.com/mkochanowski/USOSweb-automated.git

2.  Inside the project's root directory create a new virtual environment, then activate it:

.. code-block:: bash

    python3 -m venv venv

.. code-block:: bash

    # to activate on Linux:
    source venv/bin/activate 
    
    # to activate on Windows:
    .\venv\Scripts\activate


3. 	Now you can safely install required packages:
    
.. code-block:: bash

    pip install -r requirements.txt

4.  For automating the browser, install 
    `Chrome Driver <https://sites.google.com/a/chromium.org/chromedriver/downloads>`_.

    | You can skip this step if you already utilize a different driver, such as `Ghost Driver <https://github.com/detro/ghostdriver>`_ or `Edge Driver <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>`_.  
    | Learn more about configuring web drivers in the `documentation <https://docs.kochanow.ski/usos/advanced.html>`_.

4.  Done! Time for some configuration.

Basic configuration
===================

The .env file
-------------

    Your app will not execute without a properly configured ``.env`` file.  

This project comes with a ``.env.sample`` to help you get started. You only need to introduce minor changes.

The file's contents are:

.. code-block:: bash

    USOS_SETTINGS_USERNAME=""
    USOS_SETTINGS_PASSWORD=""

    USOS_SCRAPER_ROOT_URL="https://usosweb.uni.wroc.pl/kontroler.php?_action="
    USOS_SCRAPER_DESTINATIONS="dla_stud/studia/oceny/index dla_stud/studia/sprawdziany/index"
    USOS_SCRAPER_MINIMUM_DELAY=4
    USOS_SCRAPER_WEBDRIVER_HEADLESS=False
    USOS_SCRAPER_DEBUG_MODE=True

    USOS_NOTIFICATIONS_ENABLE=True
    USOS_NOTIFICATIONS_STREAMS="Email WebPush SMS"
    USOS_NOTIFICATIONS_CONFIG_FILE="notifications_config.json"


+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| Name of the setting                 | Description                                                                                     | Default value   |
+=====================================+=================================================================================================+=================+
| ``USOS_SETTINGS_USERNAME``          |                                                                                                 |                 |
+-------------------------------------+ Credentials neeeded for the process of authentication on the USOSweb interface.                 | Empty strings   |
| ``USOS_SETTINGS_PASSWORD``          |                                                                                                 |                 |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_SCRAPER_ROOT_URL``           | A root url of the USOSweb application. The default root url includes a GET parameter ``action`` | A root url for  |
|                                     | because it is used throughout the interface U might think of it as a representation of a        | the University  |
|                                     | structure similiar to ``http://usosweb.app/action/``.                                           | of Wroclaw      |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_SCRAPER_DESTINATIONS``       | Predefined actions (destinations) that will be visited by the scraper after calling             | Final grades and|
|                                     | the `run() <https://docs.kochanow.ski/usos/api.html#usos.scraper.Scraper.run>`_ method.         | course results  |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_SCRAPER_MINIMUM_DELAY``      | Minimum delay between individual executions of the ``app.py`` main script. Do not exploit the   | 4 minutes (don't|
|                                     | services you're using because you might get in trouble!                                         | go any lower)   |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_SCRAPER_WEBDRIVER_HEADLESS`` | Whether to run the web driver in headless mode (in other words: silently, without the browser   | ``False``       |
|                                     | window appearing). You might want to disable it for debugging or developing new interactions.   |                 |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_SCRAPER_DEBUG_MODE``         | Whether to run the application in debug mode that provides more additional logging statements.  | ``True``        |
|                                     | Enable it only on your local development environement to avoid collecting unnnecessary data.    |                 |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_NOTIFICATIONS_ENABLE``       | Whether to allow the dispatcher to send any notifications via configured channels.              | ``True``        |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_NOTIFICATIONS_STREAMS``      | Streams (channels) are user-configurable medias for delivering the notifications such as Email, | Email and other |
|                                     | Text messages or direct WebPush notifications to your browser.                                  | examples        |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+
| ``USOS_NOTIFICATIONS_CONFIG_FILE``  | Path to the configuration file responsible for providing necessary variables such as API Keys   | A file provided |
|                                     | or special parameters to individual channels. Utilizing a separate source for config data will  | with a project. |
|                                     | allow you to design streams that are much more flexible.                                        |                 |
+-------------------------------------+-------------------------------------------------------------------------------------------------+-----------------+

Input the credentials and the root url of the USOSweb app you want to access and you're good to go! 

To execute the app, run:

.. code-block:: bash

    python3 app.py

Receiving notifications
-----------------------

This script supports dispatching notifications via multiple channels, but Email is the one implemented by default. 
Initially, it comes with `yagmail <https://github.com/kootenpv/yagmail>`_ preinstalled, but you're free to replace it with a different library if needed.

To use yagmail you will need to configure OAuth2: `Configuring yagmail <https://github.com/kootenpv/yagmail#oauth2>`_. 
You can place the ``oauth2_creds.json`` file in the root directory of your project.

| Lastly, update the ``notifications_config.json`` with the recipient and sender email addresses. 
| You can now send notifications via email!

Monitoring for changes
----------------------

    When running on a server, remember to set ``USOS_SCRAPER_DEBUG_MODE=False`` and ``USOS_SCRAPER_WEBDRIVER_HEADLESS=True`` in the ``.env`` file. 

1.  Now that you made sure the app is configured and fully working, let's deploy it to our server.
    
    There are different ways of doing that, the most basic one would be to replicate the steps in `Getting started <#getting-started>`_ guide and copy the configuration files from your local machine.

2.  Let's set up a script that will execute the app inside of the virtual environment.

    It may look like this:

    .. code-block:: bash

        #!/bin/bash
        cd /home/username/USOSweb-automated
        source venv/bin/activate
        python3 app.py

    Replace the path with the directory you installed the script in and save the file as ``cron.sh``.

3.  The last step is to add the script to the crontab.

    Open the crontab by running:

    .. code-block:: bash

        crontab -e
    
    And add the script:

    .. code-block:: bash

        */10 * * * * /home/username/USOSweb-automated/cron.sh

    That means the ``cron.sh`` script will be executed every 10 minutes.

4.  Congratulations! Your project is fully set up.

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


Defining new entities
~~~~~~~~~~~~~~~~~~~~~

    | The current implementation of an **Entity** will be replaced in the future by an independant data structure.
    | Honestly, operating on dictionaries instead of a dedicated class feels a little weird for such an important element.

| An ``Entity`` is a dictionary structure that contains two keys: ``entity`` and ``items``.
| Think about it not only as a data type, but also as an abstraction that defines its *purpose*.

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

Entity ``course-results-tree`` defines not only what it stores in the ``items`` key, but also how to process the data - the defined behaviour is to compare the supplied items with existing data to search for changes.

1. If you want to introduce a new entity, start with a ScrapingTemplate. This is the very first step of a lifecycle of an entity.
2. Add custom behaviour for the specific entity you're implementing. Check and if needed, expand methods ``_get_filename()`` and ``analyze()`` of the ``usos.data.DataController`` class.
3. Update your rendering templates to support this type of entity.
4. Great! You now have a new type of entity that supports custom behaviour.

Notifications
-------------

Writing message templates
~~~~~~~~~~~~~~~~~~~~~~~~~

    This package comes with `Jinja2 <http://jinja.pocoo.org/>`_ as a default templating engine.

| Everybody loves Jinja2. That's why it is used as a default templating engine for this project.
| You can add your own templates by putting them into the ``templates/notifications/`` directory.

To learn more about writing templates in Jinja2, check out the `documentation <http://jinja.pocoo.org/>`_.

Implementing additional Streams (channels)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Streams are defined in ``usos/notifications.py``. To add your own channel, just subclass ``Notification`` and implement two private methods: 
``_render()`` and ``_send()``. 

The Dispatcher class automatically sets the ``self.data`` and ``self.config`` attributes that supply results from the DataController as well as channel-specific key variables from ``notifications_config.json`` file.

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

API Reference
=============

Visit https://docs.kochanow.ski/usos/api.html to get more information.
