#!/usr/bin/env python3
"""
Scan greaterwms/<subpkg> for bomiotconf.ini and emit:
 - bomiot/server/server/discovered_apps.py  (DISCOVERED_APPS list)
 - bomiot/server/server/discovered_imports.py (explicit try/except imports)
This script is intended to be run in CI before packaging.
"""
import argparse
from pathlib import Path

TEMPLATE_APPS = """# GENERATED FILE - do not edit
DISCOVERED_APPS = {apps!r}
"""

TEMPLATE_IMPORTS_HEADER = "# GENERATED FILE - explicit imports to force inclusion by Nuitka\n"
TEMPLATE_IMPORT_TRY = "try:\n    import {module}\nexcept Exception:\n    # ignored during packaging/runtime\n    pass\n\n"

def discover(greaterwms_path):
    apps = []
    p = Path(greaterwms_path)
    if not p.is_dir():
        return apps
    for entry in sorted(p.iterdir()):
        if entry.is_dir() and (entry / "bomiotconf.ini").exists():
            apps.append(f"greaterwms.{entry.name}")
    return apps

def write_files(apps, out_apps, out_imports):
    out_apps_path = Path(out_apps)
    out_apps_path.parent.mkdir(parents=True, exist_ok=True)
    out_apps_path.write_text(TEMPLATE_APPS.format(apps=apps), encoding="utf-8")

    out_imports_path = Path(out_imports)
    out_imports_path.parent.mkdir(parents=True, exist_ok=True)
    with out_imports_path.open("w", encoding="utf-8") as f:
        f.write(TEMPLATE_IMPORTS_HEADER)
        for mod in apps:
            f.write(TEMPLATE_IMPORT_TRY.format(module=mod))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--greaterwms-path", default="greaterwms")
    ap.add_argument("--out-apps", default="bomiot/server/server/discovered_apps.py")
    ap.add_argument("--out-imports", default="bomiot/server/server/discovered_imports.py")
    args = ap.parse_args()

    apps = discover(args.greaterwms_path)
    write_files(apps, args.out_apps, args.out_imports)
    print("Discovered apps:", apps)

if __name__ == "__main__":
    main()