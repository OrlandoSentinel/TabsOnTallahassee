# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .votes import FlVoteScraper
from .bills import FlBillScraper
from .people import FlPersonScraper


class Florida(Jurisdiction):
    division_id = "ocd-division/country:us/state:fl"
    classification = "government"
    name = "Florida"
    url = "http://myflorida.com"
    scrapers = {
        # "votes": FlVoteScraper,
        "bills": FlBillScraper,
        "people": FlPersonScraper,
    }
    parties = [{'name': 'Republican'},
               {'name': 'Democratic'},
               {'name': 'Independent'}]
    legislative_sessions = [
        {'name': '2011 Regular Session', 'identifier': '2011', },
        {'name': '2012 Regular Session', 'identifier': '2012', },
        {'name': '2012 Extraordinary Apportionment Session', 'identifier': '2012B', },
        {'name': '2013 Regular Session', 'identifier': '2013', },
        {'name': '2014 Regular Session', 'identifier': '2014', },
        {'name': '2014 Special Session A', 'identifier': '2014A', },
        {'name': '2015 Regular Session', 'identifier': '2015', },
        {'name': '2015 Special Session A', 'identifier': '2015A', },
        {'name': '2015 Special Session B', 'identifier': '2015B', },
        {'name': '2016 Regular Session', 'identifier': '2016', },
    ]

    def get_organizations(self):
        legis = Organization(name="Florida Legislature", classification="legislature")

        upper = Organization('Florida Senate', classification='upper', parent_id=legis._id)
        lower = Organization('Florida House', classification='lower', parent_id=legis._id)

        for n in range(1, 41):
            upper.add_post(label=str(n), role='Senator')
        for n in range(1, 121):
            lower.add_post(label=str(n), role='Representative')

        yield legis
        yield upper
        yield lower
