import unittest

from ai_debloat.knowledge import find_profiles, load_package_db


class KnowledgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = load_package_db()

    def test_loads_known_core_package(self) -> None:
        profile = self.db.get("com.google.android.gms")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.removal_risk, "critical")

    def test_partial_match(self) -> None:
        profiles = find_profiles(["com.samsung.android.game"], db=self.db)
        self.assertTrue(any(p.package == "com.samsung.android.game.gamehome" for p in profiles))


if __name__ == "__main__":
    unittest.main()
