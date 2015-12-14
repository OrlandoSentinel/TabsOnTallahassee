from django.test import override_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from preferences.models import Preferences


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class BillViewTests(StaticLiveServerTestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        u = User.objects.create_user('test')
        p = Preferences.objects.create(user=u)
        self.apikey = p.apikey

    def test_by_topic_view(self):
        response = self.client.get(reverse('by_topic'))
        self.assertEqual(response.status_code, 200)

    def test_by_topic_view_selected(self):
        response = self.client.get(reverse('by_topic_selected', args=['dudleys']))
        self.assertEqual(response.status_code, 200)
