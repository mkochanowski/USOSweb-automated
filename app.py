import browser
import logging
import sys
import re
import hashlib
import json
import config
from bs4 import BeautifulSoup

driver = browser.driver()
env = config.os.environ
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class NotificationStream:
    def __init__(self):
        self.message = ""
        self.grades = []
        self.tests = []

    def add_grade(self, grade):
        log.info("NotificationStream: Adding fresh grade")
        self.grades.append(grade)

    def add_test(self, test):
        log.info("NotificationStream: Adding fresh test")
        self.tests.append(test)

    def send(self):
        log.info("NotificationStream: sending notification")
        print("New test results:", self.tests)
        print("New grades:", self.grades)

notification_stream = NotificationStream()

class Credentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Authorization:
    def __init__(self, credentials):
        self.authorized = False
        self.username = credentials.username
        self.password = credentials.password

    def login(self):
        logging.info("Initializing login procedure")
        
        driver.get("https://usosweb.uni.wroc.pl/kontroler.php?_action=dla_stud/index")
        top_bar = driver.find_element_by_xpath('//*[@id="casmenu"]/table/tbody/tr/td[2]')
        if "Zalogowany użytkownik:" in top_bar.text:
            log.info("User already logged in")
            self.authorized = True
            return True

        try:
            login_button = driver.find_element_by_link_text('zaloguj się').click()
        except Exception as e:
            log.info("Login button could not be found")

        driver.find_element_by_name("username").send_keys(self.username)
        driver.find_element_by_name("password").send_keys(self.password)
        driver.find_element_by_name("rememberMe").click()
        driver.find_element_by_name("password").send_keys(u'\ue007')

        log.info("User successfully logged in. Saving state")
        self.authorized = True
        return True

    def is_authorized(self):
        if self.authorized: 
            log.info("User already authorized")
            return True
        else: 
            log.info("First authorization")
            return self.login()

class DataController:
    __data_directory = "data"

    def __init__(self, url):
        self.url = url
        url_encoded = url.encode('utf-8')
        self.hash = hashlib.md5(url_encoded).hexdigest()
        self.filename = "{}/{}.json".format(self.__data_directory, self.hash)

    def compare_grades(self, data):
        log.info("Initialize comparing grades for {}".format(self.hash))
        current_data = []
        with open(self.filename, 'r') as working_file:  
            try:
                current_data = json.load(working_file)
                log.info("Fetching JSON successful")
            except:
                log.info("Fetching JSON failed")

        grades = []
        for element in data:
            element = {
                'course': element[0],
                'semester': element[1],
                'grade': element[2]
            }
            grades.append(element)
        
        for element in grades:
            for old in current_data:
                if old['course'] == element['course'] and old['semester'] == element['semester'] and old['grade'] != element['grade']:
                    notification_stream.add_grade(element)

        with open(self.filename, 'w') as working_file:  
            json.dump(grades, working_file)

    def compare_tests(self, data):
        log.info("Initialize comparing tests for {}".format(self.hash))

class PageController:
    def __init__(self, url):
        self.url = url

    def tests_index(self):
        global urls_to_check
        log.info("Scrape index of tests")
        links = driver.find_elements_by_class_name("fwdlink")
        for link in links:
            print(link.get_attribute("href"))
            log.info("Add a new url to queue")
            urls_to_check.append(link.get_attribute("href"))

    def grades_column_beautify(self, text):
        text = text.replace(":", ": ")
        text = text.replace("(", " (")
        text = text.replace(")", ") ")
        for number in range(0, 10):
            text = text.replace(str(number), str(number) + " ")
        text = text.replace(" ,", ",")
        text = text.replace(", ", ",")
        return text

    def grades_index(self):
        log.info("Scrape index of grades")
        try:
            scraped_grades = []
            grades = driver.find_element_by_id("tab1")
            soup = BeautifulSoup(grades.get_attribute("innerHTML"), "html.parser")
            grades = soup.find_all('tr')
            columns = soup.find_all('td')
            index = 0
            element = []
            for column in columns:
                content = column.text
                content = content.replace("\n", " ")
                content = re.sub(r'[\ \n]{2,}', '', content)
                if index == 2:
                    content = self.grades_column_beautify(content)
                content = content.strip()
                if index == 3: 
                    index = 0
                    scraped_grades.append(element)
                    element = []
                else: 
                    index += 1
                    element.append(content)

            data = DataController(self.url)
            data.compare_grades(scraped_grades)
        except Exception as e:
            log.info("Scraping terminated, exception occured")
            log.warn(repr(e))

    def perform(self):
        if "studia/sprawdziany/index" in self.url:
            log.info("Index of tests opened")
            self.tests_index()
        elif "studia/oceny/index" in self.url:
            log.info("Index of grades opened")
            self.grades_index()
        else:
            log.info("No action programmed for that url: {}".format(self.url))

urls_to_check = [
    "https://usosweb.uni.wroc.pl/kontroler.php?_action=dla_stud/studia/oceny/index",
    "https://usosweb.uni.wroc.pl/kontroler.php?_action=dla_stud/studia/sprawdziany/index"
]

credentials = Credentials(env['USOS_USER'], env['USOS_PASS'])
authorization = Authorization(credentials)

for url in urls_to_check:
    if authorization.is_authorized():
        log.info("Navigate to {}".format(url))
        driver.get(url)
        action = PageController(url)
        action.perform()

notification_stream.send()

driver.quit()