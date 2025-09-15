#!/bin/bash
#
# Unstow All Packages Script
#
# This script is a convenience wrapper to remove all symlinks managed by GNU
# Stow for this dotfiles repository. It serves as the inverse of the 'stow.sh'
# script and includes the same macOS-specific cleanup.
#
# It can unstow all packages by default, or a single specified package.
#
# Usage:
#   ./unstow.sh
#   ./unstow.sh --only <package_name>
#
# Example:
#   # Unstow all packages
#   ./unstow.sh
#   # Unstow only the 'nvim' package
#   ./unstow.sh --only nvim
#

# Determine the absolute path of the dotfiles repository (the directory
# containing this script) to ensure it runs correctly from any location.
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME"

# Change to the dotfiles directory to execute stow commands correctly.
cd "$DOTFILES_DIR" || exit 1

echo "🔍 Finding and removing any .DS_Store files from the repo..."
find . -name ".DS_Store" -delete

# Unstow the packages. By default, it unstows all top-level directories.
# If '--only' is specified, it unstows just that single package.
if [[ "$1" == "--only" && -n "$2" ]]; then
  echo "➖ Unstowing only package: '$2'..."
  stow --delete --target="$TARGET_DIR" "$2"
else
  echo "➖ Unstowing all packages..."
  for folder in */; do
    # Remove trailing slash from folder name
    folder=${folder%/}
    echo "  -> Unstowing '$folder'"
    stow --delete --target="$TARGET_DIR" "$folder"
  done
fi

# Clean up macOS-specific symlinks that were created during the stow process.
if [[ "$(uname)" == "Darwin" ]]; then
  echo "🧹 Cleaning up macOS-specific symlinks..."
  # Check if the Nushell symlink exists before attempting to remove it.
  if [[ -L "$HOME/Library/Application Support/nushell" ]]; then
    rm "$HOME/Library/Application Support/nushell"
    echo "  -> Removed symlink for Nushell."
  fi
fi

echo "✅ Unstow operation complete."