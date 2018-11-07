from Event import Event
from Scraper import Scraper
from Utility import extract_date_time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class UBEventsCalendarScraper(Scraper):

    def __init__(self, driver_path, url='https://calendar.buffalo.edu/', timeout=10):
        Scraper.__init__(self, driver_path, url, element='list-event', timeout=timeout)
        self.event_list = []

    def get_events(self, num_pages=1, all_events=False):
        if not self.page_loaded:
            self.load_page()

        current_page = 0
        while current_page < num_pages or all_events:
            event_elements = self.browser.find_elements_by_class_name('list-event-preview')
            for event_elem in event_elements:
                header = event_elem.find_element_by_xpath('.//h3/a')
                date_time = event_elem.find_element_by_xpath('.//p')
                start, end = extract_date_time(date_time.text, tz='US/Eastern')

                ev = Event(header.text, header.get_attribute('href'), start, end)
                self.event_list.append(ev)

            if not self.next_page_button_exists():
                break

            button = self.get_next_page_button()
            button.click()
            wait = WebDriverWait(self.browser, self.timeout)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-event')))
            current_page += 1

        return self.event_list

    def next_page_button_exists(self):
        try:
            self.browser.find_element_by_class_name('icon-angle-right')
        except NoSuchElementException:
            return False
        return True

    def get_next_page_button(self):
        button_child = self.browser.find_element_by_class_name('icon-angle-right')
        button = button_child.find_element_by_xpath('..')
        return button
