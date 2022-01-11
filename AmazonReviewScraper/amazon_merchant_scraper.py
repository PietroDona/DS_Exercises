# http requests and HTML parsing
import requests
from bs4 import BeautifulSoup as bsoup
from bs4.element import Tag
# date parsing and typing
from dateutil.parser import parse as date_parser
from datetime import date
from typing import List
# custom review container
from models import Review, Product

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
BASEURL_MERCHANT = "https://www.amazon.com/s?i=merchant-items"


class MerchantScraper():
    '''Class that scrape the items sold by a merchant with me from the amazon website'''

    def __init__(self, me: str, verbose: bool = False, max_scrape=None) -> None:
        self.me = me
        self.verbose = verbose
        self.max_scrape = max_scrape

    def get_url(self, page) -> str:
        '''Formatting of the reviews URL'''
        return f"{BASEURL_MERCHANT}&me={self.me}&page={page}"

    def get_items(self):
        '''Scrape ALL the products sold by the merchant'''
        results = []
        page = 1
        # iterates on the pages until we get an empty page
        while True:
            # chack page limit
            if page > self.max_scrape:
                break
            # scrape the page
            page_list = self.get_page(page)
            # check if empty
            if not page_list:
                break
            # append the page to the result
            results += page_list
            page += 1
        return results

    def get_page(self, page) -> List[Product]:
        '''Scrape the review in a given page'''
        r = requests.get(self.get_url(page), headers=HEADERS)
        soup = bsoup(r.text, 'html.parser')

        div_items = soup.find_all(
            "div", {"data-component-type": "s-search-result"})
        result = [self.parse_item(item) for item in div_items]
        return result or None

    def parse_item(self, item: Tag) -> Product:
        '''Parse the review Tag in the dataclass cleaning the various properties'''
        asin = item.attrs.get("data-asin")
        product_name = item.find(
            "div", class_="s-title-instructions-style").get_text().strip()
        average_review_raw = item.find(
            "i", class_="a-icon").get_text().strip().split(" ")[0]
        return Product(asin=asin, product=product_name, me=self.me,
                       average_review=float(average_review_raw), producer=None)

    def get_clean_title(self, item: Tag) -> str:
        '''Clean the title from the HTML'''
        title = item.find(
            "a", {"data-hook": "review-title"}).get_text().strip()
        return title


if __name__ == "__main__":
    ams = MerchantScraper(me="A294P4X9EWVXLJ", max_scrape=3)
    print(ams.get_items())
