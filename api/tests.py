import time
import json
from django.test import TestCase
from django.contrib.auth.models import User
from opencivicdata.models import Organization, Membership, Person
from preferences.models import Preferences

PERSON_FULL_FIELDS = ('identifiers', 'other_names', 'contact_details',
                      'object_links', 'sources')
BILL_FULL_FIELDS = ('abstracts', 'other_titles', 'other_identifiers',
                    'actions', 'related_bills', 'sponsorships',
                    'documents', 'versions', 'sources')
VOTE_FULL_FIELDS = ('counts', 'votes', 'sources')


class ApiTests(TestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        u = User.objects.create_user('test')
        p = Preferences.objects.create(user=u)
        self.apikey = p.apikey

    def _api(self, method):
        return self.client.get('/api/{}&format=vnd.api%2Bjson&apikey={}'.format(
            method, self.apikey))

    def test_jurisdiction_list(self):
        with self.assertNumQueries(4):
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
        with self.assertNumQueries(4):
            resp = self._api('ocd-jurisdiction/country:us/state:fl/government/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))

        # check that legislative sessions is there by default
        assert 'legislative_sessions' in data['data']['attributes']

    def test_person_list(self):
        with self.assertNumQueries(7):
            resp = self._api('people/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        assert len(data['data']) == 50
        for field in PERSON_FULL_FIELDS:
            assert field not in data['data'][0]['attributes']
        assert 'relationships' not in data['data'][0]


    def test_person_detail(self):
        with self.assertNumQueries(11):
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

    def test_person_list_by_name_no_duplicates(self):
        p = Person.objects.get(name='Soto, Darren')
        p.other_names.create(name='Darren Soto')
        p.other_names.create(name='Soto')
        resp = self._api('people/?name=Soto')
        data = json.loads(resp.content.decode('utf8'))
        assert len(data['data']) == 1

    def test_person_list_by_member_of(self):
        resp = self._api('people/?member_of=Republican')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 107

    def test_person_list_by_member_of_id(self):
        resp = self._api('people/?member_of=ocd-organization/8fbc15ed-043f-408a-a0a2-5d9c7dd62675')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 53

    def test_person_list_by_member_of_with_name(self):
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

    def test_person_list_by_lat_lon(self):
        resp = self._api('people/?latitude=28.4&longitude=-82.2')
        data = json.loads(resp.content.decode('utf8'))
        assert data['meta']['pagination']['count'] == 2

    def test_person_include_memberships(self):
        resp = self._api(
            'people/?fields=memberships&include=memberships,memberships.organization'
        )
        data = json.loads(resp.content.decode('utf8'))
        include_counts = {'Membership': 0, 'Organization': 0}
        for inc in data['included']:
            include_counts[inc['type']] += 1

        self.assertEqual(include_counts['Membership'], 100)
        self.assertEqual(include_counts['Organization'], 4)

    def test_bill_list(self):
        with self.assertNumQueries(4):
            resp = self._api('bills/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 48)
        for field in BILL_FULL_FIELDS:
            assert field not in data['data'][0]['attributes']
        self.assertEqual(['from_organization'], list(data['data'][0]['relationships'].keys()))

    def test_bill_detail(self):
        with self.assertNumQueries(18):
            resp = self._api('ocd-bill/3cc1d006-7059-465c-b72b-d0d4a845c55c/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))

        # check that legislative sessions is there by default
        for field in BILL_FULL_FIELDS:
            self.assertIn(field, data['data']['attributes'])
        self.assertEqual(['from_organization'], list(data['data']['relationships'].keys()))

    def test_bills_by_session(self):
        resp = self._api('bills/?legislative_session=2015B')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 7)

    def test_bills_by_subject(self):
        resp = self._api('bills/?subject=legislature')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 4)

    def test_bills_by_place(self):
        resp = self._api('bills/?extras={"places":["Citrus"]}')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 6)

    def test_bills_by_org_name(self):
        resp = self._api('bills/?from_organization=Florida House of Representatives')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 23)

    def test_bills_by_org_id(self):
        resp = self._api('bills/?from_organization='
                         'ocd-organization/fe0255b6-09ae-4155-8173-c85d92b6b41c')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 25)

    def test_bills_by_sponsor_name(self):
        resp = self._api('bills/?sponsor=Corcoran')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 4)

    def test_bills_by_sponsor_resolved_name(self):
        resp = self._api('bills/?sponsor=Corcoran, Richard')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 4)

    def test_bills_by_sponsor_id(self):
        resp = self._api('bills/?sponsor=ocd-person/10394057-4944-4336-830b-6c4377fc6d45')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 4)

    def test_bills_by_query(self):
        start = time.time()
        resp = self._api('bills/?q=election')
        took = time.time() - start
        self.assertEqual(resp.data['meta']['pagination']['count'], 16)
        # if it took longer than 1 second there wasn't an index
        self.assertLess(took, 1)

    def test_bills_by_query_with_spaces(self):
        start = time.time()
        resp = self._api('bills/?q=division of elections')
        took = time.time() - start
        self.assertEqual(resp.data['meta']['pagination']['count'], 10)
        # if it took longer than 1 second there wasn't an index
        self.assertLess(took, 1)

    def test_bills_by_query_with_session(self):
        # ensure that the fulltext search can be combined
        resp = self._api('bills/?q=election&legislative_session=2015B')
        self.assertEqual(resp.data['meta']['pagination']['count'], 3)

    def test_vote_list(self):
        with self.assertNumQueries(4):
            resp = self._api('votes/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 83)
        for field in VOTE_FULL_FIELDS:
            assert field not in data['data'][0]['attributes']
        self.assertEqual({'bill', 'organization'}, set(data['data'][0]['relationships'].keys()))

    def test_vote_detail(self):
        with self.assertNumQueries(10):
            resp = self._api('ocd-vote/06c4f6c2-b9a2-4ee6-95ad-a40b80cfbc27/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))

        # check that legislative sessions is there by default
        for field in VOTE_FULL_FIELDS:
            self.assertIn(field, data['data']['attributes'])
        self.assertEqual({'bill', 'organization'}, set(data['data']['relationships'].keys()))

    def test_vote_by_voter(self):
        # an unresolved name
        resp = self._api('votes/?voter=Kerner')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 42)

    def test_vote_by_resolved_voter(self):
        # a resolved name
        resp = self._api('votes/?voter=Murphy, Amanda')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 42)

    def test_vote_by_resolved_voter_id(self):
        resp = self._api('votes/?voter=ocd-person/fc6f3850-ec2b-4529-88c5-80f663bb41f0')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 42)

    def test_vote_by_unresolved_voter_and_vote(self):
        # a resolved name
        resp = self._api('votes/?voter=Cummings&option=not voting')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 3)

    def test_vote_by_bill(self):
        resp = self._api('votes/?bill=ocd-bill/0672133f-acaf-440b-bc53-1b5dbcbb7971')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 6)

    def test_vote_by_org_id(self):
        resp = self._api('votes/?organization='
                         'ocd-organization/857ae9af-8682-42ea-a9d2-66b12b54f854')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 51)

    def test_vote_by_org_name(self):
        resp = self._api('votes/?organization=Florida Senate')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 32)

    def test_membership_list(self):
        with self.assertNumQueries(4):
            resp = self._api('memberships/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['meta']['pagination']['count'], 320)

    def test_membership_detail(self):
        with self.assertNumQueries(5):
            resp = self._api('ocd-organization/857ae9af-8682-42ea-a9d2-66b12b54f854/?')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
