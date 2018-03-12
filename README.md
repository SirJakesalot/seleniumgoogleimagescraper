## Simple example usage
```python
from seleniumgoogleimagescraper import SeleniumGoogleImageScraper
scraper = SeleniumGoogleImageScraper('firefox', 'C:\\Program Files\\Mozilla Firefox\\firefox.exe', 'C:\\Program Files\\Mozilla Firefox\\geckodriver.exe')
queries = ['minecraft', 'minecraft pig']
for query in queries:
    scraper.load_image_search_page(query)
    scraper.scroll_to_bottom()
    scraper.scrape_image_links()
scraper.download_image_links('img/repository')
```
Tip: After collecting all the links, break them up into chunks and leverage the [multiprocessing library](https://docs.python.org/3.6/library/multiprocessing.html#introduction)! Hopefully I can throw something together demonstrating this.

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/CnCb3VlcAUg/0.jpg)](https://www.youtube.com/watch?v=CnCb3VlcAUg)

The above example is seen performing queries for ['minecraft', 'minecraft pig'].
The beautiful soup method to scrape Google Image search results is limited to ~100 images. This is not good enough when trying to build an image repository. To avoid the ~100 image limit we use Selenium to simulate a scrolling user (using javascript to load the rest of the images). I have seen queries produce 800+ images at a time. The code sample I have provided is far from perfect but I thought I would share a working example! Hope anyone will be able to leverage this example.

## Installation

### selenium setup
- [firefox webdriver example](https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/WebDriver)
- [google webdriver example](https://sites.google.com/a/chromium.org/chromedriver/getting-started)

### pip dependencies
```bash
pip install requests
pip install selenium
```