import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv
from selenium import webdriver

if os.path.isfile('.env'):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

def driver():
    if not os.environ['DRIVER_HEADLESS']:
        options = webdriver.ChromeOptions() 
        options.add_argument("user-data-dir=C:\\Users\\Kochanowski\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium")
        driver = webdriver.Chrome(chrome_options=options)
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        driver_path = dir_path + '/phantomjs'
        driver = webdriver.PhantomJS(executable_path=driver_path)
        driver.set_window_size(1120, 550)

    return driver   