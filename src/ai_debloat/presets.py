from __future__ import annotations

import importlib.resources as resources
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .models import Preset


@dataclass
class Rules:
    critical_allowlist: set[str]
    known_bloatware: set[str]
    known_trackers: set[str]
    vendor_signatures: set[str]
    oem_utilities: set[str]
    sensitive_features: set[str]


def load_rules(path: Path | None = None) -> Rules:
    if path:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        with resources.files("ai_debloat.data").joinpath("rules.json").open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    return Rules(
        critical_allowlist=set(payload.get("critical_allowlist", [])),
        known_bloatware=set(payload.get("known_bloatware", [])),
        known_trackers=set(payload.get("known_trackers", [])),
        vendor_signatures=set(payload.get("vendor_signatures", [])),
        oem_utilities=set(payload.get("oem_utilities", [])),
        sensitive_features=set(payload.get("sensitive_features", [])),
    )


PRESETS: Dict[str, Preset] = {
    "low": Preset(
        name="low",
        description="Only touch obvious third-party bloat; keep system apps intact.",
        disable_system_apps=False,
        uninstall_user_apps=True,
        threshold_disable=6,
        threshold_uninstall=8,
    ),
    "balanced": Preset(
        name="balanced",
        description="Remove high-risk bloatware and trackers; disable vendor cruft when safe.",
        disable_system_apps=True,
        uninstall_user_apps=True,
        threshold_disable=4,
        threshold_uninstall=7,
    ),
    "high": Preset(
        name="high",
        description="Aggressive removal of partner/advertising bundles with OEM safeguards.",
        disable_system_apps=True,
        uninstall_user_apps=True,
        threshold_disable=4,
        threshold_uninstall=6,
    ),
    "extreme": Preset(
        name="extreme",
        description="Maximum removal while preserving boot and telephony/Play Services.",
        disable_system_apps=True,
        uninstall_user_apps=True,
        threshold_disable=3,
        threshold_uninstall=5,
    ),
}
