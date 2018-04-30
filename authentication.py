import logging

logging = logging.getLogger(__name__)


class Credentials:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class Authentication:
    def __init__(self, credentials: object, root_url: str,
                 web_driver: object) -> None:
        self.user_authenticated = False
        self.username = credentials.username
        self.password = credentials.password
        self.driver = web_driver
        self.root_url = root_url

    def sign_in(self) -> bool:
        logging.info("Initializing login procedure")

        self.driver.get(self.root_url)

        if not self._is_username_present_in_topbar():
            try:
                self.driver.find_element_by_link_text(
                    "zaloguj się").click()
                
                self._perform_login()
                
            except:
                logging.exception("Login button could not be found")

        if self._is_username_present_in_topbar():
            self.user_authenticated = True
            return True
        return False

    def is_authenticated(self) -> bool:
        if self.user_authenticated:
            logging.info("User already authenticated")
            return True
        else:
            logging.info("First authorization")
            return self.sign_in()

    def _perform_login(self) -> None:
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

    def _is_username_present_in_topbar(self) -> bool:
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

        return False
