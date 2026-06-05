# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An Ansible playbook that provisions a macOS machine — installing Homebrew packages, Mac App Store apps, configuring the Dock, enabling TouchID for sudo, and applying macOS system preferences.

## Running the playbook

Bootstrap a fresh Mac first (installs Xcode CLI tools, Homebrew, Ansible, `mas`, and Ansible Galaxy roles):

```bash
./preflight.sh
```

Run the full playbook:

```bash
ansible-playbook main.yaml --ask-become-pass
```

Run only specific sections using tags:

```bash
ansible-playbook main.yaml --ask-become-pass --tags homebrew
ansible-playbook main.yaml --ask-become-pass --tags dock
ansible-playbook main.yaml --ask-become-pass --tags gpg
ansible-playbook main.yaml --ask-become-pass --tags pam-touchid
ansible-playbook main.yaml --ask-become-pass --tags osx
ansible-playbook main.yaml --ask-become-pass --tags sudoers
ansible-playbook main.yaml --ask-become-pass --tags extra-packages
```

Dry-run (check mode):

```bash
ansible-playbook main.yaml --ask-become-pass --check
```

Lint the playbook:

```bash
ansible-lint main.yaml
yamllint .
```

Install/update Galaxy roles and collections:

```bash
ansible-galaxy install -r requirements.yaml
```

## Configuration system

Settings are split across four committed config files loaded at playbook start:

| File | Controls |
|---|---|
| `default.config.yaml` | Feature toggles (`configure_*` booleans), dotfiles, extra packages |
| `homebrew.config.yaml` | Homebrew formulae, casks, taps |
| `mas.config.yaml` | Mac App Store app IDs |
| `dock.config.yaml` | Dock items (add/remove/position) |

**Local overrides go in `config.yaml`** (gitignored). Any variable defined there overrides the committed defaults. This is the intended way to customize for a specific machine without touching tracked files.

Feature sections are gated by `configure_*` / `install_*` boolean variables in `default.config.yaml`. Setting one to `false` skips that entire section regardless of its tag.

## Architecture

`main.yaml` is the single entry point. It:
1. Loads the four config files plus optional `config.yaml`
2. Runs roles (from `./roles/` or Galaxy collections)
3. Imports task files from `tasks/`

Roles handle broad concerns (Xcode CLI tools, Dock via `geerlingguy.mac.dock`). The custom task files in `tasks/` handle everything else.

Several roles are commented out in `main.yaml` (Homebrew via `geerlingguy.mac.homebrew`, dotfiles, MAS). Homebrew package installation is handled instead by the custom `tasks/homebrew.yaml`, which calls `community.general.homebrew_cask` directly.

## Sudo/privilege escalation

`become: true` is set globally in `ansible.cfg`. Tasks that need sudo use the `bin/mac-askpass.sh` helper (an AppleScript dialog) via the `SUDO_ASKPASS` environment variable. Both `tasks/homebrew.yaml` and `tasks/pam-touchid.yaml` pass this via their `environment:` blocks.

## Adding packages

- **Homebrew formula**: add to `homebrew_installed_packages` in `homebrew.config.yaml`
- **Homebrew cask**: add to `homebrew_cask_apps` in `homebrew.config.yaml`
- **Mac App Store app**: add `{ id: <app_id>, name: "<Name>" }` to `mas_installed_apps` in `mas.config.yaml`
- **Dock item**: add entry to `dockitems_persist` in `dock.config.yaml`

## Supporting scripts

Any supporting scripts or programs (helpers, one-off utilities, maintenance tools) should live in `./bin/`. For example:

- `bin/mac_askpass.sh` — AppleScript sudo helper used by Ansible tasks
- `bin/annotate_packages.py` — annotates `homebrew_installed_packages` entries with `brew desc` descriptions

## Custom Ansible module

`modules/ansible-gpg-key/` contains a local GPG key management module, referenced in `ansible.cfg` via `library = modules/ansible-gpg-key`. The GPG task (`tasks/gpg.yaml`) is currently commented out in `main.yaml`.
