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
BASEURL_REVIEW = "https://www.amazon.com/product-reviews"


class ReviewScraper():
    '''Class that scrape the reviews of the product with given asin from the amazon website'''

    def __init__(self, asin: str, sort: str = 'recent', verbose: bool = False, max_scrape=None) -> None:
        # Order the reviews
        sort_types = ['recent', 'helpful']
        if sort not in sort_types:
            raise ValueError(
                f"Invalid sort type. Expected one of: {sort_types}")
        self.asin = asin
        self.sort = sort
        self.verbose = verbose
        self.max_scrape = max_scrape

    def get_url(self, page) -> str:
        '''Formatting of the reviews URL'''
        return f"{BASEURL_REVIEW}/{self.asin}/ref=cm_cr_arp_d_viewopt_srt?sortBy={self.sort}&pageNumber={page}"

    def get_reviews(self):
        '''Scrape ALL the reviews of the product'''
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

    def get_page(self, page) -> List[Review]:
        '''Scrape the review in a given page'''
        r = requests.get(self.get_url(page), headers=HEADERS)
        soup = bsoup(r.text, 'html.parser')
        div_reviews = soup.find_all(
            "div", id=lambda x: x and x.startswith('customer_review-'))
        result = [self.parse_review(item) for item in div_reviews]
        return result or None

    def parse_review(self, item: Tag) -> Review:
        '''Parse the review Tag in the dataclass cleaning the various properties'''
        user = self.get_clean_user(item)
        rating = self.get_clean_rating(item)
        title = self.get_clean_title(item)
        date = self.get_clean_date(item)
        verified = self.get_clean_verified(item)
        content = self.get_clean_content(item)
        helpfulvote = self.get_clean_helpfulvote(item)
        return Review(**{"user": user,
                         "asin": self.asin,
                         "rating": rating,
                         "title": title,
                         "date": date,
                         "verified": verified,
                         "content": content,
                         "helpfulvote": helpfulvote})

    def get_clean_user(self, item: Tag) -> str:
        '''Clean the user id from the HTML'''
        user = item.find("a", class_="a-profile")
        user_link = user.get('href')
        user_id = user_link.split("/")[3].split(".")[-1]
        return user_id

    def get_clean_rating(self, item: Tag) -> int:
        '''Clean the rating from the HTML'''
        rating = item.find("span", class_="a-icon-alt").get_text().strip()
        rating_int = int(rating[0])
        return rating_int

    def get_clean_title(self, item: Tag) -> str:
        '''Clean the title from the HTML'''
        title = item.find(
            "a", {"data-hook": "review-title"}).get_text().strip()
        return title

    def get_clean_date(self, item: Tag) -> date:
        '''Clean the date from the HTML'''
        # from here I can extract also the country - not implemented
        meta = item.find(
            "span", {"data-hook": "review-date"}).get_text()
        raw_date = meta.split("on")[-1].strip()
        return date_parser(raw_date).date()

    def get_clean_verified(self, item: Tag) -> bool:
        '''Clean the verified buy from the HTML'''
        return item.find("span", {"data-hook": "avp-badge"}) is not None

    def get_clean_content(self, item: Tag) -> date:
        '''Clean the content of the review from the HTML'''
        # from here I can extract also the country - not implemented
        content = item.find(
            "span", {"data-hook": "review-body"}).get_text().strip()
        return content

    def get_clean_helpfulvote(self, item: Tag) -> int or None:
        '''Clean the number of helpful votes from the HTML'''
        helpfulvote = item.find(
            "span", {"data-hook": "helpful-vote-statement"})
        if not helpfulvote:
            return None
        helpfulvote_text = helpfulvote.get_text().lower()
        helpfulvote_number = helpfulvote_text.split(" ")[0].replace("one", "1")
        return(int(helpfulvote_number))

    def get_summary(self):
        '''Scrape the summary of the product from the first page'''
        r = requests.get(self.get_url(1), headers=HEADERS)
        product_page = bsoup(r.text, 'html.parser')

        product_name = product_page.find(
            "div", class_="product-title").get_text().strip()

        producer_name_raw = product_page.find(
            "div", class_="product-by-line").get_text().strip()
        producer_name = producer_name_raw[2:]

        average_review_raw = product_page.find(
            "span", {"data-hook": "rating-out-of-text"}).get_text().strip()
        average_review = float(average_review_raw.split(" ")[0])

        return Product(asin=self.asin, product=product_name,
                       producer=producer_name, average_review=average_review,
                       me=None)


if __name__ == "__main__":
    ars = ReviewScraper(asin="B09LCMVB3F", sort="helpful", max_scrape=2)
    print(ars.get_summary())
    print(ars.get_reviews())
