from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from preferences.models import Preferences


class BillViewTests(StaticLiveServerTestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        u = User.objects.create_user('test')
        p = Preferences.objects.create(user=u)
        self.apikey = p.apikey

    def test_by_topic_view(self):
        response = self.client.get(reverse('by_topic'))
        self.assertEqual(response.status_code, 200)

    # def test_by_topic_view_selected(self):
    #     response = self.client.get(reverse('by_topic_selected'))
    #     self.assertEqual(response.status_code, 200)
