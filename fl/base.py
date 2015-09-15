import os
import subprocess
import lxml.html


class NoListItems(Exception):
    pass


class Page:
    def __init__(self, scraper, url=None, *, obj=None, **kwargs):
        self.scraper = scraper
        if url:
            self.url = url
        self.doc = lxml.html.fromstring(scraper.get(self.url).text)
        self.doc.make_links_absolute(self.url)
        self.obj = obj
        self.kwargs = kwargs

    def process_list_item(self, item):
        raise NotImplementedError()

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


class PDF:
    def __init__(self, scraper, url=None, *, obj=None, **kwargs):
        self.scraper = scraper
        if url:
            self.url = url
        self.obj = obj
        self.kwargs = kwargs

        (path, resp) = self.scraper.urlretrieve(url)

        self.text = self.convert_pdf(path, 'text').decode('utf8')
        self.lines = self.text.split('\n')
        os.remove(path)

    def convert_pdf(self, filename, type='xml'):
        commands = {'text': ['pdftotext', '-layout', filename, '-'],
                    'text-nolayout': ['pdftotext', filename, '-'],
                    'xml': ['pdftohtml', '-xml', '-stdout', filename],
                    'html': ['pdftohtml', '-stdout', filename]}
        try:
            pipe = subprocess.Popen(commands[type], stdout=subprocess.PIPE, close_fds=True).stdout
        except OSError as e:
            raise EnvironmentError("error running {}, missing executable? [{}]".format(' '.join(commands[type]), e))
        data = pipe.read()
        pipe.close()
        return data
