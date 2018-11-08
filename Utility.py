import sys
import re
import json
import yaml
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from datetime import datetime, timedelta
from pytz import timezone


ALLOWED_CONFIG_FILE_TYPES = {'ini', 'json', 'xml', 'yaml', 'yml'}

PROMPT = 'Input the file path to the text file storing the path to the driver.'
START_END_REGEX = r'(Starts|Ends):'
ALL_DAY_REGEX = r'All\sDay'
DATE_REGEX = r'(0?\d|1[0-2])/(0?\d|[12]\d|3[01])/([12]\d{3})'
TIME_REGEX = r'(0?[0-9]|1[0-2]):([0-5][0-9])(:[0-5][0-9])?\s?[AP]\.?M\.?'


class InvalidConfigFileTypeError(Exception):
    pass


def get_driver_path():
    driver_path_file = sys.argv[1] if len(sys.argv) > 1 else input(PROMPT)
    path_file_extension = driver_path_file.rsplit('.')[-1].lower()

    if path_file_extension not in ALLOWED_CONFIG_FILE_TYPES:
        raise InvalidConfigFileTypeError("`.{}` is not a valid config file extension. Allowed file types are: {}"
                                         .format(path_file_extension,
                                                 ', '.join(map(lambda s: '`.' + s + '`', ALLOWED_CONFIG_FILE_TYPES))))

    try:
        if path_file_extension == 'ini':
            config = ConfigParser()
            config.read(driver_path_file)
            return config['chromedriver']['path']

        if path_file_extension == 'json':
            with open(driver_path_file) as f:
                data = json.load(f)
                return data['chromedriver']['path']

        if path_file_extension in {'yaml', 'yml'}:
            with open(driver_path_file) as f:
                data = yaml.load(f)
                return data['chromedriver']['path']

        if path_file_extension == 'xml':
            tree = ET.parse(driver_path_file)
            root = tree.getroot()
            chromedriver_path = root.find('chromedriver').find('path').text
            start_page = root.find('settings').find('start_page').text
            end_page = root.find('settings').find('end_page').text
            all_pages = root.find('settings').find('all_pages').text
            output = root.find('settings').find('output').text
            output_path = root.find('settings').find('output_path').text
            output_mode = root.find('settings').find('output_mode').text
            return chromedriver_path

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
