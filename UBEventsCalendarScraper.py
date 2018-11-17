import re
from Event import Event
from Scraper import Scraper
from Utility import extract_date_time, extract_contact_info
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class UBEventsCalendarScraper(Scraper):
    """
    Web scraper for the University at Buffalo Events Calendar

    Attributes
    ----------
    config : Configuration
        configuration settings for the web scraper
    event_list : list
        list of events scraped from the University at Buffalo Events Calendar

    Methods
    -------
    deep_scrape(evt)
        `deep scrape` a single event -- scrape data from that event's web page
    scrape_events()
        scrape events from the University at Buffalo Events Calendar based upon the configuration settings
    next_page_button_exists()
        sees whether or not a next page button exists
    click_next_page_button()
        click on the next page button
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config : Configuration
            Configuration settings for the web scraper
        """

        Scraper.__init__(self, config.chromedriver_path, config.headless)
        self.open_url('https://calendar.buffalo.edu/', 'list-event')
        self.config = config
        self.event_list = []

    def deep_scrape(self, evt):
        """`Deep scrape` a single event -- scrape data from that event's web page.

        Parameters
        ----------
        evt : Event
            The event that will have its data scraped
        """

        # Open the event's hyperlink in a new tab
        self.open_url(evt.link, 'accordion-header-link', new_tab=True)

        # Scrape the event's description
        description_elems = self.browser.find_elements_by_xpath(".//div[@itemprop='description']")
        if description_elems:
            evt.description = description_elems[0].text

        # Scrape the event's location
        location_elems = self.browser.find_elements_by_xpath(".//section[@itemprop='location']/p")
        if location_elems:
            evt.location = location_elems[0].text

        # Scrape the event's contact information
        contact_elems = self.browser.find_elements_by_xpath(".//section[@class='event-detail-contact-person']/p")
        if contact_elems:
            evt.contact = extract_contact_info(contact_elems[0].text)

        # Scrape any additional information about the event
        additional_info_labels = self.browser.find_elements_by_xpath(".//div[@class='custom-field-label']")
        additional_info_values = self.browser.find_elements_by_xpath(".//div[@class='custom-field-value']")
        if additional_info_labels and additional_info_values:
            evt.additional_info = {}
            for label, value in zip(additional_info_labels, additional_info_values):
                evt.additional_info[re.sub(':', '', label.text)] = value.text

        # Close the tab
        self.close_tab()

    def scrape_events(self):
        """Scrape events from the University at Buffalo Events Calendar based upon the configuration settings.

        Returns
        -------
        list
            a list of events that were scraped
        """

        current_page = 0
        # While the web scraper has not reached the end page or finished looking at all pages, scrape events
        while current_page < self.config.end_page or self.config.all_pages:

            # If the current page is at or after the page to begin scraping, scrape the page
            if current_page >= self.config.start_page:
                # Get all events on the current page
                event_elements = self.browser.find_elements_by_class_name('list-event-preview')
                for event_elem in event_elements:
                    # Extract the header, event hyperlink, start time, end time, and initialize a new Event
                    header = event_elem.find_element_by_xpath('.//h3/a')
                    date_time = event_elem.find_element_by_xpath('.//p')
                    start, end = extract_date_time(date_time.text, tz='US/Eastern')
                    evt = Event(header.text, header.get_attribute('href'), start, end)

                    # If configuration settings enable deep scraping, deep scrape this event
                    if self.config.deep_scrape:
                        self.deep_scrape(evt)

                    # Append this scraped event to the event list
                    self.event_list.append(evt)

            # If a next page button does not exist, stop scraping
            if not self.next_page_button_exists():
                break

            # Click the next page button
            self.click_next_page_button()

            # Have the ChromeDriver wait until an element with class name `list_event` loads
            wait = WebDriverWait(self.browser, self.timeout)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-event')))

            # Increment the current page the web scraper is on
            current_page += 1

        # Return the event list
        return self.event_list

    def next_page_button_exists(self):
        """Sees whether or not a next page button exists.

        Returns
        -------
        bool
            True -- if a next page button exists
            False -- otherwise
        """

        try:
            self.browser.find_element_by_class_name('icon-angle-right')
        except NoSuchElementException:
            return False
        return True

    def click_next_page_button(self):
        """Click on the next page button."""

        # Get the next page button and click on it
        button_child = self.browser.find_element_by_class_name('icon-angle-right')
        button = button_child.find_element_by_xpath('..')
        button.click()
