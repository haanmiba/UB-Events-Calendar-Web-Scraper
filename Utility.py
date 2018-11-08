import sys
import re
import json
# import yaml
import xml.etree.ElementTree as ET
from exceptions import InvalidConfigFileTypeError, InvalidConfigFileValueError
from xml.etree.ElementTree import Element
from configparser import ConfigParser, SectionProxy
from datetime import datetime, timedelta
from pytz import timezone
from Configuration import Configuration


ALLOWED_CONFIG_FILE_TYPES = {'cfg', 'conf', 'config', 'ini', 'json', 'xml', 'yaml', 'yml'}
ALLOWED_TRUE_STRINGS = {'true', 't', 'yes', 'y'}
ALLOWED_FALSE_STRINGS = {'false', 'f', 'no', 'n'}

PROMPT = 'Input the file path to the text file storing the path to the driver.'
START_END_REGEX = r'(Starts|Ends):'
ALL_DAY_REGEX = r'All\sDay'
DATE_REGEX = r'(0?\d|1[0-2])/(0?\d|[12]\d|3[01])/([12]\d{3})'
TIME_REGEX = r'(0?[0-9]|1[0-2]):([0-5][0-9])(:[0-5][0-9])?\s?[AP]\.?M\.?'


def eval_config_file_boolean(text_value):
    parsed_value = None
    if text_value.strip().lower() in ALLOWED_TRUE_STRINGS:
        parsed_value = True
    elif text_value.strip().lower() in ALLOWED_FALSE_STRINGS:
        parsed_value = False
    else:
        raise InvalidConfigFileValueError('`{}` is not a valid value for the config file'.format(text_value))
    return parsed_value


def get_nested_elem(parser, func_list, key_list):
    elem = parser
    for func, key in zip(func_list, key_list):
        elem = func(elem, key)
    return elem


def parse_config_file(parser, func_list):
    chromedriver_path = get_nested_elem(parser, func_list, ['chromedriver', 'path'])
    if not isinstance(chromedriver_path, (str, unicode)):
        chromedriver_path = chromedriver_path.text

    start_page = get_nested_elem(parser, func_list, ['settings', 'start_page'])
    if not isinstance(start_page, (str, unicode, int)):
        start_page = start_page.text
    start_page = int(start_page)

    end_page = get_nested_elem(parser, func_list, ['settings', 'end_page'])
    if not isinstance(end_page, (str, unicode, int)):
        end_page = end_page.text
    end_page = int(end_page)

    all_pages = get_nested_elem(parser, func_list, ['settings', 'all_pages'])
    if not isinstance(all_pages, (str, unicode)):
        all_pages = all_pages.text
    all_pages = eval_config_file_boolean(all_pages)

    output = get_nested_elem(parser, func_list, ['settings', 'output'])
    if not isinstance(output, (str, unicode)):
        output = output.text
    output = eval_config_file_boolean(output)

    output_path = get_nested_elem(parser, func_list, ['settings', 'output_path'])
    if not isinstance(output_path, (str, unicode)):
        output_path = output_path.text

    output_mode = get_nested_elem(parser, func_list, ['settings', 'output_mode'])
    if not isinstance(output_mode, (str, unicode)):
        output_mode = output_mode.text

    c = Configuration(chromedriver_path, start_page, end_page, all_pages, output, output_path, output_mode)
    return c


def read_config_file():
    config_file_path = sys.argv[1] if len(sys.argv) > 1 else input(PROMPT)
    file_extension = config_file_path.rsplit('.')[-1].lower()

    if file_extension not in ALLOWED_CONFIG_FILE_TYPES:
        raise InvalidConfigFileTypeError("`.{}` is not a valid config file extension. Allowed file types are: {}"
                                         .format(file_extension,
                                                 ', '.join(map(lambda s: '`.' + s + '`', ALLOWED_CONFIG_FILE_TYPES))))

    try:
        if file_extension in {'cfg', 'conf', 'config', 'ini'}:
            ini_parser = ConfigParser()
            ini_parser.read(config_file_path)
            return parse_config_file(ini_parser, [ConfigParser.__getitem__, SectionProxy.__getitem__])

        if file_extension == 'json':
            with open(config_file_path) as f:
                json_parser = json.load(f)
                return parse_config_file(json_parser, [dict.__getitem__] * 2)

        if file_extension in {'yaml', 'yml'}:
            with open(config_file_path) as f:
                yaml_parser = yaml.load(f)
                return parse_config_file(yaml_parser, [dict.__getitem__] * 2)

        if file_extension == 'xml':
            tree = ET.parse(config_file_path)
            root = tree.getroot()
            return parse_config_file(root, [Element.find] * 2)

    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)

    except KeyError as e:
        print('Missing Key: {}'.format(e))
        sys.exit(1)


def extract_date_time(raw_date_time, tz):
    start_date, end_date, start_time, end_time = None, None, None, None

    if re.search(ALL_DAY_REGEX, raw_date_time):
        start_time = datetime.strptime('12:00 AM', '%I:%M %p')
        end_time = datetime.strptime('11:59 PM', '%I:%M %p')

    pattern = re.compile(DATE_REGEX)
    for match in re.finditer(pattern, raw_date_time):
        date = match.group()
        if re.search(START_END_REGEX, raw_date_time):
            if start_date:
                end_date = datetime.strptime(date, '%m/%d/%Y')
            else:
                start_date = datetime.strptime(date, '%m/%d/%Y')
        else:
            start_date = datetime.strptime(date, '%m/%d/%Y')
            end_date = datetime.strptime(date, '%m/%d/%Y')

    pattern = re.compile(TIME_REGEX)
    for match in re.finditer(pattern, raw_date_time):
        time = match.group()
        if start_time:
            end_time = datetime.strptime(time, '%I:%M %p')
        else:
            start_time = datetime.strptime(time, '%I:%M %p')

    if not end_date:
        end_date = start_date

    if not end_time:
        end_time = start_time + timedelta(hours=2)

    start = datetime.combine(start_date.date(), start_time.time())
    end = datetime.combine(end_date.date(), end_time.time())

    start_w_timezone = timezone(tz).localize(start)
    end_w_timezone = timezone(tz).localize(end)

    return start_w_timezone, end_w_timezone
