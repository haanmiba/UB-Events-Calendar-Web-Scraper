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
    pass


class InvalidConfigFileValueError(Exception):
    pass


class InvalidArgumentsError(Exception):
    pass


class OverwriteExistingFileError(Exception):
    pass


def eval_config_file_boolean(text_value):
    if text_value.strip().lower() in ALLOWED_TRUE_STRINGS:
        return True
    elif text_value.strip().lower() in ALLOWED_FALSE_STRINGS:
        return False
    else:
        raise InvalidConfigFileValueError('`{}` is not a valid value for the config file'.format(text_value))


def get_nested_elem(parser, func_list, key_list, file_ext, cast):
    elem = parser
    for func, key in zip(func_list, key_list):
        elem = func(elem, key)
    if file_ext == 'xml':
        elem = elem.text
    return cast(elem)


def parse_config_file(parser, func_list, file_ext):
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

    if export:
        if len(export_path.rsplit('.', 1)) < 2:
            raise InvalidConfigFileValueError('No file extension listed in export path `{}`'.format(export_path))

    return Configuration(chromedriver_path, headless, deep_scrape, start_page, end_page,
                         all_pages, export, overwrite, export_path, export_extension, print_evts)


def read_config_file(config_file_path):
    file_extension = config_file_path.rsplit('.')[-1].lower()

    if file_extension not in ALLOWED_CONFIG_FILE_TYPES:
        raise InvalidConfigFileTypeError("`.{}` is not a valid config file extension. Allowed file types are: {}"
                                         .format(file_extension,
                                                 ', '.join(map(lambda s: '`.' + s + '`', ALLOWED_CONFIG_FILE_TYPES))))

    try:
        if file_extension in {'cfg', 'conf', 'config', 'ini'}:
            ini_parser = ConfigParser()
            ini_parser.read(config_file_path)
            return parse_config_file(ini_parser, [ConfigParser.__getitem__, SectionProxy.__getitem__], file_extension)

        if file_extension == 'json':
            with open(config_file_path) as f:
                json_parser = json.load(f)
                return parse_config_file(json_parser, [dict.__getitem__] * 2, file_extension)

        if file_extension in {'yaml', 'yml'}:
            with open(config_file_path) as f:
                yaml_parser = yaml.load(f)
                return parse_config_file(yaml_parser, [dict.__getitem__] * 2, file_extension)

        if file_extension == 'xml':
            tree = ET.parse(config_file_path)
            root = tree.getroot()
            return parse_config_file(root, [Element.find] * 2, file_extension)

    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)

    except KeyError as e:
        print('Missing Key: {}'.format(e))
        sys.exit(1)


def read_args(args):
    chromedriver_path = os.path.abspath(args[args.index('--path')+1])
    headless = '--head' not in args
    deep_scrape = '--deep' in args
    pages = list(map(int, filter(lambda arg: arg.isnumeric(), args)))
    if len(pages) == 0:
        start_page = 0
        end_page = 1
    elif len(pages) == 1:
        start_page = 0
        end_page = pages[0]
    elif len(pages) == 2:
        start_page = pages[0] - 1
        end_page = pages[1]
    else:
        raise InvalidArgumentsError('Too many page arguments. Only 0-2 are needed.')
    all_pages = '--all' in args
    export = '--export' in args
    if '--export' == args[-1]:
        raise InvalidArgumentsError('`--export` cannot be the final argument.')
    export_path = args[args.index('--export')+1] if export else None
    export_extension = export_path.rsplit('.', 1)[-1].lower() if export_path else None
    overwrite = '--overwrite' in args
    print_evts = '--print' in args

    if export:
        if len(export_path.rsplit('.', 1)) < 2:
            raise InvalidConfigFileValueError('No file extension listed in export path `{}`'.format(export_path))

    return Configuration(chromedriver_path, headless, deep_scrape, start_page, end_page,
                         all_pages, export, overwrite, export_path, export_extension, print_evts)


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
        if attr in evt.__dict__:
            if attr == 'contact':
                print_str += 'Contact:\n'
                for label, value in evt.__dict__[attr].items():
                    print_str += '  {:<{fill}} {}\n'.format(format_attribute(label) + ':', value,
                                                            fill=max(map(len, evt.contact.keys())) + 1)
                else:
                    print_str += '\n'
            else:
                print_str += '{}:\n{}\n\n'.format(format_attribute(attr), evt.__dict__[attr])
    if 'additional_info' in evt.__dict__:
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
