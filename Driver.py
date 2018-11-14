import sys
import json
from Utility import read_config_file, InvalidConfigFileTypeError, InvalidConfigFileValueError, print_event, export_json, export_xml, ALLOWED_EXPORT_FILE_TYPES
from UBEventsCalendarScraper import UBEventsCalendarScraper
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


USAGE_STR = '''usage: python Driver.py --config <path>
usage: python Driver.py --path <driver_path> (--head) ([<last_page> | <first_page> <last_page> | --all]) (<output_path>)'''


def main():
    exit_code = 0
    try:
        config = read_config_file()
        scraper = UBEventsCalendarScraper(config)
        events = scraper.scrape_events()
        if config.output:
            if config.output_extension == 'json':
                export_json([evt.__dict__ for evt in events], config.output_path)
            elif config.output_extension == 'xml':
                export_xml([evt.__dict__ for evt in events], config.output_path)
            elif config.output_extension in {'yaml', 'yml'}:
                pass
            else:
                raise InvalidConfigFileValueError('One of the following file extensions must be provided: {}'
                                                  .format(', '.join(ALLOWED_EXPORT_FILE_TYPES)))
        else:
            for evt in events:
                try:
                    print_event(evt)
                    print('-' * 120)
                except UnicodeEncodeError:
                    pass
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
