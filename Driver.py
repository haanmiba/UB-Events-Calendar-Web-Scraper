import sys
from Utility import read_config_file, InvalidConfigFileTypeError, InvalidConfigFileValueError, print_events, export_events
from UBEventsCalendarScraper import UBEventsCalendarScraper
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


USAGE_STR = '''usage: python Driver.py --config <path>
usage: python Driver.py --path <driver_path> (--head) ([<last_page> | <first_page> <last_page> | --all]) (<export_path>)'''


def main():
    exit_code = 0
    try:
        config = read_config_file()
        scraper = UBEventsCalendarScraper(config)
        events = scraper.scrape_events()
        if config.export:
            export_events(events, config)
        if config.print_events:
            print_events(events)
    except (InvalidConfigFileTypeError, InvalidConfigFileValueError) as e:
        print(str(e))
        exit_code = 1
    except WebDriverException as e:
        scraper.quit()
        print(str(e))
        exit_code = 1
    except MaxRetryError:
        scraper.quit()
        print('Failed to establish a new connection with https://calendar.buffalo.edu/. Check network connection.')
        exit_code = 2
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
