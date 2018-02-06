import os
import sys
from selenium import webdriver

debug = True

def driver():
    if debug:
        options = webdriver.ChromeOptions() 
        options.add_argument("user-data-dir=C:\\Users\\Kochanowski\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium")
        driver = webdriver.Chrome(chrome_options=options)
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        driver_path = dir_path + '/phantomjs'
        driver = webdriver.PhantomJS(executable_path=driver_path)
        driver.set_window_size(1120, 550)

    return driver   