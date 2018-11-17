from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Scraper:
    """
    Basic web scraper, running off of selenium

    Attributes
    ----------
    browser : WebDriver
        WebDriver that controls Google Chrome
    timeout : int
        number of seconds that browser will wait for the page to load before timing out (default 10 seconds)
    num_tabs : int
        number of tabs currently open in browser's Google Chrome session

    Methods
    -------
    open_url(url, class_name, new_tab=False)
        opens a url
    close_tab(close_tab_idx=-1, dest_tab_idx=-1)
        closes a tab
    quit()
        quits the WebDriver and closes the Google Chrome session
    """

    def __init__(self, driver_path, headless=True, timeout=10):
        """
        Parameters
        ----------
        driver_path : str
            path to the ChromeDriver executable
        headless : bool
            whether or not the ChromeDriver should run headless (w/o GUI) (default True)
        timeout : int
            number of seconds that browser will wait for the page to load before timing out (default 10 seconds)
        """

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        self.browser = webdriver.Chrome(driver_path, chrome_options=options)
        self.timeout = timeout
        self.num_tabs = 1

    def open_url(self, url, class_name, new_tab=False):
        """Opens a url.

        Parameters
        ----------
        url : str
            A hyperlink for ChromeDriver to open
        class_name : str
            The class name of an element that ChromeDriver will wait until it is loaded for the page to be `ready`
        new_tab : bool
            Whether or not this url will be opened in the current tab or in a new tab

        Raises
        ------
        TimeoutError
            If the page takes too long to load or if an element with the class `class_name` cannot be found.
        """

        # If new_tab, open the hyperlink in a new tab, increment num_tabs, and switch to the new tab.
        if new_tab:
            self.browser.execute_script("window.open('{}')".format(url))
            self.num_tabs += 1
            self.browser.switch_to.window(self.browser.window_handles[-1])
        # Else, open the hyperlink in this tab.
        else:
            self.browser.get(url)

        # Have the ChromeDriver wait up to timeout seconds for the page to load.
        wait = WebDriverWait(self.browser, self.timeout)

        # If opening the hyperlink in a new tab, wait for the
        # ChromeDriver session to have num_tabs amount of tabs opened.
        if new_tab:
            wait.until(EC.number_of_windows_to_be(self.num_tabs))

        # Have the ChromeDriver wait for an element with class `class_name` to be loaded.
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    def close_tab(self, close_tab_idx=-1, dest_tab_idx=-1):
        """Closes a tab.

        Parameters
        ----------
        close_tab_idx : int
        :param close_tab_idx:
        :param dest_tab_idx:
        :return:
        """

        # Switch to the tab at close_tab_idx, close the tab, decrement the num_tabs opened,
        # and switch to the tab at dest_tab_idx.
        self.browser.switch_to.window(self.browser.window_handles[close_tab_idx])
        self.browser.close()
        self.num_tabs -= 1
        self.browser.switch_to.window(self.browser.window_handles[dest_tab_idx])

    def quit(self):
        """Quits the WebDriver and closes the Google Chrome session."""

        self.browser.quit()
