from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from opencivicdata.models import Bill, LegislativeSession, Person

from tot import settings
from preferences.models import Preferences

BILL_FULL_FIELDS = ('abstracts', 'other_titles', 'other_identifiers',
                    'actions', 'related_bills', 'sponsorships',
                    'documents', 'versions', 'sources')


class BillViewTests(TestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        u = User.objects.create_user('test')
        p = Preferences.objects.create(user=u)
        self.apikey = p.apikey

    def test_by_topic_view(self):
        response = self.client.get(reverse('by_topic'))
        self.assertEqual(response.status_code, 200)

    def test_by_topic_view_selected(self):
        response = self.client.get(reverse('by_topic_selected'))
        self.assertEqual(response.status_code, 200)
