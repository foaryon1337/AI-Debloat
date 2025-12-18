import unittest

from ai_debloat.analyzer import AnalyzerConfig, analyze_packages, score_package
from ai_debloat.models import PackageInfo, PackageAction
from ai_debloat.presets import load_rules


class AnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = load_rules()
        self.config = AnalyzerConfig(rules=self.rules)

    def test_known_bloat_uninstalled_on_high(self) -> None:
        pkg = PackageInfo(package_name="com.facebook.katana", is_system=False)
        plan = analyze_packages([pkg], preset_name="high", config=self.config)
        self.assertEqual(plan.items[0].action, PackageAction.UNINSTALL_USER)

    def test_sensitive_component_is_kept(self) -> None:
        pkg = PackageInfo(package_name="com.android.systemui", is_system=True)
        plan = analyze_packages([pkg], preset_name="extreme", config=self.config)
        self.assertEqual(plan.items[0].action, PackageAction.KEEP)

    def test_balanced_disables_vendor_app(self) -> None:
        pkg = PackageInfo(package_name="com.verizon.vvm", is_system=True)
        result = score_package(pkg, config=self.config)
        self.assertGreaterEqual(result.risk_score, 0)
        plan = analyze_packages([pkg], preset_name="balanced", config=self.config)
        self.assertEqual(plan.items[0].action, PackageAction.DISABLE)


if __name__ == "__main__":
    unittest.main()
