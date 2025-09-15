#!/bin/bash
#
# Stow All Packages Script
#
# This script is a convenience wrapper around GNU Stow to symlink all packages
# (subdirectories) from the dotfiles repository to the target directory. It
# includes special handling for macOS environments and junk file cleanup.
#
# It can stow all packages by default, or a single specified package.
#
# Usage:
#   ./stow.sh
#   ./stow.sh --only <package_name>
#
# Example:
#   # Stow all packages (e.g., nvim, zsh, git)
#   ./stow.sh
#   # Stow only the 'nvim' package
#   ./stow.sh --only nvim
#

# Determine the absolute path of the dotfiles repository (the directory
# containing this script) to ensure it runs correctly from any location.
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME"

# Change to the dotfiles directory to execute stow commands correctly.
cd "$DOTFILES_DIR" || exit 1

# Perform macOS-specific setup for applications like Nushell that may have
# non-standard configuration paths.
if [[ "$(uname)" == "Darwin" ]]; then
  echo "Performing macOS-specific setup..."
  # Ensure the ~/.config directory exists.
  mkdir -p "$HOME/.config"
  # If a real nushell config directory exists, remove it so it can be replaced
  # by a symlink from stow.
  if [[ -e "$HOME/.config/nushell" && ! -L "$HOME/.config/nushell" ]]; then
    echo "Removing existing ~/.config/nushell (which is not a symlink)..."
    rm -rf "$HOME/.config/nushell"
  fi
fi

# Clean up common junk files like .DS_Store from the repository before stowing.
echo "Cleaning up junk files..."
find . -name ".DS_Store" -delete

# Stow the packages. By default, it stows all top-level directories.
# If '--only' is specified, it stows just that single package.
if [[ "$1" == "--only" && -n "$2" ]]; then
  echo "Stowing only package: '$2'..."
  stow --target="$TARGET_DIR" "$2"
else
  echo "Stowing all packages..."
  for folder in */; do
    # Remove trailing slash from folder name
    folder=${folder%/}
    echo "  -> Stowing '$folder'"
    stow --target="$TARGET_DIR" "$folder"
  done
fi

# On macOS, Nushell requires its configuration in a different location.
# This creates a symlink from the stowed config to where Nushell expects it.
if [[ "$(uname)" == "Darwin" ]]; then
  echo "Creating macOS-specific symlinks..."
  # Remove any existing symlink or directory to prevent conflicts.
  if [[ -e "$HOME/Library/Application Support/nushell" ]]; then
    rm -rf "$HOME/Library/Application Support/nushell"
  fi
  # Link the stowed config to the required location.
  ln -s "$HOME/.config/nushell" "$HOME/Library/Application Support/nushell"
  echo "  -> Linked nushell config"
fi

echo "✅ Stow operation complete."
