import logging

logging = logging.getLogger(__name__)


class Credentials:
    """Manages and stores credentials required to successfully authenticate 
    the user.
    
    Firing up a new user instance is very simple::
    
        from usos.authentication import Credentials
        
        credentials = Credentials(
            username="123456", 
            password="password")
    
    That way, you can set up and manage multiple accounts, for example::

        john = Credentials(username="johndoe", password="...")
        anna = Credentials(username="anna1995", password="...")
    
    :param username: username used in the Central Authentication System
    :param password: password bound to the username
    """
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class Authentication:
    """Authenticates the user with provided credentials.

    Once you retrieve an instance of user's :class:`Credentials`, you 
    can proceed further with authentication. 
    In this example, an environmental variable ``USOS_SCRAPER_ROOT_URL``
    is used as a root URL of the requested USOSweb application. ::

        from usos.authentication import Authentication
        
        ...

        auth = Authentication(
            credentials=john, 
            root_url=os.environ["USOS_SCRAPER_ROOT_URL"], 
            web_driver=selenium_driver)

    :param credentials: username and password in an instance of 
        :class:`Credentials`.
    :param root_url: root url of the USOSweb application the login 
        procedure will be executed on.
    :param web_driver: an instance of 
        :class:`usos.web_driver.SeleniumDriver` responsible for 
        controlling the browser.
    """
    def __init__(self, credentials: object, root_url: str,
                 web_driver: object) -> None:
        self.user_authenticated = False
        self.username = credentials.username
        self.password = credentials.password
        self.driver = web_driver
        self.root_url = root_url

    def sign_in(self) -> bool:
        """Performs the sign in procedure using a ``web_driver`` provided 
        to the initializer.

        :returns: ``True`` if the procedure was successful.
        """
        logging.info("Initializing login procedure")

        self.driver.get(self.root_url + "&lang=pl")

        if not self._is_username_present_in_topbar():
            try:
                self.driver.find_element_by_link_text(
                    "zaloguj się").click()

                self._perform_login()

            except:
                logging.exception("Login button could not be found")
                self.driver.quit()

        if self._is_username_present_in_topbar():
            self.user_authenticated = True
            return True
        return False

    def is_authenticated(self) -> bool:
        """Checks whether the user is authenticated.
        
        Current implementation of this method firstly checks whether the
        user has been recently signed in, and if that condition is 
        negative, attempts to execute :meth:`sign_in`. ::

            if auth.is_authenticated():
                # Even though the user has not been signed in before,
                # the method will attempt to do it for him and if it 
                # succeeds, do_serious_stuff() will be executed.

                do_serious_stuff()

        
        :returns: ``False`` only if the authenication process has 
            failed."""
        if self.user_authenticated:
            logging.info("User already authenticated")
            return True
        else:
            logging.info("First authorization")
            return self.sign_in()

    def _perform_login(self) -> None:
        """Fills the sign in form with credentials passed in the 
        initializer."""
        try:
            self.driver.find_element_by_name(
                "username").send_keys(self.username)
            self.driver.find_element_by_name(
                "password").send_keys(self.password)
            self.driver.find_element_by_name("rememberMe").click()
            self.driver.find_element_by_name(
                "password").send_keys(u'\ue007')

            logging.info("Login procedure finished")
        except:
            logging.exception("Credentials could not be entered")
            self.driver.quit()

    def _is_username_present_in_topbar(self) -> bool:
        """Checks whether the username is present in the top bar of 
        Central Authentication System.
        """
        try:
            top_bar = self.driver.find_element_by_xpath(
                '//*[@id="casmenu"]/table/tbody/tr/td[2]')

            if "Zalogowany użytkownik:" in top_bar.text:
                logging.debug("Username is present in the top bar")
                self.authenticated = True
                return True
                
            self.authenticated = False
        except:
            logging.exception("Top bar could not be located")
            self.driver.quit()

        return False
