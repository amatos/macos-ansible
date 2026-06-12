# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- **`requirements.yaml`** — Added missing `community.general` collection. The
  `community.general.launchd` module used in the `Restart sshd` handler was
  failing to resolve at runtime because the collection was not declared as a
  dependency.

- **`tasks/macos.yaml`** — Fixed yamllint indentation errors caused by
  multi-line flow mappings in loop items; converted to block-style YAML.
  Corrected Jinja2 spacing (`{{macos.hostname }}` → `{{ macos.hostname }}`).
  Renamed `rosetta` block and inner task to `Install Rosetta` (uppercase
  required by ansible-lint). Switched Rosetta install from `ansible.builtin.shell`
  to `ansible.builtin.command` (no shell features required). Added
  `changed_when: false` to firewall, stealth mode, SSH enable, and Rosetta
  install tasks. Updated `notify:` references to match renamed handlers.

- **`main.yaml`** — Added `ansible.builtin.` FQCNs to all bare `import_tasks`,
  `include_vars`, and `include_tasks` actions. Added `name:` keys to all
  previously unnamed `import_tasks` entries. Renamed handlers to start with an
  uppercase letter (`restart dock` → `Restart dock`, `restart sshd` →
  `Restart sshd`). Added `changed_when: false` to the `killall Dock` handler.

- **`tasks/extra-packages.yaml`** — Added FQCNs to all module actions:
  `composer` → `community.general.composer`, `npm` → `community.general.npm`,
  `gem` → `community.general.gem`, `pip` → `ansible.builtin.pip`.

- **`tasks/gpg.yaml`** — Removed Jinja2 template variables from the middle of
  a task name (ansible-lint `name[template]`). Added `changed_when` to the
  fetch-key task. Added `set -o pipefail` and `executable: /bin/bash` to both
  piped `shell` tasks to satisfy `risky-shell-pipe`.

- **`tasks/homebrew.yaml`** — Added `changed_when: false` to `Trust added taps`
  and `Initialize tealdeer` tasks.

- **`tasks/dotfiles.yaml`** — Added `changed_when: false` to the
  `chezmoi apply` task.

- **`tasks/sudoers.yaml`** — Added FQCNs (`ansible.builtin.command`,
  `ansible.builtin.set_fact`, `ansible.builtin.copy`). Fixed implicit octal
  file mode (`0440` → `"0440"`) to satisfy `yaml[octal-values]`.

- **`tasks/terminal.yaml`** — Added FQCNs to all `command` and `copy` actions.
  Added `mode: "0644"` to the `/tmp/JJG-Term.terminal` copy task to satisfy
  `risky-file-permissions`.

- **`mas.config.yaml`** — Added missing `---` document-start marker.

### Removed

- **`mas.config.yaml`** — Removed PopClip (id: 445189367) from
  `mas_installed_apps`.

### Changed

- **`default.config.yaml`** — Added new `macos` preference defaults:
  `volumeChangeFeedback`, `navPanelExpandedStateForSaveMode` (×2),
  `printPanelExpandedStateForPrint` (×2), `disableLaunchServicesQuarantine`,
  `enableAppleFontSmoothingOnNonRetinaDisplays`, and
  `Screenshots.Format: "png"`.

- **`tasks/macos.yaml`** — Added tasks to apply the new macOS preference
  defaults: disable volume-change feedback, expand save and print panels by
  default, configure screenshot location and format, enable Apple font
  smoothing on non-Retina displays, and disable the Launch Services quarantine
  dialog.

- **`main.yaml`**, **`config.yaml`**, **`default.config.yaml`** — Applied
  `combine(recursive=True)` deep-merge pattern to the `user` dict, matching the
  existing pattern for `macos`. Added `user.gpg_email: ""` default to
  `default.config.yaml`, added `user_overrides: {}` sentinel, renamed `user:`
  to `user_overrides:` in `config.yaml`, and added a `set_fact` merge task in
  `main.yaml` `pre_tasks`.

- **`main.yaml`** — Renamed tag `osx` to `macos` on the `Configure macOS
  settings` import task for consistency with the rest of the project naming.

- **`CLAUDE.md`** — Added `## Changelog` directive instructing future agents to
  update `CHANGELOG.md` with every change.

### Added

- **`.yamllint`** — New project-specific yamllint configuration extending the
  default profile with adjustments appropriate for an Ansible data-file project:
  allows single-space inline comments (used throughout `homebrew.config.yaml`),
  raises the line-length limit to 120 characters as a warning rather than an
  error, permits one space inside flow-mapping braces (`{ name: "...", id: ... }`
  style used in `mas.config.yaml`), disables the mandatory document-start rule
  for vars files, and excludes the `roles/` directory (third-party Galaxy roles).

- **`.ansible-lint`** — New ansible-lint configuration that excludes the
  `roles/` directory from linting (third-party Galaxy roles are not owned by
  this project) and downgrades `yaml[line-length]` violations to warnings.
