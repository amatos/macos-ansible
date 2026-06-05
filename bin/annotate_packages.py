#!/usr/bin/env python3
"""
Annotates entries in homebrew_installed_packages and homebrew_cask_apps
with descriptions fetched from `brew desc`, appended as YAML comments.
"""

import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_FILE = "homebrew.config.yaml"


def collect_section(lines: list[str], section_key: str) -> list[str]:
    """Return bare package names from a named YAML list section."""
    items = []
    in_section = False
    for line in lines:
        if re.match(rf"^{re.escape(section_key)}\s*:", line):
            in_section = True
            continue
        if in_section:
            bare = re.sub(r"\s*#.*$", "", line.rstrip())
            m = re.match(r"^\s+-\s+(\S+)$", bare)
            if m:
                items.append(m.group(1))
            elif line.strip() and not line[0].isspace():
                break
    return items


def brew_formula_desc(pkg: str) -> tuple[str, str]:
    """Return (pkg, description) for a Homebrew formula via `brew desc`."""
    r = subprocess.run(["brew", "desc", pkg], capture_output=True, text=True)
    for raw in r.stdout.splitlines():
        if ":" in raw:
            return pkg, raw.split(":", 1)[1].strip()
    return pkg, ""


def brew_cask_desc(pkg: str) -> tuple[str, str]:
    """Return (pkg, description) for a Homebrew cask via `brew desc --cask`.

    Output format: 'caskname [✔]: (Display Name) Description text'
    The leading '(Display Name) ' parenthetical is stripped since it's
    redundant with the cask name and clutters the comment.
    """
    r = subprocess.run(["brew", "desc", "--cask", pkg], capture_output=True, text=True)
    for raw in r.stdout.splitlines():
        if ":" in raw:
            desc = raw.split(":", 1)[1].strip()
            desc = re.sub(r"^\([^)]+\)\s*", "", desc)  # strip "(Display Name) "
            return pkg, desc
    return pkg, ""


def fetch_descriptions(pkgs: list[str], fn) -> dict[str, str]:
    """Fetch descriptions for all packages in parallel, printing warnings."""
    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fn, p): p for p in pkgs}
        for future in as_completed(futures):
            pkg, desc = future.result()
            results[pkg] = desc
            if not desc:
                print(f"  WARNING: no description for {pkg!r}")
    found = sum(1 for d in results.values() if d)
    print(f"  {found}/{len(pkgs)} descriptions found.")
    return results


def annotate_section(
    lines: list[str],
    section_key: str,
    descriptions: dict[str, str],
) -> list[str]:
    """Return a new lines list with the named section annotated."""
    new_lines: list[str] = []
    in_section = False

    for line in lines:
        if re.match(rf"^{re.escape(section_key)}\s*:", line):
            in_section = True
            new_lines.append(line)
            continue

        if in_section:
            if line.strip() and not line[0].isspace():
                in_section = False
                new_lines.append(line)
                continue

            bare = re.sub(r"\s*#.*$", "", line.rstrip())
            m = re.match(r"^(\s+-\s+)(\S+)$", bare)
            if m:
                indent, pkg = m.group(1), m.group(2)
                desc = descriptions.get(pkg, "")
                new_lines.append(
                    f"{indent}{pkg} # {desc}\n" if desc else f"{indent}{pkg}\n"
                )
                continue
            new_lines.append(line)
            continue

        new_lines.append(line)

    return new_lines


# ── Main ──────────────────────────────────────────────────────────────────────
with open(CONFIG_FILE) as f:
    lines = f.readlines()

formulae = collect_section(lines, "homebrew_installed_packages")
print(f"Found {len(formulae)} formulae. Fetching descriptions...")
formula_descs = fetch_descriptions(formulae, brew_formula_desc)

casks = collect_section(lines, "homebrew_cask_apps")
print(f"\nFound {len(casks)} casks. Fetching descriptions...")
cask_descs = fetch_descriptions(casks, brew_cask_desc)

lines = annotate_section(lines, "homebrew_installed_packages", formula_descs)
lines = annotate_section(lines, "homebrew_cask_apps", cask_descs)

with open(CONFIG_FILE, "w") as f:
    f.writelines(lines)

print("\nDone — homebrew.config.yaml updated.")
