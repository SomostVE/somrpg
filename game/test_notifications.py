from unittest.mock import patch

from django.test import TestCase

from .models import Character


class NotificationAndRecoveryTests(TestCase):
    def test_base_layout_uses_bottom_right_notification_assets(self):
        Character.objects.create(name="Notifier")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="notification-stack"')
        self.assertContains(response, "css/v0103-notifications.css")
        self.assertContains(response, "js/notifications.js")
        self.assertNotContains(response, 'class="retro-window message-window"')

    def test_missing_page_returns_to_previous_screen_with_notification(self):
        Character.objects.create(name="Navigator", floor=2)
        response = self.client.get(
            "/feature-that-does-not-exist/",
            HTTP_REFERER="http://testserver/colony/",
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/colony/")
        self.assertContains(response, "Page indisponible / Page unavailable")
        self.assertContains(response, 'class="system-toast toast-warning"')

    @patch("game.colony_views.collect_colony_gold", side_effect=RuntimeError("unexpected"))
    def test_unexpected_colony_collection_error_recovers_without_loop(self, mocked_collect):
        Character.objects.create(name="Collector", floor=2)
        response = self.client.post("/colony/collect/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/colony/")
        self.assertContains(response, "Erreur inattendue dans la colonie / Unexpected colony error")
        self.assertContains(response, 'class="system-toast toast-error"')
        mocked_collect.assert_called_once()

    def test_colony_page_explains_the_gameplay_loop(self):
        Character.objects.create(name="Founder", floor=2)
        response = self.client.get("/colony/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FONCTIONNEMENT DE LA COLONIE")
        self.assertContains(response, "Recruter")
        self.assertContains(response, "Produire")
        self.assertContains(response, "Améliorer")
