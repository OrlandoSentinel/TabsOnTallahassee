from pupa.scrape import Scraper
from pupa.scrape import Bill


class FlBillScraper(Scraper):

    def scrape(self, session):
        print(session)
