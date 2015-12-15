from django.test import override_settings
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PreferencesTests(StaticLiveServerTestCase):

    def test_glossary_page_renders(self):
        response = self.client.get(reverse('glossary'))
        self.assertEqual(response.status_code, 200)

    def test_glossary_json_page_renders(self):
        response = self.client.get(reverse('glossary_json'))
        self.assertEqual(response.status_code, 200)
