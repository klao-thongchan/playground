# import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys # for keyboard control
from selenium.webdriver.common.by import By
from selenium.webdriver.common.window import WindowTypes
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# webdriver path
path = "C:\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(path)

sonystore = "https://store.sony.co.th/collections/playstation-5?sort_by=price-descending"

def getsony():
    driver.get(sonystore)

if __name__ == "__main__":
    print("py started")
    driver.get(sonystore)
    print(driver.find_element(By.CLASS_NAME, 'show_page').text)
    while driver.find_element(By.CLASS_NAME, 'show_page').text >= "16":
        driver.execute_script("location.reload(true);")
        driver.refresh()
        #print("refresh")
        time.sleep(1)
        getsony()
else:
    print("py ended")
