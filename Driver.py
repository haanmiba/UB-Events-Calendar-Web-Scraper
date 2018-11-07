import sys
from Utility import get_driver_path
from UBEventsCalendarScraper import UBEventsCalendarScraper
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


def main():
    path = get_driver_path()

    try:
        scraper = UBEventsCalendarScraper(path)
        scraper.load_page()
        events = scraper.get_events()
        for event in events:
            print(event)
    except WebDriverException as e:
        print(str(e))
        sys.exit()
    except MaxRetryError:
        print('Failed to establish a new connection.')
        sys.exit()


if __name__ == '__main__':
    main()
