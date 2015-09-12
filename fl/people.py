from pupa.scrape import Scraper, Person
import lxml.html
import re

class NoListItems(Exception):
    pass

class Page:
    def __init__(self, scraper, url, *, list_xpath=None, obj=None):
        self.scraper = scraper
        self.url = url
        self.doc = lxml.html.fromstring(scraper.get(url).text)
        self.doc.make_links_absolute(url)
        self.list_xpath = list_xpath
        self.obj = obj

    def process_list_item(self, item):
        pass

    def yield_list(self):
        n = 0
        for item in self.doc.xpath(self.list_xpath):
            n += 1
            processed = self.process_list_item(item)
            if processed:
                yield processed
        if not n:
            raise NoListItems()

    def process_list(self):
        n = 0
        for item in self.doc.xpath(self.list_xpath):
            n += 1
            processed = self.process_list_item(item)
        if not n:
            raise NoListItems()


class SenDetail(Page):
    def __init__(self, scraper, url, obj):
        super().__init__(scraper, url, list_xpath='//h4[contains(text(), "Office")]', obj=obj)

    def process_list_item(self, office):
        (name, ) = office.xpath('text()')
        if name == "Tallahassee Office":
            type_ = 'capitol'
        else:
            type_ = 'district'

        address_lines = [x.strip() for x in
                         office.xpath('following-sibling::div[1]/text()')
                         if x.strip()]

        clean_address_lines = []
        phone = None
        PHONE_RE = r'\(\d{3}\)\s\d{3}\-\d{4}'

        for line in address_lines:
            if re.search(r'(?i)open\s+\w+day', address_lines[0]):
                continue
            elif re.search(PHONE_RE, line):
                phone = line
                break
            else:
                clean_address_lines.append(line)

        if phone:
            self.obj.add_contact_detail(type='voice', value=phone, note=type_)

        # address
        address = "\n".join(clean_address_lines)
        address = re.sub(r'\s{2,}', " ", address)
        if address:
            self.obj.add_contact_detail(type='address', value=address, note=type_)

    def process_page(self):
        email = self.doc.xpath('//a[contains(@href, "mailto:")]')[0].get('href').split(':')[-1]
        self.obj.add_contact_detail(type='email', value=email)

        self.obj.image = self.doc.xpath('//div[@id="sidebar"]//img/@src').pop()


class SenList(Page):
    def __init__(self, scraper):
        super().__init__(scraper,
                         "http://www.flsenate.gov/Senators/",
                         list_xpath="//a[contains(@href, 'Senators/s')]")

    def process_list_item(self, item):
        name = " ".join(item.xpath('.//text()'))
        name = re.sub(r'\s+', " ", name).replace(" ,", ",").strip()

        if 'Vacant' in name:
            return

        district = item.xpath("string(../../td[1])")
        party = item.xpath("string(../../td[2])")
        if party == 'Democrat':
            party = 'Democratic'

        leg_url = item.get('href')

        leg = Person(name=name, district=district, party=party, primary_org='upper', role='Senator')
        leg.add_link(leg_url)
        leg.add_source(self.url)
        leg.add_source(leg_url)

        sd_obj = SenDetail(self.scraper, leg_url, obj=leg)
        sd_obj.process_list()
        sd_obj.process_page()

        return leg


class FlPersonScraper(Scraper):

    def scrape(self):
        sl = SenList(self)
        yield from sl.yield_list()
