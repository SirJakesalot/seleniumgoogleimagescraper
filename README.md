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

## Installation

### selenium setup
- [firefox webdriver example](https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/WebDriver)
- [google webdriver example](https://sites.google.com/a/chromium.org/chromedriver/getting-started)

### pip dependencies
```bash
pip install requests
pip install selenium
```