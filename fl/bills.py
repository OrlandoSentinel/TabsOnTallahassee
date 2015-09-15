import re
import datetime
from pupa.scrape import Scraper, Bill, Vote
from .base import Page, PDF, Spatula


class StartPage(Page):

    def process_page(self):
        try:
            pages = int(self.doc.xpath("//a[contains(., 'Next')][1]/preceding::a[1]/text()")[0])
        except IndexError:
            if not self.doc.xpath('//div[@class="ListPagination"]/span'):
                raise AssertionError("No bills found for the session")
            elif set(self.doc.xpath('//div[@class="ListPagination"]/span/text()')) != set(["1"]):
                raise AssertionError("Bill list pagination needed but not used")
            else:
                self.scraper.warning("Pagination not used; "
                                     "make sure there are only a few bills for this session")
            pages = 1

        for page_number in range(1, pages + 1):
            page_url = (self.url + '&PageNumber={}'.format(page_number))
            yield from self.get_page(BillList, url=page_url, session=self.kwargs['session'])


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

        sponsor = re.sub(r'^(?:Rep|Sen)\.\s', "", sponsor)
        for sp in sponsor.split(', '):
            bill.add_sponsorship(sp, 'primary', 'person', True)

        yield from self.get_page(BillDetail, url=bill_url, obj=bill)

        yield bill


class BillDetail(Page):
    def process_page(self):
        self.process_history()
        self.process_versions()
        self.process_analysis()
        yield from self.process_votes()

    def process_versions(self):
        try:
            version_table = self.doc.xpath("//div[@id = 'tabBodyBillText']/table")[0]
            for tr in version_table.xpath("tbody/tr"):
                name = tr.xpath("string(td[1])").strip()
                version_url = tr.xpath("td/a[1]")[0].attrib['href']
                if version_url.endswith('PDF'):
                    mimetype = 'application/pdf'
                elif version_url.endswith('HTML'):
                    mimetype = 'text/html'
                self.obj.add_version_link(name, version_url, media_type=mimetype)
        except IndexError:
            self.scraper.warning("No version table for {}".format(self.obj.identifier))

    def process_analysis(self):
        try:
            analysis_table = self.doc.xpath("//div[@id = 'tabBodyAnalyses']/table")[0]
            for tr in analysis_table.xpath("tbody/tr"):
                name = tr.xpath("string(td[1])").strip()
                name += " -- " + tr.xpath("string(td[3])").strip()
                name = re.sub(r'\s+', " ", name)
                date = tr.xpath("string(td[4])").strip()
                if date:
                    name += " (%s)" % date
                analysis_url = tr.xpath("td/a")[0].attrib['href']
                self.obj.add_document_link(name, analysis_url)
        except IndexError:
            self.scraper.warning("No analysis table for {}".format(self.obj.identifier))

    def process_history(self):
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

    def process_votes(self):
        vote_tables = self.doc.xpath("//div[@id='tabBodyVoteHistory']//table")

        for vote_table in vote_tables:
            for tr in vote_table.xpath("tbody/tr"):
                vote_date = tr.xpath("string(td[3])").strip()
                if vote_date.isalpha():
                    vote_date = tr.xpath("string(td[2])").strip()
                try:
                    vote_date = datetime.datetime.strptime(vote_date, "%m/%d/%Y %H:%M %p").strftime("%Y-%m-%d %H:%M:00")
                except ValueError:
                    self.scraper.logger.warning('bad vote date: {}'.format(vote_date))

                vote_url = tr.xpath("td[4]/a")[0].attrib['href']
                if "SenateVote" in vote_url:
                    fv = FloorVote(self.scraper, url=vote_url,
                                   date=vote_date, chamber='upper', bill=self.obj)
                    yield from fv.process_page()
                elif "HouseVote" in vote_url:
                    fv = FloorVote(self.scraper, url=vote_url,
                                   date=vote_date, chamber='lower', bill=self.obj)
                    yield from fv.process_page()
                else:
                    pass
                    #raise Exception('??? ' + vote_url)
                    #self.scrape_uppper_committee_vote(bill, vote_date, vote_url)
        else:
            self.scraper.warning("No vote table for {}".format(self.obj.identifier))


class FloorVote(PDF):
    def process_page(self):
        MOTION_INDEX = 4
        TOTALS_INDEX = 6
        VOTE_START_INDEX = 9

        motion = self.lines[MOTION_INDEX].strip()
        # Sometimes there is no motion name, only "Passage" in the line above
        if (not motion and not self.lines[MOTION_INDEX - 1].startswith("Calendar Page:")):
            motion = self.lines[MOTION_INDEX - 1]
            MOTION_INDEX -= 1
            TOTALS_INDEX -= 1
            VOTE_START_INDEX -= 1
        else:
            assert motion, "Floor vote's motion name appears to be empty"

        for _extra_motion_line in range(2):
            MOTION_INDEX += 1
            if self.lines[MOTION_INDEX].strip():
                motion = "{}, {}".format(motion, self.lines[MOTION_INDEX].strip())
                TOTALS_INDEX += 1
                VOTE_START_INDEX += 1
            else:
                break

        (yes_count, no_count, nv_count) = [
            int(x) for x in re.search(r'^\s+Yeas - (\d+)\s+Nays - (\d+)\s+Not Voting - (\d+)\s*$',
                                      self.lines[TOTALS_INDEX]).groups()
        ]
        result = 'pass' if yes_count > no_count else 'fail'

        vote = Vote(#legislative_session=self.kwargs['bill'].legislative_session,
                    start_date=self.kwargs['date'],
                    chamber=self.kwargs['chamber'],
                    bill=self.kwargs['bill'],
                    motion_text=motion,
                    result=result,
                    classification='passage',
                    )
        vote.add_source(self.url)
        vote.set_count('yes', yes_count)
        vote.set_count('no', no_count)
        vote.set_count('not voting', nv_count)

        for line in self.lines[VOTE_START_INDEX:]:
            if not line.strip():
                break

            if " President " in line:
                line = line.replace(" President ", " ")
            elif " Speaker " in line:
                line = line.replace(" Speaker ", " ")

            # Votes follow the pattern of:
            # [vote code] [member name]-[district number]
            for member in re.findall(r'\s*Y\s+(.*?)-\d{1,3}\s*', line):
                vote.yes(member)
            for member in re.findall(r'\s*N\s+(.*?)-\d{1,3}\s*', line):
                vote.no(member)
            for member in re.findall(r'\s*(?:EX|AV)\s+(.*?)-\d{1,3}\s*', line):
                vote.vote('not voting', member)

        #try:
        #    vote.validate()
        #except ValueError:
        #    # On a rare occasion, a member won't have a vote code,
        #    # which indicates that they didn't vote. The totals reflect
        #    # this.
        #    self.scraper.info("Votes don't add up; looking for additional ones")
        #    for line in self.lines[VOTE_START_INDEX:]:
        #        if not line.strip():
        #            break
        #        for member in re.findall(r'\s{8,}([A-Z][a-z\'].*?)-\d{1,3}', line):
        #            vote.other(member)
        yield vote


class FlBillScraper(Scraper, Spatula):

    def scrape(self, session):
        url = "http://flsenate.gov/Session/Bills/{}?chamber=both".format(session)
        yield from self.get_page(StartPage, url, session=session)
