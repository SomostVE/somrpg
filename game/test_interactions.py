from html.parser import HTMLParser

from django.test import TestCase

from .models import Character


class InteractionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.form_depth = 0
        self.issues = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.form_depth += 1
            if attributes.get("action") == "#":
                self.issues.append("form posts to #")
            return

        if tag == "a":
            href = attributes.get("href")
            if not href or href == "#" or href.startswith("#"):
                self.issues.append(f"inert link: {href!r}")
            return

        if tag != "button":
            return
        if "disabled" in attributes:
            return
        if self.form_depth:
            return
        if "data-language" in attributes or "data-toast-close" in attributes:
            return
        self.issues.append(f"button without form/action: {attributes.get('class', '')}")

    def handle_endtag(self, tag):
        if tag == "form" and self.form_depth:
            self.form_depth -= 1


class InteractionAuditTests(TestCase):
    def setUp(self):
        self.character = Character.objects.create(
            name="Interaction Auditor",
            floor=5,
            gold=999,
            guard_resources=999,
        )

    def test_profile_tabs_switch_real_server_panels(self):
        cases = {
            "character": "character",
            "inventory": "inventory",
            "codex": "codex",
        }
        for tab, panel in cases.items():
            with self.subTest(tab=tab):
                response = self.client.get(f"/profile/?tab={tab}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["active_profile_tab"], tab)
                self.assertContains(response, f'data-profile-panel="{panel}"')
                self.assertNotContains(response, f'href="#{tab}"')

    def test_legacy_profile_urls_open_the_expected_tab(self):
        cases = {
            "/character/": "character",
            "/inventory/": "inventory",
            "/codex/": "codex",
        }
        for url, tab in cases.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["active_profile_tab"], tab)

    def test_main_screens_have_no_inert_links_or_unbound_buttons(self):
        urls = [
            "/",
            "/profile/",
            "/profile/?tab=inventory",
            "/profile/?tab=codex",
            "/tower/",
            "/shop/",
            "/quests/",
            "/guard/",
            "/workshop/",
            "/colony/",
            "/index/",
            "/community/",
        ]
        town_sections = (
            "overview",
            "adventures",
            "training",
            "arena",
            "market",
            "smith",
            "enchant",
            "altar",
            "companions",
            "stronghold",
            "guild",
            "daily",
            "events",
        )
        urls.extend(f"/town/?section={section}" for section in town_sections)

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                parser = InteractionParser()
                parser.feed(response.content.decode())
                self.assertEqual(parser.issues, [], f"{url}: {parser.issues}")
