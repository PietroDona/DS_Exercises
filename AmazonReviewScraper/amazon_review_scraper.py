import requests
from bs4 import BeautifulSoup as bsoup
from bs4.element import Tag
from dateutil.parser import parse as date_parser
from datetime import date

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
BASEURL = "https://www.amazon.com/product-reviews"


class ReviewScraper():
    def __init__(self, asin: str, sort: str = 'recent') -> None:
        sort_types = ['recent', 'helpful']
        if sort not in sort_types:
            raise ValueError(
                f"Invalid sort type. Expected one of: {sort_types}")

        self.asin = asin
        self.sort = sort

    def get_url(self, page) -> str:
        return f"{BASEURL}/{self.asin}/ref=cm_cr_arp_d_viewopt_srt?sortBy={self.sort}&pageNumber={page}"

    def get_reviews(self):
        results = []
        page = 1
        while True:
            page_list = self.get_page(page)
            if not page_list:
                break
            results += page_list
            page += 1

        return results

    def get_page(self, page):
        r = requests.get(self.get_url(page), headers=HEADERS)
        soup = bsoup(r.text, 'html.parser')

        div_reviews = soup.find_all(
            "div", id=lambda x: x and x.startswith('customer_review-'))

        result = [self.parse_review(item) for item in div_reviews]
        return result or None

    def parse_review(self, item: Tag):
        user = self.get_clean_user(item)
        rating = self.get_clean_rating(item)
        title = self.get_clean_title(item)
        date = self.get_clean_date(item)
        verified = self.get_clean_verified(item)
        content = self.get_clean_content(item)
        helpfulvote = self.get_clean_helpfulvote(item)
        return {"user": user}

    def get_clean_user(self, item: Tag) -> str:
        user = item.find("a", class_="a-profile")
        user_link = user.get('href')
        user_id = user_link.split("/")[3].split(".")[-1]
        return user_id

    def get_clean_rating(self, item: Tag) -> int:
        rating = item.find("span", class_="a-icon-alt").get_text().strip()
        rating_int = int(rating[0])
        return rating_int

    def get_clean_title(self, item: Tag) -> str:
        title = item.find(
            "a", {"data-hook": "review-title"}).get_text().strip()
        return title

    def get_clean_date(self, item: Tag) -> date:
        # from here I can extract also the country - not implemented
        meta = item.find(
            "span", {"data-hook": "review-date"}).get_text()
        raw_date = meta.split("on")[-1].strip()
        return date_parser(raw_date).date()

    def get_clean_verified(self, item: Tag) -> bool:
        return item.find("span", {"data-hook": "avp-badge"}) is not None

    def get_clean_content(self, item: Tag) -> date:
        # from here I can extract also the country - not implemented
        content = item.find(
            "span", {"data-hook": "review-body"}).get_text().strip()
        return content

    def get_clean_helpfulvote(self, item: Tag) -> int or None:
        helpfulvote = item.find(
            "span", {"data-hook": "helpful-vote-statement"})
        if not helpfulvote:
            return None
        helpfulvote_text = helpfulvote.get_text().lower()
        helpfulvote_number = helpfulvote_text.split(" ")[0].replace("one", "1")
        return(int(helpfulvote_number))


if __name__ == "__main__":
    ars = ReviewScraper(asin="B08N5PHB83", sort="helpful")
    print(ars.get_reviews())
