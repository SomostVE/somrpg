from django.test import TestCase

from .models import Character
from .views import ACTIVE_FLOOR_SESSION_KEY


class SidebarSummaryTests(TestCase):
    def test_sidebar_shows_current_and_max_sector_once(self):
        Character.objects.create(name="Compact Hero", floor=12)
        session = self.client.session
        session[ACTIVE_FLOOR_SESSION_KEY] = 4
        session.save()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compact Hero")
        self.assertContains(response, "Secteur</span> 04 / 12", html=False)
        self.assertNotContains(response, "Secteur actuel")
        self.assertNotContains(response, "Secteur maximal débloqué")
        self.assertNotContains(response, "Current sector")
        self.assertNotContains(response, "Highest unlocked sector")
