from django.test import override_settings, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from preferences.models import TopicFollow, PersonFollow, LocationFollow, Preferences


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PreferencesTests(StaticLiveServerTestCase):

    fixtures = ['fl_testdata.json']

    def setUp(self):
        self.user = User.objects.create_user('devon', 'devon@dudleyville.com', 'dudley')
        self.preferences = Preferences.objects.create(user=self.user)
        self.person_id = 'ocd-person/016cf1f8-94ea-49a2-b1df-2701cee64ad2'

    def test_non_logged_in_prefs_redirects(self):
        response = self.client.get('/preferences/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/preferences/')

        response = self.client.get(reverse('find_legislator'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.post('/login/', {'username': 'Devon', 'password': 'Dudley'})
        self.assertEqual(response.status_code, 200)

    def test_add_topics(self):
        self.assertEqual(len(TopicFollow.objects.all()), 0)

        self.client.login(username='devon', password='dudley')
        subjects = ['get', 'the', 'tables']
        self.client.post(reverse('preferences'), {'subjects': subjects})

        topics_followed = TopicFollow.objects.filter(user=self.user)
        self.assertEqual(len(topics_followed), 3)
        self.assertEqual([topic.topic for topic in topics_followed], subjects)

    def test_add_locations(self):
        self.assertEqual(len(LocationFollow.objects.all()), 0)

        self.client.login(username='devon', password='dudley')
        locations = ['dudleyville', 'USA']
        self.client.post(reverse('preferences'), {'locations': locations})

        locations_followed = LocationFollow.objects.filter(user=self.user)
        self.assertEqual(len(locations_followed), 2)
        self.assertEqual([location.location for location in locations_followed], locations)

    def test_add_legislators(self):
        self.assertEqual(len(PersonFollow.objects.all()), 0)

        self.client.login(username='devon', password='dudley')
        representatives = ['ocd-person/016cf1f8-94ea-49a2-b1df-2701cee64ad2']
        senators = ['ocd-person/0c627de0-fa4b-4646-9a94-4d145e361efa']
        self.client.post(reverse('preferences'), {'representatives': representatives, 'senators': senators})

        people_followed = PersonFollow.objects.filter(user=self.user)
        self.assertEqual(len(people_followed), 2)
