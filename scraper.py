from urllib.parse import urlparse, urljoin

from base.tools import Tools
from base.env_setup import get_arg

import colorama

from custom_logging import xlogging

colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

depth = 0


class Scraper:
    def __init__(self, page, context, url):
        self.page = page
        self.context = context
        self.url = url
        self.internal_urls = set()
        self.external_urls = set()
        self.visited_urls = set()
        self.depth = 0  # Tracks how deep the scraper is in the tree

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

        self.page.goto(url)
        self.visited_urls.add(url)

        if self.url[-3:] == "uli":
            self.url = self.url[:-3]

        hrefs = Tools(self.page, self.context).get_elements("//a[@href]")

        for href in hrefs:
            href = href.get_attribute("href")
            if href == "" or href is None:
                continue

            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self.is_valid(href):
                continue

            if href in self.internal_urls:
                continue

            if "/fr/" in href:
                continue

            if href[-4] == ".":
                xlogging(2, f"Ignoring URL with extension: {href}")
                continue

            if href[-5] == ".":
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
        """Loops through the returned list of urls which are each looped through to get a returned list of urls for each
        which are each looped through to get a returned list of urls for each
        which are each looped through to get a returned list of urls for each recursively."""

        xlogging(2, f"{YELLOW}[*] Crawling at depth {str(self.depth).ljust(3)}| {url}{RESET}")
        links = self.get_all_website_links(url)  # Get links (after filtering) from current url

        if links is None:  # Leave
            self.depth -= 1
            return

        for link in links:
            if get_arg("maxdepth"):
                if self.depth == int(get_arg("maxdepth")):  # Leave
                    self.depth -= 1
                    return

            self.depth += 1
            self._crawl(link)  # Go deeper

        self.depth -= 1  # Leave
        return self.internal_urls

    def crawl(self):
        """Triggers the crawler to start gathering broken links"""
        return self._crawl(self.url)
