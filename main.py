from base.record_time import RecordTime
from selenium.common.exceptions import WebDriverException

from custom_logging import xlogging

from differ import Differences
from scraper import Scraper
import glob
from base.driver_setup import driver


def get_screenshot(filename):
    xlogging(3, f'Filename before replace: {filename}')
    if len(filename) == 0:
        return
    filename = filename.replace('/', '_')
    if filename[0] == '_':
        filename = filename[1:]
    xlogging(3, f'Filename after replace: {filename}')
    screenshot = False
    counter = 1
    while not screenshot:
        try:
            driver.get_full_page_screenshot_as_file(f'./input/{filename}.png')
            screenshot = True
        except WebDriverException:
            xlogging(2, f"Retrying screenshot {counter}")
        counter += 1

ref_url = ''
com_url = ''

total_test_time = RecordTime('Entire run')
total_test_time.start()

driver.get(ref_url)

ref_urls = list(Scraper(f'{ref_url}uli').crawl())

for i in ref_urls:
    if '/ics/' in i or '/logout' in i or '/autologout' in i:
        continue
    xlogging(2, f'Taking a screenshot of {i}')
    driver.get(i)
    get_screenshot(i.replace(ref_url, '') + '_ref')

driver.get(f'{com_url}uli')
com_url = com_url.replace('CFT:CFT@', '')
com_urls = list(Scraper(f'{com_url}uli').crawl())

for i in com_urls:
    if '/ics/' in i or '/logout' in i or '/autologout' in i:
        continue
    xlogging(2, f'Taking a screenshot of {i}')
    driver.get(i)
    get_screenshot(i.replace(com_url, '') + '_com')

loop_count = 0
for i in zip(ref_urls, com_urls):
    print(i, com_urls[loop_count])
    loop_count += 1

loop_count2 = 0

ref_list = glob.glob('./input/*_ref.png')
com_list = glob.glob('./input/*_com.png')

screenshot_processing = RecordTime('Comparison processing')
screenshot_processing.start()

for ref_name in ref_list:
    for com_name in com_list:
        if com_name[:-8] == ref_name[:-8]:
            Differences([ref_name, com_name]).compare()


def check_in_list(paths, find_path):
    for path in paths:
        if find_path[:-8] == path[:-8]:
            return True
        else:
            return False


xlogging(2, "Unprocessed reference images:")
for ref_name in ref_list:
    if check_in_list(com_list, ref_name):
        xlogging(2, f"Cannot find {ref_name} in comparison")

xlogging(2, "Unprocessed comparison images:")
for com_name in com_list:
    if check_in_list(ref_list, com_name):
        xlogging(2, f"Cannot find {com_name} in comparison")

loop_count2 += 1

xlogging(2, screenshot_processing.stop()[1])
xlogging(2, total_test_time.stop()[1])
