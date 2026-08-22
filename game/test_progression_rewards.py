from django.test import TestCase

from .models import Character
from .progression_rewards import earned_skills, earned_titles


class ProgressionRewardTests(TestCase):
    def test_skill_unlocks_from_objective_and_grants_real_stats(self):
        character = Character.objects.create(name="Skilled", level=3, max_hp=30)
        codes = {reward["code"] for reward in earned_skills(character)}

        self.assertIn("survivor_instinct", codes)
        self.assertEqual(character.skill_hp_bonus, 10)
        self.assertEqual(character.combat_max_hp, 50)  # 30 base + 10 Vanguard + 10 skill

    def test_multiple_passive_skills_stack(self):
        character = Character.objects.create(
            name="Frontliner",
            archetype="strider",
            floor=5,
            dungeon_clears=15,
            crafting_xp=25,
            attack=5,
            defense=1,
        )

        self.assertEqual(character.skill_attack_bonus, 3)
        self.assertEqual(character.skill_defense_bonus, 3)
        self.assertEqual(character.total_attack, 10)  # 5 base + 2 class + 3 skills
        self.assertEqual(character.total_defense, 4)

    def test_title_must_be_earned_before_it_can_be_selected(self):
        character = Character.objects.create(name="Title Hunter", floor=1)

        response = self.client.post("/profile/title/activate/", {"title": "bastion_breaker"})

        self.assertRedirects(response, "/profile/?tab=abilities")
        character.refresh_from_db()
        self.assertEqual(character.active_title, "")

    def test_active_title_grants_only_its_own_bonus(self):
        character = Character.objects.create(name="Breaker", floor=6, attack=5)
        self.assertIn("bastion_breaker", {reward["code"] for reward in earned_titles(character)})

        response = self.client.post("/profile/title/activate/", {"title": "bastion_breaker"})

        self.assertRedirects(response, "/profile/?tab=abilities")
        character.refresh_from_db()
        self.assertEqual(character.active_title, "bastion_breaker")
        self.assertEqual(character.title_attack_bonus, 2)
        self.assertEqual(character.title_hp_bonus, 0)

    def test_profile_lists_locked_and_unlocked_rewards_with_objectives(self):
        Character.objects.create(name="Reward Viewer", level=3, floor=2)

        response = self.client.get("/profile/?tab=abilities")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_profile_tab"], "abilities")
        self.assertContains(response, "COMPÉTENCES & TITRES")
        self.assertContains(response, "Instinct de survie")
        self.assertContains(response, "Premier grimpeur")
        self.assertContains(response, "DÉBLOQUÉE")
        self.assertContains(response, "VERROUILLÉ")
        self.assertContains(response, "Atteindre le niveau 3")
        self.assertContains(response, 'action="/profile/title/activate/"', html=False)
