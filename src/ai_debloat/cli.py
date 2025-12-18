from __future__ import annotations

import argparse
import sys

from .analyzer import analyze_packages
from .device import DeviceInterface
from .models import PackageAction
from .presets import PRESETS
from .report import format_action_plan, summarize_findings
from .knowledge import find_profiles, load_package_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-powered Android debloater")
    parser.add_argument(
        "--preset",
        default="balanced",
        choices=sorted(PRESETS.keys()),
        help="Aggressiveness preset",
    )
    parser.add_argument("--adb-path", default="adb", help="Path to adb binary")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan device and print recommended actions")
    scan.add_argument("--limit", type=int, default=None, help="Limit number of packages processed")

    apply_cmd = subparsers.add_parser("apply", help="Apply preset actions to the device")
    apply_cmd.add_argument("--dry-run", action="store_true", help="Only show actions without executing")

    subparsers.add_parser("presets", help="List preset descriptions")
    explain = subparsers.add_parser("explain", help="Show package metadata and risk notes")
    explain.add_argument("packages", nargs="+", help="Package names to describe")
    return parser


def _ensure_adb(device: DeviceInterface) -> None:
    if not device.check_adb():
        sys.exit("adb not found or device not authorized. Please verify `adb devices`.")


def cmd_presets() -> None:
    for name, preset in PRESETS.items():
        print(f"{name}: {preset.description}")


def cmd_explain(args: argparse.Namespace) -> None:
    db = load_package_db()
    profiles = find_profiles(args.packages, db=db)
    if not profiles:
        print("No profiles found.")
        return
    for profile in profiles:
        print(f\"\\nPackage: {profile.package}\")
        print(f\"Category: {profile.category}\")
        print(f\"Summary: {profile.summary}\")
        print(f\"Removal risk: {profile.removal_risk}\")
        if profile.depends_on:
            print(f\"Depends on: {', '.join(profile.depends_on)}\")
        if profile.notes:
            for note in profile.notes:
                print(f\"- {note}\")


def cmd_scan(args: argparse.Namespace) -> None:
    device = DeviceInterface(adb_path=args.adb_path)
    _ensure_adb(device)
    packages = device.list_packages()
    if args.limit:
        packages = packages[: args.limit]
    plan = analyze_packages(packages, preset_name=args.preset)
    print(format_action_plan(plan))
    print("\nSummary:", summarize_findings(plan.items))


def cmd_apply(args: argparse.Namespace) -> None:
    device = DeviceInterface(adb_path=args.adb_path)
    _ensure_adb(device)
    packages = device.list_packages()
    plan = analyze_packages(packages, preset_name=args.preset)

    if args.dry_run:
        print("Dry-run mode: showing planned actions\n")
        print(format_action_plan(plan))
        return

    for item in plan:
        if item.action == PackageAction.KEEP:
            continue
        print(f"Applying {item.action.value} to {item.package.package_name} ({item.reason})")
        device.apply_action(item.package, item.action)

    print("Done. Summary:", summarize_findings(plan.items))


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "presets":
        cmd_presets()
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "apply":
        cmd_apply(args)
    elif args.command == "explain":
        cmd_explain(args)
    else:
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
