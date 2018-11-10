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

    def open_url(self, url, class_name, new_tab=False):
        try:
            if new_tab:
                self.browser.execute_script("window.open('{}')".format(url))
                self.num_tabs += 1
                self.browser.switch_to.window(self.browser.window_handles[-1])
            else:
                self.browser.get(url)

            wait = WebDriverWait(self.browser, self.timeout)
            if new_tab:
                wait.until(EC.number_of_windows_to_be(self.num_tabs))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

        except TimeoutException:
            print('Took too long to load the page!')
            self.quit()

    def close_tab(self, close_tab_idx=-1, dest_tab_idx=-1):
        self.browser.switch_to.window(self.browser.window_handles[close_tab_idx])
        self.browser.close()
        self.num_tabs -= 1
        self.browser.switch_to.window(self.browser.window_handles[dest_tab_idx])

    def quit(self):
        self.browser.quit()
