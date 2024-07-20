from selenium import webdriver
from csv import DictReader

driver = webdriver.Chrome()
driver.get('http://www.facebook.com')

def getCookies(csvfile):
    with open(csvfile, encoding='utf-8-sig') as file:
        dict_reader = DictReader(csvfile)
        listdict = list(dict_reader)
    return listdict

cookies = getCookies('cookie.csv')

for i in cookies:
    driver.add_cookie()

driver.refresh()