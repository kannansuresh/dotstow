#!/bin/bash

# Absolute path to dotfiles repo (directory of this script)
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME"

cd "$DOTFILES_DIR" || exit 1

# macOS-specific setup
if [[ "$(uname)" == "Darwin" ]]; then
  mkdir -p "$HOME/.config"
  if [[ -e "$HOME/.config/nushell" && ! -L "$HOME/.config/nushell" ]]; then
    echo "Removing existing ~/.config/nushell (not managed by stow)..."
    rm -rf "$HOME/.config/nushell"
  fi
fi

# Cleanup junk files
find . -name ".DS_Store" -delete

# Selective stow
if [[ "$1" == "--only" && -n "$2" ]]; then
  stow --target="$TARGET_DIR" "$2"
else
  for folder in */; do
    folder=${folder%/}
    stow --target="$TARGET_DIR" "$folder"
  done
fi

# macOS-specific symlink for nushell
if [[ "$(uname)" == "Darwin" ]]; then
  if [[ -e "$HOME/Library/Application Support/nushell" ]]; then
    rm -rf "$HOME/Library/Application Support/nushell"
  fi
  ln -s "$HOME/.config/nushell" "$HOME/Library/Application Support/nushell"
fi
