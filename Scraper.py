from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Scraper:

    def __init__(self, driver_path, headless=True, timeout=10):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        self.browser = webdriver.Chrome(driver_path, chrome_options=options)
        self.timeout = timeout
        self.num_tabs = 1

    def load_page(self, url, class_name):
        try:
            self.browser.get(url)
            wait = WebDriverWait(self.browser, self.timeout)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        except TimeoutException:
            print('Took too long to load the page!')
            self.quit()

    def open_url_in_new_tab(self, url, class_name):
        try:
            self.browser.execute_script("window.open('{}')".format(url))
            self.num_tabs += 1
            wait = WebDriverWait(self.browser, self.timeout)
            wait.until(EC.number_of_windows_to_be(self.num_tabs))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            self.browser.switch_to.window(self.browser.window_handles[-1])
        except TimeoutException:
            print('Took too long to load the page!')
            self.quit()

    def close_tab(self, dest_tab_index=-1):
        self.browser.close()
        self.num_tabs -= 1
        self.browser.switch_to.window(self.browser.window_handles[dest_tab_index])

    def quit(self):
        self.browser.quit()
