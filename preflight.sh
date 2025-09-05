#!/usr/bin/env bash

echo "Sanity checking and installing required preflight tools"

# Install command line tooling
if [ ! -e /usr/bin/git ]; then
	echo "Running xcode-select gui for command line tools"
	xcode-select --install
	read -p "Press Enter to continue once command line tools are installed."
fi

# Install home-brew
if [ ! -e /opt/homebrew/bin/brew ]; then
	echo "Installing home-brew"
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Adding homebrew to shell environment
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install ansible
if [ ! -e /opt/homebrew/bin/ansible ]; then
	brew install ansible
fi

# Install mas (mac app store command line tool)
if [ ! -e /opt/homebrew/bin/mas ]; then
	brew install mas
fi

# Installing required packages
ansible-galaxy install -r requirements.yaml

# Ready to run ansible playbooks
echo
echo
echo "Preflight complete."
echo "To run playbooks, enter:"
echo "ansible-playbook main.yaml --ask-become-pass"
