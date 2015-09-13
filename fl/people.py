import re
from urllib import parse
from pupa.scrape import Scraper, Person
from .base import Page


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

        sd = SenDetail(self.scraper, leg_url, obj=leg)
        sd.process_list()
        sd.process_page()

        return leg


class RepList(Page):
    def __init__(self, scraper):
        super().__init__(scraper,
                         "http://www.flhouse.gov/Sections/Representatives/representatives.aspx",
                         list_xpath='//div[@id="MemberListing"]/div[@class="rep_listing1"]')


    def process_list_item(self, item):
        link = item.xpath('.//div[@class="rep_style"]/a')[0]
        name = link.text_content().strip()

        if 'Vacant' in name or 'Resigned' in name or 'Pending' in name:
            return

        party = item.xpath('.//div[@class="party_style"]/text()')[0].strip()
        party = {'D': 'Democratic', 'R': 'Republican'}[party]

        district = item.xpath('.//div[@class="district_style"]/text()')[0].strip()

        leg_url = link.get('href')
        split_url = parse.urlsplit(leg_url)
        member_id = parse.parse_qs(split_url.query)['MemberId'][0]
        image = "http://www.flhouse.gov/FileStores/Web/Imaging/Member/{}.jpg".format(member_id)

        rep = Person(name=name, district=district, party=party, primary_org='lower', role='Representative',
                     image=image)
        rep.add_link(leg_url)
        rep.add_source(leg_url)
        rep.add_source(self.url)

        rd = RepDetail(self.scraper, leg_url, obj=rep)
        rd.scrape_office('Capitol Office')
        rd.scrape_office('District Office')

        return rep


class RepDetail(Page):
    def scrape_office(self, name):
        pieces = [x.tail.strip() for x in self.doc.xpath('//strong[text()="{}"]/following-sibling::br'.format(name))]

        if not pieces:
            # TODO: warn?
            return
        address = []

        for piece in pieces:
            if piece.startswith('Phone:'):
                # Phone: \r\n     (303) 111-2222
                if re.search(r'\d+', piece):
                    phone = piece.split(None, 1)[1]
                else:
                    phone = None
            else:
                address.append(re.sub(r'\s+', ' ', piece))

        type_ = 'capitol' if 'Capitol' in name else 'district'

        self.obj.add_contact_detail(type='address', value='\n'.join(address), note=type_)
        if phone:
            self.obj.add_contact_detail(type='voice', value=phone, note=type_)


class FlPersonScraper(Scraper):

    def scrape(self):
        sl = SenList(self)
        yield from sl.yield_list()
        rl = RepList(self)
        yield from rl.yield_list()
