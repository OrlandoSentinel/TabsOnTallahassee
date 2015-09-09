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
        #"votes": FlVoteScraper,
        #"bills": FlBillScraper,
        "people": FlPersonScraper,
    }
    parties = [{'name': 'Republican'},
               {'name': 'Democratic'},
               {'name': 'Independent'}]

    def get_organizations(self):
        #REQUIRED: define an organization using this format
        #where org_name is something like Seattle City Council
        #and classification is described here:
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
