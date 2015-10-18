from django.test import TestCase

class ApiTests(TestCase):

    fixtures = ['fl_testdata.json']

    def _api(self, method):
        return self.client.get('/api/{}&format=vnd.api%2Bjson'.format(method))

    def test_jurisdiction_list(self):
        resp = self._api('jurisdictions/?')
        self.assertEqual(resp.status_code, 200)

    def test_person_list(self):
        resp = self._api('people/?')
        self.assertEqual(resp.status_code, 200)

    def test_bill_list(self):
        resp = self._api('bills/?')
        self.assertEqual(resp.status_code, 200)

    def test_vote_list(self):
        resp = self._api('votes/?')
        self.assertEqual(resp.status_code, 200)

    def test_jurisdiction_detail(self):
        resp = self._api('ocd-jurisdiction/country:us/state:fl/government/?')
        self.assertEqual(resp.status_code, 200)
