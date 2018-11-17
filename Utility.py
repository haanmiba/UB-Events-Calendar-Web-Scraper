import sys
import os
import re
import json
import yaml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
from configparser import ConfigParser, SectionProxy
from datetime import datetime, timedelta
from pytz import timezone
from Configuration import Configuration


ALLOWED_CONFIG_FILE_TYPES = {'cfg', 'conf', 'config', 'ini', 'json', 'xml', 'yaml', 'yml'}
ALLOWED_TRUE_STRINGS = {'true', 't', 'yes', 'y'}
ALLOWED_FALSE_STRINGS = {'false', 'f', 'no', 'n'}
ALLOWED_EXPORT_FILE_TYPES = {'json', 'xml', 'yaml', 'yml'}

START_END_REGEX = r'(Starts|Ends):'
ALL_DAY_REGEX = r'All\sDay'
DATE_REGEX = r'(0?\d|1[0-2])/(0?\d|[12]\d|3[01])/([12]\d{3})'
TIME_REGEX = r'(0?[0-9]|1[0-2]):([0-5][0-9])(:[0-5][0-9])?\s?[AP]\.?M\.?'
CONTACT_NAME_REGEX = r'^[a-zA-Z ,-]+$'
PHONE_NUMBER_REGEX = r'\(?\d{3}\)?(\s|-)?\d{3}(\s|-)?\d{4}'
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+'


class InvalidConfigFileTypeError(Exception):
    """An exception that indicates a config file had an invalid file type."""
    pass


class InvalidConfigFileValueError(Exception):
    """An exception that indicates a config file contained invalid values."""
    pass


class InvalidArgumentsError(Exception):
    """An exception that indicates that the command line arguments for the program's execution are invalid."""
    pass


class OverwriteExistingFileError(Exception):
    """An exception that indicates a file already exists and the program cannot overwrite it."""
    pass


def eval_config_file_boolean(text_value):
    """Convert a config file text value into a boolean.

    Parameters
    ----------
    text_value : str
        The text value to be converted into a boolean

    Returns
    -------
    bool
        True -- if the text value is one of the accepted `true` strings;
        False -- if the text value is one of the accepted `false` strings

    Raises
    ------
    InvalidConfigFileValueError
        If the text value does is not any of the accepted `true` or `false` strings.
    """

    # Return True if the text value is one of the accepted `true` strings
    if text_value.strip().lower() in ALLOWED_TRUE_STRINGS:
        return True
    # Return False if the text value is one of the accepted `false` strings
    elif text_value.strip().lower() in ALLOWED_FALSE_STRINGS:
        return False
    # Else, raise an InvalidConfigFileValueError exception
    else:
        raise InvalidConfigFileValueError('`{}` is not a valid value for the config file'.format(text_value))


def get_nested_elem(parser, func_list, key_list, file_ext, cast):
    """Retrieve the value of a nested element from within a config file.

    Parameters
    ----------
    parser : ConfigParser (.ini, .config, .cfg), dict (.json, .yaml, .yml), or Element (.xml)
        The object that will store the structure of elements
    func_list : list
        A list of functions that will be called on the structure of elements to get the nested element
    key_list : list
        A list of str that is the `path` within the config file to retrieve the nested element
    file_ext : str
        File extension for the config file
    cast : function
        The data type that the element's text value will be converted into

    Returns
    -------
    object
        Depending on the function of cast, the text value of the nested element can be converted into any data type
    """

    elem = parser
    # Have element be set to the result of calling `func` on elem to get the value of the key `key`
    for func, key in zip(func_list, key_list):
        elem = func(elem, key)
    # If the file extension is `.xml`, convert the element to its text value.
    if file_ext == 'xml':
        elem = elem.text
    # Cast the text value into the desired data type and return it
    return cast(elem)


def validate_start_end_pages(start_page, end_page):
    if start_page < 0:
        raise InvalidConfigFileValueError('Start page must be a non-negative number. The number given was `{}`'
                                          .format(start_page+1))
    if end_page < 0:
        raise InvalidConfigFileValueError('End page must be greater than or equal to 1. The number given was `{}`'
                                          .format(end_page))
    if end_page < start_page:
        raise InvalidConfigFileValueError('End page must be at or after start page, not before.')


def check_file_extension_exists(file_name):
    if len(file_name.rsplit('.', 1)) < 2:
        raise InvalidConfigFileValueError('No file extension listed in export path `{}`'.format(file_name))


def parse_config_file(parser, func_list, file_ext):
    """Parse the configuration file to retrieve all of the configuration settings.

    Parameters
    ----------
    parser : ConfigParser (.ini, .config, .cfg), dict (.json, .yaml, .yml), or Element (.xml)
        The object that will store the structure of elements
    func_list : list
        A list of functions that will be called on the structure of elements to get the nested element
    file_ext : str
        File extension for the config file

    Returns
    -------
    Configuration
        an instance of Configuration that stores all of the configuration settings for the program's execution

    Raises
    ------
    InvalidConfigFileValueError
        if any values within the configuration file are invalid
    """

    # Retrieve all of the configuration settings from the config file
    chromedriver_path = os.path.abspath(get_nested_elem(parser, func_list, ['chromedriver', 'path'], file_ext, str))
    headless = get_nested_elem(parser, func_list, ['chromedriver', 'headless'], file_ext, eval_config_file_boolean)
    deep_scrape = get_nested_elem(parser, func_list, ['settings', 'deep_scrape'], file_ext, eval_config_file_boolean)
    start_page = get_nested_elem(parser, func_list, ['settings', 'start_page'], file_ext, int) - 1
    end_page = get_nested_elem(parser, func_list, ['settings', 'end_page'], file_ext, int)
    all_pages = get_nested_elem(parser, func_list, ['settings', 'all_pages'], file_ext, eval_config_file_boolean)
    export = get_nested_elem(parser, func_list, ['settings', 'export'], file_ext, eval_config_file_boolean)
    overwrite = get_nested_elem(parser, func_list, ['settings', 'overwrite'], file_ext, eval_config_file_boolean)
    export_path = get_nested_elem(parser, func_list, ['settings', 'export_path'], file_ext, str)
    export_extension = export_path.rsplit('.', 1)[-1].lower()
    print_evts = get_nested_elem(parser, func_list, ['settings', 'print'], file_ext, eval_config_file_boolean)

    # Validate start and end pages
    validate_start_end_pages(start_page, end_page)

    # If the configuration setting for exporting data is enabled and
    # the export file path has no file extension, raise an InvalidConfigFileValueError
    if export:
        check_file_extension_exists(export_path)

    # Create a new instance of Configuration and return it
    return Configuration(chromedriver_path, headless, deep_scrape, start_page, end_page,
                         all_pages, export, overwrite, export_path, export_extension, print_evts)


def read_config_file(config_file_path):
    """Read the configuration file and extract the configuration settings for the program's execution.

    Parameters
    ----------
    config_file_path : str
        The file path to where the configuration file is located

    Returns
    -------
    Configuration
        an instance of Configuration that stores all of the configuration settings for the program's execution

    Raises
    ------
    InvalidConfigFileValueError
        if any values within the configuration file are invalid
    InvalidConfigFileTypeError
        if the configuration file is a file type that the program cannot read from
    """

    # If the configuration file path has no file extension, raise an InvalidConfigFileValueError
    if len(config_file_path.rsplit('.')) < 2:
        raise InvalidConfigFileValueError('No file extension listed in config file path `{}`'.format(config_file_path))

    # If the configuration file extension is not any of the allowed
    # configuration file types, raise an InvalidConfigFileTypeError
    file_extension = config_file_path.rsplit('.')[-1].lower()
    if file_extension not in ALLOWED_CONFIG_FILE_TYPES:
        raise InvalidConfigFileTypeError("`.{}` is not a valid config file extension. Allowed file types are: {}"
                                         .format(file_extension,
                                                 ', '.join(map(lambda s: '`.' + s + '`', ALLOWED_CONFIG_FILE_TYPES))))

    try:
        # Read a config file of file type: .cfg, .conf, .config, .ini
        if file_extension in {'cfg', 'conf', 'config', 'ini'}:
            ini_parser = ConfigParser()
            ini_parser.read(config_file_path)
            return parse_config_file(ini_parser, [ConfigParser.__getitem__, SectionProxy.__getitem__], file_extension)

        # Read a config file of file type .json
        if file_extension == 'json':
            with open(config_file_path) as f:
                json_parser = json.load(f)
                return parse_config_file(json_parser, [dict.__getitem__] * 2, file_extension)

        # Read a config file of file type: .yaml, .yml
        if file_extension in {'yaml', 'yml'}:
            with open(config_file_path) as f:
                yaml_parser = yaml.load(f)
                return parse_config_file(yaml_parser, [dict.__getitem__] * 2, file_extension)

        # Read a config file of file type .xml
        if file_extension == 'xml':
            tree = ET.parse(config_file_path)
            root = tree.getroot()
            return parse_config_file(root, [Element.find] * 2, file_extension)

    # Handle exception where the file cannot be found
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)

    # Handle exception where a key within the configuration file cannot be found
    except KeyError as e:
        print('Missing Key: {}'.format(e))
        sys.exit(1)


def extract_start_end_pages(pages):
    # If the no page numbers were entered, have the start page be 0 and end page be 1
    if len(pages) == 0:
        return 0, 1

    # If one page number was entered, have the start page be 0 and end page be the entered page
    elif len(pages) == 1:
        return 0, pages[0]

    # If two page numbers were entered, have the start page be pages[0]-1 and have the end page be pages[1]
    elif len(pages) == 2:
        return pages[0] - 1, pages[1]

    # If more than two page numbers were entered, raise an InvalidArgumentsError
    else:
        raise InvalidArgumentsError('Too many page arguments. Only 0-2 are needed.')


def read_args(args):
    """Read command line arguments and extract the configuration settings for the program's execution.

    Parameters
    ----------
    args : list
        Command line arguments

    Returns
    -------
    Configuration
        an instance of Configuration that stores all of the configuration settings for the program's execution

    Raises
    ------
    InvalidArgumentsError
        if any of the command line arguments are invalid
    """

    # Extract ChromeDriver path, headless, deep scrape
    chromedriver_path = os.path.abspath(args[args.index('--path')+1])
    headless = '--head' not in args
    deep_scrape = '--deep' in args

    # Extract the numbers of the pages that will be scraped
    pages = list(map(int, filter(lambda arg: arg.isnumeric(), args)))
    start_page, end_page = extract_start_end_pages(pages)

    # Validate the start and end pages
    validate_start_end_pages(start_page, end_page)

    # Extract all pages and export configuration settings
    all_pages = '--all' in args
    export = '--export' in args

    # If the `--export` flag is the last command line argument, raise an InvalidArgumentError
    if '--export' == args[-1]:
        raise InvalidArgumentsError('`--export` cannot be the final argument.')

    # Extract export path, export file extension, overwrite, print_events
    export_path = args[args.index('--export')+1] if export else None
    export_extension = export_path.rsplit('.', 1)[-1].lower() if export_path else None
    overwrite = '--overwrite' in args
    print_evts = '--print' in args

    # If the configuration setting for exporting data is enabled and
    # the export file path has no file extension, raise an InvalidConfigFileValueError
    if export:
        check_file_extension_exists(export_path)

    # Create a new instance of Configuration and return it
    return Configuration(chromedriver_path, headless, deep_scrape, start_page, end_page,
                         all_pages, export, overwrite, export_path, export_extension, print_evts)


def extract_date_time(raw_date_time, tz):
    """Extract the date & time from a raw string.

    Parameters
    ----------
    raw_date_time : str
        The raw string containing information about an event's date & time
    tz : str
        The timezone of the event

    Returns
    -------
    (str, str)
        A tuple with the event start datetime and event end datetime, both formatted as: MM/DD/YYYY HH:MM AM/PM UTC-OFFSET
    """

    start_date, end_date, start_time, end_time = None, None, None, None

    # If an event is `All Day`, set the start time to be 12:00 AM and end time to be 11:59 PM
    if re.search(ALL_DAY_REGEX, raw_date_time):
        start_time = datetime.strptime('12:00 AM', '%I:%M %p')
        end_time = datetime.strptime('11:59 PM', '%I:%M %p')

    # Extract the start and end dates of an event
    pattern = re.compile(DATE_REGEX)
    for match in re.finditer(pattern, raw_date_time):
        date = match.group()

        # If the event has distinct start and end dates, extract them
        if re.search(START_END_REGEX, raw_date_time):
            if start_date:
                end_date = datetime.strptime(date, '%m/%d/%Y')
            else:
                start_date = datetime.strptime(date, '%m/%d/%Y')
        # Else, set the start and end dates to the same date
        else:
            start_date = datetime.strptime(date, '%m/%d/%Y')
            end_date = datetime.strptime(date, '%m/%d/%Y')

    # Extract the start and end times of an event
    pattern = re.compile(TIME_REGEX)
    for match in re.finditer(pattern, raw_date_time):
        time = match.group()
        if start_time:
            end_time = datetime.strptime(time, '%I:%M %p')
        else:
            start_time = datetime.strptime(time, '%I:%M %p')

    # If end_date is None, set it to start_date
    if not end_date:
        end_date = start_date

    # If end_time is None, set it to two hours after start_time
    if not end_time:
        end_time = start_time + timedelta(hours=2)

    # Combine the start/end dates & start/end times into datetime objects
    start = datetime.combine(start_date.date(), start_time.time())
    end = datetime.combine(end_date.date(), end_time.time())

    # Add timezones to the datetime objects
    start_w_timezone = timezone(tz).localize(start)
    end_w_timezone = timezone(tz).localize(end)

    # Return the event start datetime and event end datetime, both formatted as: MM/DD/YYYY HH:MM AM/PM UTC-OFFSET
    return start_w_timezone.strftime('%m/%d/%Y %I:%M %p %Z%z'), end_w_timezone.strftime('%m/%d/%Y %I:%M %p %Z%z')


def extract_contact_info(raw_contact):
    parsed_data = {}

    contact_names = re.findall(CONTACT_NAME_REGEX, raw_contact, flags=re.MULTILINE)
    if contact_names:
        parsed_data['name'] = '\n'.join(contact_names)

    pattern = re.compile(EMAIL_REGEX)
    for match in re.finditer(pattern, raw_contact):
        email = match.group()
        parsed_data['email'] = email

    pattern = re.compile(PHONE_NUMBER_REGEX)
    for match in re.finditer(pattern, raw_contact):
        phone_number = match.group()
        parsed_data['phone_number'] = phone_number

    return parsed_data


def format_attribute(attr):
    return ' '.join(map(lambda x: x.capitalize(), re.split(r' |_', attr)))


def print_event(evt):
    print_str = evt.__str__()
    for attr in ['location', 'contact', 'description']:
        if evt.__dict__[attr]:
            if attr == 'contact':
                print_str += 'Contact:\n'
                for label, value in evt.__dict__[attr].items():
                    print_str += '  {:<{fill}} {}\n'.format(format_attribute(label) + ':', value,
                                                            fill=max(map(len, evt.contact.keys())) + 1)
                else:
                    print_str += '\n'
            else:
                print_str += '{}:\n{}\n\n'.format(format_attribute(attr), evt.__dict__[attr])
    if evt.__dict__['additional_info']:
        print_str += 'Additional Info:\n'
        for label, value in evt.additional_info.items():
            print_str += '  {:<{fill}} {}\n'.format(label+':', value, fill=max(map(len, evt.additional_info.keys()))+1)

    print(print_str.strip())


def print_events(events):
    for evt in events:
        try:
            print_event(evt)
            print('-' * 120)
        except UnicodeEncodeError:
            pass


def export_json(events, export_file_path):
    with open(export_file_path, 'w') as f:
        json.dump({'events': events}, f, indent=4)


def convert_dict_to_xml(parent, d):
    for key, value in d.items():
        element = ET.SubElement(parent, key)
        if isinstance(value, dict):
            convert_dict_to_xml(element, value)
        else:
            element.text = value


def export_xml(events, export_file_path):
    root = ET.Element('events')
    for evt in events:
        evt_element = ET.SubElement(root, 'event')
        convert_dict_to_xml(evt_element, evt)
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
    with open(export_file_path, 'w') as xml_file:
        xml_file.write(xml_str)


def export_yaml(events, export_file_path):
    with open(export_file_path, 'w') as yaml_file:
        yaml.dump({'events': events}, yaml_file, default_flow_style=False)


def export_events(events, config):
    if not config.overwrite and os.path.isfile(config.export_path):
        raise OverwriteExistingFileError('`{}` already exists.'.format(config.export_path))

    os.makedirs(os.path.dirname(config.export_path), exist_ok=True)
    if config.export_extension == 'json':
        export_json([evt.__dict__ for evt in events], config.export_path)
    elif config.export_extension == 'xml':
        export_xml([evt.__dict__ for evt in events], config.export_path)
    elif config.export_extension in {'yaml', 'yml'}:
        export_yaml([evt.__dict__ for evt in events], config.export_path)
    else:
        raise InvalidConfigFileValueError('One of the following file extensions must be provided: {}'
                                          .format(', '.join(ALLOWED_EXPORT_FILE_TYPES)))
