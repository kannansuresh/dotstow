#!/bin/bash

# Absolute path to dotfiles repo (directory of this script)
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME"

cd "$DOTFILES_DIR" || exit 1

echo "🔍 Finding and removing any .DS_Store files..."
find . -name ".DS_Store" -delete

# Selective unstow
if [[ "$1" == "--only" && -n "$2" ]]; then
  echo "➖ Unstowing only: $2"
  stow --delete --target="$TARGET_DIR" "$2"
else
  echo "➖ Unstowing all folders..."
  for folder in */; do
    folder=${folder%/}
    echo "  Unstowing $folder"
    stow --delete --target="$TARGET_DIR" "$folder"
  done
fi

# Clean up macOS-specific symlink for nushell
if [[ "$(uname)" == "Darwin" ]]; then
  echo "🧹 Cleaning up macOS-specific symlinks..."
  # Check if the symlink exists before attempting to remove it.
  if [[ -L "$HOME/Library/Application Support/nushell" ]]; then
    rm "$HOME/Library/Application Support/nushell"
    echo "  Removed symlink for Nushell."
  fi
fi

echo "✅ Unstow complete."