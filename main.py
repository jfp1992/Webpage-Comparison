from base.env_setup import Browser
from base.record_time import RecordTime
from base.test_base import TestBase
from playwright.sync_api import sync_playwright

from custom_logging import xlogging

from differ import Differences
from scraper import Scraper
import glob


def get_screenshot(filename, page):
    xlogging(3, f"Filename before replace: {filename}")
    if len(filename) == 0:
        return
    filename = filename.replace("/", "_")
    if filename[0] == "_":
        filename = filename[1:]

    xlogging(3, f"Filename after replace: {filename}")
    page.screenshot(path=f"./input/{filename}.png")


def check_in_list(paths, find_path):
    for path in paths:
        if find_path[:-8] == path[:-8]:
            return True
        else:
            return False

TestBase
with sync_playwright() as p:
    context = Browser(p).start()
    page = context.new_page()

    ref_url = ""
    com_url = ""

    total_test_time = RecordTime("Entire run")
    total_test_time.start()

    page.goto(ref_url)

    ref_urls = list(Scraper(page, context, f"{ref_url}uli").crawl())

    for url in ref_urls:
        if "/ics/" in url or "/logout" in url or "/autologout" in url:
            continue
        xlogging(2, f"Taking a screenshot of {url}")
        page.goto(url)
        get_screenshot(url.replace(ref_url, "") + "_ref", page)

    page.goto(f"{com_url}uli")
    com_url = com_url.replace("CFT:CFT@", "")
    com_urls = list(Scraper(page, context, f"{com_url}uli").crawl())

    for url in com_urls:
        if "/ics/" in url or "/logout" in url or "/autologout" in url:
            continue
        xlogging(2, f"Taking a screenshot of {url}")
        page.goto(url)
        get_screenshot(url.replace(com_url, "") + "_com", page)

    loop_count = 0
    for i in zip(ref_urls, com_urls):
        print(i, com_urls[loop_count])
        loop_count += 1

    loop_count2 = 0

    ref_list = glob.glob("./input/*_ref.png")
    com_list = glob.glob("./input/*_com.png")

    screenshot_processing = RecordTime("Comparison processing")
    screenshot_processing.start()

    for ref_name in ref_list:
        for com_name in com_list:
            if com_name[:-8] == ref_name[:-8]:
                Differences([ref_name, com_name]).compare()

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

    page.pause()
