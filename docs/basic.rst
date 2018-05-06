Basic configuration
===================

The .env file
-------------

.. important::

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

.. important::

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
