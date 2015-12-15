from django.test import override_settings, Client
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PreferencesTests(StaticLiveServerTestCase):

    def test_non_logged_in_prefs_redirects(self):
        response = self.client.get('/preferences/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/preferences/')

        response = self.client.get(reverse('find_legislator'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        client = Client()
        response = client.post('/login/', {'username': 'Devon', 'password': 'Dudley'})
        self.assertEqual(response.status_code, 200)
