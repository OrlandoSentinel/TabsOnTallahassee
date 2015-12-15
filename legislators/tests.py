from django.test import override_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from preferences.models import Preferences


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class LegislatorViewTests(StaticLiveServerTestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        u = User.objects.create_user('test')
        p = Preferences.objects.create(user=u)
        self.apikey = p.apikey

    def test_find_legislator_page(self):
        response = self.client.get(reverse('find_legislator'))
        self.assertEqual(response.status_code, 200)

    def test_legislator_detail(self):
        response = self.client.get(reverse('legislator_detail', args=['Devon Dudley']))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_add_legislator_adds_to_preferences(self):
        #TODO
        pass
