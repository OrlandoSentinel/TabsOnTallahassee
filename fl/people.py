from pupa.scrape import Scraper, Person
import lxml.html
import re


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

    def process_list(self):
        for item in self.doc.xpath(self.list_xpath):
            processed = self.process_list_item(item)
            if processed:
                yield processed


class SenDetail(Page):
    def __init__(self, scraper, url, obj):
        super().__init__(scraper, url, list_xpath='//h4[contains(text(), "Office")]', obj=obj)

    def process_list_item(self, office):
        (name, ) = office.xpath('text()')
        if name == "Tallahassee Office":
            type_ = 'capitol'
        else:
            type_ = 'district'

        # phone
        PHONE_RE = r'\(\d{3}\)\s\d{3}\-\d{4}'
        if re.search(PHONE_RE, address_lines[-1]):
            phone = address_lines.pop()
        else:
            phone = None
        if phone:
            self.obj.add_contact_detail(type='phone', value=phone, note=type_)

        # address
        address_lines = [x.strip() for x in
                         office.xpath('following-sibling::div[1]/text()')
                         if x.strip()]
        if re.search(r'(?i)open\s+\w+day', address_lines[0]):
            address_lines = address_lines[1: ]
        assert ", FL" in address_lines[-1]
        address = "\n".join(address_lines)
        address = re.sub(r'\s{2,}', " ", address)

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

        # for consistency
        #if party == 'Democrat':
        #    party = 'Democratic'

        leg_url = item.get('href')

        leg = Person(name=name, district=district, party=party, primary_org='upper')
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
        yield from sl.process_list()
