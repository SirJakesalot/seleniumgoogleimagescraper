import time
import shutil
import os
import json
import logging
import re
import requests
import urllib.parse

# vendor
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.options import Options


class SeleniumGoogleImageScraperException(Exception):
    """General GoogleImageScraper exception"""
    pass


class SeleniumGoogleImageScraper(object):
    """Object to handle scraping images from a google image search.

    Args:
        browser_type (str): Currently supports Firefox and Chrome browsers.
        browser_executable (str): Filesystem path to the browser.
        webdriver_executable (str): Filesystem path to the browser's webdriver.

    Attributes:
        browser_type (str): Currently supports Firefox and Chrome browsers.
        browser_executable (str): Filesystem path to the browser.
        webdriver_executable (str): Filesystem path to the browser's webdriver.
        _driver (BrowserDriver): Respective browser driver loaded.
        links (set): Unique collection of links found from the search.
        logger (Logger): Logging mechanism.

    """

    def __init__(self, browser_type, browser_executable, webdriver_executable):
        # passed in args
        self.browser_type = browser_type
        self.browser_executable = browser_executable
        self.webdriver_executable = webdriver_executable

        # built args
        self._driver = None
        self.links = set()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @property
    def driver(self):
        """Build the selenium driver if it does not exist."""
        if not self._driver:
            self.logger.info('building selenium: "{}" webdriver...'.format(self.browser_type))
            if self.browser_type == 'chrome':
                chrome_opts = Options()
                chrome_opts.binary_location = self.browser_executable
                self._driver = webdriver.Chrome(chrome_options=chrome_opts, executable_path=self.webdriver_executable)
            elif self.browser_type == 'firefox':
                binary = FirefoxBinary(self.browser_executable)
                self._driver = webdriver.Firefox(firefox_binary=binary, executable_path=self.webdriver_executable)
            else:
                raise SeleniumGoogleImageScraperException('invalid browser type: "{}", please choose between: [chrome, firefox]'.format(self.browser_type))
        return self._driver

    @driver.deleter
    def driver(self):
        self.close_driver()

    def close_driver(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def load_image_search_page(self, query, search_url='https://www.google.co.in/search?{}'):
        """Use the selenium driver to load the google image search page.

        Args:
            query (str): Google image query.
            search_url (str): Base Google image query url.

        """
        search_url_params = {'q': query, 'source': 'lnms', 'tbm': 'isch'}
        url_encoded_params = urllib.parse.urlencode(search_url_params)
        self.driver.get(search_url.format(url_encoded_params))

    def scroll_to_bottom(self, scroll_wait_time=2, show_more_results_button_id='smb',
                         scroll_script='window.scrollTo(0, document.body.scrollHeight);var h=document.body.scrollHeight;return h;'):
        """Scroll to the bottom of the Google image search page to load all the images.

        Args:
            scroll_wait_time (int): Seconds to wait while the page loads.
            show_more_results_button_id (str): HTML id for the "show more results" button.
            scroll_script (str): Javascript snippet to scroll to the bottom of the screen.

        """
        time.sleep(scroll_wait_time)
        height = self.driver.execute_script(scroll_script)
        self.logger.info('height: "{}"'.format(height))
        cursor = 0
        while cursor < height:
            time.sleep(scroll_wait_time)
            cursor = height
            height = self.driver.execute_script(scroll_script)
            self.logger.info('looking for "Show more results" button...')
            try:
                button = self.driver.find_element_by_id(show_more_results_button_id)
                button.click()
                self.logger.info('loading more images...')
            except ElementNotInteractableException as e:
                self.logger.info('button not yet visible on screen, (cursor="{}", height="{}")'.format(cursor, height))

    def scrape_image_links(self, image_xpath='//div[contains(@class, "rg_meta")]', meta_data_url_key='ou'):
        """Parse Google image search page for the image links.

        Args:
            image_xpath (str): Xpath to the image meta data.
            meta_data_url_key (str): Json meta data key for the url.

        """
        image_meta_data = self.driver.find_elements_by_xpath(image_xpath)
        self.logger.info('number of images found: "{}"'.format(len(image_meta_data)))
        for meta_data in image_meta_data:
            meta_json = json.loads(meta_data.get_attribute('innerHTML'))
            url = meta_json[meta_data_url_key]
            self.logger.debug('found image url: "{}"'.format(url))
            self.links.add(url)

    def download_image_link(self, link, dst):
        """Download an image link.

        Args:
            link (str): URL to an image.
            dst (str): Filesystem path to download the image to.

        """
        self.logger.debug('downloading: "{}", to: "{}"'.format(link, dst))
        response = requests.get(link, stream=True)
        with open(dst, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

    def download_image_links(self, download_path='', extensions={'jpg', 'png', 'gif'}, link_regex_pattern=r'.*\.(\w+)'):
        """Load a Google image search page and download its images.

        Args:
            download_path (str): Filesystem path to download to.
            extensions (list): Image extensions to download.
            link_regex_pattern (str): Regex pattern to find extensions.

        """
        self.close_driver()
        self.logger.info('total number of links found to download: "{}"'.format(len(self.links)))
        link_regex = re.compile(link_regex_pattern)
        skipped_link_download_count = 0
        for i, link in enumerate(list(self.links)):
            link_extension_exists = link_regex.search(link.lower())
            if link_extension_exists:
                link_extension = link_extension_exists.groups()[0]
                valid_extension = not extensions or link_extension in extensions
                if valid_extension:
                    filename = '{}.{}'.format(i, link_extension)
                    dst = os.path.join(download_path, filename)
                    try:
                        self.download_image_link(link, dst)
                    except Exception as e:
                        self.logger.info('skipping download of: "{}"'.format(link))
                        skipped_link_download_count += 1
                else:
                    self.logger.info('skipping download of: "{}"'.format(link))
                    skipped_link_download_count += 1
        self.logger.info('number of links skipped being downloaded: "{}"'.format(skipped_link_download_count))
        self.logger.info('number of links actually downloaded: "{}"'.format(len(self.links) - skipped_link_download_count))

if __name__ == '__main__':

    g = SeleniumGoogleImageScraper('firefox', 'C:\\Program Files\\Mozilla Firefox\\firefox.exe', 'C:\\Program Files\\Mozilla Firefox\\geckodriver.exe')
    queries = ['minecraft', 'minecraft pig']
    for query in queries:
        g.load_image_search_page(query)
        g.scroll_to_bottom()
        g.scrape_image_links()
    g.download_image_links(download_path='img/repository')
