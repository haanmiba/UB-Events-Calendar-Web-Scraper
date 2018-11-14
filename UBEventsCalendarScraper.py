import re
from Event import Event
from Scraper import Scraper
from Utility import extract_date_time, extract_contact_info
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class UBEventsCalendarScraper(Scraper):

    def __init__(self, config):
        Scraper.__init__(self, config.chromedriver_path, config.headless)
        self.open_url('https://calendar.buffalo.edu/', 'list-event')
        self.config = config
        self.event_list = []

    def deep_scrape(self, evt):
        self.open_url(evt.link, 'accordion-header-link', new_tab=True)

        description_elems = self.browser.find_elements_by_xpath(".//div[@itemprop='description']")
        if description_elems:
            evt.description = description_elems[0].text

        location_elems = self.browser.find_elements_by_xpath(".//section[@itemprop='location']/p")
        if location_elems:
            evt.location = location_elems[0].text

        contact_elems = self.browser.find_elements_by_xpath(".//section[@class='event-detail-contact-person']/p")
        if contact_elems:
            evt.contact = extract_contact_info(contact_elems[0].text)

        additional_info_labels = self.browser.find_elements_by_xpath(".//div[@class='custom-field-label']")
        additional_info_values = self.browser.find_elements_by_xpath(".//div[@class='custom-field-value']")
        if additional_info_labels and additional_info_values:
            evt.additional_info = {}
            for label, value in zip(additional_info_labels, additional_info_values):
                evt.additional_info[re.sub(':', '', label.text)] = value.text

        self.close_tab()

    def scrape_events(self):
        current_page = 0
        while current_page < self.config.end_page or self.config.all_pages:

            if self.config.start_page <= current_page:
                event_elements = self.browser.find_elements_by_class_name('list-event-preview')
                for event_elem in event_elements:
                    header = event_elem.find_element_by_xpath('.//h3/a')
                    date_time = event_elem.find_element_by_xpath('.//p')
                    start, end = extract_date_time(date_time.text, tz='US/Eastern')
                    evt = Event(header.text, header.get_attribute('href'), start, end)

                    if self.config.deep_scrape:
                        self.deep_scrape(evt)

                    self.event_list.append(evt)

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
