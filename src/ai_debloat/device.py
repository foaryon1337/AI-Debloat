from __future__ import annotations

import subprocess
from typing import Iterable, List

from .models import ActionItem, PackageInfo, PackageAction


class DeviceInterface:
    """Thin wrapper around adb to allow mocking for tests."""

    def __init__(self, adb_path: str = "adb") -> None:
        self.adb_path = adb_path

    def _run(self, args: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.adb_path, *args], check=True, capture_output=True, text=True
        )

    def check_adb(self) -> bool:
        try:
            self._run(["devices"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def list_packages(self) -> List[PackageInfo]:
        """Return installed packages with paths. Requires adb access."""
        result = self._run(["shell", "pm", "list", "packages", "-f"])
        packages: List[PackageInfo] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or not line.startswith("package:"):
                continue
            # Format: package:/path/to/base.apk=com.example.app
            try:
                path_part, package_name = line.split("=", 1)
            except ValueError:
                continue
            path = path_part.replace("package:", "", 1)
            is_system = any(part in path for part in ["/system/", "/vendor/", "/product/"])
            packages.append(PackageInfo(package_name=package_name, path=path, is_system=is_system))
        return packages

    def apply_action(self, package: PackageInfo, action: PackageAction) -> None:
        if action == PackageAction.KEEP:
            return
        if action == PackageAction.DISABLE:
            self._run(["shell", "pm", "disable-user", "--user", "0", package.package_name])
        elif action == PackageAction.UNINSTALL_USER:
            self._run(["shell", "pm", "uninstall", "--user", "0", package.package_name])

    def batch_apply(self, items: Iterable[ActionItem], dry_run: bool = False) -> None:
        for item in items:
            if dry_run:
                continue
            self.apply_action(item.package, item.action)


class MockDevice(DeviceInterface):
    """Mocked device for tests."""

    def __init__(self, packages: List[PackageInfo]):
        super().__init__(adb_path="adb-mock")
        self._packages = packages
        self.applied: List[tuple[str, PackageAction]] = []

    def _run(self, args: List[str]):  # type: ignore[override]
        raise RuntimeError("MockDevice should not call adb")

    def list_packages(self) -> List[PackageInfo]:  # type: ignore[override]
        return self._packages

    def apply_action(self, package: PackageInfo, action: PackageAction) -> None:  # type: ignore[override]
        self.applied.append((package.package_name, action))
