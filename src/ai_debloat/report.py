from __future__ import annotations

from typing import Iterable

from .models import ActionItem, ActionPlan, PackageAction


def format_action_plan(plan: ActionPlan) -> str:
    lines = [f"Preset: {plan.preset}", "", f"Total packages evaluated: {len(plan.items)}"]
    actionable = [item for item in plan.items if item.action != PackageAction.KEEP]
    lines.append(f"Actions to perform: {len(actionable)}")
    lines.append("")
    for item in actionable:
        lines.append(
            f"- {item.package.package_name}: {item.action.value} (reason: {item.reason})"
        )
    if not actionable:
        lines.append("No changes recommended under this preset.")
    return "\n".join(lines)


def summarize_findings(items: Iterable[ActionItem]) -> str:
    counts = {action: 0 for action in PackageAction}
    for item in items:
        counts[item.action] += 1
    return ", ".join(f"{action.value}={counts[action]}" for action in PackageAction)
