import re
import datetime
from pupa.scrape import Scraper, Bill
from .base import Page

class StartPage(Page):

    def process_page(self):
        try:
            page_count = int(self.doc.xpath("//a[contains(., 'Next')][1]/preceding::a[1]/text()")[0])
        except IndexError:
            if not self.doc.xpath('//div[@class="ListPagination"]/span'):
                raise AssertionError("No bills found for the session")
            elif set(self.doc.xpath('//div[@class="ListPagination"]/span/text()')) != set(["1"]):
                raise AssertionError("Bill list pagination needed but not used")
            else:
                self.scraper.warning("Pagination not used; "
                                     "make sure there're only a few bills for this session")
            page_count = 1

        for page_number in range(1, page_count + 1):
            page_url = (self.url + '&PageNumber={}'.format(page_number))
            blp = BillList(self.scraper, page_url, session=self.kwargs['session'])
            yield from blp.yield_list()


class BillList(Page):
    #list_xpath = "//a[contains(@href, '/Session/Bill/{}/')]".format(session)
    list_xpath = "//a[contains(@href, '/Session/Bill/')]"

    def process_list_item(self, item):
        bill_id = item.text.strip()
        title = item.xpath("string(../following-sibling::td[1])").strip()
        sponsor = item.xpath("string(../following-sibling::td[2])").strip()
        bill_url = item.attrib['href'] + '/ByCategory'

        if bill_id.startswith(('SB ', 'HB ', 'SPB ', 'HPB ')):
            bill_type = 'bill'
        elif bill_id.startswith(('HR ', 'SR ')):
            bill_type = 'resolution'
        elif bill_id.startswith(('HJR ', 'SJR ')):
            bill_type = 'joint resolution'
        elif bill_id.startswith(('SCR ', 'HCR ')):
            bill_type = 'concurrent resolution'
        elif bill_id.startswith(('SM ', 'HM ')):
            bill_type = 'memorial'
        else:
            raise ValueError('Failed to identify bill type.')

        bill = Bill(bill_id, self.kwargs['session'], title, classification=bill_type)
        bill.add_source(bill_url)

        # single sponsor for FL bills
        sponsor = re.sub(r'^(?:Rep|Sen)\.\s', "", sponsor)
        bill.add_sponsorship(sponsor, 'primary', 'person', True)

        bdp = BillDetail(self.scraper, bill_url, obj=bill)
        bdp.process_page()

        return bill


class BillDetail(Page):
    def process_page(self):
        hist_table = self.doc.xpath("//div[@id = 'tabBodyBillHistory']//table")[0]

        for tr in hist_table.xpath("tbody/tr"):
            date = tr.xpath("string(td[1])")
            date = datetime.datetime.strptime(date, "%m/%d/%Y").date().isoformat()

            actor = tr.xpath("string(td[2])")
            if not actor:
                continue
            chamber = {'Senate': 'upper', 'House': 'lower'}.get(actor, None)
            if chamber:
                actor = None

            act_text = tr.xpath("string(td[3])").strip()
            for action in act_text.split(u'\u2022'):
                action = action.strip()
                if not action:
                    continue

                action = re.sub(r'-(H|S)J\s+(\d+)$', '', action)

                atype = []
                if action.startswith('Referred to'):
                    atype.append('committee-referral')
                elif action.startswith('Favorable by'):
                    atype.append('committee-passage')
                elif action == "Filed":
                    atype.append("filing")
                elif action.startswith("Withdrawn"):
                    atype.append("withdrawal")
                elif action.startswith("Died"):
                    atype.append("failure")
                elif action.startswith('Introduced'):
                    atype.append('introduction')
                elif action.startswith('Read 2nd time'):
                    atype.append('reading-2')
                elif action.startswith('Read 3rd time'):
                    atype.append('reading-3')
                elif action.startswith('Adopted'):
                    atype.append('passage')
                elif action.startswith('CS passed'):
                    atype.append('passage')

                self.obj.add_action(action, date, organization=actor, chamber=chamber,
                                    classification=atype)

class FlBillScraper(Scraper):

    def scrape(self, session):
        url = "http://flsenate.gov/Session/Bills/{}?chamber=both".format(session)
        yield from StartPage(self, url, session=session).process_page()
