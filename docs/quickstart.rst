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

.. note::

    | You can skip this step if you already utilize a different driver, such as `Ghost Driver <https://github.com/detro/ghostdriver>`_ or `Edge Driver <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>`_.  
    | Learn more about configuring web drivers in the `documentation <https://docs.kochanow.ski/usos/advanced.html>`_.

4.  Done! Time for some configuration.
