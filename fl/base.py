import lxml.html


class NoListItems(Exception):
    pass


class Page:
    def __init__(self, scraper, url=None, *, obj=None):
        self.scraper = scraper
        if url:
            self.url = url
        self.doc = lxml.html.fromstring(scraper.get(self.url).text)
        self.doc.make_links_absolute(self.url)
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
            self.process_list_item(item)
        if not n:
            raise NoListItems()
