# AI Debloater

A deeply thought-out, future-proof Android debloater that combines deterministic rules with
context-aware heuristics. It connects to devices over ADB, analyses installed packages, and
applies safety-first presets ranging from **Low** to **Extreme** without breaking boot or core
functionality.

## Features
- **Preset-driven**: Low, Balanced, High, and Extreme levels tuned for different risk profiles.
- **Safety rails**: Always keeps boot-critical and Play Services components; guarded extreme mode.
- **Heuristic analysis**: Scores packages using vendor signatures, tracker keywords, and known
  bloat/spyware corpora.
- **Action planner**: Produces dry-run friendly execution plans before removal/disablement.
- **Reports**: Summary of findings with rationale per package.
- **Extensible**: Rule sets and presets are data-driven for easy tailoring.

## Quickstart
1. Ensure `adb` is installed and your device is visible (`adb devices`).
2. Install the tool in editable mode:
   ```bash
   pip install -e .
   ```
3. View presets and safety notes:
   ```bash
   ai-debloat presets
   ```
4. Run a scan (no changes made):
   ```bash
   ai-debloat scan --preset balanced
   ```
5. Apply actions with a dry run first:
   ```bash
   ai-debloat apply --preset high --dry-run
   # If satisfied
   ai-debloat apply --preset high
   ```
6. Inspect specific packages with curated metadata and risk notes:
   ```bash
   ai-debloat explain com.google.android.gms com.samsung.android.bixby.agent
   ```

## Preset Philosophy
- **Low**: Only disables obvious partner bloat; leaves system apps intact.
- **Balanced**: Removes high-risk third-party bloat and trackers; disables vendor cruft when safe.
- **High**: Aggressively removes partner/advertising bundles while keeping OEM essentials.
- **Extreme**: Maximum removal with reinforced allowlists to keep boot, telephony, and Play
  Services stable.

## Development
- Source is under `src/ai_debloat` with modular components for device IO, analysis, presets, and
  reporting.
- Tests live in `tests/` and use the standard library `unittest` runner.

Run the test suite:
```bash
PYTHONPATH=src python -m unittest
```

## Caveats
- The tool relies on ADB; make sure USB debugging is enabled and authorized.
- Actual package names can differ by OEM/carrier; review dry-run output before applying changes.
- The heuristic corpus is curated to be conservative; extend `data/rules.json`,
  `ai_debloat/data/packages.json`, or `ai_debloat/presets.py` to suit your device fleet.
