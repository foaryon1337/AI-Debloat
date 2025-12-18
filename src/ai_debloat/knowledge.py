from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "packages.json"


@dataclass
class PackageProfile:
    package: str
    category: str
    summary: str
    depends_on: List[str]
    removal_risk: str
    notes: List[str]

    @property
    def slug(self) -> str:
        return self.package.lower()


def load_package_db(path: Path | None = None) -> Dict[str, PackageProfile]:
    db_path = path or DEFAULT_DB_PATH
    with db_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    profiles: Dict[str, PackageProfile] = {}
    for item in payload:
        profile = PackageProfile(
            package=item["package"],
            category=item.get("category", "unknown"),
            summary=item.get("summary", ""),
            depends_on=item.get("depends_on", []),
            removal_risk=item.get("removal_risk", "unknown"),
            notes=item.get("notes", []),
        )
        profiles[profile.slug] = profile
    return profiles


def find_profiles(names: Iterable[str], db: Optional[Dict[str, PackageProfile]] = None) -> List[PackageProfile]:
    profiles = db or load_package_db()
    results: List[PackageProfile] = []
    for name in names:
        key = name.lower()
        profile = profiles.get(key)
        if profile:
            results.append(profile)
            continue
        # try startswith match for vendor namespaces
        matched = next((p for slug, p in profiles.items() if slug.startswith(key)), None)
        if matched:
            results.append(matched)
    return results
