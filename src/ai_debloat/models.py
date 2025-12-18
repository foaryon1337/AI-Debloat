from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional


class PackageAction(str, Enum):
    KEEP = "keep"
    DISABLE = "disable"
    UNINSTALL_USER = "uninstall_user"


@dataclass
class PackageInfo:
    package_name: str
    path: Optional[str] = None
    is_system: bool = False
    is_enabled: Optional[bool] = None
    label: Optional[str] = None

    @property
    def identifier(self) -> str:
        return self.label or self.package_name


@dataclass
class AnalysisReason:
    code: str
    detail: str


@dataclass
class AnalysisResult:
    package: PackageInfo
    risk_score: int
    reasons: List[AnalysisReason] = field(default_factory=list)
    recommended_action: PackageAction = PackageAction.KEEP

    def summarize_reasons(self) -> str:
        return "; ".join(r.detail for r in self.reasons)


@dataclass
class Preset:
    name: str
    description: str
    disable_system_apps: bool
    uninstall_user_apps: bool
    threshold_disable: int
    threshold_uninstall: int

    def decide(self, result: AnalysisResult) -> PackageAction:
        if result.risk_score >= self.threshold_uninstall and self.uninstall_user_apps:
            return PackageAction.UNINSTALL_USER
        if result.risk_score >= self.threshold_disable and self.disable_system_apps:
            return PackageAction.DISABLE
        return PackageAction.KEEP


@dataclass
class ActionItem:
    package: PackageInfo
    action: PackageAction
    reason: str


@dataclass
class ActionPlan:
    preset: str
    items: List[ActionItem]

    def __iter__(self) -> Iterable[ActionItem]:
        return iter(self.items)
