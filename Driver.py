import sys
from Utility import (read_config_file, read_args,
                     InvalidConfigFileTypeError, InvalidConfigFileValueError,
                     OverwriteExistingFileError, print_events, export_events)
from UBEventsCalendarScraper import UBEventsCalendarScraper
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


USAGE_STR = '''usage: python Driver.py --config <path>
usage: python Driver.py --path <driver_path> (--head) (--deep) (--print) ([<last_page> | <first_page> <last_page> | --all]) (--export <export_path>) (--overwrite)'''

ALLOWED_ARGS = {'--config', '--path', '--head', '--deep', '--print', '--all', '--export', '--overwrite'}


def main():
    if len(sys.argv) < 3:
        print('This program requires at least 3 command line arguments.')
        print(USAGE_STR)
        sys.exit(1)

    invalid_args = set(filter(lambda x: x.startswith('--'), sys.argv)) - ALLOWED_ARGS
    if invalid_args:
        print('`{}` is not a valid argument.'.format(next(iter(invalid_args))))
        print(USAGE_STR)
        sys.exit(1)

    exit_code = 0
    try:
        if sys.argv[1] == '--config':
            config = read_config_file(sys.argv[2])
        elif sys.argv[1] == '--path':
            config = read_args(sys.argv)
        scraper = UBEventsCalendarScraper(config)
        events = scraper.scrape_events()
        if config.export:
            export_events(events, config)
        if config.print_events:
            print_events(events)
    except (InvalidConfigFileTypeError, InvalidConfigFileValueError) as e:
        print('{}: {}'.format(e.__class__.__name__, str(e)))
        exit_code = 1
    except (WebDriverException, OverwriteExistingFileError) as e:
        scraper.quit()
        print('{}: {}'.format(e.__class__.__name__, str(e)))
        exit_code = 1
    except MaxRetryError:
        scraper.quit()
        print('Failed to establish a new connection with https://calendar.buffalo.edu/. Check network connection.')
        exit_code = 2
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
