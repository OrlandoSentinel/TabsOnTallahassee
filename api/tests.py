import json
from django.test import TestCase
from opencivicdata.models import Person, Organization, Membership

PERSON_FULL_FIELDS = ('identifiers', 'other_names', 'contact_details',
                      'object_links', 'sources')

class ApiTests(TestCase):

    fixtures = ['fl_testdata.json']

    def _api(self, method):
        return self.client.get('/api/{}&format=vnd.api%2Bjson'.format(method))

    def test_jurisdiction_list(self):
        resp = self._api('jurisdictions/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        assert len(data['data']) == 1

        # check legislative_sessions isn't there by default
        assert 'legislative_sessions' not in data['data'][0]['attributes']

        # ensure self URL is correct (was being masked by .url attribute)
        url = data['data'][0]['links']['self']
        assert '/api/ocd-jurisdiction/country:us/state:fl/government/' in url

    def test_jurisdiction_detail(self):
        resp = self._api('ocd-jurisdiction/country:us/state:fl/government/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))

        # check that legislative sessions is there by default
        assert 'legislative_sessions' in data['data']['attributes']

    def test_person_list(self):
        resp = self._api('people/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        assert len(data['data']) == 50
        for field in PERSON_FULL_FIELDS:
            assert field not in data['data'][0]['attributes']
        assert 'relationships' not in data['data'][0]

    def test_person_detail(self):
        resp = self._api('ocd-person/0446be69-7504-417d-97c1-136589908ee5/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))

        # check that legislative sessions is there by default
        for field in PERSON_FULL_FIELDS:
            assert field in data['data']['attributes']
        assert 'memberships' in data['data']['relationships']

    def test_person_list_by_name(self):
        resp = self._api('people/?name=John')
        data = json.loads(resp.content.decode('utf8'))
        assert len(data['data']) == 4

    def test_person_list_by_member_of(self):
        resp = self._api('people/?member_of=Republican')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 107

    def test_person_list_by_member_of_name(self):
        resp = self._api('people/?member_of=Republican&name=John')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 3

    def test_person_list_by_former_member_of(self):
        resp = self._api('people/?ever_member_of=Republican')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 107

        # add former membership to republican party to democrat
        r = Organization.objects.get(name='Republican')
        Membership.objects.create(person_id='ocd-person/0446be69-7504-417d-97c1-136589908ee5',
                                  organization=r, end_date='2000')

        # ever_member_of now returns 108 & member_of still returns 107
        resp = self._api('people/?ever_member_of=Republican')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 108
        resp = self._api('people/?member_of=Republican')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 107

    # TODO get lat long working
    #def test_person_list_by_lat_lon(self):
    #    resp = self._api('people/?latitude=39&longitude=-88')
    #    data = json.loads(resp.content.decode('utf8'))
    #    assert data['meta']['pagination']['count'] == 2

    def test_bill_list(self):
        resp = self._api('bills/?')
        self.assertEqual(resp.status_code, 200)

    def test_vote_list(self):
        resp = self._api('votes/?')
        self.assertEqual(resp.status_code, 200)
