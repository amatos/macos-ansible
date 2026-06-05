#!/usr/bin/env python3
"""
Annotates each entry in homebrew_installed_packages with a description
fetched from `brew desc`, appended as a YAML comment.
"""

import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_FILE = "homebrew.config.yaml"

# ── 1. Read file ──────────────────────────────────────────────────────────────
with open(CONFIG_FILE) as f:
    lines = f.readlines()

# ── 2. Collect package names from homebrew_installed_packages only ─────────────
packages = []
in_section = False
for line in lines:
    if re.match(r"^homebrew_installed_packages\s*:", line):
        in_section = True
        continue
    if in_section:
        # strip any existing comment before extracting name
        bare = re.sub(r"\s*#.*$", "", line.rstrip())
        m = re.match(r"^\s+-\s+(\S+)$", bare)
        if m:
            packages.append(m.group(1))
        elif line.strip() and not line[0].isspace():
            break  # hit the next top-level key

print(f"Found {len(packages)} packages. Fetching descriptions in parallel...")


# ── 3. Fetch descriptions — one call per package so aliases are never a problem ─
def brew_desc(pkg: str) -> tuple[str, str]:
    """Return (pkg, description) using `brew desc`."""
    r = subprocess.run(["brew", "desc", pkg], capture_output=True, text=True)
    for raw in r.stdout.splitlines():
        if ":" in raw:
            return pkg, raw.split(":", 1)[1].strip()
    return pkg, ""


descriptions: dict[str, str] = {}
with ThreadPoolExecutor(max_workers=12) as pool:
    futures = {pool.submit(brew_desc, p): p for p in packages}
    for future in as_completed(futures):
        pkg, desc = future.result()
        descriptions[pkg] = desc
        if not desc:
            print(f"  WARNING: no description found for {pkg!r}")

found = sum(1 for d in descriptions.values() if d)
print(f"Fetched descriptions for {found}/{len(packages)} packages.")

# ── 4. Rewrite only the homebrew_installed_packages section ───────────────────
new_lines: list[str] = []
in_section = False

for line in lines:
    if re.match(r"^homebrew_installed_packages\s*:", line):
        in_section = True
        new_lines.append(line)
        continue

    if in_section:
        # End of section: non-empty line that is not indented
        if line.strip() and not line[0].isspace():
            in_section = False
            new_lines.append(line)
            continue

        # Strip any existing comment, then extract the package name
        bare = re.sub(r"\s*#.*$", "", line.rstrip())
        m = re.match(r"^(\s+-\s+)(\S+)$", bare)
        if m:
            indent, pkg = m.group(1), m.group(2)
            desc = descriptions.get(pkg, "")
            if desc:
                new_lines.append(f"{indent}{pkg} # {desc}\n")
            else:
                new_lines.append(f"{indent}{pkg}\n")
            continue
        # blank lines or anything else pass through unchanged
        new_lines.append(line)
        continue

    new_lines.append(line)

# ── 5. Write back ─────────────────────────────────────────────────────────────
with open(CONFIG_FILE, "w") as f:
    f.writelines(new_lines)

print("Done — homebrew.config.yaml updated.")
