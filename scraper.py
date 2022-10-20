from base.driver_setup import driver

from urllib.parse import urlparse, urljoin
from base.tools import Element
import colorama

from custom_logging import xlogging

colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

depth = 0


class Scraper:
    def __init__(self, url):
        self.url = url
        self.internal_urls = set()
        self.external_urls = set()
        self.visited_urls = set()

    def is_valid(self, href):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(href)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def get_all_website_links(self, url):
        """
        Returns all URLs that is found on `url` in which it belongs to the same website
        """

        if url in self.visited_urls:
            return

        urls = set()

        domain_name = urlparse(self.url).netloc
        xlogging(2, f"Domain: {domain_name}")

        driver.get(url)
        self.visited_urls.add(url)

        if self.url[-3:] == 'uli':
            self.url = self.url[:-3]

        hrefs = Element('//a[@href]').presence_multi()

        for href in hrefs:
            href = href.get_attribute('href')
            if href == "" or href is None:
                continue

            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self.is_valid(href):
                continue

            if href in self.internal_urls:
                continue

            if '/fr/' in href:
                continue

            if href[-4] == '.':
                xlogging(2, f"Ignoring URL with extension: {href}")
                continue

            if href[-5] == '.':
                xlogging(2, f"Ignoring URL with extension: {href}")
                continue

            if domain_name not in href:
                if href not in self.external_urls:
                    xlogging(2, f"{GRAY}[!] External link: {href}{RESET}")
                    self.external_urls.add(href)
                continue

            xlogging(2, f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            self.internal_urls.add(href)

        return urls

    def _crawl(self, url):
        """
        Crawls a web page and extracts all links.
        You'll find all links in `external_urls` and `internal_urls` global set variables.
        params:
            max_urls (int): number of max urls to crawl, default is 30.
        """
        global depth
        xlogging(2, f"{YELLOW}[*] Crawling: {url}{RESET} Depth: {depth}")
        links = self.get_all_website_links(url)
        if links is None:
            depth -= 1
            return self.internal_urls
        for link in links:
            depth += 1
            self._crawl(link)
        depth -= 1
        return self.internal_urls

    def crawl(self):
        return self._crawl(self.url)
