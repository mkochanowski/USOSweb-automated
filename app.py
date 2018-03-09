import logging
import sys
import re
import hashlib
import json
import config
import yagmail
import traceback
from bs4 import BeautifulSoup

driver = config.driver()
env = config.os.environ

log = logging.getLogger()
log.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

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

    def comparison(self, old, new):
        result_string = "<span style='color: red;'>{}</span>→<strong style='color: green;'>{}</strong>".format(old, new)
        return result_string

    def tests_summary(self, header):
        log.info("Creating summary for tests")
        
        if len(self.tests) > 0:
            self.message += "<br/><strong>{}</strong><br/>".format(header)
            for element in self.tests:
                self.message += "{}: {}<br/>".format(element['entry_name'], self.comparison(element['old_result'], element['result']))
                if 'comment' in element:
                    self.message += '↳ <small><i>{}</i></small> <br/>'.format(element['comment'])

    def grades_summary(self, header):
        log.info("Creating summary for grades")
        
        if len(self.grades) > 0:
            self.message += "<br/><strong>{}</strong><br/>".format(header)
            for element in self.grades:
                self.message += "{}: {}<br/>".format(
                    element['course'], 
                    self.comparison(element['old_grade'], element['grade'])
                )
    
    def build_mail_template(self):
        log.info("Initializing template")

        self.message = '<link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,600,700&amp;subset=latin-ext" rel="stylesheet"><div style="font-family: \'Source Sans Pro\', sans-serif;">'
        self.message += "Skrypt wykrył, że zaszły następujące zmiany:<br/>"
        
        self.tests_summary("Sprawdziany / punkty")
        self.grades_summary("Oceny semestralne")
        
        log.info("Template building complete")

    def send(self):
        log.info("NotificationStream: Check whether any changes have been made")
        if len(self.grades) > 0 or len(self.tests) > 0:
            log.info("NotificationStream: sending notification")
            yag = yagmail.SMTP("askxememah@gmail.com", oauth2_file="oauth2_creds.json")
            
            self.build_mail_template()
            yag.send('uwr-usos@kochanow.ski', 'USOS: Powiadomienie o nowych wynikach', self.message)
            log.info("E-mail notification sent")
        else:
            log.info("NotificationStream: No changes detected, terminating")

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
        log.info("Initialize comparing grades for [{}]".format(self.hash))
        current_data = []
        try:
            with open(self.filename, 'r') as working_file:  
                try:
                    current_data = json.load(working_file)
                    log.info("Fetching JSON successful")
                except:
                    log.info("Fetching JSON failed")
        except IOError:
            log.info("File does not exist")

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
                    element['old_grade'] = old['grade']
                    notification_stream.add_grade(element)

        with open(self.filename, 'w') as working_file:  
            json.dump(grades, working_file)

    def compare_tests(self, data):
        log.info("Initialize comparing tests for [{}]".format(self.hash))
        current_data = []
        try:
            with open(self.filename, 'r') as working_file:  
                try:
                    current_data = json.load(working_file)
                    log.info("Fetching JSON successful")
                except:
                    log.info("Fetching JSON failed")
        except IOError:
            log.info("File does not exist")

        for element in data:
            for old in current_data:
                if old['entry_name'] == element['entry_name'] and old['unique_id'] == element['unique_id']:
                    if "result" not in old:
                        old['result'] = "(brak wyniku)"
                    if "result" not in element:
                        element['result'] = "(brak wyniku)"
                    if old['result'] != element['result']:
                        element['old_result'] = old['result']
                        notification_stream.add_test(element)

        with open(self.filename, 'w') as working_file:  
            json.dump(data, working_file)
class PageController:
    def __init__(self, url):
        self.url = url

    def tests_single(self):
        log.info("Scrape single test category")
        try:
            scraped_entries = []
            tree = driver.find_element_by_id("drzewo")
            soup = BeautifulSoup(tree.get_attribute("innerHTML"), "html.parser")
            soup = soup.find_all("table")
            unique_id = 100
            for table in soup:
                items = table.find_all("td")
                new_element = {}
                for item in items:
                    title = item.contents[0].strip()
                    if title:
                        new_element['entry_name'] = title
                    for i in item.contents:
                        if i.name != None:
                            if "Dodatkowy opis:" not in i.text and "- max" not in i.text and "Związane grupy" not in i.text and "korze" not in i.text and i.text and "- ocena" not in i.text:
                                content = i.text
                                content = re.sub(r'[\ \n]{2,}', '', content)
                                # print(i.name, content)

                                if i.name == 'b':
                                    new_element['result'] = content
                                if i.name == 'span' and 'pkt' in i.text and 'result' in new_element:
                                    new_element['result'] += " pkt"
                                if i.name == 'span' and 'brak' in i.text:
                                    new_element['result'] = i.text

                                if 'comment' in new_element:
                                    new_element['comment'] += " " + i.text.strip()
                                    if "Komentarz" in i.text:
                                        new_element['comment'] += " Sprawdź na USOS"

                                if "Wystawiający" in i.text:
                                    new_element['comment'] = i.text
                    
                if new_element:
                    new_element['unique_id'] = unique_id
                    unique_id += 1
                    scraped_entries.append(new_element)

            data = DataController(self.url)
            data.compare_tests(scraped_entries)
        except Exception as e:
            log.info("Scraping terminated, exception occured")
            log.warn(repr(e))
            log.warn(traceback.format_exc())

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
            log.warn(traceback.format_exc())

    def perform(self):
        if "studia/sprawdziany/index" in self.url:
            log.info("Index of tests opened")
            self.tests_index()
        elif "studia/oceny/index" in self.url:
            log.info("Index of grades opened")
            self.grades_index()
        elif "studia/sprawdziany/pokaz" in self.url:
            log.info("Single test opened")
            self.tests_single()
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