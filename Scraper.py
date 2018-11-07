from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Scraper:

    def __init__(self, driver_path, url, element, timeout=10):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.browser = webdriver.Chrome(driver_path, chrome_options=options)
        self.url = url
        self.element = element
        self.timeout = timeout
        self.page_loaded = False

    def load_page(self):
        self.page_loaded = False
        try:
            self.browser.get(self.url)
            wait = WebDriverWait(self.browser, self.timeout)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, self.element)))
            self.page_loaded = True
        except TimeoutException:
            print('Took too long to load the page!')
            self.quit()

    def quit(self):
        self.browser.quit()
