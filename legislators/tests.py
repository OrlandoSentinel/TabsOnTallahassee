from django.test import override_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from preferences.models import Preferences, PersonFollow


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class LegislatorViewTests(StaticLiveServerTestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        self.user = User.objects.create_user('devon', 'devon@dudleyville.com', 'dudley')
        self.preferences = Preferences.objects.create(user=self.user)
        self.person_id = 'ocd-person/016cf1f8-94ea-49a2-b1df-2701cee64ad2'

    def test_find_legislator_page(self):
        response = self.client.get(reverse('find_legislator'))
        self.assertEqual(response.status_code, 200)

    def test_legislator_detail(self):
        response = self.client.get(reverse(
            'legislator_detail',
            args=[self.person_id]))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_add_legislator_adds_to_personfollow(self):
        self.assertEqual(len(PersonFollow.objects.all()), 0)
        self.client.login(username='devon', password='dudley')
        self.client.post(reverse('legislator_detail', args=[self.person_id]))
        person = PersonFollow.objects.get(user=self.user, person_id=self.person_id)
        self.assertEqual(person.person_id, self.person_id)
