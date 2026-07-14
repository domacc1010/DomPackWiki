#!/usr/bin/env python3
"""
build_all.py — the one command to run after updating datapacks.zip.

    python3 tools/extract_data.py /path/to/unzipped/datapacks
    python3 tools/build_all.py

This runs build_static_pages.py (regenerates every template page with the
current nav) and then build_dynamic_pages.py (overlays the 5 pages driven
by extracted datapack JSON) in the correct order, so nothing goes stale or
out of sync.
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

def run(script):
    print(f"\n=== {script} ===")
    result = subprocess.run([sys.executable, os.path.join(HERE, script)])
    if result.returncode != 0:
        print(f"{script} failed — stopping.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    run("build_static_pages.py")
    run("build_dynamic_pages.py")
    print("\nSite rebuilt.")
