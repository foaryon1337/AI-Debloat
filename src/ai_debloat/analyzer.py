from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .models import (
    ActionItem,
    ActionPlan,
    AnalysisReason,
    AnalysisResult,
    PackageAction,
    PackageInfo,
)
from .presets import Rules, load_rules, PRESETS


@dataclass
class AnalyzerConfig:
    rules: Rules


DEFAULT_CONFIG = AnalyzerConfig(rules=load_rules())


def _keyword_hits(package_name: str, keywords: Iterable[str]) -> List[str]:
    hits = []
    lowered = package_name.lower()
    for kw in keywords:
        if kw in lowered:
            hits.append(kw)
    return hits


def score_package(pkg: PackageInfo, config: AnalyzerConfig = DEFAULT_CONFIG) -> AnalysisResult:
    rules = config.rules
    reasons: List[AnalysisReason] = []
    risk = 0

    if pkg.package_name in rules.critical_allowlist:
        reasons.append(AnalysisReason(code="allowlist", detail="Critical service"))
        return AnalysisResult(pkg, risk_score=0, reasons=reasons, recommended_action=PackageAction.KEEP)

    if pkg.package_name in rules.known_bloatware:
        risk += 6
        reasons.append(AnalysisReason(code="bloatware", detail="Known bloatware"))

    if pkg.package_name in rules.known_trackers:
        risk += 8
        reasons.append(AnalysisReason(code="tracker", detail="Known tracker/ads"))

    vendor_hits = _keyword_hits(pkg.package_name, rules.vendor_signatures)
    if vendor_hits:
        risk += 3
        reasons.append(
            AnalysisReason(code="vendor", detail=f"Vendor/carrier signature ({', '.join(vendor_hits)})")
        )

    if pkg.is_system:
        risk += 1
        reasons.append(AnalysisReason(code="system", detail="System package"))

    if pkg.package_name in rules.oem_utilities:
        risk = max(risk - 2, 0)
        reasons.append(AnalysisReason(code="oem", detail="OEM utility (prefer keep)"))

    sensitive_hits = _keyword_hits(pkg.package_name, rules.sensitive_features)
    if sensitive_hits:
        risk = max(risk - 3, 0)
        reasons.append(
            AnalysisReason(code="sensitive", detail=f"Sensitive component ({', '.join(sensitive_hits)})")
        )

    if "ad" in pkg.package_name:
        risk += 1
        reasons.append(AnalysisReason(code="ads", detail="Contains advertising keyword"))

    if "test" in pkg.package_name or "trial" in pkg.package_name:
        risk += 1
        reasons.append(AnalysisReason(code="trial", detail="Trial/demo hint"))

    recommended_action = PackageAction.KEEP
    return AnalysisResult(pkg, risk_score=risk, reasons=reasons, recommended_action=recommended_action)


def analyze_packages(
    packages: Iterable[PackageInfo], preset_name: str, config: AnalyzerConfig = DEFAULT_CONFIG
) -> ActionPlan:
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset '{preset_name}'")
    preset = PRESETS[preset_name]
    rules = config.rules
    items: List[ActionItem] = []

    for pkg in packages:
        result = score_package(pkg, config=config)

        if pkg.package_name in rules.critical_allowlist:
            action = PackageAction.KEEP
            reason = "Critical allowlist"
        elif pkg.is_system and not preset.disable_system_apps:
            action = PackageAction.KEEP
            reason = "System app retained in this preset"
        elif any(r.code == "sensitive" for r in result.reasons):
            action = PackageAction.KEEP
            reason = "Sensitive component"
        else:
            action = preset.decide(result)
            if pkg.is_system and action == PackageAction.UNINSTALL_USER:
                action = PackageAction.DISABLE
                reason = "System app guarded to disable"
            elif action == PackageAction.KEEP:
                reason = "Below preset thresholds"
            elif action == PackageAction.DISABLE:
                reason = result.summarize_reasons() or "Disable via preset"
            else:
                reason = result.summarize_reasons() or "Uninstall via preset"

        result.recommended_action = action
        items.append(ActionItem(package=pkg, action=action, reason=reason))

    return ActionPlan(preset=preset_name, items=items)
