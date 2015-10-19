from django.test import TestCase
import json


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

        # ensure self URL is correct
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

    def test_bill_list(self):
        resp = self._api('bills/?')
        self.assertEqual(resp.status_code, 200)

    def test_vote_list(self):
        resp = self._api('votes/?')
        self.assertEqual(resp.status_code, 200)
