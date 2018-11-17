import sys
from Utility import (read_config_file, read_args,
                     InvalidConfigFileTypeError, InvalidConfigFileValueError,
                     OverwriteExistingFileError, print_events, export_events)
from UBEventsCalendarScraper import UBEventsCalendarScraper
from selenium.common.exceptions import WebDriverException, TimeoutException
from urllib3.exceptions import MaxRetryError


# Usage message that represents the correct command line usage.
USAGE_STR = '''usage: python Driver.py --config <path>
usage: python Driver.py --path <driver_path> (--head) (--deep) (--print) ([<last_page> | <first_page> <last_page> | --all]) (--export <export_path>) (--overwrite)'''

# Set of allowed command line arguments.
ALLOWED_FLAGS = {'--config', '--path', '--head', '--deep', '--print', '--all', '--export', '--overwrite'}


def main():
    """Main method to scrape data from the University at Buffalo Events Calendar."""

    # Check if the user input less than 3 command line arguments. If so, terminate the program with exit code 1.
    if len(sys.argv) < 3:
        print('This program requires at least 3 command line arguments.')
        print(USAGE_STR)
        sys.exit(1)

    # Check if the user used an invalid argument. If so, terminate the program with exit code 1.
    invalid_args = set(filter(lambda x: x.startswith('--'), sys.argv)) - ALLOWED_FLAGS
    if invalid_args:
        print('`{}` is not a valid argument.'.format(next(iter(invalid_args))))
        print(USAGE_STR)
        sys.exit(1)

    exit_code = 0
    try:
        # If the second command line argument is `--config`, create configurations from a config file.
        if sys.argv[1] == '--config':
            config = read_config_file(sys.argv[2])
        # Else, if the second command line argument is `--path`, create configurations from the command line argmuents.
        elif sys.argv[1] == '--path':
            config = read_args(sys.argv)

        scraper = UBEventsCalendarScraper(config)  # Initialize a web scraper for the UB Events Calendar.
        events = scraper.scrape_events()           # Scrape events from the UB Events Calendar.

        # Export the scraped events if the config allows exporting.
        if config.export:
            export_events(events, config)

        # Print out the scraped events if the config allows printing.
        if config.print_events:
            print_events(events)

    # Handle exceptions that deal with issues with the configuration file or overwriting an existing file.
    except (InvalidConfigFileTypeError, InvalidConfigFileValueError, OverwriteExistingFileError) as e:
        print('{}: {}'.format(e.__class__.__name__, str(e)))
        exit_code = 1

    # Handle exceptions that deal with issues with the web scraper.
    except (WebDriverException, TimeoutException) as e:
        scraper.quit()
        print('{}: {}'.format(e.__class__.__name__, str(e)))
        exit_code = 1

    # Handle exceptions that deal with network issues.
    except MaxRetryError:
        scraper.quit()
        print('Failed to establish a new connection with https://calendar.buffalo.edu/. Check network connection.')
        exit_code = 2

    # Terminate program with `exit_code`.
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
